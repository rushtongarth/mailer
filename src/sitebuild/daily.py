import requests
import pathlib
from datetime import datetime, date

from configparser import ConfigParser, ExtendedInterpolation
    

class DailyBuild(object):
     '''daily site build 
     '''
     
     day = {
         0 : 'monday',
         1 : 'tuesday',
         2 : 'wednesday',
         3 : 'thursday',
         4 : 'friday'
     }
     
     def __init__(self,config=None,date_obj=None):
         self._date = date_obj or date.today()
         self.dow = self._date.weekday()
         self.dow_verbose = self.day[self.dow]
         self.__config_load(config)
         
     def __config_load(self,config):
         P = pathlib.Path(config).resolve()
         if not P.exists():
             err_str = "The file: '{}' does not exist"
             raise FileNotFoundError(err_str.format(P))
         self.cfg = ConfigParser(
             interpolation = ExtendedInterpolation()
         )
         with P.open() as f:
             self.cfg.read_file(f)

     def deploy(self,to_load):
         url = self.cfg.get('app_page','apiurl')
         payload = {
             'action' : 'deploy',
             'site' : self.cfg.get('DEFAULT','appsite'),
             'key' : self.cfg.get('app_page','apikey'),
             'resource': '{}.html'.format(self.dow_verbose),
             'code':to_load
         }
         return requests.post(url,data=payload).json()
         

