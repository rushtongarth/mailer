from MailBox import ReadMail,SendMail

def ReadAll(ReadMailObj):
  ids = ReadMailObj.get_mids()
  for m in ids:
    msg = ReadMailObj.get_by_id(m)
    yield (ReadMailObj.get_date(),msg)
