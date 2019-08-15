from googleapiclient.discovery import build
import pickle as pkl

def ListMessagesMatchingQuery(cred_file,qstr="no-reply@arxiv.org"):
    
    with open(cred_file,'r') as cf:
        creds = pkl.load(cf)
    
    service = build('gmail', 'v1', credentials=creds)
    M = service.users().messages()
    L = m.list(userId="me",q=qstr).execute()
    
    messages = []
    if 'messages' in L:
      messages.extend(L['messages'])
    while 'nextPageToken' in L:
      page_token = L['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
