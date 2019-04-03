from src.db.loader import DataBaser
import operator as op
import itertools as it
import numpy as np
import pandas as pd
import sqlalchemy as sql
from difflib import SequenceMatcher as seqm
from string import punctuation as punct


class LoadDigest(object):
  def __init__(self,digest):
    self.dd = digest
  def prep(self):
    attr = ['date','body','link','shakey','title']
    ebase, arts = self.dd.as_dblist()
    art_attr = zip(*map(op.attrgetter(*attr),arts))
    art_dict = dict(zip(attr,art_attr))
    df = pd.DataFrame.from_dict(art_dict)
    dups = df[df.duplicated('shakey',keep=False)]
    # now use sequence matcher from diff lib
    #diff function
    F = lambda Y: seqm(lambda X: X in punct,Y.title.upper(),Y.body).ratio()
    # get ratios
    dups = dups[dups.apply(F,axis=1)<0.6]
