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

def self_dups(arts):
  shas = np.fromiter(map(op.attrgetter('shakey'),arts),dtype='U64')
  idx  = np.argsort(shas)
  srt  = shas[idx]
  vals, idx_0, c = np.unique(srt,return_counts=True,return_index=True)
  vals = vals[c > 1]
  loc  = filter(lambda X: X.size>1,np.split(idx,idx_0[1:]))
  loc  = np.array([x for x in loc]).squeeze()
  return vals,loc

def get_idx(array):
  return np.arange(len(array))

def get_db_shas(db_dir,db_file):
  engine = sql.create_engine('sqlite:///'+os.path.join(DBDIR,DBFILE))
  ses = sqlorm.sessionmaker(bind=engine)()
  api = dbapi(ses)
  return np.array([x[0] for x in api.get_cols('shakey').all()],dtype='U64')

def get_mess_shas(article_array):
  sk = op.attrgetter('shakey')
  mp = map(sk,article_array)
  return np.fromiter(mp,dtype='U64')

def db_sha_comp(arts):
  # recalc index
  idx_only = get_idx(arts)
  # get db shas and message shas
  dbshas = get_db_shas(DBDIR,DBFILE)
  msshas = get_mess_shas(arts)
  # compare sha vals
  inter,idx_db,idx_ms = np.intersect1d(dbshas,msshas,return_indices=True)
  # isolate dups and uniques
  #dups = idx_ms
  uniq = arts[~np.isin(idx_only,idx_ms)]
  return idx_ms, uniq

def dedup(arts):
  idx_arts = get_idx(arts)
  val,mess_dup = self_dups(arts)
  _arts = arts[~np.isin(idx_arts,mess_dup)]
  idx, uniq = db_sha_comp(_arts)
  shift = [np.array(i < idx,dtype=int) for i in mess_dup]
  shift = np.sum(shift,axis=0)
  dup_idx = np.concatenate([mess_dup,idx+shift])
  de_duped = arts[~np.isin(idx_arts,dup_idx)]
  return dup_idx, de_duped

def dedup_load(digest):
  ebase,arts = digest.as_dblist()
  dup_idx, de_duped = dedup(arts)
  
  ebase.articles = de_duped.tolist()
  return ebase



