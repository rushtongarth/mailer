import typing
import operator as op
import collections as co
from string import punctuation
import numpy as np
import pandas as pd
from src.gmailer.listing.listing import MessageListing


PandasDF = typing.TypeVar('pandas.core.frame.DataFrame')




def get_authors(listing_obj, idx=0):
    D = co.defaultdict(set)
    arts = listing_obj[idx].Articles
    for x in arts:
        for y in x.authors:
            D[y] |= set(x.authors) - set([y])
    return D


def message_df(idx=0, credentials='creds.pkl'):
    ML = MessageListing(credentials)
    arr = ML[idx]
    attrs = ['artid', 'authors', 'body', 'categories', 'link', 'title']
    get = op.attrgetter(*attrs)
    df = pd.DataFrame(map(get, arr.Articles), columns=attrs)
    return df


def vocab(frame):
    p = punct.replace('.', '').replace('!', '').replace('?', '')
    tr = str.maketrans(dict.fromkeys(p, ' '))
    trans = frame.body.str.translate(tr)
    text = trans.str.replace(r'[.!?]', '@', regex=True)
    text = text.str.replace('\s+', ' ', regex=True)
    text = text.str.replace('\ss\s', 's ', regex=True)
    text = text.str.replace('[0-9]', '#', regex=True)
    text = text.str.split('@').explode().str.strip()
    text = text[text != '']
    return text

def googobj(creds='creds.pkl'):
    import pickle as pkl
    from googleapiclient.discovery import build
    with open(creds, 'rb') as f:
        creds = pkl.load(f)
    return build('gmail', 'v1', credentials=creds)
    

def send_test_gmail(gobj,mess_to,mess_from):
    from email.mime.text import MIMEText
    import base64
    message = MIMEText("<html><h1>Hello</h1><p>World</p></html>",'html')
    message['to'] = mess_to
    message['from'] = mess_from
    message['subject'] = 'testing'
    msg = {'raw': base64.urlsafe_b64encode(message.as_string()).decode()}
    try:
        tosend = gobj.users().messages().send(userId="me",body=msg).execute()
        return tosend
    except Exception as E:
        raise E


class Sanitizer(object):
    
    def __init__(self, fullframe, eos='@', punct=['.', '?', '!']):
        self.df = fullframe
        no_eos = punctuation.translate(
            str.maketrans(dict.fromkeys(punct, '')))
        __punct = dict.fromkeys(no_eos, ' ')
        self.punct_tr = str.maketrans(__punct)
        self.eos_tr = str.maketrans(dict.fromkeys(punct, eos))
        self.eos = eos

    def __vocab(self, series):
        text = series.str.replace('e.g.', 'for example',regex=False)
        text = series.str.replace('i.e.', 'that is',regex=False)
        text = series.str.translate(self.punct_tr)
        text = text.str.translate(self.eos_tr)
        text = text.str.replace('\s+', ' ', regex=True)
        text = text.str.replace('\ss\s', 's ', regex=True)
        text = text.str.replace('[0-9]', '#', regex=True)
        text = text.str.split(self.eos).explode().str.strip()
        return text[text.str.len() > 0]
        
    def vocab(self, col1='body', col2='title', s_s='<s>', s_e='</s>'):
        """Build a vocab as in get to the point."""
        #self._word_to_id = {}
        #self._id_to_word = {}
        ## total number of words
        #self._count = 0
        ## tokens for input padding and out-of-vocab words
        #PAD_TOK, UNK_TOK = '[PAD]', '[UNK]'
        ## start/end of decoder input sequence
        #START, END = '[START]', '[END]'
        ## [UNK], [PAD], [START] and [STOP] get the ids 0,1,2,3.
        #for w in [UNK_TOK, PAD_TOK, START, STOP]:
            #self._word_to_id[w] = self._count
            #self._id_to_word[self._count] = w
            #self._count += 1
        
        #txt = self.__vocab(self.df.get(col1), s_s, s_e)
        # pad the encoder input, decoder input and target sequence
        return s_s + self.__vocab(self.df.get(col1)) + s_e
        
        





