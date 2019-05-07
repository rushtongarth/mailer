import torch

class Encoder(torch.nn.Module):
  
  def __init__(self, input_size, hidden_size):
    super(Encoder, self).__init__()
    self.hidden_size = hidden_size
    self.embedding = torch.nn.Embedding(input_size, hidden_size)
    self.frwd_gru = torch.nn.GRU(hidden_size, hidden_size, batch_first=True)
    self.bkwd_gru = torch.nn.GRU(hidden_size, hidden_size, batch_first=True)
    self.out_cval = torch.nn.Linear(2 * self.hidden_size, self.hidden_size)
    self.out_hval = torch.nn.Linear(2 * self.hidden_size, self.hidden_size)
  def forward(self,frwd_vals,bkwd_vals):
    bs,max_len,*_ = frwd_vals.size()
    sz1 = bs, max_len, self.hidden_size * 2
    frwd_emb = self.embedding(frwd_vals)
    bkwd_emb = self.embedding(bkwd_vals)
    mask = frwd_vals.eq(0).detach()
    frwd_out,frwd_state = self.frwd_gru(frwd_emb)
    bkwd_out,bkwd_state = self.bkwd_gru(bkwd_emb)
    hidden_concat = torch.cat((frwd_out,bkwd_out),2)
    inv_mask = mask.eq(0).unsqueeze(2)
    inv_mask = inv_mask.expand(sz1).float().detach()
    hidden_out = hidden_concat * inv_mask
    final_hproj = self.out_hval(torch.cat((frwd_state[0].squeeze(0), bkwd_state[0].squeeze(0)), 1))
    final_cproj = self.out_cval(torch.cat((frwd_state[1].squeeze(0), bkwd_state[1].squeeze(0)), 1))
    return hidden_out, final_hproj, final_cproj, mask
