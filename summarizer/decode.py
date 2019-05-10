from . import torch

class PointerAttention(torch.nn.Module):
  '''
  :param input_size:
  :param hidden_size:
  :param vocab_size:
  :param wordEmbed:
  :param min_length:
  '''
  def __init__(self, input_size, hidden_size, vocab_size, wordEmbed, min_length=40):
    super(PointerAttention, self).__init__()
    self.input_size  = input_size
    self.hidden_size = hidden_size
    self.vocab_size  = vocab_size
    self.word_embed  = wordEmbed
    self.decoderRNN  = torch.nn.GRU(self.input_size, self.hidden_size, batch_first=True)
    # parms for attention
    self.Wh = torch.nn.Linear(2 * self.hidden_size, 2*self. hidden_size)
    self.Ws = torch.nn.Linear(self.hidden_size, 2*self.hidden_size)
    self.w_c = torch.nn.Linear(1, 2*self.hidden_size)
    self.v = torch.nn.Linear(2*self.hidden_size, 1)
    # parms for p_gen
    # w_h is doubled due to concat of BiDi encoder states
    self.w_h = torch.nn.Linear(2 * self.hidden_size, 1)
    self.w_s = torch.nn.Linear(self.hidden_size, 1)
    self.w_x = torch.nn.Linear(self.input_size, 1)
    # parms for output proj
    self.V = torch.nn.Linear(self.hidden_size * 3, self.vocab_size)
    self.min_length = min_length
  def forward(self, fwd_val, bkd_val):
    pass
#
