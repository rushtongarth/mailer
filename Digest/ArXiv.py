import itertools as it
import operator as op
import numpy as np
from string import punctuation as puncn
from functools import reduce

def title_link(x):
  p = np.char.find(x,'Title')
  p+= np.char.find(x,'https://arxiv.org')+2
  return np.sum(p>0)
def multi_drop(X,strs):
  Y = X.copy()
  for s in strs:
    Y = np.char.replace(Y,s,'')
  return np.char.strip(Y)

def grab_patt(X):
  patts = (
    'Title:','Categories:','https://arxiv.org'
    )
  return X.startswith(patts)

class ArXivDigest(object):
  def __init__(self,message_array):
    self.arr = message_array

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

  def cat_to_onehot(self):
    self.find_categories()
    tmp = np.char.split(self.categories,' ')
    unq = reduce(lambda X,Y: X.union(Y),map(set,tmp))
    self.unq = np.array(sorted(unq))
    mp = map(lambda X: np.intersect1d(X,self.unq,return_indices=True),tmp)
    _,_,idx = zip(*mp)
    self.zs  = np.zeros((len(self.unq),len(idx)))
    
    

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
    pos = np.array([np.r_[i:j] for i,j in np.nditer([st,end])])
    pos+= np.arange(pos.shape[0])[:,None]*l
    subs= a[pos].tostring()
    return np.frombuffer(subs,dtype=(str,(end-st).max()))

  def slicer(self):
    T = self.get_titles()
    L = self.get_links()
    C = self.get_categories()
    S = sorted(np.nditer((T,L,C)),key=lambda X: X[-1])
    G = [(len(g),k,g) for k,g in [(k,list(g)) for k,g in it.groupby(S,lambda X:X[-1])]]
    G = sorted(G,key=lambda X: X[0],reverse=True)
    return G,T,L,C
  def get_discriptions(self):
    
    L1 = self.get_art()
    L2 = np.concatenate((L1[1:],[-1]))
    sl = it.starmap(slice,zip(L1,L2))
    chop = [self.arr[x] for x in sl]
    disc = filter(lambda Y: len(' '.join(Y).split('\\\\'))>3,chop)
    for a in disc:
      t,b = ' '.join(a).split('\\\\')[1:-1]
      ts = t[t.find('Title: ')+6:t.find("Authors:")].strip()
      bs = ''.join(map(lambda X: ' ' if X in puncn else X,b)).strip()
    
  


  #def __parse_helper(self,obj):
    #keep = np.char.not_equal(obj,'').astype(int)
    #keep*= np.char.find(obj,'---')
    #fobj = obj[np.where(keep)]
    #splt = np.where(np.char.find(fobj,'\\\\')+1)[0]
    #loar = np.array_split(fobj,splt)
    #mask = np.where([title_link(x) for x in loar])[0]
    #prep = np.concatenate(op.itemgetter(*mask)(loar))
    #prep = multi_drop(prep,['\\\\',',','(',')'])
    #prep = [x[0].strip() for x in np.char.split(prep,'  ')]
    #finl = np.fromiter(filter(grab_patt,prep),dtype='<U80')
    #return finl

  #def listing_parser(self):
    #listings = self.get_art()
    #sl1 = np.concatenate((listings[1:],[-1]))
    #sl = it.starmap(slice,zip(listings,sl1))
    #listing = []
    #for x in sl:
      #listing.append(self.__parse_helper(self.arr[x]))
    #listing = np.array(listing,dtype=str)
    #self.listing = np.char.replace(listing,'Title: ','')
    #return self.listing











