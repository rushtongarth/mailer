
from Digest import ArxLoader
from db.loader import DataBaser,ArticleBase,dbinit
import os


THISFILE = os.path.abspath(__file__)
CURR,FNM = os.path.split(THISFILE)
ODIR,ext = os.path.splitext(FNM)

ROOTDIR = os.path.dirname(CURR)
OUTPDIR = os.path.join(ROOTDIR,ODIR)
DATADIR = os.path.join(OUTPDIR,'arxiv.articles.db')

def load_prep(database,abstracts):
  shas = [x.shakey for x in abstracts]
  

def loader_from_digest(Message,Digest,database=DATADIR):
  if not os.path.exists(database):
    dbinit(database)
  abstracts = ArxLoader(Message,Digest)
  with DataBaser(database) as db:
    count = db.load_objs(abstracts)
  return count

def loader_from_abstracts(abstracts,database=DATADIR):
  if not os.path.exists(database):
    dbinit(database)
  with DataBaser(database) as db:
    count = db.load_objs(abstracts)
  return count
