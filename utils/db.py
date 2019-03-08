
from Digest import DailyDigest
from db import DataBaser,EmailBase,ArticleBase
import os
import numpy as np


THISFILE = os.path.abspath(__file__)
CURR,FNM = os.path.split(THISFILE)
ODIR,ext = os.path.splitext(FNM)

ROOTDIR = os.path.dirname(CURR)
OUTPDIR = os.path.join(ROOTDIR,ODIR)
DATADIR = os.path.join(OUTPDIR,'arxiv.articles.db')

def build_erec(digested):
  '''consume a daily digest and return loadable email
  '''
  email_id = int(np.unique(digested.records['mid'])[0])
  date_str = str(np.unique(digested.records['date_msg'])[0])
  erec = EmailBase(**{
    'uid':email_id,
    'date':date_str
  })
  art_list = [
    ArticleBase(**a.format_for_db()) for a in digested.as_dblist()
  ]
  erec.articles = art_list
  return erec

## only loads one at a time
def load_digest(digested,database=DATADIR):
  erec = build_erec(digested)
  with DataBaser(database) as db:
    db.load_objs(erec)
  return len(erec.articles)

def load_container(MessageContainer,subscriptions,database=DATADIR,idx=-1):
  DD = DailyDigest(MessageContainer,subscriptions,idx)
  added = load_digest(DD)
  return added

def bulk_loader(MessageContainer,subscriptions):
  mc_len  = len(MessageContainer)
  to_load = [0]*mc_len
  MC = lambda X: (
    X,
    DailyDigest(MessageContainer,subscriptions,X)
  )
  for e,dig in map(MC,range(mc_len)):
    erec = EmailBase(**{
      'uid':int(np.unique(dig.records['mid'])[0]),
      'date':str(np.unique(dig.records['date_msg'])[0]),
    })
    arts = [
      ArticleBase(**a.format_for_db()) for a in dig.as_dblist()
    ]
    erec.articles = arts
    to_load[e] = erec
  return to_load
