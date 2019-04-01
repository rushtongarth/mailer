import datetime
import operator as op
import email
import numpy as np

class MessageContainer(object):
  
  def __init__(self,message_count,message_array):
    '''
    MessageContainer
    
    container class for housing emails
    
    :param int message_count: number of messages in input
    :param message_array: array containing the message and uid
    :type message_array: list[tuple[bytes,bytes]] or list[tuple[str,str]]
    '''
    self.mcount = message_count
    self.marray = message_array
  def __repr__(self):
    ostr = '<{count}|start={d1}|end={d2}>'
    ostr = ostr.format(
      count=self.mcount,
      start=self.__min_date().strftime('%Y-%m-%d'),
      end=self.__max_date().strftime('%Y-%m-%d')
    )
    return ostr
  def __min_date(self):
    if not hasattr(self,'_mindate'):
      self._mindate = min(map(op.itemgetter('date'),self))
    return self._mindate
  def __max_date(self):
    if not hasattr(self,'_maxdate'):
      self._maxdate = max(map(op.itemgetter('date'),self))
    return self._maxdate
  def __len__(self):
    return self.mcount
  def __iter__(self):
    for i,msg in self.marray:
      yield self.__mhelper(i,msg)
    #return iter(self.__mhelper(i,msg) for i,msg in self.marray)
  def __to_list(self):
    self.mlist = [
      self.__mhelper(i,msg) for i,msg in self.marray
    ]
  def __getitem__(self,idx):
    if not hasattr(self,'mlist'):
      self.__to_list()
    return self.mlist[idx]
  def __mhelper(self,i,m):
    if 'Date' in m.keys():
      _dt = email.utils.parsedate_tz(m['Date'])
      _dt = email.utils.mktime_tz(_dt)
    else:
      _dt = int(datetime.datetime.now().strftime('%s'))
    return {
      'subject': m['Subject'],
      'date'   : datetime.datetime.fromtimestamp(_dt),
      'mid'    : i,
      'arr'    : self.message_proc(m)
    }
  def __read_part(self,part):
    # read message parts
    if part.get_content_maintype() != 'text':
      for subp in part.get_payload():
        yield from self.__read_part(subp)
    else:
      yield part.get_payload()

  def message_proc(self,mess):
    # process messages
    mess_parts = self.__read_part(mess)
    _arr = [np.array(pt.splitlines()) for pt in mess_parts]
    _arr = np.array([np.char.strip(y) for y in _arr])
    return _arr.squeeze()
