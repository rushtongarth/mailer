import imaplib,email,re,datetime

import numpy as np

from MailBox.MailBox import AbstractMailBox


class ReadMail(AbstractMailBox):
  '''ReadMail Class: establish a connection to read emails
     
     Parameters:
       user     : username
       pswd     : password
       location : folder in which to search
       sender   : sender to search for
  '''
  def __init__(self,user,pswd,location,sender):
    self.user = user
    self.pswd = pswd
    self.fold = location
    self.set_sender(sender)
    super().__init__(user,pswd,location)
  def __enter__(self):
    self.mbox = imaplib.IMAP4_SSL('imap.gmail.com')
    r,d = self.mbox.login(self.user,self.pswd)
    if r != 'OK':
      print(d)
      raise IOError('unable to log in')
    r,d = self.mbox.select(self.fold)
    if r!='OK':
      print(d)
      raise IOError('could not find: %s'%self.fold)
    return self
  def __exit__(self,*args):
    self.mbox.close()
  def set_sender(self,sender):
    self.sender = sender
  def _ids(self):
    search_str = '(FROM "{:}")'.format(self.sender)
    res,data = self.mbox.uid('search',None,search_str)
    if res != 'OK':
      self.mids = [b'']
    else:
      self.mids = next(map(bytes.split,data))

  def get_mids(self):
    if not hasattr(self,'mids'):
      self._ids()
    return self.mids
  
  def get_by_uid(self,toget):
    res,data = self.mbox.uid('fetch',toget,"(RFC822)")
    self.mess = email.message_from_bytes(data[0][1])
    return self.mess
  
  def get_latest_raw(self):
    ids = self.get_mids()
    message = self.get_by_uid(ids[-1])
    return message
  def get_all_raw(self):
    mids = self.get_mids()
    _get = b','.join(mids)
    res,data = self.mbox.uid('fetch',toget,"(RFC822)")
    mess_list = []
    if res != 'OK':
      return mess_list
    for i in range(0,len(data),2):
      _curr = email.message_from_bytes(data[i][1])
      mess_list.append(_curr)
    return mess_list

  def get_ids(self):
    return self.get_mids()
    




class MessageParser(ReadMail):
  def __init__(self,user,pswd,location="INBOX",sender="no-reply@arxiv.org",mess_id):
    super().__init__(user,pswd,location,sender)
    self.set_mess(mess_id)
    _ = self.get_date()

  def set_mess(self,mid):
    m = self.get_by_uid(mid)
    self.mess_arr = self.mail_proc(m)
  
 
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






