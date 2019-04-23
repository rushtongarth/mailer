import os
import operator as op
import numpy as np
import sqlalchemy as sql
import sqlalchemy.orm as sqlorm
from src.Digest.DailyDigest import DailyDigest
from src.db.api import dbapi
from src.db.schema import EmailBase, ArticleBase



class Cleanup(object):
  def __init__(self,digests,db_dir=None,db_file=None,session=None):
    self.digested = digests
    if session:
      self.ses = session
    else:
      self.dbp = 'sqlite:///'
      self.dbp+= os.path.join(db_dir,db_file)
      engine = sql.create_engine(self.dbp)
      self.ses  = sqlorm.sessionmaker(bind=engine)()
  def get_uniq(self):
    
    C = np.empty(len(self.digested),dtype=EmailBase)
    for e,digs in enumerate(self.digested):
      sc = SingleCleanup(digs,self.p1,self.p2)
      mgdups, dbdups, ebase = sc.dedup_ebase()
      C[e] = sc.ebase
    return C


class SingleCleanup(object):
  '''
  Perform clean up on input daily digest
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
    ''' '''
    self._msg_shas = np.fromiter(
      map(op.attrgetter('shakey'),self._arts),
      dtype='U64')
  def __db_shas(self):
    ''' '''
    shas = dbapi(self.ses).get_cols('shakey').all()
    self._db_shas = np.array([x[0] for x in shas], dtype='U64')
  @property
  def msg_shas(self):
    ''' '''
    if not hasattr(self,'_msg_shas'):
      self.__mess_shas()
    return self._msg_shas
  @property
  def db_shas(self):
    ''' '''
    if not hasattr(self,'_db_shas'):
      self.__db_shas()
    return self._db_shas
  def __mess_dups(self):
    ''' '''
    shas, idx = self.msg_shas, np.argsort(self.msg_shas)
    vals, idx0, c = np.unique(
      shas[idx],return_counts=True,return_index=True)
    splt = np.split(idx,idx0[1:])
    loc  = filter(lambda X: X.size>1,splt)
    self.dup_vals = vals[c > 1]
    self.dup_idx  = np.array([x for x in loc]).squeeze().astype(int)
  def sha_comp(self):
    '''get db shas and message shas, then compare sha vals
    
    :returns: indices of duplicate shas and array of uniq articles
    :rtype: :class:`numpy.ndarray`
    '''
    # recalc index
    idx_arts = np.arange(self._arts.shape[0])
    # get db shas and message shas, then compare sha vals
    ixn, idb, self.idx_ms = np.intersect1d(
      self.db_shas,self.msg_shas,return_indices=True
    )
    # isolate dups and uniques in message
    uniq = self._arts[~np.isin(idx_arts,self.idx_ms)]
    return self.idx_ms, uniq
  def dedup(self):
    ''' '''
    idx_arts  = np.arange(self._arts.shape[0])
    idx, uniq = self.sha_comp()
    dupped    = np.concatenate([self.dup_idx,idx]).astype(int)
    self.arts = self._arts[~np.isin(idx_arts,dupped)]
    return self._arts[self.dup_idx], self._arts[idx], self.arts
  def dedup_ebase(self):
    mgdups,dbdups,a = self.dedup()
    self.ebase.articles = self.arts.tolist()
    return mgdups, dbdups, self.ebase




