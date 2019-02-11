import textwrap
import numpy as np
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base



Base = declarative_base()


class EmailBase(Base):
  '''Class container for received emails'''
  __tablename__ = 'email'
  id       = sql.Column(sql.Integer,primary_key=True)
  uid      = sql.Column(sql.Integer)
  date     = sql.Column(sql.String)
  articles = relationship('ArticleBase', back_populates="email")
  def __repr__(self):
    s = "<Email(uid={i},date={d},articles={n})>"
    s = s.format(
      i=self.uid,d=self.date,n=len(self.articles)
    )
    return s


class ArticleBase(Base):
  '''Class container for arxiv journals'''
  __tablename__ = 'Article'
  shakey   = sql.Column(sql.String(64), primary_key=True)
  date     = sql.Column(sql.String)
  title    = sql.Column(sql.Text)
  pri_cats = sql.Column(sql.String)
  all_cats = sql.Column(sql.String)
  body     = sql.Column(sql.Text)
  link     = sql.Column(sql.String)
  ncats    = sql.Column(sql.Integer)
  email_id = sql.Column(sql.Integer, sql.ForeignKey('email.uid'))
  email    = relationship('EmailBase', back_populates="articles")
  
  def __repr__(self):
    sout = "<Article(title={t},categories={c})>"
    t1 = textwrap.shorten(self.title, width=20)
    return sout.format(d=self.date,t=t1,c=self.pri_cats,l=self.link)


  
