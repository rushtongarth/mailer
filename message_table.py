import typing
import operator as op
import collections as co
from string import punctuation
import numpy as np
import pandas as pd
from src.gmailer.listing.listing import MessageListing

PandasDF = typing.TypeVar('pandas.core.frame.DataFrame')


def get_authors(listing_obj, idx=0):
    D = co.defaultdict(set)
    arts = listing_obj[idx].Articles
    for x in arts:
        for y in x.authors:
            D[y] |= set(x.authors) - set([y])
    return D


def message_df(idx=0, credentials='creds.pkl'):
    ML = MessageListing(credentials)
    arr = ML[idx]
    attrs = ['artid', 'authors', 'body', 'categories', 'link', 'title']
    get = op.attrgetter(*attrs)
    df = pd.DataFrame(map(get, arr.Articles), columns=attrs)
    return df


def vocab(frame):
    p = punct.replace('.', '').replace('!', '').replace('?', '')
    tr = str.maketrans(dict.fromkeys(p, ' '))
    trans = frame.body.str.translate(tr)
    text = trans.str.replace(r'[.!?]', '@', regex=True)
    text = text.str.replace('\s+', ' ', regex=True)
    text = text.str.replace('\ss\s', 's ', regex=True)
    text = text.str.replace('[0-9]', '#', regex=True)
    text = text.str.split('@').explode().str.strip()
    text = text[text != '']
    return text

def googobj(creds='creds.pkl'):
    import pickle as pkl
    from googleapiclient.discovery import build
    with open(creds, 'rb') as f:
        creds = pkl.load(f)
    return build('gmail', 'v1', credentials=creds)
    

class Sanitizer(object):
    
    def __init__(self, fullframe, eos='@', punct=['.', '?', '!']):
        self.df = fullframe
        no_eos = punctuation.translate(
            str.maketrans(dict.fromkeys(punct, '')))
        __punct = dict.fromkeys(no_eos, ' ')
        self.punct_tr = str.maketrans(__punct)
        self.eos_tr = str.maketrans(dict.fromkeys(punct,eos))
        self.eos = eos

    def __vocab(self, series):
        text = series.str.translate(self.punct_tr)
        text = text.str.translate(self.eos_tr)
        text = text.str.replace('\s+', ' ', regex=True)
        text = text.str.replace('\ss\s', 's ', regex=True)
        text = text.str.replace('[0-9]', '#', regex=True)
        text = text.str.split(self.eos).explode().str.strip()
        text = text[text != '']
        return text
        
        




