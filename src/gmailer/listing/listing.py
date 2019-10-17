import pickle as pkl
import operator as op
import numpy as np
from googleapiclient.discovery import build
from ..message.message import Message


class MessageListing(object):

    """Message listing class

    This class is designed to act as a container for messages
    coming out of an inbox.
    """
    def __init__(self, credentials, **kwargs):
        qstr = " ".join([
            "from:no-reply@arxiv.org",
            "subject:(cs daily)",
        ])
        self.qstr = kwargs.get('query', qstr)
        self.user = "me"
        with open(credentials, 'rb') as f:
            creds = pkl.load(f)
        self.service = build(
            'gmail', 'v1', credentials=creds
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
        ids = map(op.itemgetter('id'), messages)
        self.mids = np.fromiter(ids, dtype=(str, 16))

    def __len__(self):
        return self.message_ids.shape[0]

    def __getitem__(self, idx):
        toget = self.message_ids[idx]
        kw = dict(userId=self.user, format='raw')
        if isinstance(toget, np.ndarray) and len(toget) > 1:
            m = np.array([
                Message(self.msgs.get(id=x, **kw).execute()) for x in toget
            ])
            return m
        else:
            m = self.msgs.get(id=toget, **kw).execute()
            return Message(m)

    def __repr__(self):
        ostr = "<message_ids={mid}|query={qstr}>"
        return ostr.format(
            mid=self.message_ids.shape[0],
            qstr=self.qstr
        )

    @property
    def message_ids(self):
        """list all message ids"""
        if hasattr(self, 'mids'):
            return self.mids
        self.__mids()
        return self.mids
