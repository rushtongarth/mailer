import imaplib,email,re,datetime
import numpy as np

from MailBox.ReadMail import ReadMail

class MessageParser(ReadMail):
  '''MessageParser class: general purpose message parsing
  '''
  def __init__(self,user,pswd,location="INBOX",sender="no-reply@arxiv.org",mess_id=-1):
    '''MessageParser constructor
       
       Parameters:
        user     : username
        pswd     : password
        location : folder in which to search
        sender   : sender to search for
        mess_id  : message uid to load
                   (default: -1, this yields the latest email)    
    '''
    super().__init__(user,pswd,location,sender)
    self.mid = mess_id
  def __repr__(self):
    base = '<mess: {mid}|{loc}'
    if hasattr(self,'msg'):
      base+='|{dt}>'
      d = self.get_date().strftime('%Y-%m-%d')
      return base.format(mid=self.mid,loc=self.fold,dt=d)
    else:
      base+='>'
      return base.format(mid=self.mid,loc=self.fold)
  def set_mess(self):
    if self.mid<0:
      self.msg = self.get_latest_raw()
    else:
      self.msg = self.get_by_uid(self.mid)
    self.mess_arr = self.mail_proc(self.msg)
  def get_mess(self):
    return self.mess_arr
 
  def __read_part(self,part):
    # read message parts
    if part.get_content_maintype() != 'text':
      for subp in part.get_payload():
        yield from self.__read_part(subp)
    else:
      yield part.get_payload()

  def mail_proc(self,mess):
    # process messages
    _arr = [np.array(pt.splitlines()) for pt in self.__read_part(mess)]
    _arr = np.array([np.char.strip(y) for y in _arr])
    return _arr.squeeze()
  # date handling
  def __datehelp(self):
    if 'Date' in self.mess.keys():
      _dt = email.utils.parsedate_tz(self.mess['Date'])
      _dt = email.utils.mktime_tz(_dt)
    else:
      _dt = datetime.datetime.now()
      _dt = int(_dt.strftime('%s'))
    self.set_date(_dt)
  def get_date(self):
    if not hasattr(self,'dt'):
      self.__datehelp()
    return self.dt
  def set_date(self,set_to):
    self.dt = datetime.datetime.fromtimestamp(set_to)
  def db_prep(self):
    ## TODO: add into ArXiv digest how to handle this
    pass
  def __call__(self,**kwargs):
    self.__dict__.update(kwargs)
    self.set_mess()
    _ = self.get_date()
    return self
