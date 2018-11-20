import sqlite3
import os

THISFILE = os.path.abspath(__file__)
THISDIR = os.path.dirname(THISFILE)
DATADIR = os.path.join(THISDIR,'arxiv.articles.db')

CREATE_TABLE = '''
create table Arxiv 
(
  date       text,
  categories text,
  ncats      integer,
  title      text,
  link       text,
  abstract   blob
)'''


class DataBaser(object):
  '''database connector class
  
  '''
  def __init__(self,dbname):
    self.dbname = dbname
  def __enter__(self):
    self.conn = sqlite3.connect(self.dbname)
    return self.conn
  def get_cursor(self):
    self.cursor = self.conn.cursor()
    return self.cursor
  def __exit__(self,*args):
    self.conn.close()


def creator(dbname):
  if os.path.exists(dbname):
    return 1
  db = DataBaser(dbname)
  with db:
    c = db.get_cursor()
    c.execute(CREATE_TABLE)
    db.conn.commit()
  return 0

def insertion(articles,dbname=DATADIR):
  db = DataBaser(dbname)
  with db:
    c = db.get_cursor()
    c.executemany("INSERT INTO Arxiv VALUES (?,?,?,?,?,?)",articles)
    db.conn.commit()
  
