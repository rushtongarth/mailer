from src.db.loader import DataBaser
import operator as op
import itertools as it
import functools as ft
import numpy as np
import pandas as pd
import sqlalchemy as sql

import string
punct = string.punctuation



class LoadDigest(object):
  def __init__(self,digest,session):
    self.dd = digest
  def dedup(self):
    frame = self.dd.as_df()
    subdf = frame[['body','title','link']]
    dfdup = subdf.duplicated(subset=['link','title'],keep=False)
    _dups = subdf[dfdup].sort_values(by='link')
    #idx1  = _dups[_dups.body.ne(_dups.title)].index
    idx  = _dups[_dups.body.eq(_dups.title)].index
    return frame.drop(index=idx)
