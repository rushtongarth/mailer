# Mailer
---
Basic mailbox opener for digesting long emails and peeling out the most important information.

this is changing soon...

### Current Digest System
---
To run the code one needs to execute the following:

```python

from MailBox import MessageParser

user = you@example.com
pswd = somepassword


with MessageParser(user,pswd) as mail:
  mb = mail()
  curr = mb.get_mess()
subs = [
  ('cs.AI','Artificial Intelligence'),
    ...,
]
arx = ArXivDigest(subs,curr)
```

Process the emails and then send an output

```python
body = some_html_with_my_email
with SendMail(user,pswd) as outbound:
    outbound.set_from(un)
    outbound.set_to(send_to)
    res = outbound.distribute('my email subject',body)
```
which can be loaded into a configuration file which has the form:

```
[DEFAULT]
template = my_template_html_file.html

[Service Address]
name = email_to_send_from@example.com
pass = service_password

[Receivers]
to_list = person@example.com
cc_list = bcc_person@example.com

[ArxivDigest]
search_for = "identifying characteristic of received mail"

```
More to come on full usage...
