import os
import functools as ft
import numpy as np
from Digest import DailyDigest
from db import DataBaser,EmailBase,ArticleBase

#sqlalchemy.sql.schema.Column

class dbapi(object):
  '''dbapi : database interface to make my life easier'''
  def __init__(self,session):
    self.Q = session.query
  def get_cols(self,*args,order_col='date'):
    col_names = set([
      'shakey',   'date', 'title', 'pri_cats', 
      'all_cats', 'body', 'link',     'ncats',
      'email_id'
    ])
    ordering = getattr(ArticleBase,order_col)
    col_args = set(args) & col_names
    cols = [
      getattr(ArticleBase,x) for x in col_args
    ]
    no_order = self.Q(*cols)
    return np.array(no_order.order_by(ordering).all())
  @property
  def abstracts(self,order_col='date'):
    ordering = getattr(ArticleBase,order_col)
    no_order = self.Q(ArticleBase.body)
    return np.array(no_order.order_by(ordering).all())
  @property
  def categories(self,order_col='date'):
    ordering = getattr(ArticleBase,order_col)
    no_order = self.Q(ArticleBase.pri_cats,ArticleBase.all_cats)
    return np.array(no_order.order_by(ordering).all())
  @property
  def titles(self,order_col='date'):
    ordering = getattr(ArticleBase,order_col)
    no_order = self.Q(ArticleBase.title)
    return np.array(no_order.order_by(ordering).all())
  @property
  def shas(self,order_by='date'):
    ordering = getattr(ArticleBase,order_col)
    no_order = self.Q(ArticleBase.shakey)
    return np.array(no_order.order_by(ordering).all())
