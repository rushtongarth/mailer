from .ArXiv import ArXivDigest
from .Article import Article
import itertools as it
import numpy as np



def ArxLoader(message,ArxDigest):
  '''prep digest for db insertion'''
  ms_date = message.get_date()
  grouped = ArxDigest.group_abstracts()
  keys = [
    'date_received','title',
    'pri_categories','all_categories',
    'body','link'
  ]
  kwargs = dict.fromkeys(keys)
  kwargs['date_received']=ms_date.date()
  art_list = []
  for long_p_cats, p_cats, arts in grouped:
    kwargs['pri_categories']=p_cats
    for title,categories,body,lnk in arts:
      kwargs['title']=title
      kwargs['all_categories']=categories
      kwargs['body']=body
      kwargs['link']=lnk
      A = Article(**kwargs)
      art_list.append(A)
  return art_list


