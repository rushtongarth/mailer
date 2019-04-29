import pandas as pd
import torchtext
import spacy
import sqlalchemy as sql
import sqlalchemy.orm as sqlorm
import numpy as np
from db.api import dbapi

spen = spacy.load('en')
tokz = lambda X: [tok.text for tok in map(spen.tokenizer,X)]

class Preprocess(object):
  '''
  Process text data for model consumption
  
  cols = ['body','title']
  case='lower'
  '''
  def __init__(self,session,**kwargs):
    self.api = dbapi(session)
    self.cols = kwargs.get('cols',['body','title'])
    self.case = kwargs.get('case','lower')
    # internal parms
    data = self.api.as_df(*self.cols)
    self.data = data.reindex(self.cols,axis=1)
  
  @property
  def tocase(self):
    _c = getattr(pd.Series.str,self.case)
    return lambda X: _c(X.str)
    
    
  def __src_prep(self,col):
    to_prep = getattr(self.data,col)
    to_prep = to_prep.str.replace('\s{2,}',' ')
    df_prep = to_prep.str.split(pat='\. ',expand=True)
    for col in df_prep:
      df_prep[col] = '<s>'+df_prep[col]+'</s>'
    to_prep.fillna('<pad>',inplace=True)
  #def

