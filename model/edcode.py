
from utils import torch

class EncodeDecode(torch.nn.Module):
  """
  A standard Encoder-Decoder architecture. Base for this and many 
  other models.
  """
  def __init__(self,
               encoder, decoder,
               src_embed, trg_embed,
               generator):
    super(EncodeDecode, self).__init__()
    self.encoder = encoder
    self.decoder = decoder
    self.src_embed = src_embed
    self.trg_embed = trg_embed
    self.generator = generator

  def forward(self, src, trg, src_mask, trg_mask, src_lengths, trg_lengths):
    """Take in and process masked src and target sequences."""
    encoder_hl, encoder_fl = self.encode(src, src_mask, src_lengths)
    return self.decode(encoder_hl, encoder_fl, src_mask, trg, trg_mask)
    
  def encode(self, src, src_mask, src_lengths):
    return self.encoder(self.src_embed(src), src_mask, src_lengths)
    
  def decode(self, encoder_hidden, encoder_final, src_mask, trg, trg_mask,
             decoder_hidden=None):
  return self.decoder(self.trg_embed(trg), encoder_hidden, encoder_final,
                      src_mask, trg_mask, hidden=decoder_hidden)


