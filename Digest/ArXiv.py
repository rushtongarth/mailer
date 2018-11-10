import itertools as it
import operator as op
import numpy as np


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
  def __links(self):
    _posn = np.char.find(self.arr,'https://arxiv.org/abs')+1
    self.lks = self.arr[np.where(_posn)]
    st = np.char.find(self.lks,'https://')
    ed = np.char.find(self.lks,',')-1
    self.links = self.__sl_vctzd('lks',st,ed)

  def get_links(self):
    '''Getter for links'''
    if not hasattr(self,'links'):
      self.__links()
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
    pat1,pat2 = 'Title: ','Author'
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

  #def slicer(self):
    #T = np.where(np.char.find(self.arr,'Title: ')+1)[0]
    #A = np.where(np.char.find(self.arr,'Author')+1)[0]
    #L = np.where(np.char.find(self.arr,'https://arxiv.org/abs')+1)[0]
    #_ts = np.array([' '.join(self.arr[i:j]) for i,j in zip(T,A)])
    #ts = np.char.replace(_ts,"Title: ",'')
    #_lk = self.arr[L]
    ##slicer_vectorized
    #lk=np.char.find(_lk,'https:')
    #_lk.view(str
    #return ts,lk
  


  def __parse_helper(self,obj):
    keep = np.char.not_equal(obj,'').astype(int)
    keep*= np.char.find(obj,'---')
    fobj = obj[np.where(keep)]
    splt = np.where(np.char.find(fobj,'\\\\')+1)[0]
    loar = np.array_split(fobj,splt)
    mask = np.where([title_link(x) for x in loar])[0]
    prep = np.concatenate(op.itemgetter(*mask)(loar))
    prep = multi_drop(prep,['\\\\',',','(',')'])
    prep = [x[0].strip() for x in np.char.split(prep,'  ')]
    finl = np.fromiter(filter(grab_patt,prep),dtype='<U80')
    return finl

  def listing_parser(self):
    listings = self.get_art()
    sl1 = np.concatenate((listings[1:],[-1]))
    sl = it.starmap(slice,zip(listings,sl1))
    listing = []
    for x in sl:
      listing.append(self.__parse_helper(self.arr[x]))
    listing = np.array(listing,dtype=str)
    self.listing = np.char.replace(listing,'Title: ','')
    return self.listing

#titles: 
#T,A=np.where(np.char.find(arx.arr,'Title: ')+1)[0],np.where(np.char.find(arx.arr,'Author')+1)[0]
#_ts = np.array([' '.join(arx.arr[i:j]) for i,j in zip(T,A)])
#ts = np.char.replace(_ts,'Title: ','')
#links=arx.arr[np.where(np.char.find(arx.arr,'https://arxiv.org/abs')+1)[0]]










