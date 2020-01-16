import typing
import operator as op
import collections as co
from string import punctuation as punct
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

def debug(idx, creds):
    import pickle as pkl
    from googleapiclient.discovery import build
    from base64 import urlsafe_b64decode
    from email import message_from_bytes

    qstr = " ".join([
        "from:no-reply@arxiv.org",
        "subject:(cs daily)",
    ])
    qstr = kwargs.get('query', qstr)
    messages = []
    kw = dict(userId="me", q=qstr)
    with open(credentials, 'rb') as f:
        creds = pkl.load(f)
    service = build('gmail', 'v1', credentials=creds)
    _msgs = service.users().messages()
    msgs = _msgs.list(**kw).execute()
    if 'messages' in msgs:
        messages.extend(msgs['messages'])
    while 'nextPageToken' in msgs:
        kw['pageToken'] = msgs['nextPageToken']
        msgs = msgs.list(**kw).execute()
        messages.extend(msgs['messages'])
    ids = map(op.itemgetter('id'), messages)
    mids = np.fromiter(ids, dtype=(str, 16))

    m = msgs.get(id=mids[idx], userId="me", format='raw').execute()
    mess = message_from_bytes(urlsafe_b64decode(m['raw'].encode('ASCII'))
    mess = np.array(mess.as_string().splitlines())
    _end = np.where(np.char.startswith(mess, '%%--%%--%%'))[0]
    _art = np.where(np.char.startswith(mess, 'arXiv:'))[0]
    _art = _art[_art < _end[0]]
    slices = np.vstack((_art, np.concatenate((_art[1:], _end)))).T
    Articles = np.empty(slices.shape[0], dtype=object)
    for e, s in enumerate(slices):
        art = np.array([i for i in mess[slice(*s)] if len(i)])
        Articles[e] = Article(art)
    return Articles





