import os
import operator as op
import numpy as np

import sqlalchemy as sql
import sqlalchemy.orm as sqlorm

from src.Digest.DailyDigest import DailyDigest
from src.db.api import dbapi
from src.db.loader import DataBaser
from src.db.schema import EmailBase,ArticleBase

DBDIR = '/home/stephen/Code/dev/mailer/src/db'                                                                                                       
DBFILE = 'arxiv.articles.db'

def self_dups(dd):
  ebase, arts = dd.as_dblist()
  shas = np.fromiter(map(op.attrgetter('shakey'),arts),dtype='U64')
  idx  = np.argsort(shas)
  srt  = shas[idx]
  vals, idx_0, c = np.unique(srt,return_counts=True,return_index=True)
  vals = vals[c > 1]
  loc  = filter(lambda X: X.size>1,np.split(idx,idx_0[1:]))
  loc  = np.array([x for x in loc]).squeeze()
  return vals,loc

def sha_dedup(digest):
  ebase,arts = digest.as_dblist()
  
  engine = sql.create_engine('sqlite:///'+os.path.join(DBDIR,DBFILE))
  ses = sqlorm.sessionmaker(bind=engine)()
  api = dbapi(ses)
  dbshas = np.array([x[0] for x in api.get_cols('shakey').all()],dtype='U64')
  msshas = np.fromiter(map(op.attrgetter('shakey'),arts),dtype='U64')
  
  inter,idx_db,idx_ms = np.intersect1d(dbshas,msshas,return_indices=True)
  art_dedup = arts[~np.isin(np.arange(len(arts)),idx_ms)]
  ebase.articles = art_dedup.tolist()
  
