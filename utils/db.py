
from db.loader import DataBaser  
import os


THISFILE = os.path.abspath(__file__)
CURR,FNM = os.path.split(THISFILE)
ODIR,ext = os.path.splitext(FNM)

ROOTDIR = os.path.dirname(CURR)
OUTPDIR = os.path.join(ROOTDIR,ODIR)
DATADIR = os.path.join(OUTPDIR,'arxiv.articles.db')




def loader(database=DATADIR,abstracts=[]):
  with DataBaser(database) as db:
    count = db.load_objs(abstracts)
  return count

  
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
  
