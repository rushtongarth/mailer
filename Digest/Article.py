from .AbstractArticle import AbstractArticle
from string import punctuation as punct
import numpy as np
#
punct = punct.replace('.','')

class Article(AbstractArticle):
  def __init__(self,shakey='',
               date_received='9999-99-99',title='',
               pri_categories='',all_categories='',
               body='',link=''):
    self.shakey = shakey
    self.dt     = str(date_received)
    self.title  = title
    self.body   = self.body_clean(body)
    self.link   = link
    self.acats  = ','.join(all_categories)
    self.pcats  = pri_categories
    self.ncats  = len(self.pcats)
    super().__init__(self.dt,self.title,self.link)
  def body_clean(self,text):
    tmp = '. '.join(text)
    npt = ''.join(map(lambda X: ' ' if X in punct else X,tmp))
    return npt.upper()
  def __repr__(self):
    sout = "<Article(date={d},title={t},categories={c})>"
    t1 = self.title if len(self.title)<=30 else self.title[:27]+'...'
    return sout.format(d=self.dt,t=t1,c=self.pcats,l=self.link)
  
  def format_for_db(self):
    '''prep for loading to database'''
    return {
      'shakey'   : self.shakey,
      'date'     : self.dt,
      'title'    : self.title,
      'pri_cats' : self.pcats,
      'all_cats' : self.acats,
      'body'     : self.body,
      'link'     : self.link,
      'ncats'    : self.ncats,
      }
