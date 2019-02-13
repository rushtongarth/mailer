
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

## only loads one at a time
def load_digest(digested,database=DATADIR):
  with DataBaser(database) as db:
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
    db.curr_sess.add(erec)
    db.curr_sess.commit()
  return len(art_list)

def load_container(MessageContainer,subscriptions,database=DATADIR,idx=-1):
  DD = DailyDigest(MessageContainer,subscriptions,idx)
  added = load_digest(DD)
  return added
