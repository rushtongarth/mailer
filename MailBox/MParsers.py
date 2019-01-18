import email,datetime,numpy as np
from MailBox.ReadMail import ReadMail

class MessageParser(ReadMail):
  '''MessageParser class: general purpose message parsing'''
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
    self.set_mid(mess_id)
  def set_mid(self,mid):
    '''set message id'''
    self.mid = mid
  def get_mid(self):
    '''get message id'''
    return self.mid
  def set_mess(self):
    '''set_mess : setter for the current message'''
    if self.mid<0:
      self.msg = self.get_latest_raw()
      self.set_mid(self.mid_list[-1])
    else:
      self.msg = self.get_by_uid(b'%d'%self.mid)
    self.mess_arr = self.mail_proc(self.msg)
  def get_mess(self):
    '''get_mess : getter for the current message'''
    return self.mess_arr
  
  def __repr__(self):
    base = '<mess: {mid}|{loc}'
    base = base.format(
      mid=self.mid,loc=self.fold
    )
    if hasattr(self,'msg'):
      d = self.get_date().strftime('%Y-%m-%d')
      base+='|{dt}'.format(dt=d)
    base+='>'
    return base
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
    '''get date of message'''
    if not hasattr(self,'dt'):
      self.__datehelp()
    return self.dt
  def set_date(self,set_to):
    '''set date of message'''
    self.dt = datetime.datetime.fromtimestamp(set_to)
  def get_date_id(self):
    return self.get_date(),self.get_mid()
  def __call__(self,**kwargs):
    '''MessageParser class call:
       Parameters:
         kwargs : dict : keyword arguments accepted by MessageParser
       returns:
         MessageParser class
    '''
    self.__dict__.update(kwargs)
    self.set_mess()
    self.__datehelp()
    return self
