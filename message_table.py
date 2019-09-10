import operator as op
import numpy as np
import pandas as pd
from api_test import Message, MessageListing, Article

ML = MessageListing('creds.pkl')
arr = ML[-1]
attrs = ['artid', 'authors', 'body', 'categories', 'link', 'title']
get = op.attrgetter(*attrs)
df = pd.DataFrame(map(get,arr.Articles),columns=attrs)
