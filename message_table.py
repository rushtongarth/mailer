import typing
import operator as op
import numpy as np
import pandas as pd
from api_test import Message, MessageListing, Article
from string import punctuation as punct

PandasDF = typing.TypeVar('pandas.core.frame.DataFrame')

def message_df(idx = 0, credentials = 'creds.pkl'):
    ML = MessageListing(credentials)
    arr = ML[idx]
    attrs = ['artid', 'authors', 'body', 'categories', 'link', 'title']
    get = op.attrgetter(*attrs)
    df = pd.DataFrame(map(get,arr.Articles),columns=attrs)
    return df

def str_app(series,func,*args,**kwargs):
    s1 = getattr(series,'str')
    s2 = getattr(s1,func)
    return s2(*args,**kwargs)

def build_vocab(frame):
    p = punct.replace('.','')
    d = dict.fromkeys(p,' ')
    tr = str.maketrans(d)
    text = frame.body.explode()
    text = str_app(text,'translate',tr)
    text = str_app(text,'replace','\s+',' ',regex=True)
    text = str_app(text,'lower')
    text = str_app(text,'split').explode()
    return text



