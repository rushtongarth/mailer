from sqlalchemy.orm import sessionmaker
#from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sql
import numpy as np

from .schema import Base

#Base = declarative_base()

#class ArticleBase(Base):
  #'''Class container for arxiv journals'''
  #__tablename__ = 'Article'
  #shakey   = sql.Column(sql.String(64), primary_key=True)
  #date     = sql.Column(sql.String)
  #title    = sql.Column(sql.Text)
  #pri_cats = sql.Column(sql.String)
  #all_cats = sql.Column(sql.String)
  #body     = sql.Column(sql.Text)
  #link     = sql.Column(sql.String)
  #ncats    = sql.Column(sql.Integer)
  #def __repr__(self):
    #sout = "<Article(date={d},title={t},categories={c})>"
    #t1 = self.title if len(self.title)<30 else self.title[:27]+'...'
    #return sout.format(d=self.date,t=t1,c=self.pri_cats,l=self.link)

def dbinit(dbname):
  DB_LOC = 'sqlite:///'+dbname
  engine = sql.create_engine(DB_LOC)
  Base.metadata.create_all(engine)


class DataBaser(object):
  '''database connector class
  
  '''
  def __init__(self,dbname,dbtype='sqlite:///'):
    self.dbname = dbtype+dbname
  def __enter__(self):
    self.eng = sql.create_engine(self.dbname)
    self.Session = sessionmaker(bind=self.eng)
    self.curr_sess = self.Session()
    return self
  def __exit__(self,*args):
    self.curr_sess.close()
  
  def load_objs(self,list_in):
    
    known = [r[0] for r in self.curr_sess.query(ArticleBase.shakey)]
    up_list = [x for x in list_in if x.shakey not in known]
    N = len(up_list)
    self.arts = np.empty(N,dtype=object)
    for e,art in enumerate(up_list):
      A = ArticleBase(**art.format_for_db())
      self.arts[e] = A
    self.curr_sess.add_all(self.arts)
    self.curr_sess.commit()
    return N
  def __exit__(self,*args):
    self.curr_sess.close()


  
