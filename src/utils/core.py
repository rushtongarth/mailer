
import argparse
import os
import datetime
import configparser
import json
import jinja2
import numpy as np

class CoreLoader(object):
  def __init__(self,**kwargs):
    '''CoreLoader
    Args:
      test_mode     : bool : is testing (default of false)
      config        : str  : path to file
      subscriptions : str  : path to file
    '''
    self.test = kwargs.get('test_mode',False)
    self.conf = kwargs.get('config','')
    self.subs = kwargs.get('subscriptions','')
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

def mailprep(digest):
  grouped = []
  for disc,elements in digest.grouping:
    title = elements['title']
    links = elements['link']
    acats = np.char.join(', ',elements['all_cats'])
    grouped.append((disc,list(zip(title,links,acats))))
  return grouped


def send_mailz(mail_obj,send_from,send_to,cc_to,test=False):
  mail_obj.set_sender(send_from)
  mail_obj.set_to(send_to)
  if not test:
    mail_obj.set_cc(cc_to)
    ostr = ','.join(cc_to) if isinstance(cc_to,list) else cc_to
    print("cc'd to: {}".format(ostr))


