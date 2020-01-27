import numpy as np
import pickle as pkl
from googleapiclient.discovery import build
from base64 import urlsafe_b64decode
from email import message_from_bytes



def mimic(idx, creds, prepack=False):
    # Get message ids
    qstr = " ".join([
        "from:no-reply@arxiv.org",
        "subject:(cs daily)",
    ])
    messages = []
    kw = dict(userId="me", q=qstr)
    with open(creds, 'rb') as f:
        creds = pkl.load(f)
    service = build('gmail', 'v1', credentials=creds)
    
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
    # 
    m = service_messages.get(id=mids[idx], userId="me", format='raw').execute()
    mess = message_from_bytes(urlsafe_b64decode(m['raw'].encode('ASCII')))
    mess = np.array(mess.as_string().splitlines())
    _end = np.where(np.char.startswith(mess, '%%--%%--%%'))[0]
    trunc = mess[:_end[0]]
    sw = np.where(np.char.startswith(trunc, 'arXiv:'))[0]
    _art = sw[np.where(np.char.startswith(trunc[sw-1],'\\\\'))[0]]
    #_art = np.where(np.char.startswith(mess, 'arXiv:'))[0]
    _art = _art[_art < _end[0]]
    slices = np.vstack((_art, np.concatenate((_art[1:], _end)))).T
    if prepack:
        return mess, slices
    Articles = np.empty(slices.shape[0], dtype=object)
    for e, s in enumerate(slices):
        Articles[e] = np.array([i for i in mess[slice(*s)] if len(i)])
    return Articles

