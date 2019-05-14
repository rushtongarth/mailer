from . import torch

from .achtung import EncoderAttention, DecoderAttention

class Decoder(torch.nn.Module):
    def __init__(self):
        super(Decoder, self).__init__()
        self.enc_atn = EncoderAttention()
        self.dec_atn = DecoderAttention()
        self.x_context = torch.nn.Linear(config.hidden_dim*2 + config.emb_dim, config.emb_dim)
        self.lstm = torch.nn.LSTMCell(config.emb_dim, config.hidden_dim)
        init_lstm_wt(self.lstm)
        self.p_gen_linear = torch.nn.Linear(config.hidden_dim * 5 + config.emb_dim, 1)
        # p_vocab
        self.V = torch.nn.Linear(config.hidden_dim*4, config.hidden_dim)
        self.V1 = torch.nn.Linear(config.hidden_dim, config.vocab_size)
        init_linear_wt(self.V1)

    def forward(self, x_t, s_t, enc_out, enc_padding_mask, ct_e, extra_zeros, enc_batch_extend_vocab, sum_temporal_srcs, prev_s):
        x = self.x_context(torch.cat([x_t, ct_e], dim=1))
        s_t = self.lstm(x, s_t)
        dec_h, dec_c = s_t
        st_hat = torch.cat([dec_h, dec_c], dim=1)
        ct_e, attn_dist, sum_temporal_srcs = self.enc_attention(st_hat, enc_out, enc_padding_mask, sum_temporal_srcs)
        # intra-decoder attention
        ct_d, prev_s = self.dec_attention(dec_h, prev_s)
        p_gen = torch.cat([ct_e, ct_d, st_hat, x], 1)
        # p_gen dim = bs,1
        p_gen = self.p_gen_linear(p_gen)
        p_gen = torch.sigmoid(p_gen)
        # out dim = bs, 4*n_hid
        out = torch.cat([dec_h, ct_e, ct_d], dim=1)
        # out dim = bs, n_hid
        out = self.V(out)
        # out dim = bs, n_vocab
        out = self.V1(out)
        vocab_dist = torch.nn.functional.softmax(out, dim=1)
        vocab_dist = p_gen * vocab_dist
        attn_dist_ = (1 - p_gen) * attn_dist
        # pointer mechanism (as suggested in eq 9 https://arxiv.org/pdf/1704.04368.pdf)
        if extra_zeros is not None:
            vocab_dist = torch.cat([vocab_dist, extra_zeros], dim=1)
        final_dist = vocab_dist.scatter_add(1, enc_batch_extend_vocab, attn_dist_)
        return final_dist, s_t, ct_e, sum_temporal_srcs, prev_s
