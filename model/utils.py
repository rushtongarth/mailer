
import torch

USE_CUDA = torch.cuda.is_available()

class Generator(torch.nn.Module):
  """Define standard linear + softmax generation step."""
  def __init__(self, hidden_size, vocab_size):
    super(Generator, self).__init__()
    self.proj = torch.nn.Linear(hidden_size, vocab_size, bias=False)
  def forward(self, x):
    return torch.nn.functional.log_softmax(self.proj(x), dim=-1)
