import re,datetime
from hashlib import sha256
import numpy as np

## TODO
# Add connector/formatter for db
class ArXivArticle(object):
  date_key = re.compile(
    r''.join([
      '.*',
      '([MTWF][ouehr][nedui], ',
      '[0-9]{,2} ',
      '[JFMASOND][a-z][a-z] ',
      '[0-9]{4} ',
      '[0-9]{2}:[0-9]{2}:[0-9]{2} ',
      'GMT)',
      '.*'])
  )
  attr = {
    'shakey':None,
    'date_received':None,
    'title':None,
    'pri_categories':None,
    'all_categories':None,
    'body':None,
    'link':None
  }
  def __init__(self,text_arr): 
    self.raw = text_arr
  def __repr__(self):
    return str(self.attr)
  def __hash__(self):
    if not hasattr(self,_hash):
      self.__hash()
    return hash(self._hash)
  def __pat_match(self,patt): 
    '''pat_match: match pattern on instance text_arr'''
    found = np.char.find(self.raw,patt)+1 
    return np.where(found)[0]
  def __submit_date(self):
    pat1  = 'Date: '
    idx   = self.__pat_match(pat1)
    if idx>0:
      _date = self.raw[idx]
      _date = _date.replace(pat1,'')
      dstr  = _date[:_date.index('GMT')+3]
    else:
      _dstr = [
        date_key.match(x).group(1)
        for x in self.raw if date_key.match(x)
      ]
      dstr = _dstr[0]
    self.date = datetime.datetime.strptime(
        dstr,'%a, %d %b %Y %H:%M:%S %Z'
      )
    self.attr['date_received'] = self.date
  def __hash(self):
    bytes_title = bytes(self.get_title().item(),'utf8')
    self._hash = sha256(bytes_title).hexdigest()
    self.attr['shakey'] = self._hash

  def __title(self): 
    
    pat1,pat2 = 'Title: ','Authors: '
    loc1 = self.__pat_match(pat1)
    loc2 = self.__pat_match(pat2)
    pat_range = np.r_[loc1:loc2]
    tstr = ' '.join(self.raw[pat_range])
    self.title  = np.char.replace(tstr,pat1,'')
    self.attr['title'] = self.title
  def __link(self):
    
    patt = '\\\\ ( https://arxiv.org/abs'
    locn = self.__pat_match(patt)
    mtch = self.raw[locn]
    link = re.match(r'\\\\ \((.*),.*',mtch.item())
    if link is None:
      raise RuntimeError('the stupid set link function broke')
    self.link = link.group(1).strip()
    self.attr['link'] = self.link
  def __cats(self):
    patt = 'Categories: '
    locn = self.__pat_match(patt)
    cats = self.raw[locn]
    cats = np.char.replace(cats,patt,'')
    cats = np.char.split(cats,' ').item()
    self.categories = np.array(cats)
    self.attr['all_categories']=self.categories
  def __abstract(self):
    pat1 = '\\\\'
    locs = self.__pat_match(pat1)
    if len(locs)==2:
      self.abstract = self.get_title()
    elif len(locs)==3:
      chunk = locs[1:]+[1,0]
      self.abstract = self.raw[slice(*chunk)]
    else:
      raise RuntimeError('the stupid abstract function broke')
    self.attr['body'] = self.abstract
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
  


