
import numpy as np,datetime,email

class MessageContainer(object):
  
  def __init__(self,message_count,message_array):
    '''
    message_array should contain the message and uid
    '''
    self.mcount = message_count
    self.marray = message_array
  def __len__(self):
    return self.mcount
  
  def __iter__(self):
    return iter(
      self.__mhelper(i,msg) for i,msg in self.marray
    )
  def __getitem__(self,idx):
    if not hasattr(self,'aslist'):
      self.mlist = [
        self.__mhelper(i,msg) for i,msg in self.marray
      ]
    return self.mlist[idx]
  def __mhelper(self,i,m):
    if 'Date' in m.keys():
      _dt = email.utils.parsedate_tz(m['Date'])
      _dt = email.utils.mktime_tz(_dt)
    else:
      _dt = int(datetime.datetime.now().strftime('%s'))
    return {
      'subject': m['Subject'],
      'date'   : _dt,
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
  
  #could these be static
  #def __datehelp(self):
    #if 'Date' in self.mess.keys():
      #_dt = email.utils.parsedate_tz(self.mess['Date'])
      #_dt = email.utils.mktime_tz(_dt)
    #else:
      #_dt = datetime.datetime.now()
      #_dt = int(_dt.strftime('%s'))
    #self.set_date(_dt)
  #def get_date(self):
    #'''get date of message'''
    #if not hasattr(self,'dt'):
      #self.__datehelp()
    #return self.dt
  #def set_date(self,set_to):
    #'''set date of message'''
    #self.dt = datetime.datetime.fromtimestamp(set_to)
