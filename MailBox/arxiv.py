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
  def set_header(self,header_array=None):
    if header_array:
      self.head = header_array
    else:
      h1 = np.char.find(self.arr,'Submissions')+1
      h1+= np.char.find(self.arr,'received from')+1
      h1 = slice(*(np.where(h1)[0]+[0,1]))
      self.head = self.arr[h1]
  def get_header(self):
    if hasattr(self,'head'):
      return self.head
    else:
      self.set_header()
      return self.head
  def get_art(self):
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
    if posn_array:
      self.art_posn = posn_array
    else:
      self.art_posn = self.__set_art()

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
    self.listing = np.char.replace(listing,'Title: ','') ## ERROR
    return self.listing

  

