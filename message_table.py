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



class Sanitizer(object):
    def __init__(self, fullframe, eos='@', punct=['.', '?', '!']):
        self.df = fullframe
        no_eos = punctuation.translate(
            str.maketrans(dict.fromkeys(punct, '')))
        __punct = dict.fromkeys(no_eos, ' ')
        self.punct_tr = str.maketrans(__punct)
        self.eos_tr = str.maketrans(dict.fromkeys(punct, eos))
        self.eos = eos
    @staticmethod
    def strapp(ser, *args, **kwargs):
        atr = op.attrgetter('str')(ser)
        fn = op.methodcaller(*args, **kwargs)
        return fn(atr)
    def __vocab(self, column):
        series = self.df.get(column)
        series = (
            series.pipe(self.strapp, 'replace', 'e\.\s*g\.', 'for example')
                  .pipe(self.strapp, 'replace', 'i\.\s*e\.', 'that is')
                  .pipe(self.strapp, 'translate', self.punct_tr)
                  .pipe(self.strapp, 'translate', self.eos_tr)
                  .pipe(self.strapp, 'replace', '\s+', ' ')
                  .pipe(self.strapp, 'replace', '\ss\s', 's ')
                  .pipe(self.strapp, 'replace', '[0-9]', '#')
                  .pipe(self.strapp, 'split', self.eos)
        )
        text = series.explode().str.strip()
        return text[text.str.len() > 0]
    def vocab(self, series):
        series = self.__vocab(series)
        return series        





