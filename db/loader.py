
import os
import numpy as np
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
  shas = np.fromiter(map(lambda X: X[0], Q),dtype='U64')
  return shas


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
  
  def load_objs(self,list_in):
    self.curr_sess.add_all([list_in])
    self.curr_sess.commit()

  
