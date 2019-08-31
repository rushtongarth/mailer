from googleapiclient.discovery import build
import pickle as pkl
import operator as op
import numpy as np
from base64 import urlsafe_b64decode
from email import message_from_bytes

class MessageListing(object):
    
    def __init__(self,credentials,query="from:no-reply@arxiv.org"):
        self.qstr = query
        self.user = "me"
        with open(credentials,'rb') as f:
            creds = pkl.load(f)
        self.service = build(
            'gmail','v1',credentials=creds
        )

        self.msgs = self.service.users().messages()
    
    
    def __mids(self):
        """pull all message ids from email address"""
        messages = []
        kw = dict(userId=self.user, q=self.qstr)
        _msgs = self.msgs.list(**kw)
        msgs = _msgs.execute()
        if 'messages' in msgs:
            messages.extend(msgs['messages'])
        while 'nextPageToken' in msgs:
            kw['pageToken'] = msgs['nextPageToken']
            msgs = self.msgs.list(**kw).execute()
            messages.extend(msgs['messages'])
        ids = map(op.itemgetter('id'),messages)
        self.mids = np.fromiter(ids,dtype=(str,16))
    @staticmethod
    def get_where(array,pattern):
        return np.where(np.char.startswith(array,pattern))[0]

    @property
    def message_ids(self):
        """list all message ids"""
        if hasattr(self,'mids'):
            return self.mids
        self.__mids()
        return self.mids
    def messages(self):
        """list all messages"""
        kw = dict(userId=self.user, format='raw')
        pat1 = 'arXiv:'
        pat2 = '%%--%%--%%'
        for _id in self.message_ids:
            kw['id'] = _id
            mess = self.msgs.get(**kw).execute()['raw'].encode('ASCII')
            _obj = message_from_bytes(urlsafe_b64decode(mess))
            _arr = _obj.as_string().splitlines()
            _old = self.get_where(_arr,pat2)
            _new = self.get_where(_arr,pat1)
            _new = _new[_new < _old[0]]
            col2 = np.concatenate((_new[1:],_old))
            mmat = np.vstack((_new,col2)).T
            

#class MessageReader(object):
#    def __init__(self,credentials,query="from:no-reply@arxiv.org"):


#from googleapiclient.discovery import build
#import pickle as pkl, operator as op, numpy as np, base64, email

#ML = MessageListing(c)
#arr = ML.messages
#mess = ML.msgs.get(userId='me',id=arr[0],format='raw').execute()
#msg_str = base64.urlsafe_b64decode(mess['raw'].encode('ASCII'))
#email_arr = email.message_from_bytes(msg_str).as_string().splitlines()
#repeat_mark = np.where(np.char.startswith(email_arr,'%%--%%--%%'))[0]
#X = np.where(np.char.startswith(email_arr,'arXiv:'))[0]
#X1 = X[X<repeat_mark[0]]
#Y = np.vstack((X1,np.concatenate((X1[1:],loc1)))).T
#articles = [email_arr[slice(*row)] for row in Y]
