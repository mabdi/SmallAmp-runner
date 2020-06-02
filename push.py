import requests
import json
import libtmux
import os
import time
import atexit

nameOfPane = 'smallamp'
tmpContentFile = "/tmp/smallAmp.content"
tmpProject = "/tmp/smallAmpProject.smallAmp"
tmpCurrent = '/tmp/AmpCurrent.smallamp'
outFile = '/home/ubuntu/pharo-projects/{}/out/{}.log'
sleepSeconds = 10 * 60
fileExpireSeconds = 30*60

if not os.path.exists(tmpContentFile):
    with open(tmpContentFile, 'w'): pass


with open("../onesignal.txt") as f:
   lines = f.readlines()
   app_id = lines[0].strip()
   app_auth_key = lines[1].strip()

current = ''
project = ''
if os.path.exists(tmpCurrent):
   with open(tmpCurrent) as f:
       current = f.read().strip()
   project = current.split(':')[0]
   current = current.split(':')[1]

if not os.path.exists(tmpProject):
    with open(tmpProject, 'w') as f:
       f.write(project)

header = {"Content-Type": "application/json; charset=utf-8",
          "Authorization": "Basic " + app_auth_key}

def sendPush(txt):
   payload = {"app_id": app_id,
           "included_segments": ["All"],
           "contents": {"en": txt}}
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
   lastContent = getOldContent()
   setOldContent(content)
   if content == lastContent:
      if checkOutFileModified():
         sendCtrlC()
         return 'I killed a process: ' + project + '>' + current
      else:
         return 'Screen not changed for a while: ' + project + '>' +  current

def checkOutFileModified():
   if not os.path.exists(tmpCurrent):
       return False
   lastModification = os.stat(outFile.format(project,current)).st_mtime
   return time.time() - lastModification > fileExpireSeconds

def sendCtrlC():
   server = libtmux.Server()
   pane = server.find_where({ "session_name": nameOfPane }).attached_window.panes[0]
   pane.send_keys('C-c', enter=False, suppress_history=False)

def checkProjectName():
   with open(tmpProject) as f:
      lastP =  f.read()
   if lastP != project:
     with open(tmpProject, 'w') as f:
        f.write(project)
     return 'Project started: ' + project

def onFailure():
   sendPush('Script failed. please check.')

atexit.register(onFailure)


while True:
   msg = ''
   try:
      msg = checkContent()
      #checkProjectName()
      if not  msg is None:
          msg =  time.strftime('%x') + ":" +msg
   except UnboundLocalError as ex:
      msg = "Exception in the script at: "+ time.strftime('%x')
   if not msg is None:
        sendPush(msg)
   time.sleep(sleepSeconds)
