from src.db.loader import DataBaser
import operator as op
import itertools as it
import numpy as np
import pandas as pd
import sqlalchemy as sql
import difflib as diff
import string

punct = string.punctuation



class LoadDigest(object):
  def __init__(self,digest):
    self.dd = digest
    self.sm = diff.SequenceMatcher(lambda X: X in punct)
  def __ratio(self,X,Y):
    # diff function to calculate diffs
    self.sm.set_seqs(X,Y)
    return self.sm.ratio()
  def __dups(self,attrlist):
    idx  = np.argsort(attrlist)
    srt  = attrlist[idx]
    vals, idx_0, c = np.unique(srt,return_counts=True,return_index=True)
    vals = vals[c > 1]
    loc  = np.split(idx,idx_0[1:])
    loc  = list(filter(lambda X: X.size>1,loc))
    return vals,loc
  def prep(self):
    attr = ['date','body','link','shakey','title']
    ebase, arts = self.dd.as_dblist()
    shas = np.fromiter(map(op.attrgetter('shakey'),arts),dtype='U64')
    vals,loc = self.__dups(shas)
    if vals:
      #compare and keep one
      pass
