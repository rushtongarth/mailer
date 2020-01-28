import pickle as pkl
from base64 import urlsafe_b64decode
from email import message_from_bytes
from googleapiclient.discovery import build


def googobj(creds='creds.pkl'):
    with open(creds, 'rb') as f:
        creds = pkl.load(f)
    return build('gmail', 'v1', credentials=creds)


def get_ids(creds='creds.pkl', count=None, gobj=None):
    # Get message ids
    qstr = " ".join([
        "from:no-reply@arxiv.org",
        "subject:(cs daily)",
    ])
    messages = []
    kw = dict(userId="me", q=qstr)
    if not gobj:
        with open(creds, 'rb') as f:
            creds = pkl.load(f)
        service = build('gmail', 'v1', credentials=creds)
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
        length = mids.size
        part = np.random.randint(length,size=(count,))
        mids = mids[part]
    return mids


class BulkFetcher(object):
    container = []
    def __init__(self, gobj, count, mlist=None):
        self.gobj = gobj
        if mlist:
            self.mlist = mlist
            self.count = len(mlist)
        else:
            self.count = count

    def decoder(self, rid, response, exception):
        if exception is not None:
            print(exception)
        else:
            m = response['raw'].encode('ASCII')
            mess = message_from_bytes(urlsafe_b64decode(m))
            self.container.append(response)

    def bulk(self):
        batch = self.gobj.new_batch_http_request()
        bobj = self.gobj.users().messages()
        kw = dict(userId='me', format='raw')
        for mid in toget:
            kw['id'] = mid
            #t = gobj.users().messages().get(**kw)
            t = bobj.get(**kw)
            batch.add(t, callback=self.decoder)

        return batch.execute()        

#def bulk(gobj, count, mlist=None):
    #if mlist:
        #toget = mlist
    #else:
        #toget = get_ids(gobj=gobj,count=count)

    #container = []
    #def fetch(rid, response, exception):
        #if exception is not None:
            #print(exception)
        #else:
            #m = response['raw']
            #mess = message_from_bytes(urlsafe_b64decode(m['raw'].encode('ASCII')))
            #container.append(response)
    #batch = gobj.new_batch_http_request()
    #kw = dict(userId='me', format='raw')
    #for mid in toget:
        #kw['id'] = mid
        #t = gobj.users().messages().get(**kw)
        #batch.add(t, callback=fetch)
    
    #return batch.execute()

