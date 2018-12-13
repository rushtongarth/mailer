from ArXiv import ArXivDigest


class DigestRecord(ArXivDigest):
  
  def __init__(self,subscriptions,message_array,into_db):
    super().__init__(subscriptions,message_array)
    self.out_db = into_db

  def find_abstracts(self):
    T  = self.get_titles()
    Lk = self.get_links()
    Ct = self.get_categories()
    L1 = self.get_art()
    L2 = np.concatenate((L1[1:],[-1]))
    SL = it.starmap(slice,zip(L1,L2))
    chop = [(e,self.arr[x]) for e,x in enumerate(SL)]
    F = lambda X: np.where(np.char.find(X,'\\\\')+1)[0].shape[0]
    var = filter(lambda Z: F(Z[1])==3,chop)
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
