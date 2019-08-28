from googleapiclient.discovery import build
import pickle as pkl
import operator as op
import numpy as np

class MessageListing(object):
    
    def __init__(self,credentials,query="from:no-reply@arxiv.org"):
        self.qstr = query
        self.service = build(
            'gmail','v1',credentials=credentials
        )
        self.msgs = self.service.users().messages()

    @property
    def messages(self):
        if hasattr(self,'mlist'):
            return self.mlist
        messages = []
        kw = dict( userId="me", q=self.qstr )
        _msgs = self.msgs.list(**kw)
        msgs = _msgs.execute()
        if 'messages' in msgs:
            messages.extend(msgs['messages'])
        while 'nextPageToken' in msgs:
            kw['pageToken'] = msgs['nextPageToken']
            msgs = self.msgs.list(**kw).execute()
            messages.extend(msgs['messages'])
        ids = map(op.itemgetter('id'),messages)
        self.mlist = np.fromiter(ids,dtype=(str,16))
        return self.mlist
    
#class MessageReader(object):
#    def __init__(self,credentials,query="from:no-reply@arxiv.org"):


#import base64
#import email
#msg_str = base64.urlsafe_b64decode(mess['raw'].encode('ASCII'))
#mime_msg = email.message_from_bytes(msg_str).as_string().splitlines()
#X = np.where(np.char.startswith(email_arr,'arXiv'))[0]
#sum(np.char.count(email_arr[slice(X[-1],-1)],'\\\\'))
