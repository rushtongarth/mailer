
import os
import configparser
import jinja2
import json

class CoreLoader(object):
  '''load configuration files and settings
  
  :param bool test_mode: testing flag (default: false)
  :param str config: path configuration to file
  :param str template: path to html file containing email template
  :param str json: path to json file containing subscription data
  '''
  def __init__(self,**kwargs):
    self.test = kwargs.get('test_mode',False)
    self.conf = kwargs.get('config','')
    self.temp = kwargs.get('template','')
    self.json = kwargs.get('jsonfile','')
  def __repr__(self):
    outstr="<data from: {fn}>"
    name = os.path.basename(self.conf)
    return outstr.format(fn=name)
  def __fex(self,str_in):
    return os.path.exists(str_in)
  def __loadconfig(self):
    self.C = configparser.ConfigParser(
      interpolation = configparser.ExtendedInterpolation()
    )
    with open(self.conf,'r') as cf:
      self.C.read_file(cf)
    creds = self.C['Service Address']
    self.name = creds['name']
    self.pswd = creds['pass']
    addrs = self.C['Receivers']
    self.to_ad = addrs['to_list'].split()
    self.cc_ad = addrs['cc_list'].split()
  @property
  def credentials(self):
    if not all([hasattr(self,'name'),hasattr(self,'pswd')]):
      self.__loadconfig()
    return self.name,self.pswd
  @property
  def addresses(self):
    if not all([hasattr(self,'to_ad'),hasattr(self,'cc_ad')]):
      self.__loadconfig()
    return self.to_ad,self.cc_ad
  @property
  def header(self):
    nm,ps = self.credentials
    to,cc = self.addresses
    return nm,ps,to,cc
  @property
  def template(self):
    if not hasattr(self,'_template'):
      with open(self.temp,'r') as f:
        tmp = f.read()
      self._template = jinja2.Template(tmp)
    return self._template
  @property
  def jsonfile(self):
    if not hasattr(self,'_json'):
      with open(self.json,'r') as f:
        self._json = json.load(f)
    return self._json
  @property
  def subscriptions(self):
    return list(self.jsonfile['subscription'].items())
