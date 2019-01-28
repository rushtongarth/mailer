import itertools as it,operator as op
import numpy as np,re
from functools import reduce


class ArXivDigest(object):
  subscriptions = []
  def __init__(self,subscriptions,message_array):
    self.arr = message_array
    self.subscriptions.extend(subscriptions)
    self.subscr_arr = np.array(self.subscriptions)

  def __get_idx(self,patt):
    '''find indices of pattern in array'''
    return np.where(np.char.find(self.arr,patt)+1)
  def __hdr_idx(self):
    sk1 = re.compile('received from  [MTWF][ouehr][nedui]')
    sk2 = re.compile('Submissions')
    loc = np.array([
      e for e,v in enumerate(self.arr)
        if sk1.match(v) or sk2.match(v)
    ])
    if len(loc)!=2:
      raise RuntimeError('the stupid set header index function broke')
    loc+=[-1,2]
    self.head_idx = np.r_[slice(*loc)]
  def set_header(self,header_array=None):
    '''Setter for header'''
    if header_array:
      self.head_idx = header_array
    else
      self.__hdr_idx()

  def get_header(self):
    '''Getter for Header'''
    if not hasattr(self,'head'):
      self.__hdr_idx()
    return self.head_idx

  def __set_art(self):
    
    h1 = self.get_header()
    a1 = self.__get_idx(''.join(['-']*78))
    return a1[a1>h1[-1]]
  
  def get_art(self):
    '''Getter for articles'''
    if not hasattr(self,'art_posn'):
      self.set_art()
    return self.art_posn
  
  def set_art(self,posn_array=None):
    '''Setter for articles'''
    if posn_array:
      self.art_posn = posn_array
    else:
      self.art_posn = self.__set_art()

  def sub_arr(self):
    '''sub_arr:
         initialize subarray containing only article data
         helper for get_sub_arr
       Parameters: ArXivDigest object
       returns:    None
    '''
    A = self.get_art()
    junk  = np.ones((A.shape[0],2),dtype=int) * -1
    junk[:,0]   = A
    junk[:-1,1] = A[1:]
    self.sub = np.concatenate([
      self.arr[slice(*r)] for r in junk
    ])
    self.junk = junk-A[0]
    self.junk[-1,-1] = -1
  def get_sub_arr(self):
    '''get_sub_arr:
         get subarray containing only article data
       Parameters: ArXivDigest object
       returns:    sub array
    '''
    if not hasattr(self,'sub'):
      self.sub_arr()
    return self.sub
  def __len__(self):
    if not hasattr(self,'sub'):
      self.sub_arr()
    return self.junk.shape[0]
  def __getitem__(self,idx):
    # needs a try except...
    if not hasattr(self,'sub'):
      self.sub_arr()
    return self.sub[slice(*self.junk[idx])]
  def __setitem__(self,idx,val):
    # needs a try except...
    if not hasattr(self,'sub'):
      self.sub_arr()
    self.sub[slice(*self.junk[idx])]=val
  def __iter__(self):
    '''iterate through articles'''
    if not hasattr(self,'sub'):
      self.sub_arr()
    return iter(self.sub[i:j] for i,j in self.junk)
  
  ## TODO
  ## migrate the element-wise operations to a subclass
  
  def find_links(self):
    '''find_links: identify links in email
                   method supports link getter
       Parameters: ArXivDigest object
       returns:    None
    '''
    pat1,pat2 = 'Title: ','arXiv:'
    self.sub_arr()
    arxs = np.where(np.char.find(self.sub,pat1)+1)[0]
    axid = self.sub[arxs-3]
    if not np.char.startswith(axid,pat2).all():
      # addition to handle when not all links are located
      sp_pat = ''.join(['-']*78)
      arxs = np.where(np.char.find(self.sub,sp_pat)+1)[0]
      axid = self.sub[arxs+2]
      if not np.char.startswith(axid,pat2).all():
        raise RuntimeError('not all arxiv links found')
    links = np.char.replace(axid,pat2,'https://arxiv.org/abs/')
    self.links = np.array([x[0] for x in np.char.split(links,' ')])

  def get_links(self):
    '''Getter for links in email'''
    if not hasattr(self,'links'):
      self.find_links()
    return self.links

  def __cat_match(self,X):
    return np.intersect1d(X,self.subscr_arr[:,0]).size
  def find_categories(self):
    patt = 'Categories: '
    idx = self.__get_idx(patt)
    cats = np.char.replace(self.arr[idx],patt,'')
    splt = np.char.split(cats,' ')
    locs = [e for e,i in enumerate(splt) if self.__cat_match(i)>0]
    self.categories = cats[locs]

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

  def __build_catmat(self):
    cols = np.hsplit(
      self.subscr_arr,self.subscr_arr.shape[-1]
    )
    tags,descr = map(np.squeeze,cols)
    emp = np.empty_like(tags)
    #
    cats = self.get_categories()
    all_cats = np.char.split(cats,' ')
    shp = all_cats.shape+tags.shape
    mycats = np.zeros(shp,dtype=bool)
    #
    for e,r in enumerate(all_cats):
      _,_,tmp = np.intersect1d(r,tags,return_indices=True)
      mycats[e,tmp]=True
    self.catmat = np.where(mycats,tags,emp)

  def get_catmat(self):
    if not hasattr(self,'catmat'):
      self.__build_catmat()
    return self.catmat
  
  def cat_grouper(self):
    '''group rows of catmat by subscriptions'''
    cm = self.get_catmat()
    _,cols = cm.shape
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
    #  on 2018-12-17 arXiv:1802.02952 didn't have a link
    #  this broke :(
    for k,idx in cg.items():
      long_cat = ', '.join(map(sb.get,k.split(',')))
      S = sorted(np.nditer((T[idx],L[idx],C[idx])),key=lambda X: X[-1])
      grouped.append((long_cat,S))
    return sorted(grouped,reverse=True)

  def find_abstracts(self):
    
    F = lambda X: np.where(np.char.find(X,'\\\\')+1)[0]
    G = lambda X: F(X).shape[0]
    len_nz = filter(lambda Z: G(Z)>0,self)
    T = self.get_titles()
    L = self.get_links()
    C = self.get_categories()
    self.abstracts = []
    for i,v in enumerate(len_nz):
      shp = F(v).shape[0]
      if shp!=3:
        use = np.array([T[i]])
        tup = (T[i], C[i], use, L[i])
      elif shp==3:
        idx = ( F(v) * [0,1,1] )+[0,1,0]
        idx_slc = idx[np.where(idx)]
        ast = v[slice(*idx_slc)]
        tup = (T[i], C[i], ast, L[i])
      self.abstracts.append( tup )
    self.abstracts = np.array(self.abstracts,dtype=object)
  def get_abstracts(self):
    if not hasattr(self,'abstracts'):
      self.find_abstracts()
    return self.abstracts
  def group_abstracts(self):
    # TODO: unify this with the layout needed for DB load
    #       maybe as a "plugin" for the container?
    cg = self.cat_grouper()
    sb = dict(self.subscriptions)
    abstr = self.get_abstracts()
    grouped = []
    for k,idx in cg.items():
      long_cat = ', '.join(map(sb.get,k.split(',')))
      S = sorted(abstr[idx],key=lambda X: X[-1])
      grouped.append((long_cat,k,S))
    return sorted(grouped,reverse=True)
    
    
    
  

