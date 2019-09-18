import operator as op
import numpy as np
import pandas as pd
from api_test import Message, MessageListing, Article
import string

def message_df(idx = 0, credentials = 'creds.pkl'):
    ML = MessageListing(credentials)
    arr = ML[idx]
    attrs = ['artid', 'authors', 'body', 'categories', 'link', 'title']
    get = op.attrgetter(*attrs)
    df = pd.DataFrame(map(get,arr.Articles),columns=attrs)
    return df

def build_vocab(frame):
    text = frane.body.explode()
    text = text.str.replace(',','')
    text = text.str.replace('-',' ')
    text = text.str.replace('/',' ')
    text = text.str.lower()
    
