import numpy as np
import re

class ArXivDigest(object):

    subscriptions = []

    def __init__(self, subscriptions, message_array, date=None):
        self.arr = message_array
        self.subscriptions.extend(subscriptions)
        self.subscr_arr = np.array(self.subscriptions)
        self.date = str(date) or '9999-99-99'

    def __get_idx(self, patt):
        """find indices of pattern in array"""
        return np.where(np.char.find(self.arr, patt) + 1)

    def __hdr_idx(self):
        sk1 = re.compile('received from  [MTWF][ouehr][nedui]')
        sk2 = re.compile('Submissions')
        loc = np.array([
            e for e, v in enumerate(self.arr) if sk1.match(v) or sk2.match(v)
        ])
        if len(loc) != 2:
            raise RuntimeError('the stupid set header index function broke')
        loc += [-1, 2]
        self.head_idx = np.r_[slice(*loc)]

    def set_header(self, header_array=None):
        """Setter for header"""
        if header_array:
            self.head_idx = header_array
        else:
            self.__hdr_idx()

    def get_header(self):
        """Getter for Header"""
        if not hasattr(self, 'head'):
            self.__hdr_idx()
        return self.head_idx

    def __set_art(self):
    
        h1 = self.get_header()
        a1 = self.__get_idx(''.join(['-']*78))[0]
        return a1[a1 > h1[-1]]
  
    def get_art(self):
        """Getter for articles"""
        if not hasattr(self, 'art_posn'):
            self.set_art()
        return self.art_posn
  
    def set_art(self, posn_array=None):
        """Setter for articles"""
        if posn_array:
            self.art_posn = posn_array
        else:
            self.art_posn = self.__set_art()

    def sub_arr(self):
        """sub_arr:
            initialize subarray containing only article data
            helper for get_sub_arr
        Parameters: ArXivDigest object
        returns:    None
        """
        A = self.get_art()
        junk = np.ones((A.shape[0], 2), dtype=int) * -1
        junk[:, 0] = A
        junk[:-1, 1] = A[1:]
        self.sub = np.concatenate([
            self.arr[slice(*r)] for r in junk
        ])
        self.junk = junk-A[0]
        self.junk[-1,-1] = self.arr.shape[0] - A[0]

    def get_sub_arr(self):
        """get_sub_arr - get subarray containing only article data
        
        Parameters: ArXivDigest object
        returns:    sub array
        """
        if not hasattr(self, 'sub'):
            self.sub_arr()
        return self.sub
  
    def __len__(self):
        if not hasattr(self, 'sub'):
            self.sub_arr()
        return self.junk.shape[0]
  
    def __getitem__(self, idx):
        # needs a try except...
        if not hasattr(self, 'sub'):
            self.sub_arr()
        return self.sub[slice(*self.junk[idx])]
  
    def __setitem__(self, idx, val):
        # needs a try except...
        if not hasattr(self, 'sub'):
            self.sub_arr()
        self.sub[slice(*self.junk[idx])] = val

    def __iter__(self):
        """iterate through articles"""
        if not hasattr(self, 'sub'):
            self.sub_arr()
        return iter(self.sub[i:j] for i, j in self.junk)

    def __repr__(self):
        ostr = '<{cname}|{date}|{acount}>'
        ostr = ostr.format(**{
            'cname': type(self).__name__,
            'date': self.date,
            'acount': len(self)
        })
        return ostr
    
    
    
  

