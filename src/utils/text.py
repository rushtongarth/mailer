import pandas as pd
import torch
import torchtext
import sqlalchemy as sql
import sqlalchemy.orm as sqlorm
import numpy as np

from src.db.api import dbapi
from src.utils.dfds import DataFrameDataset

if torch.cuda.is_available():
  DEVICE = torch.device('cuda')
else:
  DEVICE = torch.device('cpu')

class BatchTuple(object):
  def __init__(self, dataset, x_var, y_var):
    self.dataset, self.x_var, self.y_var = dataset, x_var, y_var
  def __iter__(self):
    for batch in self.dataset:
      x = getattr(batch, self.x_var) 
      y = getattr(batch, self.y_var)                 
      yield (x, y)
  def __len__(self):
    return len(self.dataset)



class Preprocess(object):
  '''
  Process text data for model consumption
  
  cols = ['body','title']
  case='lower'
  '''
  def __init__(self,session,**kwargs):
    self.api  = dbapi(session)
    self.cols = kwargs.get('cols',['body','title'])
    self.case = kwargs.get('case','lower')
    # internal parms
    data = self.api.as_df(*self.cols)
    self.data = data.reindex(self.cols,axis=1)
  
  def __dataset(self):
    fld = {
      'tokenize':lambda X: X.split(),
      'lower':True,
      'init_token':'<s>',
      'eos_token':'</s>'
    }
    self.TEXT = torchtext.data.Field(**fld)
    self.F = {'body':TEXT,'title':TEXT}
    self.ds = DataFrameDataset(self.data,F)
    train,testing,valid = df_as_ds.split(split_ratio=[.7,.1,.2])
    self.TEXT.build_vocab(train)
    train_iter,test_iter,valid_iter = torchtext.data.Iterator.splits(
      (train,testing,valid),
      batch_sizes=(16, 256, 256),
      sort_key=lambda X: len(X.body),
      device=DEVICE,
      shuffle=True,
      sort_within_batch=False,
      repeat=False
    )
    train_iter_tuple = BatchTuple(train_iter, "body", "title")
    test_iter_tuple = BatchTuple(val_iter, "body", "title")
    val_iter_tuple = BatchTuple(val_iter, "body", "title")
 
  def prep(self,df_as_ds):
    
    
    train_iter,test_iter, val_iter = data.BucketIterator.splits(
      (trn,test, vld), batch_sizes=(batch_size, int(batch_size*1.6)),
      device=(0 if USE_GPU else -1), 
      sort_key=lambda x: len(x.source),
      shuffle=True, sort_within_batch=False, repeat=False
    )

