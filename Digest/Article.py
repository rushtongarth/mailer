
from AbstractArticle import AbstractArticle
from string import punctuation as pnt
#


class Article(AbstractArticle):
  def __init__(self,date_received,title,categories,body,link):
    self.dt    = str(date_received)
    self.title = title
    self.body  = self.body_clean(body)
    self.link  = link
    self.cats  = categories.split()
    self.ncats = len(self.cats)
    super().__init__(date,title,link)
  def body_clean(self,text):
    tmp = ' '.join(text)
    npt = ''.join(map(lambda X: ' ' if X in pnt else X,tmp))
    npt = npt.upper().split()
    return ' '.join(npt)
  def __repr__(self):
    sout = "<Article(date={d},title={t},categories={c})>"
    t1 = self.title if len(self.title)<=30 else self.title[:27]+'...'
    return sout.format(d=self.date,t=t1,c=self.cats,l=self.link)
  
  def format_for_db(self):

    return {
      'date'      : self.dt,
      'title'     : self.title,
      'categories': self.cats,
      'body'      : self.body,
      'link'      : self.link,
      'ncats'     : self.ncats,
      }
