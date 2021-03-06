import imaplib
import email
import datetime
import re
import numpy as np
# custom modules
from .MailBox import AbstractMailBox
from .MailErrors import login_check,unknown_loc,fetch_check,search_check
from .MessageContainer import MessageContainer

class ReadMail(AbstractMailBox):
  '''
  ReadMail
  
  Establish a connection to read emails. Acts as a context 
  manager for more convenience and usability
  
  :param user: username for account
  :type user: str
  :param pswd: password for account
  :type pswd: str
  :param location: where in inbox to search for messages
  :type location: str
  :param sender: sender to search for
  :type sender: str
  
  Example::
    mail = ReadMail('username','password',"INBOX",'example@example.com')
  '''
  def __init__(self,user,pswd,location,sender,index=None):
    self.sk = re.compile(b'.*UID (?P<num>[0-9]{1,}) RFC.*')
    self.user = user
    self.pswd = pswd
    self.folder = location
    self.sender = sender
    self.idx = index
    super().__init__(user,pswd,location)
  def __enter__(self):
    self.mbox = imaplib.IMAP4_SSL('imap.gmail.com')
    r,d = self.mbox.login(self.user,self.pswd)
    login_check(r,d)
    r,d = self.mbox.select(self.folder)
    unknown_loc(r,self.folder,d)
    # load available ids to object assuming everything else worked
    self._ids()
    if self.idx is not None:
      if not isinstance(self.idx,(list,tuple)):
        self.idx = list(self.idx)
      self.__subset(self.idx)
    else:
      self.__full_pull()
    return self
  def __exit__(self,*args):
    self.mbox.close()

  def __len__(self):
    '''length of marray'''
    return len(self._messages)
  
  def __iter__(self):
    '''iterator for messages'''
    for head,mess in self._messages:
      pr = self.sk.match(head)
      mt = email.message_from_bytes(mess)
      yield pr.group('num'),mt
  def __getitem__(self,idx):
    tmp = self._messages[idx]
    pr = self.sk.match(tmp[0])
    mt = email.message_from_bytes(tmp[1])
    return pr.group('num'),mt

  def __mbsearch(self,*args):
    '''search helper'''
    search_arg = list(args) + ['FROM "{:}"'.format(self.sender)]
    search_str = '('+' '.join(search_arg)+')'
    r,d = self.mbox.uid('search',None,search_str)
    return search_check(r,d)

  def __fetcher(self,toget):
    '''message fetching helper'''
    res,data = self.mbox.uid('fetch',toget,"(RFC822)")
    fetch_check(res,data,toget)
    return data
  def _ids(self):
    '''_ids: find uids reported by mailbox'''
    if not hasattr(self,'mid_list'):
      data = self.__mbsearch()
      self.mid_list = next(map(bytes.split,data))
  def __full_pull(self):
    idstr = b','.join(self.mid_list)
    prep = self.__fetcher(idstr)
    # remove non message entries from prep
    self._messages = [x for x in prep if isinstance(x,tuple)]
  def __subset(self,idxes):
    ids = np.array(self.mid_list)[idxes]
    idstr = b','.join(ids)
    prep = self.__fetcher(idstr)
    # remove non message entries from prep
    self._messages = [x for x in prep if isinstance(x,tuple)]
    
  @property
  def messages(self):
    '''
    messages
    
    getter for messages
    
    :return: list of message tuples
    :rtype: list 
    '''
    if not hasattr(self,'_messages'):
      self.__full_pull()
    return self._messages
  @property
  def MessageContainer(self):
    '''
    MessageContainer
    
    convert messages into :class:`MessageContainer` format
    
    :return: message container
    :rtype: :class:`MessageContainer`
    '''
    marr = [(x,y) for x,y in self]
    mc = MessageContainer(len(marr),marr)
    return mc

  def get_by_uid(self,toget):
    '''get_by_uid'''
    idx = self.mid_list.index(toget)
    num,mess = self[idx]
    return num,mess

  def get_latest_raw(self):
    '''get_latest_raw'''
    return self.get_by_uid(self.mid_list[-1])


