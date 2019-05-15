from . import torch

class Encoder(torch.nn.Module):
  
    def __init__(self, input_size, hidden_size, n_layers=1, dropout=0):
        super(Encoder, self).__init__()
        self.n_layers = n_layers
        self.hidden_size = hidden_size
        __drop = 0 if n_layers>1 else dropout
        self.embedding = torch.nn.Embedding(input_size, hidden_size)
        # Initialize GRU
        self.rnn = torch.nn.GRU(
            hidden_size, hidden_size, n_layers,
            dropout = __drop,
            batch_first = True,
            bidirectional = True,
        )
        self.out_cval = torch.nn.Linear(2 * self.hidden_size, self.hidden_size)
        self.out_hval = torch.nn.Linear(2 * self.hidden_size, self.hidden_size)

    def forward(self, in_seqs, in_lens, hidden=None):
        embed = self.embedding(in_seqs)
        # Pack padded batch of sequences for RNN module
        packed = torch.nn.utils.rnn.pack_padded_sequence(
            embed, in_lens, batch_first=True
        )
        e_out, e_hid = self.rnn(packed,hidden)
        e_out, _ = torch.nn.utils.rnn.pad_packed_sequence(
            e_out, batch_first=True
        )
        # e_out dim = bs, n_seq, 2*n_hid
        e_out = e_out.contiguous()
        # e_hid dim = 2, bs, n_hid
        h, c = e_hid
        # bs, 2*n_hid
        h = torch.cat(list(h), dim=1)
        c = torch.cat(list(c), dim=1)
        # bs,n_hid
        h_reduced = torch.nn.functional.relu(self.out_hval(h))
        c_reduced = torch.nn.functional.relu(self.out_cval(c))
        return e_out, (h_reduced, c_reduced)
