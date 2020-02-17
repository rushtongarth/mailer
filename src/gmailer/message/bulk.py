import operator as op
import itertools as it
import numpy as np
import pandas as pd

from src.gmailer.message.message import Message
from src.gmailer.listing.listing import MessageListing


class BulkFetcher(MessageListing):
    """Bulk message listing fetcher
    
    Parameters
    ----------
    credentials: :class:`pickle.pickle` or str
        pickle file or path to pickle file containing the api credentials.
    message_list : :class:`np.ndarray`, optional
        messages id list to use, if unset then the full list will be the
        source of any downstream selections
    count : int, optional
        number of messages to select (default: 10)
    selection : str, optional
        If unset then the first `count` messages from list of 
        message ids will be used.  If set to `'rand'` then a random sample
        of messages of size `count` from message id list will be used
    
    """
    container = []

    def __init__(self, credentials, **kwargs):
        count = kwargs.pop('count',10)
        selection = kwargs.pop('selection',None)
        mlist = kwargs.pop('message_list',None)
        super().__init__(credentials, **kwargs)
        self.gobj = self.service
        if mlist is not None:
            self.mlist = mlist
        else:
            l = len(self)
            if selection == 'rand':
                locs = np.random.randint(0, high=l, size=(count,))
            else:
                locs = np.r_[(l-count):l]
            self.mlist = self.message_ids[locs]
    def __frame(self):
        _arts = map(op.attrgetter('Articles'), self.container)
        _arts = it.chain.from_iterable(_arts)
        attrs = ['artid', 'authors', 'body', 'categories', 'link', 'title']
        arts = map(op.attrgetter(*attrs), _arts)
        self._df = pd.DataFrame(arts, columns=attrs) 

    def __decoder(self, rid, response, exception):
        if exception is not None:
            print(exception)
        else:
            mess = Message(response)
            self.container.append(mess)

    def get(self):
        batch = self.gobj.new_batch_http_request()
        bobj = self.gobj.users().messages()
        kw = dict(userId='me', format='raw')
        for mid in self.mlist:
            kw['id'] = mid
            t = bobj.get(**kw)
            batch.add(t, callback=self.__decoder)
        batch.execute()
    
    @property
    def df(self):
        if len(self.container) == 0:
            self.get()
        if not hasattr(self, '_df'):
            self.__frame()
        return self._df
