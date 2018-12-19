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
    sep= np.char.find(self.arr,''.join(['-']*78))+1
    a1 = np.where( sep )[0]
    return a1[a1>h1[-1]]

  def set_art(self,posn_array=None):
    '''Setter for articles'''
    if posn_array:
      self.art_posn = posn_array
    else:
      self.art_posn = self.__set_art()
  
  def sub_arr(self):
    A = self.get_art()
    junk  = np.ones((A.shape[0],2),dtype=int)
    junk *= -1
    junk[:,0]   = A
    junk[:-1,1] = A[1:]
    prep = [self.arr[slice(*r)] for r in junk]
    self.sub = np.concatenate(prep)
    self.junk = junk-A[0]

  def find_links(self):
    pat1,pat2 = 'Title: ','arXiv:'
    self.sub_arr()
    arxs = np.where(np.char.find(self.sub,pat1)+1)[0]
    axid = self.sub[arxs-3]
    if not np.char.startswith(axid,pat2).all():
      raise RuntimeError('not all arxiv links found')
    links = np.char.replace(axid,pat2,'https://arxiv.org/abs/')
    self.links = np.array([x[0] for x in np.char.split(links,' ')])


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
    str_shape = (end-st).max()
    chopped = np.empty(
      (arr.shape[-1],str_shape),
      dtype=(str,str_shape)
    )
    ix = np.nditer([st,end],flags=['c_index']);
    with ix:
      for i,j in ix:
        el = a[l*ix.index+np.r_[i:j]]
        chopped[ix.index,:len(el)] = el
    mpd = map(lambda X: ''.join(X),chopped)
    return np.fromiter(mpd,dtype=(str,str_shape))
  
  def __cat_prep(self):
    '''determine lengths '''
    C = self.get_categories()
    splt = np.char.split(C,' ')[:,None]
    lens = np.fromiter(map(len,splt[:,0]),dtype=int)
    Cshp = C.shape+(max(lens),)
    self._catmat = np.empty(Cshp,dtype=C.dtype)
    for e,(l,s) in enumerate(zip(lens,splt)):
      self._catmat[e,:l]=s.item()
  
  def cat_grouper(self):
    self.__cat_prep()
    shp = len(self._catmat),len(self.subscriptions)
    cm = np.zeros(shp)
    for e,(tag,desc) in enumerate(self.subscriptions):
      x,y = np.where(np.char.find(self._catmat,tag)+1)
      cm[x,e] = 1
    t,_ = zip(*self.subscriptions)
    tag = np.array(t)
    emp = np.empty_like(tag)
    self.catmat = np.where(cm.astype(bool),tag,emp)
    _,cols = self.catmat.shape
    # find each filled position in category matrix
    ucols,idx = np.unique(self.catmat,axis=0,return_inverse=True)
    cats = dict()
    for i in range(len(ucols)):
      k=','.join(filter(None,ucols[i]))
      cats[k]=np.where(idx==i)
    return cats

  def outcats(self):
    
    cg = self.cat_grouper()
    sb = dict(self.subscriptions)
    T = self.get_titles()
    L = self.get_links()
    C = self.get_categories()
    grouped = []
    # TODO: T,L,C should be same lengths
    #  on 2018-12-17  arXiv:1802.02952 didn't have a link
    #  this broke :(
    for k,idx in cg.items():
      long_cat = ', '.join(map(sb.get,k.split(',')))
      S = sorted(np.nditer((T[idx],L[idx],C[idx])),key=lambda X: X[-1])
      grouped.append((long_cat,S))
    return sorted(grouped,reverse=True)

