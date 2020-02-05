import pickle as pkl
from googleapiclient.discovery import build



def googobj(creds='creds.pkl'):
    with open(creds, 'rb') as f:
        creds = pkl.load(f)
    return build('gmail', 'v1', credentials=creds)
