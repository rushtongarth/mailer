import pandas as pd
import torchtext
import spacy
import sqlalchemy as sql
import sqlalchemy.orm as sqlorm
import numpy as np
from db.api import dbapi

class Preprocess(object):
  '''preprocess text data'''
  def __init__(self,session,cols = None):
    self.api = dbapi(session)
    if cols is None:
      cols = ['body','title']
    data = self.api.as_df(*cols)
    self.data = data.reindex(cols,axis=1)
    
  def __src_prep(self,col):
    to_prep = getattr(self.data,col)
    to_prep = to_prep.str.replace('\s{2,}',' ')
    to_prep = to_prep.str.split(pat='. ',expand=True)
    to_prep.fillna('<pad>',inplace=True)

