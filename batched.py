import pickle as pkl
import operator as op
import numpy as np
from googleapiclient.discovery import build
from src.gmailer.message.message import Message


def googobj(creds='creds.pkl'):
    with open(creds, 'rb') as f:
        creds = pkl.load(f)
    return build('gmail', 'v1', credentials=creds)


def get_ids(creds='creds.pkl', count=None, gobj=None):
    # Get message ids
    qstr = " ".join(["from:no-reply@arxiv.org",
                     "subject:(cs daily)"])
    messages = []
    kw = dict(userId="me", q=qstr)
    if not gobj:
        service = googobj(creds=creds)
    else:
        service = gobj
    service_messages = service.users().messages()
    _msgs = service_messages.list(**kw)
    msgs = _msgs.execute()
    if 'messages' in msgs:
        messages.extend(msgs['messages'])
    while 'nextPageToken' in msgs:
        kw['pageToken'] = msgs['nextPageToken']
        msgs = service_messages.list(**kw).execute()
        messages.extend(msgs['messages'])
    ids = map(op.itemgetter('id'), messages)
    mids = np.fromiter(ids, dtype=(str, 16))
    if count:
        if count < 0:
            mids = mids[count:]
        else:
            length = mids.size
            part = np.random.randint(length, size=(count,))
            mids = mids[part]
    return mids



