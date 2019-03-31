
import textwrap,sys


class Error(Exception):
  def __init__(self,message,error):
    super().__init__(message)
    self.mess  = message
    self.error = error
  def __repr__(self):
    ln = '#'.join(['#']*40)
    errstr = '{0}\n{1}\n{0}'
    mess = '{}\n\n{}'.format(self.mess,self.error)
    mess = textwrap.indent(mess,'# ',lambda line: True)
    return errstr.format(ln,mess)
    
class MailBoxError(Error):
  def __init__(self,error):
    mstr = 'MailBoxError:'
    super().__init__(mstr,error)
class MailSearchError(Error):
  def __init__(self,error):
    mstr = 'MailSearchError: Search unsuccessful'
    super().__init__(mstr,error)

def login_check(val,strin):
  if val == 'OK':
    return 0
  else:
    errstr='received <%s> unable to log in'%str(strin)
    try: 
      raise MailBoxError(errstr)
    except MailBoxError as err: 
      print(repr(err),file=sys.stderr) 
      raise
    finally:
      return -1

def unknown_loc(val,strin,received):
  if val=='OK':
    return 0
  else:
    errstr = 'Unable to locate <%s>'%str(strin)
    errstr+= 'received: [%s]'%str(received)
    try:
      raise MailBoxError(errstr)
    except MailBoxError as err:
      print(repr(err),file=sys.stderr) 
      raise
    finally:
      return -1
def fetch_check(val,received,terms):
  if val=='OK':
    return 0
  else:
    errstr = 'Search for:\n%s\n'%str(terms)
    errstr+= 'Returned %s'%str(received)
    try:
      raise MailSearchError(errstr)
    except MailSearchError as err:
      print(repr(err),file=sys.stderr)
      raise
    finally:
      return -1
def search_check(val,data):
  if val == 'OK':
    return data
  else:
    return [b'']


