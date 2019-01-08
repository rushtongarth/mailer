from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as sql


#THISFILE = os.path.abspath(__file__)
#THISDIR = os.path.dirname(THISFILE)
#DATADIR = os.path.join(THISDIR,'arxiv.articles.db')

Base = declarative_base()

class ArticleBase(Base):
  '''Class container for arxiv journals'''
  __tablename__ = 'Article'
  id       = sql.Column(sql.Integer, primary_key=True)
  date     = sql.Column(sql.String)
  title    = sql.Column(sql.Text)
  pri_cats = sql.Column(sql.String)
  all_cats = sql.Column(sql.String)
  body     = sql.Column(sql.Text)
  link     = sql.Column(sql.String)
  ncats    = sql.Column(sql.Integer)
  def __repr__(self):
    sout = "<Article(date={d},title={t},categories={c})>"
    t1 = self.title if len(self.title)<30 else self.title[:27]+'...'
    return sout.format(d=self.date,t=t1,c=self.categories,l=self.link)
  


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


  
