import datetime
from base64 import urlsafe_b64decode
from email import message_from_bytes
import numpy as np
from ..article.article import Article


class Message(object):
    """Message object for Parsing articles from an email

    Parameters
    ----------
        message_obj : email dictionary

    Other Parameters
    ----------------
        article : `str`, optional
            pattern on which to split. Default ``'arXiv:'``
        end_posn : `str`, optional
            end pattern.  Default ``'%%--%%--%%'``

    """
    __slots__ = ('ID', 'Date', 'Articles')

    def __init__(self, message_obj, **patterns):
        apos = patterns.get('article', 'arXiv:')
        epos = patterns.get('end_posn', '%%--%%--%%')
        aend = patterns.get('art_end', '\\\\')
        self.ID = message_obj['id']
        self.Date = datetime.datetime.fromtimestamp(
            int(message_obj['internalDate'])/1000.0
        )
        mess = message_from_bytes(
            urlsafe_b64decode(message_obj['raw'].encode('ASCII'))
        )
        mess = np.array(mess.as_string().splitlines())
        self._art_proc(mess, apos, aend, epos)

    def __len__(self):
        return self.Articles.shape[0]

    def __repr__(self):
        ostr = "<ID={0}|Date={1:%Y-%m-%d}|Articles={2}>"
        return ostr.format(
            self.ID, self.Date, self.Articles.shape[0]
        )

    def _art_proc(self, mess, apos, aend, epos):
        _end = np.where(np.char.startswith(mess, epos))[0]
        trunc = mess[:_end[0]]
        sw = np.where(np.char.startswith(trunc, apos))[0]
        _art = sw[np.where(np.char.startswith(trunc[sw-1], aend))[0]]

        _art = _art[_art < _end[0]]
        slices = np.vstack(
            (_art, np.concatenate((_art[1:], _end)))
        ).T
        self.Articles = np.empty(slices.shape[0], dtype=object)
        for e, s in enumerate(slices):
            art = np.array([i for i in mess[slice(*s)] if len(i)])
            self.Articles[e] = Article(art)






