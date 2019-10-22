from .listing.listing import MessageListing
import pandas as pd
import operator as op


#class api(object):
    #"""
    #"""
    
    #def __init__(self,creds):
        #self.mlist = MessageListing(creds)

    #def __len__(self):
        #return len(self.mlisting)
    
    #def __iter__(self):
        #for i in range(len(self)):
            
            #yield self.mlisting[i]

def message_df(idx=0, credentials='creds.pkl'):
    ML = MessageListing(credentials)
    arr = ML[idx]
    attrs = ['artid', 'authors', 'body', 'categories', 'link', 'title']
    get = op.attrgetter(*attrs)
    df = pd.DataFrame(map(get, arr.Articles), columns=attrs)
    return df
