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


def vocab(frame, col="body"):
    p = punct.replace('.','').replace('!','').replace('?','')
    tr = str.maketrans(dict.fromkeys(p, ' '))
    to_parse = frame.get(col)
    text = to_parse.str.translate(tr)
    text = text.str.replace(r'[.!?]', '@', regex=True)
    text = text.str.replace('\s+', ' ', regex=True)
    text = text.str.replace('\ss\s', 's ', regex=True)
    text = text.str.replace('[0-9]', '#', regex=True)
    text = text.str.split('@').explode().str.strip()
    text = text[text != '']

#

