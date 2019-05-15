from . import torch, DEVICE


class EncoderAttention(torch.nn.Module):

    def __init__(self,hidden_size):
        super(EncoderAttention, self).__init__()
        hsz_2 = 2 * hidden_size
        self.W_h = torch.nn.Linear(hsz_2, hsz_2, bias=False)
        self.W_s = torch.nn.Linear(hsz_2, hsz_2)
        self.v = torch.nn.Linear(hsz_2, 1, bias=False)

    def forward(self, st_hat, h, enc_padding_mask):
        '''
        Perform attention over encoder hidden states
        
        :param st_hat: decoder hidden state at current time step
        :param h: encoder hidden states
        :param enc_padding_mask:
        
        Computing attention distribution as it is
        calculated as in Bahdanau et al. (2015)
        '''
        # et dim = bs, n_seq, 2*n_hid
        et = self.W_h(h)
        # dec_fea dim = bs,1,2*n_hid
        dec_fea = self.W_s(st_hat).unsqueeze(1)
        # et dim = bs, n_seq, 2*n_hid
        et = torch.tanh(et + dec_fea)
        # et dim -> bs, n_seq
        et = self.v(et).squeeze(2)
        et1 = torch.nn.functional.softmax(et,dim=1)
        # assign 0 probability for padded elements
        attn = et1 * enc_padding_mask
        nmz_fact = attn.sum(1, keepdim=True)
        attn = attn / nmz_fact
        # attn: dim -> bs,1,n_seq
        attn = attn.unsqueeze(1)
        # Compute encoder context vector
        # ct_e: dim -> bs, 1, 2*n_hid
        ct_e = torch.bmm(attn, h)
        ct_e = ct_e.squeeze(1)
        attn = attn.squeeze(1)
        
        return ct_e, attn
#

# adapted from pytorch docs.
# http://pytorch.org/tutorials/intermediate/seq2seq_translation_tutorial.html
class DecoderAttention(torch.nn.Module):
    def __init__(self, hidden_size, output_size, dropout_p=0.1, max_length=MAX_LENGTH):
        super(DecoderAttention, self).__init__()
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.dropout_p = dropout_p
        self.max_length = max_length

        self.embedding = torch.nn.Embedding(self.output_size, self.hidden_size)
        self.attn = torch.nn.Linear(self.hidden_size * 2, self.max_length)
        self.attn_combine = torch.nn.Linear(self.hidden_size * 2, self.hidden_size)
        self.dropout = torch.nn.Dropout(self.dropout_p)
        self.gru = torch.nn.GRU(self.hidden_size, self.hidden_size)
        self.out = torch.nn.Linear(self.hidden_size, self.output_size)

    def forward(self, input, hidden, encoder_outputs):
        embedded = self.embedding(input).view(1, 1, -1)
        embedded = self.dropout(embedded)

        attn_weights = torch.nn.functional.softmax(
            self.attn(torch.cat((embedded[0], hidden[0]), 1)), dim=1)
        attn_applied = torch.bmm(attn_weights.unsqueeze(0),
                                 encoder_outputs.unsqueeze(0))

        output = torch.cat((embedded[0], attn_applied[0]), 1)
        output = self.attn_combine(output).unsqueeze(0)

        output = torch.nn.functional.relu(output)
        output, hidden = self.gru(output, hidden)

        output = torch.nn.functional.log_softmax(self.out(output[0]), dim=1)
        return output, hidden, attn_weights

    def initHidden(self):
        return torch.zeros(1, 1, self.hidden_size, device=DEVICE)



