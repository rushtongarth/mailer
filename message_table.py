import typing
import operator as op
import collections as co
from string import punctuation as punct

import pandas as pd
from api_test import MessageListing


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


def str_app(series, func, *args, **kwargs):
    s1 = getattr(series, 'str')
    s2 = getattr(s1, func)
    return s2(*args, **kwargs)

def vocab(frame):
    p = punct.replace('.','').replace('!','').replace('?','')
    d = dict.fromkeys(p, ' ')
    tr = str.maketrans(d)
    trans = frame.body.str.translate(tr)
    text = trans.str.replace(r'[.!?]','@')
    # finish me...

#def build_vocab(frame):
    #p = punct.replace('.','').replace('!','').replace('?','')
    #d = dict.fromkeys(p, ' ')
    #tr = str.maketrans(d)
    ##text = frame.body.explode()
    ##t.str.replace('[0-9]','#')
    #text = str_app(text, 'translate', tr)
    #text = df2.str.replace(r'[.!?]','@')
    #text = str_app(text, 'replace', '\s+', ' ', regex=True)
    #text = str_app(text, 'lower')
    #text = str_app(text, 'split').explode()
    #return text

def batched(creds):
    from googleapiclient.discovery import build
    import googleapiclient.http as gttp
    import numpy as np
    
    kw = dict(
        userId='me',
        q=" ".join(["from:no-reply@arxiv.org","subject:(cs daily)"])
    )
    messages = []
    msgs = service.users().messages().list(**kw) 
    _msgs = msgs.execute() 
    messages.extend(_msgs['messages']) 
    while 'nextPageToken' in _msgs: 
        kw['pageToken'] = _msgs['nextPageToken'] 
        _msgs = service.users().messages().list(**kw).execute() 
        messages.extend(_msgs['messages'])
    ids = np.fromiter(
        map(op.itemgetter('id'), messages),
        dtype=(str, 16)
    )
    batch = gttp.BatchHttpRequest()
    bkw = dict(userId='me', format='raw')
    for mid in ids:
        bkw['id'] = mid
        batch.add(service.users().messages().get(**bkw))
    for request_id in batch._order:
        resp, content = batch._responses[request_id]
        message = json.loads(content)




