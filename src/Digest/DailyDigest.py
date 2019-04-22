import numpy as np
import operator as op
import datetime
import pandas as pd
from string import punctuation as punct

from src.Digest.ArXiv import ArXivDigest
from src.Digest.ArticleContainer import ArXivArticle
#from .Article import Article
from src.db.schema import ArticleBase,EmailBase

punct = punct.replace('.','')

class DailyDigest(object):
  '''
  DailyDigest
  
  Produces an object ready for consumption by either the
  db loader or the message sender
  
  :param message_container: a MessageContainer object
  :type message_container: :class:`MessageContainer`
  :param subscriptions: list of current subscriptions
  :type subscriptions: list[tuple[str,str]]
  :param int idx: index of message to process (defaults to -1)
  '''
  dt = [
    ('mid','i8'),('date_msg','M8[us]'),('shakey','U64'),
    ('date_art','M8[us]'), ('title','O'), ('pri_cats','O'),
    ('all_cats','O'), ('body','O'), ('link','U79'),
  ]
  def __init__(self,message_container,subscriptions,idx=-1):
    self.sub_arr = np.array(subscriptions)
    self.msg_con = message_container[idx]
    self.arx_msg = ArXivDigest(
      subscriptions,
      self.msg_con['arr'],
      self.msg_con['date']
    )
    self.arx_art = np.empty(
      len(self.arx_msg),
      dtype=ArXivArticle
    )
  def __repr__(self):
    ostr = "<{cn}|{Len}|{dt}>"
    ostr = ostr.format(**{
      'cn' : type(self).__name__,
      'Len': len(self.records),
      'dt' : self.msg_con['date'].strftime('%Y-%m-%d')
    })
    return ostr
  @property
  def listing(self):
    self.__listing()
    return self.arx_art
  def __listing(self):
    for e,arx in enumerate(self.arx_msg):
      self.arx_art[e] = ArXivArticle(arx,self.sub_arr)
  @property
  def grp_mat(self):
    if not hasattr(self,'_gmat'):
      self.__gmat()
    return self._gmat
  def __gmat(self):
    tags = self.sub_arr[:,0]
    emp = np.empty_like(tags)
    shp = (self.arx_art.shape[0],tags.shape[0])
    mycats = np.zeros(shp,dtype=bool)
    for e,r in enumerate(self.listing):
      _,_,tmp = np.intersect1d(
        r.pri_cats,tags,return_indices=True
      )
      mycats[e,tmp]=True
    self._gmat = np.where(mycats,tags,emp)
  @property
  def records(self):
    if not hasattr(self,'_records'):
      self.__recs()
    return self._records
  def __recs(self):
    rec_attrs = op.attrgetter(
      'shakey','date','title',
      'pri_cats','all_cats',
      'abstract','link'
    )
    dte = self.msg_con['date']
    mid = self.msg_con['mid']
    self._records = np.array(
      [(mid,dte)+rec_attrs(x) for x in self.listing],
      dtype=self.dt
    )
  @property
  def grouping(self):
    if not hasattr(self,'_grouping'):
      self.__grouping()
    return self._grouping
  def __grouping(self):
    subs = self.sub_arr
    ucols,idx = np.unique(
      self.grp_mat,axis=0,return_inverse=True
    )
    flds = ['title','link','all_cats']
    self._grouping = []
    for e,rw in enumerate(ucols):
      _,_,locs = np.intersect1d(
        rw,subs[:,0],return_indices=True
      )
      long_cat = ', '.join(subs[locs,1])
      curr_ix = np.where(idx==e)
      rec_slc = self.records[flds][curr_ix]
      self._grouping.append((long_cat,rec_slc))
  def as_recarr(self):
    return self.records.view(np.recarray)
  def as_df(self):
    cols, _ = zip(*self.dt)
    tups = []
    for mid,mdt,sh,ldt,title,pcat,acat,abst,link in self.records:
      tups.append((
        mid, mdt, sh, ldt, title,
        ','.join(pcat), ','.join(acat), '. '.join(abst),
        link,
      ))
    return pd.DataFrame(tups,columns=cols)
  def dateprep(self,obj):
    cast = obj.astype(datetime.datetime)
    return cast.strftime("%Y-%m-%d")
  def body_clean(self,text):
    tmp = '. '.join(text)
    npt = ''.join(map(lambda X: ' ' if X in punct else X,tmp))
    return npt.upper()
  def as_dblist(self):
    dict_arr = np.empty(self.records.shape,dtype=ArticleBase)
    ebase = EmailBase(**{
      'uid'  : int(self.records['mid'][0]),
      'date' : self.dateprep(self.records['date_msg'][0]),
    })
    for e,el in enumerate(self.records):
      data = {
        'shakey'   : el['shakey'],
        'date'     : self.dateprep(el['date_art']),
        'title'    : el['title'],
        'pri_cats' : ','.join(el['pri_cats']),
        'all_cats' : ','.join(el['all_cats']),
        'body'     : self.body_clean(el['body']),
        'link'     : el['link'],
        'ncats'    : len(el['pri_cats']),
        'email_id' : int(self.records['mid'][0]),
        #'email'    : ebase,
      }
      dict_arr[e] = ArticleBase(**data)
    return ebase,dict_arr





