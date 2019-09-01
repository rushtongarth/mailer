import datetime
import pickle as pkl
import operator as op
import collections as co

from base64 import urlsafe_b64decode
from email import message_from_bytes
from googleapiclient.discovery import build
import numpy as np



class Message(object):
    __slots__ = ('ID','Date','Articles')
    
    def __init__(self,message_obj):
        self.ID = message_obj['id']
        self.Date = datetime.datetime.fromtimestamp(
            int(message_obj['internalDate'])/1000.0
        )
        mess = message_from_bytes(
            urlsafe_b64decode(
                message_obj['raw'].encode('ASCII')
            ))
        mess = np.array(mess.as_string().splitlines())
        self._art(mess)
        
    def _art(self,mess):
        _end = np.char.startswith(mess,'%%--%%--%%')
        _end = np.where(_end)[0]
        _art = np.char.startswith(mess,'arXiv:')
        _art = np.where(_art)[0]
        _art = _art[_art < _end[0]]
        slices = np.vstack(
            (_art,np.concatenate((_art[1:],_end)))
        ).T
        self.Articles = np.empty(slices.shape[0],dtype=object)
        for e,s in enumerate(slices):
            self.Articles[e] = np.array(
                [i for i in mess[slice(*s)] if len(i)]
            )
            
        

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
    def __len__(self):
        return self.message_ids.shape[0]
    #def __getitem__(self,idx): to do...
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
        for _id in self.message_ids:
            mess = self.msgs.get(id=_id,**kw).execute()
            news = Message(mess)
        
            
            
            

