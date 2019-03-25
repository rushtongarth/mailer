
from utils import torch

class AttentionLayer(torch.nn.Module):
  """Implements MLP attention"""
  def __init__(self, hidden_size, key_size=None, query_size=None):
    super(AttentionLayer, self).__init__()
    # We assume a bi-directional encoder so key_size is 2*hidden_size
    key_size = 2 * hidden_size if key_size is None else key_size
    query_size = hidden_size if query_size is None else query_size
    self.key_layer = torch.nn.Linear(key_size, hidden_size, bias=False)
    self.query_layer = torch.nn.Linear(query_size, hidden_size, bias=False)
    self.energy_layer = torch.nn.Linear(hidden_size, 1, bias=False)
    # to store attention scores
    self.alphas = None

  def forward(self, query=None, proj_key=None, value=None, mask=None):
    assert mask is not None, "mask is required"
    # We first project the query (the decoder state).
    # The projected keys (the encoder states) were already pre-computated.
    query = self.query_layer(query)
    # Calculate scores.
    scores = self.energy_layer(torch.tanh(query + proj_key))
    scores = scores.squeeze(2).unsqueeze(1)
    # Mask out invalid positions.
    # The mask marks valid positions so we invert it using `mask & 0`.
    scores.data.masked_fill_(mask == 0, -float('inf'))
    # Turn scores to probabilities.
    self.alphas = torch.nn.functional.softmax(scores, dim=-1)
    # The context vector = weighted sum of values
    context = torch.bmm(self.alphas, value)
    # context shape: [B, 1, 2D]
    # alphas  shape: [B, 1, M]
    return context, alphas
