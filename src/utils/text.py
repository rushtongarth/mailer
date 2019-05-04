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

class Preprocess(object):
  '''
  Process text data for model consumption
  
  :param session: database session to use for API connection
  :type session: :class:`sqlalchemy.orm.session`
  :param columns: list of columns to consider
  :type columns: List[str]
  :param case: case conversion string
  :param split_ratio: list of ratios to split the data
  :param batch_sizes: batch sizes for data
  
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
      'tokenize':lambda X: X.split(),
      'include_lengths':True, 'batch_first':True,
      'lower':case, 'eos_token':'</s>',
      'unk_token':'<unk>', 'pad_token':'<pad>'
    }
    self.TEXT = torchtext.data.Field(init_token=None,**fld)
    self.LABL = torchtext.data.Field(init_token='<s>',**fld)
  @property
  def dataset(self):
    if hasattr(self,'__ds'):
      return self.__ds
    for c in self.data:
      tmp = getattr(self.data,c)
      tmp.update(tmp.str.replace('\s{2,}',' '))
    # 
    F = {'body': self.TEXT, 'title': self.LABL}
    self.__ds = DataFrameDataset(self.data,F)
    return self.__ds
    

  def prep(self):
    '''
    returns list of batch tuples for train,test,validation
    in that order
    '''
    train,test,valid = self.dataset.split(split_ratio=self.sp_r)
    self.TEXT.build_vocab(train.body)
    self.LABL.build_vocab(train.title)
    tr_it,te_it,vd_it = torchtext.data.Iterator.splits(
      (train,test,valid),
      batch_sizes=self.b_sz,
      sort_key=lambda X: len(X.body),
      device=DEVICE,
      shuffle=True, sort_within_batch=False, repeat=False
    )
    #return [Batched(x, "body", "title") for x in [tr_it,te_it,vd_it]]
    return tr_it,te_it,vd_it
#








