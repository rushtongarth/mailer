import typing
import operator as op
import collections as co
from string import punctuation
import numpy as np
import pandas as pd
import pickle as pkl
from googleapiclient.discovery import build
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
    return pd.DataFrame(map(get, arr.Articles), columns=attrs)


def str_apply(ser,*args,**kwargs):
    fn = op.methodcaller(*args, **kwargs)
    return fn(getattr(ser,'str'))

class Sanitizer(object):
    
    def __init__(self, fullframe, eos='@', punct=['.', '?', '!']):
        self.df = fullframe
        no_eos = punctuation.translate(
            str.maketrans(dict.fromkeys(punct, '')))
        __punct = dict.fromkeys(no_eos, ' ')
        self.punct_tr = str.maketrans(__punct)
        self.eos_tr = str.maketrans(dict.fromkeys(punct, eos))
        self.eos = eos

    def __vocab(self, column):
        series = self.df.get(column)
        series = (
            series.pipe(str_apply, 'replace', 'e\.\s*g\.', 'for example')
                  .pipe(str_apply, 'replace', 'i\.\s*e\.', 'that is')
                  .pipe(str_apply, 'translate', self.punct_tr)
                  .pipe(str_apply, 'translate', self.eos_tr)
                  .pipe(str_apply, 'replace', '\s+', ' ')
                  .pipe(str_apply, 'replace', '\ss\s', 's ')
                  .pipe(str_apply, 'replace', '[0-9]', '#')
                  .pipe(str_apply, 'split', self.eos)
        )
        text = series.explode().str.strip()
        return text[text.str.len() > 0]
        
    def vocab(self, column_name):
        """Build a vocab as in get to the point."""
        series = self.__vocab(column_name)
        return series
        
        





