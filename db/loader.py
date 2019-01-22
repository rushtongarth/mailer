from sqlalchemy.orm import sessionmaker

import sqlalchemy as sql
import numpy as np

from .schema import Base,ArticleBase,EmailBase



def dbinit(dbname):
  DB_LOC = 'sqlite:///'+dbname
  engine = sql.create_engine(DB_LOC)
  Base.metadata.create_all(engine)




class DataBaser(object):
  '''database connector class'''
  def __init__(self,dbname,dbtype='sqlite:///'):
    """DataBaser : database connection class
    Args:
      dbname : str : name of resulting db file
      dbtype : str : database typing string
    """
    self.dbname = dbtype+dbname
  def __enter__(self):
    self.eng = sql.create_engine(self.dbname)
    self.Session = sessionmaker(bind=self.eng)
    self.curr_sess = self.Session()
    return self
  def __exit__(self,*args):
    self.curr_sess.close()
  
  def load_objs(self,list_in):
    '''this needs to be overhauled'''
    pass




  
