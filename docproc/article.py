from string import punctuation as pnt
from datetime import date
import numpy as np

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sql
#import Column, Integer, String
Base = declarative_base()

class ArticleBase(Base):
  '''Class container for arxiv journals'''
  __tablename__ = 'Article'
  id = sql.Column(sql.Integer, primary_key=True)
  date = sql.Column(sql.String)
  title = sql.Column(sql.String)
  categories = sql.Column(sql.String)
  body = sql.Column(sql.String)
  link = sql.Column(sql.String)
  ncats = sql.Column(sql.Integer)
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
    return ArticleBase(**{
      'date':str(date.today()),
      'title':self.title,
      'categories':self.categories,
      'body':self.body,
      'link':self.link,
      'ncats':self.ncats,
      })

