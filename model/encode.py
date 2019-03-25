
from utils import torch

class Encoder(torch.nn.Module):
  """Encoder: encode a sequence of word embeddings"""
  def __init__(self, input_size, hidden_size, num_layers=1, dropout=0.):
    super(Encoder, self).__init__()
    self.nlayers = num_layers
    self.rnn = torch.nn.GRU(
      input_size, hidden_size, num_layers,
      batch_first=True,
      bidirectional=True,
      dropout=dropout
    )

  def forward(self, x, mask, lengths):
    """
    Applies a B-GRU to sequence of embeddings x.
    The input mini-batch x needs to be sorted by length.
    x should have dimensions [batch, time, dim].
    """
    packed = torch.nn.utils.rnn.pack_padded_sequence(
      x, lengths,
      batch_first=True
    )
    output, final = self.rnn(packed)
    output, _ = torch.nn.utils.rnn.pad_packed_sequence(
      output, batch_first=True
    )
    # we need to manually concatenate 
    # the final states for both directions
    final = torch.cat([
      final[0:final.size(0):2], # forward
      final[1:final.size(0):2], # backward
      dim=2
    ]) # [num_layers, batch, 2*dim]

    return output, final
