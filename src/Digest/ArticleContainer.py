import re
import datetime
from hashlib import sha256
import numpy as np

dsk = re.compile(
    r' '.join([
        '.*(?P<date>[MTWFS][aehoru][deintu],', '[0-9]{,2}',
        '[JFMASOND][a-z][a-z]',
        '[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} GMT).*'])
    )


class ArXivArticle(object):

    """Arxive Article container"""

    def __init__(self, text_arr, user_subs):
        self.raw = text_arr
        self.subs = np.array(user_subs)

    def __repr__(self):
        ostr = '<{}|{}|{}>'
        ostr = ostr.format(
            hash(self),
            self.date,
            self.title[:45]
        )
        return ostr

    def __hash__(self):
        return hash(self.shakey)

    def __eq__(self, other):
        if self.shakey == other.shakey:
            return True
        return False

    def __pat_match(self, patt, mode=None):
        """pat_match: match pattern on instance text_arr"""
        if mode == 'start':
            found = np.char.startswith(self.raw, patt)
        else:
            found = np.char.find(self.raw, patt)+1
        return np.where(found)[0]

    @property
    def date(self):
        _dstr = [
            dsk.match(x).group('date') for x in self.raw if dsk.match(x)
        ]
        dstr = _dstr[0]
        self.__art_date = datetime.datetime.strptime(
            dstr, '%a, %d %b %Y %H:%M:%S %Z'
        )
        return self.__art_date

    @property
    def shakey(self):
        if not hasattr(self, '_shakey'):
            self.__shakey()
        return self._shakey

    def __shakey(self):
        h = sha256(bytes(self.link, 'utf8'))
        self._shakey = h.hexdigest()

    @property
    def title(self):
        if not hasattr(self, '_title'):
            self.__title()
        return self._title

    def __title(self):
        pat1, pat2 = 'Title: ', 'Authors: '
        loc1 = self.__pat_match(pat1, 'start')
        loc2 = self.__pat_match(pat2, 'start')
        pat_range = np.r_[loc1:loc2]
        tstr = ' '.join(self.raw[pat_range])
        tstr = np.char.replace(tstr, pat1, '')
        self._title = tstr.item()

    @property
    def link(self):
        if not hasattr(self, '_link'):
            self.__link()
        return self._link

    def __link(self):
        patt = '\\\\ ( https://arxiv.org/abs'
        locn = self.__pat_match(patt)
        if len(locn) == 0:
            self._link = ''
        else:
            mtch = self.raw[locn]
            link = re.match(r'\\\\ \((.*),.*', mtch.item())
            if link is None:
                raise RuntimeError('the stupid set link function broke')
            self._link = link.group(1).strip()

    @property
    def all_cats(self):
        if not hasattr(self, '_all_cats'):
            self.__cats()
        return self._all_cats

    def __cats(self):
        patt = 'Categories: '
        locn = self.__pat_match(patt, 'start')
        cats = self.raw[locn].item()
        cats = np.char.replace(cats, patt, '')
        cats = np.char.split(cats, ' ')
        self._all_cats = np.array(cats.item())

    @property
    def pri_cats(self):
        if not hasattr(self, '_pri_cats'):
            self.__pcats()
        return self._pri_cats

    def __pcats(self):
        tags, descr = np.hsplit(
            self.subs,
            self.subs.shape[-1]
        )
        inter, all_tags, sub_tags = np.intersect1d(
            self.all_cats, tags, return_indices=True
        )
        mycats = np.zeros(tags.shape, dtype=bool)
        mycats[sub_tags] = True
        self._pri_cats = self.subs[mycats.squeeze()][:, 0]

    @property
    def abstract(self):
        if not hasattr(self, '_abstract'):
            self.__abstract()
        return self._abstract

    def __abstract(self):
        pat1 = '\\\\'
        locs = self.__pat_match(pat1, 'start')
        if len(locs) == 2:
            abst = self.title
        elif len(locs) >= 3:
            chunk = locs[1:]+[1, 0]
            abst = self.raw[slice(*chunk)]
            abst = ' '.join(abst)
        else:
            print(self.__dict__)
            raise RuntimeError('the stupid abstract function broke')
        self._abstract = np.array([
            l.strip() for l in abst.split('.') if len(l.strip())
        ])

    def to_dict(self):
        return dict(
            shakey=self.shakey,
            date_received=self.date,
            title=self.title,
            pri_categories=self.pri_cats,
            all_categories=self.all_cats,
            body=self.abstract,
            link=self.link,
        )
