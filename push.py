import requests
import json
import libtmux
import os
import time


nameOfPane = 'smallamp'
tmpContentFile = "/tmp/smallAmp.content"

if not os.path.exists(tmpContentFile):
    with open(tmpContentFile, 'w'): pass

with open("../onesignal.txt") as f:
   lines = f.readlines()
   app_id = lines[0].strip()
   app_auth_key = lines[1].strip()

header = {"Content-Type": "application/json; charset=utf-8",
          "Authorization": "Basic " + app_auth_key}

payload = {"app_id": app_id,
           "included_segments": ["All"],
           "contents": {"en": "Check Me PLZ"}}

def sendPush():
   req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))

def getSessionText():
   server = libtmux.Server()
   session = server.find_where({ "session_name": nameOfPane })
   return '\n'.join( session.cmd('capture-pane', '-p').stdout)

def getOldContent():
   with open(tmpContentFile) as f:
      return f.read()

def setOldContent(txt):
   with open(tmpContentFile, 'w') as f:
      f.write(txt)

def checkContent():
   content = getSessionText()
   if content == getOldContent():
      sendPush()
   setOldContent(content)

while True:
   checkContent()
   time.sleep(30* 60) #every 10 minutes
