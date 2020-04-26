import argparse
import os
import glob
import sys
from datetime import datetime
import re
import json

parser = argparse.ArgumentParser(description='Evaluate SmallAmp on selected projects.')
parser.add_argument('-p', '--project', help='Process on just specified project')
parser.add_argument('-s', '--step', help='Process only specified step' , choices=['vm', 'load', 'stat', 'amp'] )
parser.add_argument('-f', '--force', help='Use force' , action='store_true')
parser.add_argument('-r', '--report', help='Generate report',  choices=['stat', 'amp'])

args = parser.parse_args()
force = args.force
step = args.step
project =args.project
report = args.report

home = os.path.expanduser("~")
manifestDirectory = "projects/"
manifestFile = manifestDirectory + "manifest.tsv"
templateFile = "statTemplate.txt"
baseAddress = home + '/Pharo-Base/'
projectsDirectory = home + '/pharo-projects/'
statStFileName = 'stats.st'
loaderStFileName = 'loader.st'
pharoVM = home + '/Pharo/pharo'
todoFileName = 'todo.txt'
doneFileName = 'done.txt'

def parseManifest(manifestFile):
   manifest = []
   with open(manifestFile, "r") as f:
      lines = f.readlines()
   for line in lines:
     if not line.strip() or line.startswith('#'): 
       continue 
     cols = line.split("\t")
     manifest.append({'name': cols[0].strip(), 'prefix': cols[1].strip(), 'file': manifestDirectory + cols[2].strip() })
   return manifest

def duplicateVM(projectName):
   destinationURL = projectsDirectory + projectName
   if not force and os.path.exists(destinationURL):
       print('Image folder is already exists. Skip vm step. ')
   else:
       if os.path.exists(destinationURL):
          os.system('rm -rf ' + destinationURL)
       os.system('cp -r '+ baseAddress + ' ' + destinationURL)
       print('Image duplicated: '+ destinationURL)

def makeStat(projectName, projectPrefix, projectFile):
   installerURL = projectsDirectory + projectName + '/' + statStFileName
   if not force and os.path.exists(installerURL):
      print('State file found. skip stat step.')
      return
   with open(templateFile, "r") as f:
      template = f.read()
   with open(installerURL, "w") as f:
      f.write(template.format(projectPrefix))
   print('StatScript is made '+ installerURL)
   destinationURL = projectsDirectory + projectName
   cwd = os.getcwd()
   os.chdir(destinationURL)
   os.system(pharoVM + ' Pharo.image st '+ statStFileName +' --save --quit > projectStat.log')
   os.chdir(cwd)

def loadProject(projectName, projectPrefix, projectFile):
   loaderFile = projectsDirectory + projectName + '/' + loaderStFileName
   if not force and os.path.exists(loaderFile):
      print('loader file found. skip load step.')
      return
   os.system('cp  '+ projectFile + ' ' + loaderFile)
   destinationURL = projectsDirectory + projectName
   cwd = os.getcwd()
   os.chdir(destinationURL)
   os.system(pharoVM + ' Pharo.image st '+ loaderStFileName +' --save --quit > projectLoad.log')
   os.chdir(cwd)


def checkDone(projectName, className):
    doneFile = projectsDirectory + projectName + '/' + doneFileName
    if not os.path.exists(doneFile):
       with open(doneFile, 'w'): pass
    with open(doneFile,"r") as f:
       dones = f.readlines()
    for cname in dones:
       if cname == className:
           return True
    return False


def markAsDone(projectName, className):
    doneFile = projectsDirectory + projectName + '/' + doneFileName
    with open(doneFile,"a+") as f:
        f.write(className)
        f.write(os.linesep)

def runAmplification(projectName):
   todoFile = projectsDirectory + projectName + '/' + todoFileName
   with open(todoFile,"r") as f:
      todo = f.readlines()

   for cname in todo:
       className = cname.strip()
       if not className:
          continue
       if force or not checkDone(projectName, className):
          print('Amplifying: ' + className)
          cwd = os.getcwd()
          os.chdir(projectsDirectory + projectName)
          if not os.path.exists('out'):
                os.makedirs('out')
          cmd = 'SmallAmp initializeDefault testCase: {} ; amplifyEval'.format( className )
          os.system(pharoVM + ' Pharo.image eval --save \''+ cmd  +'\' > out/amplification'+ className +'.log')
          os.chdir(cwd)
          markAsDone(projectName, className)
       else:
          print('Skipping: ' + className)

def reportStat(projectName):
   statFile = projectsDirectory + projectName + '/' + statStFileName
   with open(statFile) as f:
      stat = f.read()
   matches = re.findall("#(\w+)->(\d+)\.?", data)
   matches = {tuple[0]:int(tuple[1]) for tuple in matches}
   print(projectName + '\t' + ','.join(str(x) for x in [
        1 if matches['testsFails'] ==0 and matches['testsErrors'] ==0 else 0,
        matches['packages'],
        matches['classes'],
        matches['tests'],
        matches['focousedTests'],
        matches['focousedTestsMethods']
   ]))

def reportAmp(projectName):
   directory = projectsDirectory + projectName
   todoFile = projectsDirectory + projectName + '/' + todoFileName
   json_files = [pos_json for pos_json in os.listdir(directory) if pos_json.endswith('.txt')] #TODO: change to .json
   with open(todoFile,"r") as f:
      todo = f.readlines()
   for cname in todo:
      className = cname.strip()
      with open(directory + '/out/amplification' + className + '.log') as f:
         log = f.read()
      if not "Run finish" in log:
        print(projectName + ',' + className + ',' + 'Unfinished Run (Image Crash?)')
        return
      if "Error details" in log:
         errDet = re.findall('Error details:(.+)',log)[0]
         ampMethods = re.findall('assert amplification:(.+)',log)
         lastMethod = ampMethods[-1] if len(ampMethods) > 0 else ''
         print(projectName + ',' + className + ',' + 'Finished with Error ({}) {}'.format(errDet,lastMethod))
         return
      for jsFile in json_files:
         if className in jsFile:
            with open(directory + "/"+ jsFile) as f:
               jsonStr = f.read()
            jsonObj = json.loads(jsonStr)
            print(projectName + ',' + className + ',' + 'Finished successfully' + ',' + ','.join(str(x) for x in [
               jsonObj['mutationScoreBefore'],
               jsonObj['mutationScoreAfter'],
               jsonObj['timeTotal'],
               len(jsonObj['amplifiedMethods'])
            ]))

def processMain():
   projects = parseManifest(manifestFile)
   for p in projects:
     #print(project,p['name'],step)
     if project is None or project == p['name']:
        if step is None or step == 'vm':
           duplicateVM(p['name'])
        if step is None or step == 'load':
           loadProject(p['name'], p['prefix'], p['file'])
        if step is None or step == 'stat':
           makeStat(p['name'], p['prefix'], p['file'])
        if step is None or step == 'amp':
           runAmplification(p['name'])

def reportMain():
   projects = parseManifest(manifestFile)
   for p in projects:
      if project is None or project == p['name']:
         if report == 'stat':
            reportStat(p['name'])
         elif report == 'amp':
            reportAmp(p['name'])

print('Script started at: ', datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
if not report is None:
   reportMain()
else:
   processMain() #default action
print('Script finished at: ', datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

