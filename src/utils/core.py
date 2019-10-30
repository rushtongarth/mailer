import argparse
import datetime
import numpy as np

from src.utils.ConfLoader import CoreLoader


def mailprep(digest):
    grouped = []
    for disc, elements in digest.grouping:
        title = elements['title']
        links = elements['link']
        acats = np.char.join(',  ', elements['all_cats'])
        grouped.append((disc, list(zip(title, links, acats))))
    return grouped


def send_mailz(mail_obj, send_from, send_to, cc_to=None, test=False):
    mail_obj.set_sender(send_from)
    mail_obj.set_to(send_to)
    if not test:
        mail_obj.set_cc(cc_to)
        ostr = ', '.join(cc_to) if isinstance(cc_to, list) else cc_to
        print("cc'd to: {}".format(ostr))
