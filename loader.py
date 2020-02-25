import pickle as pkl
import operator as op
import numpy as np
from googleapiclient.discovery import build


class GoogleObj(object):
    def __init__(self, credentials, **kwargs):
        qstr = " ".join([
            "from:no-reply@arxiv.org",
            "subject:(cs daily)",
        ])
        self.qstr = kwargs.get('query', qstr)
        self.user = "me"
        with open(credentials, 'rb') as f:
            creds = pkl.load(f)
        self.service = build('gmail', 'v1', credentials=creds)
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
        ids = map(op.itemgetter('id'), messages)
        self._mids = np.fromiter(ids, dtype=(str, 16))

    @property
    def mids(self):
        if hasattr(self, '_mids'):
            self.__mids()
        return self._mids

    def __enter__(self):
        # load available ids to object assuming everything else worked
        self.__mids()
        return self

    def __exit__(self, *args):
        pass







