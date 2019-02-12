
from Digest import DailyDigest
from db.loader import DataBaser
from db.schema import EmailBase,ArticleBase
import os


THISFILE = os.path.abspath(__file__)
CURR,FNM = os.path.split(THISFILE)
ODIR,ext = os.path.splitext(FNM)

ROOTDIR = os.path.dirname(CURR)
OUTPDIR = os.path.join(ROOTDIR,ODIR)
DATADIR = os.path.join(OUTPDIR,'arxiv.articles.db')


def load_digest(MessageContainer,subscriptions,database=DATADIR,idx=-1):
  DD = DailyDigest(MessageContainer,subscriptions,idx)
  with DataBaser(database) as db:
    erec = EmailBase(**{
      'uid':np.unique(DD.records['mid'])[0],
      'date':str(np.unique(DD.records['date_msg'])[0])
    })
    erec.articles = [
      ArticleBase(**a.format_for_db()) for a in DD.as_dblist()
    ]
    db.curr_sess.add(erec)
    db.curr_sess.commit()

  return 
