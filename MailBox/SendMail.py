import os,string,time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from MailBox.MailBox import AbstractMailBox

class SendMail(AbstractMailBox):
  def __init__(self,user,pswd,location="smtp.gmail.com"):
    self.user = user
    self.pswd = pswd
    self.fold = location
    super().__init__(user,pswd,location)

  def set_to(self,to):
    self.receiver = to
  def get_to(self):
    if hasattr(self,'receiver'):
      return self.receiver
    self.set_to(self.user)
    return self.receiver
  
  def set_from(self,sender):
    self.sender = sender
  def get_from(self):
    if hasattr(self,'sender'):
      return self.sender
    self.set_from(self.user)
    return self.sender
  
  def __enter__(self):
    self.conn = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    r,d = self.conn.login(self.user, self.pswd)
    return self
  def __exit__(self,*args):
    self.conn.close()
  def distribute(self,subj,content):
    if isinstance(self.receiver,list):
      msg_to = ','.join(self.receiver)
    else:
      msg_to = self.receiver
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subj
    msg['To'] = msg_to
    part1 = MIMEText('', 'plain')
    part2 = MIMEText(content, 'html')
    msg.attach(part1)
    msg.attach(part2)
    out = self.conn.sendmail(self.get_from(),self.get_to(),msg.as_string())
    if len(out):
      print("errors in sending to:")
      print(out)
      return 1
    return 0
    
