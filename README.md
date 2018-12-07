# Mailer
---
Basic mailbox opener for digesting long emails and peeling out the most important information.

### Current Digest System
---
To run the code one needs to execute the following:

```python
user = you@example.com
pswd = somepassword
with ReadMail(user,pswd) as mail:
    curr = mail.get_latest()
```
Process the emails and then send an output
```python
body = some_html_with_my_email
with SendMail(user,pswd) as outbound:
    outbound.set_from(un)
    outbound.set_to(send_to)
    res = outbound.distribute('my email subject',body)
```
which can be loaded into a configuration file, this is under development
