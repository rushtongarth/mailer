from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sql
import os


THISFILE = os.path.abspath(__file__)
THISDIR = os.path.dirname(THISFILE)
DATADIR = os.path.join(THISDIR,'arxiv.articles.db')

#CREATE_TABLE = '''
#create table Arxiv 
#(
  #date       text,
  #categories text,
  #ncats      integer,
  #title      text,
  #link       text,
  #abstract   blob
#)'''

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
  def __init__(self,date_received,title,categories,body,link):
    self.dt    = ste(date_received)
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
  def format_for_db(self,received_on=None):
    return ArticleBase(**{
      'date':str(dt),
      'title':self.title,
      'categories':self.categories,
      'body':self.body,
      'link':self.link,
      'ncats':self.ncats,
      })

class DataBaser(object):
  '''database connector class
  
  '''
  def __init__(self,dbname,dbtype='sqlite3:///'):
    self.dbname = dbname
  def __enter__(self):
    self.eng = sql.create_engine(dbtype+dbname)
    self.Session = sessionmaker(bind=self.eng)
    self.curr_sess = self.Session()
    return self
  def __exit__(self,*args):
    self.curr_sess.close()
  
  def load_objs(self,list_in):
    N = len(list_in)
    self.arts = np.empty(N,dtype=object)
    for e,(t,c,b,l) in enumerate(list_in):
      A = Article(title=t,categories=c,body=b,link=l)
      self.arts[e] = A.format_for_db()
    self.curr_sess.add_all(self.arts)
    self.curr_sess.commit()
    return N
  def __exit__(self,*args):
    self.curr_sess.close()


def loader(database=DATADIR,abstracts=[]):
  with DataBaser(database) as db:
    count = db.load_objs(abstracts)
  return count

#class ArticleLoader(object):
  #def __init__(self,list_in):
    #self.N = len(list_in)
    #self.objs = list_in
    #self.arts = np.empty(self.N,dtype=object)
  #def get_list(self):
    #for e,(t,c,b,l) in enumerate(self.objs):
      #A = Article(title=t,categories=c,body=b,link=l)
      #self.arts[e] = A.format_for_db()
    #return self.arts
  
  #def load_all(self,session):
    #session.add_all(self.get_list())
    
#def creator(dbname):
  #if os.path.exists(dbname):
    #return 1
  #db = DataBaser(dbname)
  #with db:
    #c = db.get_cursor()
    #c.execute(CREATE_TABLE)
    #db.conn.commit()
  #return 0

#def insertion(articles,dbname=DATADIR):
  #db = DataBaser(dbname)
  #with db:
    #c = db.get_cursor()
    #c.executemany("INSERT INTO Arxiv VALUES (?,?,?,?,?,?)",articles)
    #db.conn.commit()
  
