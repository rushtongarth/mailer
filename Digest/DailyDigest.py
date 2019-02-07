import numpy as np
import operator as op
from .ArXiv import ArXivDigest
from .ArticleContainer import ArXivArticle


class DailyDigest(object):
  dt = [
    ('mid',int),('date_msg','M8[us]'),
    ('shakey','<U64'), ('date_received','M8[us]'),
    ('title',object), ('pri_cats',object),
    ('all_cats',object), ('body',object),
    ('link','U79')
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
  @property
  def listing(self):
    self.__listing()
    return self.arx_art
  def __listing(self):
    for e,arx in enumerate(self.arx_msg):
      self.arx_art[e] = ArXivArticle(arx,self.sub_arr)
  @property
  def grouping(self):
    if not hasattr(self,'_grouping'):
      self.__grouping()
    return self._grouping
  def __grouping(self):
    tags = self.sub_arr[:,0]
    emp = np.empty_like(tags)
    mycats = np.zeros(
      (self.arx_art.shape[0],tags.shape[0]),
      dtype=bool
    )
    for e,r in enumerate(self.listing):
      _,_,tmp = np.intersect1d(r.pri_cats,tags,return_indices=True)
      mycats[e,tmp]=True
    gmat = np.where(mycats,tags,emp)
    ucols,idx = np.unique(gmat,axis=0,return_inverse=True)
    self._grouping = dict()
    for i in range(len(ucols)):
      k=','.join(filter(None,ucols[i]))
      self._grouping[k]=np.where(idx==i)
    
     
    
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
      dtype=self.dt)
  def as_recarr(self):
    return self.records.view(np.recarray) 
