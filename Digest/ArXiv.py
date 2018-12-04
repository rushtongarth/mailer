import itertools as it
import operator as op
import numpy as np
from functools import reduce


class ArXivDigest(object):
  subscriptions = []
  def __init__(self,subscriptions,message_array):
    self.arr = message_array
    self.subscriptions.extend(subscriptions)

  def __get_idx(self,patt):
    '''find indices of pattern in array'''
    return np.where(np.char.find(self.arr,patt)+1)
  
  
  def set_header(self,header_array=None):
    '''Setter for header'''
    if header_array:
      self.head = header_array
    else:
      h1 = np.char.find(self.arr,'Submissions')+1
      h1+= np.char.find(self.arr,'received from')+1
      self.head = np.where(h1)[0]
      h1 = slice(*(self.head+[0,1]))
      self.head = self.arr[h1]

  def get_header(self):
    '''Getter for Header'''
    if hasattr(self,'head'):
      return self.head
    else:
      self.set_header()
      return self.head

  def get_art(self):
    '''Setter for articles'''
    if hasattr(self,'art_posn'):
      return self.art_posn
    else:
      self.set_art()
      return self.art_posn

  def __set_art(self):
    h1 = np.char.find(self.arr,'Submissions')+1
    h1+= np.char.find(self.arr,'received from')+1
    h1 = np.where(h1)[0]+1
    a1 = np.where( np.char.find(self.arr,''.join(['-']*78))+1)[0]
    return a1[a1>h1[-1]]

  def set_art(self,posn_array=None):
    '''Setter for articles'''
    if posn_array:
      self.art_posn = posn_array
    else:
      self.art_posn = self.__set_art()

  def find_links(self):
    _posn = self.__get_idx('https://arxiv.org/abs')[0]
    diffs = _posn[np.where(_posn[1:]-_posn[:-1]<3)[0]+1]
    _posn = _posn[~np.isin(_posn,diffs)]
    self.lks = self.arr[_posn]
    st = np.char.find(self.lks,'https://')
    ed = np.char.find(self.lks,',')-1
    self.links = self.__sl_vctzd('lks',st,ed)

  def get_links(self):
    '''Getter for links'''
    if not hasattr(self,'links'):
      self.find_links()
    return self.links

  def find_categories(self):
    patt = 'Categories: '
    idx = self.__get_idx(patt)
    self.categories = np.char.replace(self.arr[idx],patt,'')

  def get_categories(self):
    if not hasattr(self,'categories'):
      self.find_categories()
    return self.categories

  def find_titles(self):
    pat1,pat2 = 'Title: ','Authors: '
    tp = self.__get_idx(pat1)+self.__get_idx(pat2)
    _ts = [' '.join(self.arr[np.r_[i:j]]) for i,j in np.nditer(tp)]
    self.titles  = np.char.replace(_ts,pat1,'')

  def get_titles(self):
    '''Getter for titles'''
    if not hasattr(self,'titles'):
      self.find_titles()
    return self.titles
  
  def __sl_vctzd(self,array,st,end):
    '''Vectorized string slicer
    parameters:
      array:   str: name of array from self to slice
      st   : array: array of starting positions
      end  : array: array of ending positions
    returns:
      array that has been sliced
    '''
    arr = getattr(self,array)
    a,l = arr.view((str,1)),arr.itemsize//4
    # this doesn't do what is expected
    pos = np.array([np.r_[i:j] for i,j in np.nditer([st,end])])
    ## if lines start and end a different positions then
    ## the broadcast below doesn't have the appropriate dimensions
    ## 
    pos+= np.arange(pos.shape[0])[:,None]*l
    subs= a[pos].tostring()
    return np.frombuffer(subs,dtype=(str,(end-st).max()))
  
  def __cat_prep(self):
    '''determine lengths '''
    C = self.get_categories()
    splt = np.char.split(C,' ')[:,None]
    lens = np.fromiter(map(len,splt[:,0]),dtype=int)
    Cshp = C.shape+(max(lens),)
    self.catmat = np.empty(Cshp,dtype=C.dtype)
    itr = np.nditer([lens,splt],flags=['refs_ok','c_index'])
    with itr:
      for l,c in itr:
        self.catmat[itr.index,:l] = c.item()
    return self.catmat
  
  def cat_grouper(self):
    cm = self.__cat_prep()
    
    return cm

  def slicer(self):
    T = self.get_titles()
    L = self.get_links()
    C = self.get_categories()
    S = sorted(np.nditer((T,L,C)),key=lambda X: X[-1])
    
    
    # TODO zip lens and spl then load into tofill and compare with actual subscriptions
    G = [(len(g),k,g) for k,g in [(k,list(g)) for k,g in it.groupby(S,lambda X:X[-1])]]
    G = sorted(G,key=lambda X: X[0],reverse=True)
    return G,T,L,C

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








