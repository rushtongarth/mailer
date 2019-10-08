import datetime
import pickle as pkl
import operator as op
import collections as co

from base64 import urlsafe_b64decode
from email import message_from_bytes
from googleapiclient.discovery import build
import numpy as np
import pandas as pd

class Article(object):
    """Article loader
    
    Load and process articles has the following specific slots
        artid, title, authors, categories, link, body
    
    Parameters
    ----------
        art_obj : article object
        
    """
    __slots__ = ('artid','title','authors','categories','link','body')
    
    def __init__(self,art_obj,**patterns):
        splitter = patterns.get('splitter','\\\\')
        tpat = patterns.get('title','Title: ')
        apat = patterns.get('authors','Authors: ')
        cpat = patterns.get('categories','Categories: ')
        # Need to add a startswith statement to finding
        #  the location of the splitter pattern
        found = np.char.find(art_obj,splitter)+1
        locs = np.where(found)[0]
        #
        head, body = np.split(art_obj,locs)[:2]
        self.artid = head[0].split()[0]
        self.__head(head, tpat, apat, cpat)
        self.__categories(head, cpat)
        self.__body(body)

    def __repr__(self):
        ostr = "<id={0}|title={1}|categories={2}>"
        return ostr.format(
            self.artid, self.title, ','.join(self.categories)
        )

    def __multirow(self, head, start_pattern, end_pattern):
        _range = np.char.startswith(head, start_pattern)
        _range |= np.char.startswith(head, end_pattern)
        idx = np.where(_range)[0]
        try:
            raw = head[slice(*idx)].copy()
        except Exception as E:
            print(np.char.startswith(head, start_pattern))
            print(np.char.startswith(head, end_pattern))
            print(head)
            print(idx)
            raise E
        
        raw[0] = raw[0][len(start_pattern):]
        return np.char.strip(raw)

    def __head(self, head, tpat, apat, cpat):
        self.title = ' '.join(self.__multirow(head, tpat, apat))
        astr = ' '.join(self.__multirow(head, apat, cpat))
        astr = astr.replace(' and ',', ')
        self.authors = np.array(astr.split(', '))
        
        lc = np.char.lower(self.artid.split(':'))
        self.link = 'https://{0}.org/abs/{1}'.format(*lc)
        
    def __categories(self, head, cpat):
        locs = np.char.startswith(head, cpat)
        clist = head[locs].item()[len(cpat):].split()
        self.categories = np.array(clist)

    def __body(self, body):
        onestr = ' '.join(np.char.strip(body[1:]))
        sents = onestr.split('. ')
        self.body = np.array(sents)

#
class Message(object):
    """Message object
    
    Parse messages from email
    """
    __slots__ = ('ID','Date','Articles')
    
    def __init__(self,message_obj,**patterns):
        apos = patterns.get('article','arXiv:')
        epos = patterns.get('end_posn','%%--%%--%%')
        self.ID = message_obj['id']
        self.Date = datetime.datetime.fromtimestamp(
            int(message_obj['internalDate'])/1000.0
        )
        mess = message_from_bytes(
            urlsafe_b64decode(
                message_obj['raw'].encode('ASCII')
            ))
        mess = np.array(mess.as_string().splitlines())
        self._art_proc(mess,apos,epos)

    def __len__(self):
        return self.Articles.shape[0]

    def __repr__(self):
        ostr = "<ID={0}|Date={1:%Y-%m-%d}|Articles={2}>"
        return ostr.format(
            self.ID, self.Date, self.Articles.shape[0]
        )

    def _art_proc(self,mess,apos,epos):
        _end = np.where(np.char.startswith(mess,epos))[0]
        _art = np.where(np.char.startswith(mess,apos))[0]
        _art = _art[_art < _end[0]]
        slices = np.vstack(
            (_art,np.concatenate((_art[1:],_end)))
        ).T
        self.Articles = np.empty(slices.shape[0],dtype=object)
        for e,s in enumerate(slices):
            art = np.array(
                [i for i in mess[slice(*s)] if len(i)]
            )
            self.Articles[e] = Article(art)

class MessageListing(object):
    """Message listing class 
    
    This class is designed to act as a container for messages 
    coming out of an inbox.  
    """
    def __init__(self,credentials,**kwargs):
        qstr = " ".join([
            "from:no-reply@arxiv.org",
            "subject:(cs daily)",
        ])
        self.qstr = kwargs.get('query',qstr)
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

    def __getitem__(self,idx):
        toget = self.message_ids[idx]
        kw = dict(userId = self.user,format = 'raw')
        if isinstance(toget,np.ndarray) and len(toget)>1:
            m = np.array([
                Message(self.msgs.get(id = x,**kw).execute()) for x in toget
            ])
            return m
        else:
            m = self.msgs.get(id = toget,**kw).execute()
            return Message(m)

    def __repr__(self):
        ostr = "<message_ids={mid}|query={qstr}>"
        return ostr.format(
            mid = self.message_ids.shape[0],
            qstr = self.qstr
        )

    @property
    def message_ids(self):
        """list all message ids"""
        if hasattr(self,'mids'):
            return self.mids
        self.__mids()
        return self.mids
    #def article_dataframe(self):
        #attr = ['artid', 'authors', 'body', 'categories', 'link', 'title']
        #data = [
            #[getattr(x,y) for y in attr] for x in arr.Articles
        #]
        #return pd.DataFrame(arr.Articles,columns=attr)
#




def get_authors(listing_obj,idx=0):
    D = co.defaultdict(set)
    arts = listing_obj[idx].Articles
    for x in arts:
        for y in x.authors:
            D[y] |= set(x.authors) - set([y])
    
    return D



 
 
 
 
 
    
#
