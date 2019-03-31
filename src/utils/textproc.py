import pandas as pd,torchtext,spacy,sqlalchemy as sql,sqlalchemy.orm as sqlorm,numpy as np
from db.api import dbapi

DATADIR = '/home/stephen/Code/dev/mailer/db/arxiv.articles.db'
ses = sqlorm.sessionmaker(bind=sql.create_engine('sqlite:///'+DATADIR))()
api = dbapi(ses)
cols = api.get_cols('title','body')
df = pd.DataFrame({'body':cols[:,1],'title':cols[:,0]})
spen = spacy.load('en')
def tokz(tin): return [tok.text for tok in spen.tokenizer(tin)]
UNK,PAD,SOS,EOS,LWR = "<unk>","<pad>","<s>","</s>",True
kwgs={'tokenize':tokz,'batch_first':True,'lower':LWR,'include_lengths':True,'unk_token':UNK,'pad_token':PAD,'init_token':None, 'eos_token':EOS}
SRC = torchtext.data.Field(**kwgs)
TRG = torchtext.data.Field(**kwgs)

abstracts  = api.abstracts
categories = api.categories[:,0]
df = pd.DataFrame({'pcat':categories})
pri_cats = df.pcat.str.split(pat=',',expand=True)
pri_cats = pri_cats.rename(columns={i:'c%d'%i for i in pri_cats.columns})
pri_cats = pri_cats.applymap(lambda X: '' if X is None else X)


TEXT = torchtext.data.Field(sequential=True,tokenize=lambda X: X.split(' '))
LABL = torchtext.data.Field(sequential=False,use_vocab=False)
data_set = [("abstract",TEXT),("cat1",LABL)]

fields = {'body':SRC,'title':TRG}


ds = DataFrameDataset(df,fields)
train,valid,test = ds.split(split_ratio=[.7,.2,.1])
SRC.build_vocab(train)
TRG.build_vocab(train)
train_iter,test_iter,valid_iter = torchtext.data.Iterator.splits((train,test),batch_sizes=(16, 256, 256),sort_key=lambda X: len(X.body))

