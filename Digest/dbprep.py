from .ArXiv import ArXivDigest
import itertools as it
import numpy as np

class DigestRecord(ArXivDigest):
  
  def __init__(self,subscriptions,message_array,into_db):
    super().__init__(subscriptions,message_array)
    self.out_db = into_db

  def find_abstracts(self):
    
    F = lambda X: np.where(np.char.find(X,'\\\\')+1)[0].shape[0]
    var = filter(lambda Z: F(Z[1])==3,self)
    abstracts = []
    for i,v in var:
      idx = np.where(np.char.find(v,'\\\\')+1)[0]
      idx = (idx  * [0,1,1])+[0,1,0]
      ast = v[slice(*idx[np.where(idx)])]
      abstracts.append((T[i],Ct[i],ast,Lk[i]))
    self.abstracts = abstracts
  def get_abstracts(self):
    if not hasattr(self,'abstracts'):
      self.find_abstracts()
    return self.abstracts
  

