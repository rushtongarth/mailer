import smtplib
from base64 import urlsafe_b64decode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.gmailer import googobj
from .MailBox import AbstractMailBox


def send_test_gmail(gobj, body, mess_to, mess_from):
    message = MIMEText(body)
    message['to'] = mess_to
    message['from'] = mess_from
    message['subject'] = 'testing'
    mstr = message.as_string()
    msg = dict(raw=urlsafe_b64encode(mstr).decode())
    gmessages = gobj.users().messages()
    try:
        tosend = gmessages.send(userId="me", body=msg).execute()
        return tosend
    except Exception as E:
        raise E

class SendMail(AbstractMailBox):
    """SendMail

    Establish a connection to send emails. Can act as a
    context manager for more convenience and usability

    :param user: username for account
    :type user: str
    :param pswd: password for account
    :type pswd: str
    :param location: where in inbox to search for messages
    :type location: str

    Example::
        mail = SendMail('username', 'password', location='smtp.example.com')
    """
    def __init__(self, user, pswd, location="smtp.gmail.com"):
        self.user = user
        self.pswd = pswd
        self.locn = location
        super().__init__(user, pswd, location)

    def set_to(self, to):
        self.receiver = to

    def get_to(self):
        if hasattr(self, 'receiver'):
            return self.receiver
        self.set_to(self.user)
        return self.receiver

    def set_cc(self, cc):
        self.cc = cc

    def get_cc(self):
        return self.cc

    def dist_prep(self, el):
        if isinstance(el, list):
            return ','.join(el)
        else:
            return el

    def set_sender(self, sender):
        self.sender = sender

    def get_sender(self):
        if hasattr(self, 'sender'):
            return self.sender
        self.set_sender(self.user)
        return self.sender

    def __enter__(self):
        self.conn = smtplib.SMTP_SSL(self.locn, 465)
        r, d = self.conn.login(self.user, self.pswd)
        return self

    def __exit__(self, *args):
        self.conn.close()

    def distribute(self, subject, content):
        """Prepare messages for sending

        :param subject: email subject line
        :type subject: str
        :param content: html email content
        :type html: str
        :return: status
        :rtype: int

        Example::
            body = "<html><p>Hello world</p></html>"
            status = SendMailobj.distribute("title", body)
        """

        msg_to = self.dist_prep(self.receiver)
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['To'] = msg_to
        msg['From'] = self.get_sender()
        if hasattr(self, 'cc'):
            msg['Bcc'] = self.dist_prep(self.cc)
        part1 = MIMEText('', 'plain')
        part2 = MIMEText(content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        out = self.conn.send_message(msg)
        status = 0
        if len(out):
            status = 1
            print("errors in sending to:")
            print(out)
            return status
        return status
