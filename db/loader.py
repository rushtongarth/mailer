
import os
import numpy as np
import operator as op
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from .schema import Base,ArticleBase,EmailBase



def dbinit(dbname):
  DB_LOC = dbname
  engine = sql.create_engine(DB_LOC)
  Base.metadata.create_all(engine)

def get_shas(dbpath=None):
  dbpath = 'sqlite:////home/stephen/Code/dev/mailer/db/arxiv.articles.db'                                                                              
  S = sessionmaker(bind=sql.create_engine(dbpath))()
  stmt = sql.text('select shakey from article')
  stmt = stmt.columns(ArticleBase.shakey)
  Q = S.query(ArticleBase.shakey).from_statement(stmt).all()
  shas = np.array(Q).squeeze()
  return shas

#def shacomp(from_db,from_em):
  ##from_db = get_shas(dbpath)
  ##from_em = np.fromiter(map(op.attrgetter('shakey'),incoming.articles),dtype='U64')
  #ix = np.setdiff1d(from_em,from_db)
  #rm = np.where(~np.in1d(from_em,ix))[0]
  ##for idx in rm:
  ##  incoming.articles.pop(idx)
  #return rm
    
  

class DataBaser(object):
  '''database connector class'''
  def __init__(self,dbname,dbtype='sqlite:///'):
    """DataBaser : database connection class
    Args:
      dbname : str : name of resulting db file
      dbtype : str : database typing string
    """
    self.dbname = dbtype+dbname
    if not os.path.exists(self.dbname):
      dbinit(self.dbname)
  def __enter__(self):
    self.eng = sql.create_engine(self.dbname)
    self.Session = sessionmaker(bind=self.eng)
    self.curr_sess = self.Session()
    return self
  def __exit__(self,*args):
    self.curr_sess.close()
  def _shas(self):
    stmt = sql.text('select shakey from article')
    stmt = stmt.columns(ArticleBase.shakey)
    Q = self.curr_sess.query(ArticleBase.shakey).from_statement(stmt)
    self.__shas = np.array(Q.all()).squeeze()
  @property
  def shas(self):
    if not hasattr(self,'__shas'):
      self._shas()
    return self.__shas
  def shacomp(self,incoming):
    from_em = np.fromiter(
      map(
        op.attrgetter('shakey'),
        incoming.articles
      ),dtype='U64')
    ix = np.setdiff1d(from_em,self.shas)
    if len(ix):
      rm = np.where(~np.in1d(from_em,ix))[0]
      rm = sorted(rm,reverse=True)
      for idx in rm:
        try:
          incoming.articles.pop(idx)
        except IndexError as er:
          print(idx,rm)
          raise er

  def load_objs(self,list_in):
    if isinstance(list_in,list):
      L = list_in
    else:
      L = [list_in]
    for x in L:
      self.shacomp(x)
    self.curr_sess.add_all(L)
    self.curr_sess.commit()

  
