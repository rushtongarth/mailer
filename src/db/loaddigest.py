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
  def __hasdups(self,df,col):
    bools = df.duplicated(col,keep=False)
    return bools.any()
  def prep(self):
    attr = ['date','body','link','shakey','title']
    ebase, arts = self.dd.as_dblist()
    art_attr = zip(*map(op.attrgetter(*attr),arts))
    art_dict = dict(zip(attr,art_attr))
    self.df = pd.DataFrame.from_dict(art_dict)
    if self.__hasdups(self.df,'shakey'):
      dups = self.df[self.df.duplicated('shakey',keep=False)].copy()
      dups.update(dups.title.str.upper().str.replace(' ',''))
      # get ratios and keep low values
      #notclose=[
      #  for e,(a,b) in dups[['date'
      
