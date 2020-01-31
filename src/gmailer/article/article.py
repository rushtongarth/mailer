import numpy as np


class Article(object):
    """Article loader

    Load and process articles has the following specific slots
        artid, title, authors, categories, link, body

    Parameters
    ----------
        art_obj : numpy.ndarray
            article object

    Other Parameters
    ----------------
        splitter : `str`, optional
            pattern on which to split. Default ``'\\\\'``
        title : `str`, optional
            title pattern.  Default ``'Title: '``
        authors : `str`, optional
            author pattern.  Default ``'Authors: '``
        categories : `str`, optional
            category pattern.  Default ``'Categories: '``
    """
    __slots__ = (
        'artid', 'title', 'authors', 'categories', 'link', 'body'
    )

    def __init__(self, art_obj, **patterns):
        splitter = patterns.get('splitter', '\\\\')
        tpat = patterns.get('title', 'Title: ')
        apat = patterns.get('authors', 'Authors: ')
        cpat = patterns.get('categories', 'Categories: ')
        found = np.char.find(art_obj, splitter)+1
        # Added equal one to avoid false matches
        locs = np.where(found == 1)[0]
        head, body = np.split(art_obj, locs)[:2]
        self.artid = head[0].split()[0]
        self.__head(head, tpat, apat, cpat)
        self.__categories(head, cpat)
        self.__body(body)

    def __repr__(self):
        ostr = "<id={0}|title={1}|categories={2}>"
        return ostr.format(
            self.artid, self.title, ', '.join(self.categories)
        )

    def __multirow(self, head, start_pattern, end_pattern):
        _range = np.char.startswith(head, start_pattern)
        _range |= np.char.startswith(head, end_pattern)
        idx = np.where(_range)[0]
        raw = head[slice(*idx)].copy()
        raw[0] = raw[0][len(start_pattern):]
        return np.char.strip(raw)

    def __head(self, head, tpat, apat, cpat):
        self.title = ' '.join(self.__multirow(head, tpat, apat))
        astr = ' '.join(self.__multirow(head, apat, cpat))
        astr = astr.replace(' and ', ', ')
        # needs update from article 2001.02960
        # account for multiple splits per author
        self.authors = np.array(astr.split(', '))

        lc = np.char.lower(self.artid.split(':'))
        self.link = 'https://{0}.org/abs/{1}'.format(*lc)

    def __categories(self, head, cpat):
        locs = np.char.startswith(head, cpat)
        clist = head[locs].item()[len(cpat):].split()
        self.categories = np.array(clist)

    def __body(self, body):
        onestr = ' '.join(np.char.strip(body[1:]))
        # self.body = np.array(onestr.split('. '))
        self.body = onestr
