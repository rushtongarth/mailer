
import os,string,time,smtplib
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
  
  def set_cc(self,cc):
    self.cc = cc
  def get_cc(self):
    return self.cc
  
  def dist_prep(self,el):
    if isinstance(el,list):
      return ','.join(el)
    else:
      return el
  
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

    msg_to = self.dist_prep(self.receiver)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subj
    msg['To']      = msg_to
    msg['From']    = self.get_from()
    if hasattr(self,'cc'):
      msg['Bcc']   = self.dist_prep(self.cc)
    part1 = MIMEText('', 'plain')
    part2 = MIMEText(content, 'html')
    msg.attach(part1)
    msg.attach(part2)
    out = self.conn.send_message(msg)

    if len(out):
      print("errors in sending to:")
      print(out)
      return 1
    return 0
    
