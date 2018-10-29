import imaplib,email
import numpy as np

class MailBox(object):
  
  def __init__(self,user,pswd,folder="INBOX"):
    self.user = user
    self.pswd = pswd
    self.fold = folder
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

  def get_mids(self,sender="no-reply@arxiv.org"):
    search_str = '(FROM "{:}")'.format(sender)
    res,data = self.mbox.search(None,search_str)
    if res != 'OK':
      raise IOError('something is wrong with the search')
    return next(map(bytes.split,data))

  def __read_part(self,part):
    if part.get_content_maintype() != 'text':
      for subp in part.get_payload():
        yield from self.__read_part(subp)
    else:
      yield part.get_payload()

  def mail_proc(self,mess):
    _arr = [np.array(pt.splitlines()) for pt in self.__read_part(mess)]
    _arr = np.array([np.char.strip(y) for y in _arr])
    return _arr.squeeze()
      
  def get_by_id(self,toget):
    res,data = self.mbox.fetch(toget,"(RFC822)")
    self.mess = email.message_from_bytes(data[0][1])
    return self.mail_proc(self.mess)
