import os
import argparse
from src.db.loader import dbinit

parser = argparse.ArgumentParser('utilities for email parser')
parser.add_argument('-r','--refresh',nargs=1,help='path to new db')

curr_dir = os.path.dirname(os.path.abspath(__file__))

def db_refresh(path=None):
  
  dbp = os.path.join(path,'arxiv.articles.db')
  dbt = 'sqlite:///'
  dbinit(dbt+dbp)
  return os.path.exists(dbp)

if __name__ == '__main__':
  args = parser.parse_args()
  if args.refresh:
    pth = args.refresh
  else:
    pth = curr_dir
  if db_refresh(path=pth):
    print('created db located at:\n{}'.format(pth))
  else:
    print('failed to create db at:\n{}'.format(pth))
  
