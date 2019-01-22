from .AbstractArticle import AbstractArticle
from string import punctuation as pnt
import numpy as np
#
class ArXivArticle(object):
  def __init__(self,text_arr): 
    self.raw = text_arr 
  def __pat_match(self,patt): 
    found = np.char.find(self.raw,patt)+1 
    return np.where(found)[0]
  def __title(self): 
    pat1,pat2 = 'Title: ','Authors: '
    loc1 = self.__pat_match(pat1)
    loc2 = self.__pat_match(pat2)
    pat_range = np.r_[loc1:loc2]
    tstr = ' '.join(self.raw[pat_range])
    self.title  = np.char.replace(tstr,pat1,'')
  def __link(self):
    patt = 'arXiv:'
    locn = self.__pat_match(patt)[:1]
    link = self.raw[locn]
    self.link = np.char.replace(link,patt,'https://arxiv.org/abs/')
  def __cats(self):
    patt = 'Categories: '
    locn = self.__pat_match(patt)
    cats = self.raw[locn]
    self.categories = np.char.replace(cats,patt,'')
  def get_title(self): 
    if not hasattr(self,'title'): 
      self.__title() 
    return self.title
  def get_link(self):
    if not hasattr(self,'link'): 
      self.__link() 
    return self.link
  def get_cats(self):
    if not hasattr(self,'categories'): 
      self.__cats() 
    return self.categories
  
  


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
    self.acats  = ','.join(all_categories.split())
    self.pcats  = pri_categories
    self.ncats  = len(self.pcats.split(','))
    super().__init__(self.dt,self.title,self.link)
  def body_clean(self,text):
    tmp = ' '.join(text)
    npt = ''.join(map(lambda X: ' ' if X in pnt else X,tmp))
    npt = npt.upper().split()
    return ' '.join(npt)
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
