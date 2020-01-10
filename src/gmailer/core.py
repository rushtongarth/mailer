from .listing.listing import MessageListing
from string import punctuation as punct
import pandas as pd
import collections as co
import operator as op



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


def str_app(series, func, *args, **kwargs):
    s1 = getattr(series, 'str')
    s2 = getattr(s1, func)
    return s2(*args, **kwargs)


def build_vocab(frame, col="body"):
    p = punct.replace('.', '')
    d = dict.fromkeys(p, ' ')
    tr = str.maketrans(d)
    text = getattr(frame,col)
    text = str_app(text, 'translate', tr)
    text = str_app(text, 'replace', '\s+', ' ', regex=True)
    text = str_app(text, 'lower')
    text = str_app(text, 'split').explode()
    return text



#
