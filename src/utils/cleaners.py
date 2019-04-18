import os
import operator as op
import numpy as np
import sqlalchemy as sql
import sqlalchemy.orm as sqlorm
from src.Digest.DailyDigest import DailyDigest
from src.db.api import dbapi
from src.db.loader import DataBaser
from src.db.schema import EmailBase,ArticleBase



class Cleanup(object):
  def __init__(self,digests,dbdir,dbfile):
    self.digested = digests
    self.p1 = dbdir
    self.p2 = dbfile
  def get_uniq(self):
    C = np.empty(len(self.digested),dtype=tuple)
    for e,digs in enumerate(self.digested):
      sc = SingleCleanup(digs,self.p1,self.p2)
      C[e] = sc.dedup_ebase()
    return C

# bundle into class
class SingleCleanup(object):
  '''
  perform clean up on input daily digest
  clean up consists of 
  
  1. deduping within a single digest
  
  2. deduping records that already exist 
     in the database
  
  Currrently database functionality is built
  around sqlite but this could be generalized
  
  :param digested: preprocessed digest object
  :type digested: :class:`src.Digest.DailyDigest`
  :param str db_dir: database directory
  :param str db_file: database filename
  :param session: database session
  :type session: :class:`sqlalchemy.orm.session.Session`
  '''
  def __init__(self,digested,db_dir=None,db_file=None,session=None):
    self.ebase, self._arts = digested.as_dblist()
    if session:
      self.ses = session
    else:
      self.dbp = 'sqlite:///'
      self.dbp+= os.path.join(db_dir,db_file)
      engine = sql.create_engine(self.dbp)
      self.ses  = sqlorm.sessionmaker(bind=engine)()

    self.__mess_dups()
    
  def __mess_shas(self):
    self._msg_shas = np.fromiter(
      map(op.attrgetter('shakey'),self._arts),
      dtype='U64')
  def __db_shas(self):
    shas = dbapi(self.ses).get_cols('shakey').all()
    self._db_shas = np.array([x[0] for x in shas], dtype='U64')
  @property
  def msg_shas(self):
    if not hasattr(self,'_msg_shas'):
      self.__mess_shas()
    return self._msg_shas
  @property
  def db_shas(self):
    if not hasattr(self,'_db_shas'):
      self.__db_shas()
    return self._db_shas
  def __mess_dups(self):
    shas, idx = self.msg_shas, np.argsort(self.msg_shas)
    vals, idx0, c = np.unique(
      shas[idx],return_counts=True,return_index=True)
    splt = np.split(idx,idx0[1:])
    loc  = filter(lambda X: X.size>1,splt)
    self.dup_vals = vals[c > 1]
    self.dup_idx  = np.array([x for x in loc]).squeeze()
  def sha_comp(self):
    # recalc index
    idx_arts = np.arange(self._arts.shape[0])
    # get db shas and message shas, then compare sha vals
    inter, idx_db, idx_ms = np.intersect1d(
      self.db_shas,self.msg_shas,return_indices=True
    )
    # isolate dups and uniques in message
    self.idx_ms = idx_ms
    uniq = self._arts[~np.isin(idx_arts,idx_ms)]
    return self.idx_ms, uniq
  def dedup(self):
    idx_arts = np.arange(self._arts.shape[0])
    idx, uniq = self.sha_comp()
    # adapt this for removing idx_ms case
    #idx + np.sum(
    #  [np.array(i < idx,dtype=int) for i in self.dup_idx],
    #  axis=0
    #)
    dupped = np.concatenate([self.dup_idx,idx]).astype(int)
    self.dupart = self._arts[dupped]
    self.arts   = self._arts[~np.isin(idx_arts,dupped)]
    return self.dupart, self.arts
  def dedup_ebase(self):
    d,a = self.dedup()
    self.ebase.articles = self.arts.tolist()
    return self.dupart, self.ebase




