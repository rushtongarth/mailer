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
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subj
    msg['To'] = self.get_to()
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
    
#def send_email(**kwargs):
  #FROM = kwargs.get('FROM')
  #pwd = kwargs.get('pwd')
  #recipient = kwargs.get('recipients')
  #subj = kwargs.get('subject')
  #if isinstance(recipient,list):
    #TO = ', '.join(recipient)
  #elif isinstance(recipient,str):
    #TO = recipient
  #else:
    #TO = FROM
  ## Create message container - the correct MIME type is multipart/alternative.
  #msg = MIMEMultipart('alternative')
  #msg['Subject'] = subj
  ##msg['From'] = FROM
  #msg['To'] = TO

  ## Create the body of the message (a plain-text and an HTML version).
  #text,html = build_email()
  ## Record the MIME types of both parts - text/plain and text/html.
  #part1 = MIMEText(text, 'plain')
  #part2 = MIMEText(html, 'html')
  ## Attach parts into message container.
  ## According to RFC 2046, the last part of a multipart message, in this case
  ## the HTML message, is best and preferred.
  #msg.attach(part1)
  #msg.attach(part2)
  #try:
    ## Send the message via SMTP_SSL gmail server.
    #server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    #server_ssl.login(FROM, pwd)
    ## sendmail function takes 3 arguments: sender's address, recipient's address
    ## and message to send - here it is sent as one string.
    #server_ssl.sendmail(FROM, TO, msg.as_string())
    #server_ssl.close()
    #print('successfully sent')
  #except:
    #print('failed to send')
