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

class Batched(object):
  '''
  
  '''
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
    self.cols = kwargs.get('columns',['body','title'])
    _case = kwargs.get('case','lower')
    case = True if _case=='lower' else False
    self.sp_r = kwargs.get('split_ratio',[.7,.1,.2])
    self.b_sz = kwargs.get('batch_sizes',(16, 256, 256))
    # internal parms
    self.data = self.api.as_df(*self.cols).reindex(self.cols,axis=1)
    fld = {
      'tokenize':lambda X: X.split(),'include_lengths':True,
      'lower':case,'init_token':'<s>','eos_token':'</s>'
    }
    self.TEXT = torchtext.data.Field(**fld)
    F = {'body':TEXT,'title':TEXT}
    self.ds = DataFrameDataset(self.data,F)

  def batch_tuples(self):
    '''
    returns list of batch tuples for train,test,validation
    in that order
    '''
    train,testing,valid = self.ds.split(split_ratio=self.sp_r)
    self.TEXT.build_vocab(train)
    tr_it,te_it,vd_it = torchtext.data.Iterator.splits(
      (train,testing,valid),
      batch_sizes=self.b_sz,
      sort_key=lambda X: len(X.body),
      device=DEVICE,
      shuffle=True, sort_within_batch=False, repeat=False
    )
    return [Batched(x, "body", "title") for x in [tr_it,te_it,vd_it]]
    
 
    
    


