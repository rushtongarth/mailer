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
  def __mbsearch(self,*args,default=True):
    search_arg = list(args)
    if default:
      search_arg+= ['FROM "{:}"'.format(self.sender)]
    search_str = ' '.join(search_arg)
    _to_search = '({})'.format(search_str)
    r,d = self.mbox.uid('search',None,_to_search)
    if r != 'OK':
      return [b'']
    return d
  def _ids(self):
    #search_str = '(FROM "{:}")'.format(self.sender)
    #search_str = self.__mbsearch()
    #res,data = self.mbox.uid('search',None,search_str)
    data = self.__mbsearch()
    #if res != 'OK':
    #  self.mids = [b'']
    #else:
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
  def get_unread(self):
    return self.__mbsearch('UNSEEN')









