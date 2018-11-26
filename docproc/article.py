from string import punctuation as pnt
from datetime import date
import numpy as np

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
Base = declarative_base()
class ArticleBase(Base):
  '''Class container for arxiv journals'''
  __tablename__ = 'Article'
  id = Column(Integer, primary_key=True)
  date = Column(String)
  title = Column(String)
  categories = Column(String)
  body = Column(String)
  link = Column(String)
  ncats = Column(Integer)
  def __repr__(self):
    sout = "<Article(date={d},title={t},categories={c})>"
    t1 = self.title if len(self.title)<30 else self.title[:27]+'...'
    return sout.format(d=self.date,t=t1,c=self.categories,l=self.link)
  
class Article(object):
  
  def __init__(self,title,categories,body,link):
    self.title = title
    self.categories = categories
    self.body = self.body_clean(body)
    self.link = link
    self.ncats = len(categories.split())
  def body_clean(self,text):
    tmp = ' '.join(text)
    npt = ''.join(map(lambda X: ' ' if X in pnt else X,tmp))
    npt = npt.upper().split()
    return ' '.join(npt)
  def format_for_db(self):
    #dt = str(date.today())
    return ArticleBase(**{
      'date':str(date.today()),
      'title':self.title,
      'categories':self.categories,
      'body':self.body,
      'link':self.link,
      'ncats':self.ncats,
      })
  def load(self):
    

class ArticleList(Article):
  def __init__(self,list_in):
    self.N = len(list_in)
    self.objs = list_in
    self.arts = np.empty(self.N,dtype=object)
  def get_list(self):

    for e,(t,c,b,l) in enumerate(self.objs):
      A = Article(title=t,categories=c,body=b,link=l)
      self.arts[e] = A.format_for_db()
    return self.arts
      
