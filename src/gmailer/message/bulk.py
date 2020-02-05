import operator as op
import itertoools as it
import numpy as np
import pandas as pd

from src.gmailer.message.message import Message


class BulkFetcher(object):
    container = []

    def __init__(self, gobj, count=10, mlist=None):
        self.gobj = gobj
        if mlist is not None:
            self.mlist = mlist
            self.count = len(mlist)
        else:
            self.count = count
            self.mlist = get_ids(count=count, gobj=gobj)

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
        _arts = map(op.attrgetter('Articles'), self.container)
        _arts = it.chain.from_iterable(_arts)
        attrs = ['artid', 'authors', 'body', 'categories', 'link', 'title']
        arts = map(op.attrgetter(*attrs), _arts)
        self._df = pd.DataFrame(arts, columns=attrs)
        return self._df
