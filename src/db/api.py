import numpy as np
import pandas as pd

from src.db.schema import ArticleBase


class dbapi(object):
    """dbapi : database interface to make my life easier"""
    def __init__(self, session, order_col='date'):
        self.sess = session
        self.Q = session.query
        self.set_order(order_col)
        self.attr = lambda X: getattr(ArticleBase, X)

    def set_order(self, ordering):
        self.order = ordering

    def get_order(self):
        return self.order

    def get_cols(self, *args):
        col_names = set([
            'shakey', 'date', 'title', 'pri_cats', 'all_cats',
            'body', 'link', 'ncats', 'email_id'
        ])
        ordering = self.attr(self.get_order())
        col_args = set(args) & col_names
        cols = [
            getattr(ArticleBase, x) for x in col_args
        ]
        no_order = self.Q(*cols)
        return no_order.order_by(ordering)

    def as_df(self, *args):
        query = self.get_cols(*args)
        return pd.read_sql(query.statement, query.session.bind)

    @property
    def abstracts(self):
        ordering = self.attr(self.get_order())
        no_order = self.Q(ArticleBase.body)
        return np.array(no_order.order_by(ordering).all())

    @property
    def categories(self, order_col='date'):
        ordering = self.attr(self.get_order())
        no_order = self.Q(ArticleBase.pri_cats, ArticleBase.all_cats)
        return np.array(no_order.order_by(ordering).all())

    @property
    def titles(self, order_col='date'):
        ordering = self.attr(self.get_order())
        no_order = self.Q(ArticleBase.title)
        return np.array(no_order.order_by(ordering).all())

    @property
    def shas(self, order_col='date'):
        ordering = self.attr(self.get_order())
        no_order = self.Q(ArticleBase.shakey)
        return np.array(no_order.order_by(ordering).all())

    def load_single_ebase(self, ebase):
        try:
            self.sess.add(ebase)
        except Exception as err:
            o = 'error with email: {e.uid}'
            print(o.format(e=ebase))
            print(err)
            self.sess.rollback()
