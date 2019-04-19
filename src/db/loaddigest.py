
import operator as op
import itertools as it
import functools as ft
import string
import numpy as np
import pandas as pd
import sqlalchemy as sql

from contextlib import ContextDecorator
from src.db.loader import DataBaser

punct = string.punctuation

class LoadHelper(object):
  def __init__(self,session):
    self.sessn = session
    
  def load(self,toload):
    if isintance(toload,(list,tuple)):
      add_op = self.sessn.add_all
    else:
      add_op = self.sessn.add
    try:
      add_op(toload)
      self.sessn.commit()
      retval = 0
    except:
      self.session.rollback()
      retval = -1


class LoadDigest(ContextDecorator):
  """Provide a transactional scope around a series of operations.
  
  :param str dbdir: directory containing database
  :param str dbfile: database filename
  """
  def __init__(self,dbdir,dbfile):
    path = os.path.join(dbdir,dbfile)
    self.db = 'sqlite:///'+path
    self.engine = sql.create_engine(self.db)
  
  def __enter__(self):
    _ses = sqlorm.sessionmaker(bind=self.engine)
    self.session = _ses()
    return LoadHelper(self.session)
  def __exit__(self):
    self.session.close()
  
