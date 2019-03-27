
from utils import torch,Generator,USE_CUDA
from encode import Encoder
from decode import Decoder
from attention import AttentionLayer
from edcode import EncodeDecoder


def make_model(src_vocab, tgt_vocab, emb_size=256, h_size=512, num_layers=1, dropout=0.1):
    "Helper: Construct a model from hyperparameters."

    attention = AttentionLayer(h_size)

    model = EncoderDecoder(
        Encoder(emb_size, h_size, num_layers=num_layers, dropout=dropout),
        Decoder(emb_size, h_size, attention, num_layers=num_layers, dropout=dropout),
        torch.nn.Embedding(src_vocab, emb_size),
        torch.nn.Embedding(tgt_vocab, emb_size),
        Generator(hidden_size, tgt_vocab))

    return model.cuda() if USE_CUDA else model


def train(
