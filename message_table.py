import operator as op
import numpy as np
import pandas as pd
from api_test import Message, MessageListing, Article
from string import punctuation

def message_df(idx = 0, credentials = 'creds.pkl'):
    ML = MessageListing(credentials)
    arr = ML[idx]
    attrs = ['artid', 'authors', 'body', 'categories', 'link', 'title']
    get = op.attrgetter(*attrs)
    df = pd.DataFrame(map(get,arr.Articles),columns=attrs)
    return df

def build_vocab(frame):
    d = dict.fromkeys(punctuation,' ')
    tr = str.maketrans(d)
    text = frame.body.explode()
    text = text.str.translate(tr)
    text = text.str.replace('\s+',' ',regex=True)
    text = text.str.lower()
    text = text.str.split().explode()
    return text
    
    
