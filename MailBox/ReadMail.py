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
    '''set message sender'''
    self.sender = sender
  def __mbsearch(self,*args,default=True):
    '''search helper'''
    search_arg = list(args)
    if default:
      search_arg+= ['FROM "{:}"'.format(self.sender)]
    search_str = ' '.join(search_arg)
    _to_search = '({})'.format(search_str)
    r,d = self.mbox.uid('search',None,_to_search)
    if r != 'OK':
      return [b'']
    return d
  def __fetcher(self,toget):
    '''message fetching helper'''
    res,data = self.mbox.uid('fetch',toget,"(RFC822)")
    if res!='OK':
      print(res,data,sep='\n',end='\n\n')
      raise IOError('could not find messages')
    return data
  def _ids(self):

    data = self.__mbsearch()
    self.mid_list = next(map(bytes.split,data))
  def get_mid_list(self):

    if not hasattr(self,'mid_list'):
      self._ids()
    return self.mid_list
  
  def get_by_uid(self,toget):

    data = self.__fetcher(toget)
    self.mess = email.message_from_bytes(data[0][1])
    return self.mess
  
  def get_latest_raw(self):
    
    ids = self.get_mid_list()
    message = self.get_by_uid(ids[-1])
    return message
  
  def get_all_raw(self):
    mids = self.get_mid_list()
    toget = b','.join(mids)
    data = self.__fetcher(toget)
    mess_list = []
    for i in range(0,len(data),2):
      _curr = email.message_from_bytes(data[i][1])
      mess_list.append(_curr)
    return mess_list

  def get_ids(self):
    return self.get_mid_list()
  def get_unread(self):
    return self.__mbsearch('UNSEEN')









