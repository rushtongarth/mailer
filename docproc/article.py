from string import punctuation as pnt
from datetime import date
import numpy as np
class Article(object):
  '''Class container for arxiv journals'''
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
    dt = str(date.today())
    return (dt,self.categories,self.ncats,self.title,self.link,self.body)

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
      
