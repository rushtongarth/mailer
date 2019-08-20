from googleapiclient.discovery import build
import pickle as pkl


class MessageListing(object):
    
    def __init__(self,credentials,query="from:no-reply@arxiv.org"):
        self.qstr = query
        self.service = build(
            'gmail','v1',credentials=credentials
        )
        self.msgs = self.service.users().messages()
        #self.msgs = msgs.list(userId="me",q=query).execute()

    @property
    def messages(self):
        if hasattr(self,'mlist'):
            return self.mlist
        self.mlist = []
        _msgs = self.msgs.list(userId="me",q=self.query)
        msgs = _msgs.execute()
        if 'messages' in msgs:
            self.mlist.extend(msgs['messages'])
        kw = dict(
            userId="me",
            q=self.qstr
        )
        while 'nextPageToken' in msgs:
            kw['pageToken'] = msgs['nextPageToken']
            msgs = self.msgs.list(**kw).execute()
            self.mlist.extend(msgs['messages'])
        return self.mlist



