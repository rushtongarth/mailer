import re
import datetime
from hashlib import sha256
import numpy as np

## TODO
# Add connector/formatter for db
date_key = re.compile(
  r' '.join([
    '.*(?P<date>[MTWF][ouehr][nedui],','[0-9]{,2}',
    '[JFMASOND][a-z][a-z]',
    '[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} GMT).*'])
  )

class ArXivArticle(object):

  def __init__(self,text_arr,user_subs): 
    self.raw  = text_arr
    self.subs = np.array(user_subs)
    self.__extract()
  def __extract(self):
    self.__hash()
    self.__title()
    self.__link()
    self.__submit_date()
    self.__cats()
    self.__abstract()
    self.attr = dict.fromkeys([
      'shakey','date_received','title','pri_categories',
      'all_categories','body','link'])
    _ = self.get_attrs()
  def __repr__(self):
    return str(self.attr)
  def __hash__(self):
    return hash(self.shakey)
  def __eq__(self,other):
    if self.attr['shakey']==other.attr['shakey']:
      return True
    else:
      return False
  def __pat_match(self,patt,mode=None):
    '''pat_match: match pattern on instance text_arr'''
    if mode == 'start':
      found = np.char.startswith(self.raw,patt)
    else:
      found = np.char.find(self.raw,patt)+1
    return np.where(found)[0]
  def __submit_date(self):
    pat1  = 'Date: '
    idx   = self.__pat_match(pat1,'start')
    if idx.shape[0] > 0:
      _date = self.raw[idx].item()
      _date = _date.replace(pat1,'')
      dstr  = _date[:_date.index('GMT')+3]
    else:
      _dstr = [
        date_key.match(x).group('date') 
        for x in self.raw if date_key.match(x)
      ]
      dstr = _dstr[0]
    self.date = datetime.datetime.strptime(
        dstr,'%a, %d %b %Y %H:%M:%S %Z'
      )
  def __hash(self):
    bytes_title = bytes(self.get_title().item(),'utf8')
    self.shakey = sha256(bytes_title).hexdigest()

  def __title(self): 
    
    pat1,pat2 = 'Title: ','Authors: '
    loc1 = self.__pat_match(pat1,'start')
    loc2 = self.__pat_match(pat2,'start')
    pat_range = np.r_[loc1:loc2]
    tstr = ' '.join(self.raw[pat_range])
    ## THIS SHOULD BE ONLY A STRING!!!
    self.title  = np.char.replace(tstr,pat1,'')
    
  def __link(self):
    
    patt = '\\\\ ( https://arxiv.org/abs'
    locn = self.__pat_match(patt)
    mtch = self.raw[locn]
    link = re.match(r'\\\\ \((.*),.*',mtch.item())
    if link is None:
      raise RuntimeError('the stupid set link function broke')
    self.link = link.group(1).strip()

  def __cats(self):
    patt = 'Categories: '
    locn = self.__pat_match(patt)
    cats = self.raw[locn].item()
    cats = np.char.replace(cats,patt,'')
    cats = np.char.split(cats,' ')
    self.categories = np.array(cats.item())
  def __pcats(self):
    tags,descr = np.hsplit(
      self.subs,self.subs.shape[-1]
      )
    inter,all_tags,sub_tags = np.intersect1d(
      self.categories,
      tags,
      return_indices=True
      )
    mycats = np.zeros(tags.shape,dtype=bool)
    mycats[sub_tags]=True
    self.pri_cats = self.subs[mycats.squeeze()]
  
  def __abstract(self):
    pat1 = '\\\\'
    locs = self.__pat_match(pat1,'start')
    
    if len(locs)==2:
      abst = self.get_title().item()
    elif len(locs)>=3:
      chunk = locs[1:]+[1,0]
      abst = self.raw[slice(*chunk)]
      abst = ' '.join(abst)
    else:
      print(self.__dict__)
      raise RuntimeError('the stupid abstract function broke')
    self.abstract = np.array([
      l.strip() for l in abst.split('.') if len(l.strip())
    ])
  def get_title(self): 
    if not hasattr(self,'title'): 
      self.__title() 
    return self.title
  def get_link(self):
    if not hasattr(self,'link'): 
      self.__link() 
    return self.link
  def get_cats(self):
    if not hasattr(self,'categories'): 
      self.__cats() 
    return self.categories
  def get_abstract(self):
    if not hasattr(self,'abstract'):
      self.__abstract()
    return self.abstract
  def get_date(self):
    if not hasattr(self,'date'):
      self.__submit_date()
    return self.date
  def get_attrs(self):
    self.attr['shakey'] = self.shakey
    self.attr['date_received'] = self.get_date()
    self.attr['title'] = self.get_title().item()
    #self.attr['pri_categories']=self.get_cats()
    self.attr['all_categories']=self.get_cats()
    self.attr['body'] = self.get_abstract()
    self.attr['link'] = self.get_link()
    return self.attr


