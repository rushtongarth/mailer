import os
import operator as op
import itertools as it
import numpy as np
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from .schema import Base,ArticleBase,EmailBase



def dbinit(dbname):
  DB_LOC = dbname
  engine = sql.create_engine(DB_LOC)
  Base.metadata.create_all(engine)

def get_shas(dbpath):
  S = sessionmaker(bind=sql.create_engine(dbpath))()
  stmt = sql.text('select shakey from article')
  stmt = stmt.columns(ArticleBase.shakey)
  Q = S.query(ArticleBase.shakey).from_statement(stmt).all()
  shas = np.array(Q).squeeze()
  return shas

class DataBaser(object):
  '''database connector class'''
  def __init__(self,dbname,dbtype='sqlite:///'):
    """DataBaser : database connection class

    :param str dbname: name of resulting db file
    :param str dbtype: database typing string
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
    self.curr_sess.commit()
    self.curr_sess.close()
