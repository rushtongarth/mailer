import imaplib,email,datetime,numpy as np,re

from MailBox.MailBox import AbstractMailBox
from .MailErrors import login_check,unknown_loc,fetch_check,search_check
from .MessageContainer import MessageContainer

class ReadMail(AbstractMailBox):
  '''ReadMail Class: establish a connection to read emails
  Args:
    user     : username
    pswd     : password
    location : folder in which to search
    sender   : sender to search for
  '''
  def __init__(self,user,pswd,location,sender):
    self.sk = re.compile(b'.*UID (?P<num>[0-9]{1,}) RFC.*')
    self.user = user
    self.pswd = pswd
    self.folder = location
    self.sender = sender
    super().__init__(user,pswd,location)
  def __enter__(self):
    self.mbox = imaplib.IMAP4_SSL('imap.gmail.com')
    r,d = self.mbox.login(self.user,self.pswd)
    login_check(r,d)
    r,d = self.mbox.select(self.folder)
    unknown_loc(r,self.folder,d)
    # load available ids to object assuming everything else worked
    self._ids()
    self.get_all()
    return self
  def __exit__(self,*args):
    self.mbox.close()
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
    '''_ids'''
    if not hasattr(self,'mid_list'):
      data = self.__mbsearch()
      self.mid_list = next(map(bytes.split,data))
  def get_all(self):
    idstr = b','.join(self.mid_list)
    prep = self.__fetcher(idstr)
    self.messages = [x for x in prep if x!=b')']
  def __len__(self):
    return len(self.messages)
  def __iter__(self):
    for head,mess in self.messages:
      pr = self.sk.match(head)
      mt = email.message_from_bytes(mess)
      yield pr.group('num'),mt
  def __getitem__(self,idx):
    tmp = self.messages[idx]
    pr = self.sk.match(tmp[0])
    mt = email.message_from_bytes(tmp[1])
    return pr.group('num'),mt

  def as_MessageContainer(self):
    marr = [(x,y) for x,y in self]
    mc = MessageContainer(len(marr),marr)
    return mc

  def get_by_uid(self,toget):
    '''get_by_uid'''
    idx = self.mid_list.index(toget)
    num,mess = self[idx]
    #self.mess = email.message_from_bytes(data[0][1])
    return num,mess

  def get_latest_raw(self):
    '''get_latest_raw'''
    return self.get_by_uid(self.mid_list[-1])

  #def __read_part(self,part):
    ## read message parts
    #if part.get_content_maintype() != 'text':
      #for subp in part.get_payload():
        #yield from self.__read_part(subp)
    #else:
      #yield part.get_payload()

  #def mail_proc(self,mess):
    ## process messages
    #mess_parts = self.__read_part(mess)
    #_arr = [np.array(pt.splitlines()) for pt in mess_parts]
    #_arr = np.array([np.char.strip(y) for y in _arr])
    #return _arr.squeeze()

  #def get_all_raw(self):
    #'''get_all_raw'''
    #mids = self.get_mid_list()
    #toget = b','.join(mids)
    #data = self.__fetcher(toget)
    #mess_list = []
    #for i in range(0,len(data),2):
      #_curr = email.message_from_bytes(data[i][1])
      #mess_list.append(_curr)
    #return mess_list

  #def get_unread(self):
    #'''get_unread'''
    #return self.__mbsearch('UNSEEN')


  #def set_sender(self,sender):
    #self.sender = sender
  #def get_all(self):
    #ml = self.get_all_raw()
    #for e,m in enumerate(ml):
      #ml[e] = self.mail_proc(m)
    #return ml
  #def get_mid_list(self):
    #'''get_mid_list'''
    #return self.mid_list
  #def get_ids(self):
    #'''get_ids'''
    #return self.mid_list
  #def fetch(self,toget):
    #return self.__fetcher(toget)
