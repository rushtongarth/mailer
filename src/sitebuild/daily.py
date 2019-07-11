import requests
import pprint
import json
from datetime import datetime, date


class DailyBuild(object):
     '''daily site builder 
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
         self.url = config.get('app_page','apiurl')
         self.payload = {
             'site' : config.get('DEFAULT','appsite'),
             'key' : config.get('app_page','apikey'),
         }
     def deploy(self,to_load):
         payload = dict(
             action = 'deploy',
             resource = '{}.html'.format(self.dow_verbose),
             code = to_load,
             **self.payload
         )
         obj = requests.post(self.url,data=payload).json()
         if any(obj.values()):
             print("ERROR!")
             pprint.pprint(obj,width=40,indent=2)
         else:
             pprint.pprint(obj,width=40,indent=2)
         return obj
         

