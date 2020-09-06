import argparse
import os
import glob
import sys
from datetime import datetime
import re
import json
from config import *
from zipfile import ZipFile
import time

def duplicateVM(force, projectName):
   destinationURL = projectsDirectory + projectName
   if not force and os.path.exists(destinationURL):
       print('Image folder is already exists. Skip vm step. ')
   else:
       if os.path.exists(destinationURL):
          os.system('rm -rf ' + destinationURL)
       os.system('cp -r '+ baseAddress + ' ' + destinationURL)
       print('Image duplicated: '+ destinationURL)

def packResult(force, projectName, projectPrefix, projectFile):
   projectDirectory = projectsDirectory + projectName
   zipFile = zipDirectory + projectName + str(int(time.time())) + '.zip'
   file_paths = []
   for filename in glob.glob(projectDirectory+'/*'):
            if filename.lower().endswith(('.txt', '.log', '.st', '.json')):
               file_paths.append(filename)

   with ZipFile(zipFile, 'w') as zip:
        for file in file_paths:
            arcname = file[len(projectsDirectory):]
            zip.write(file, arcname)

def moveToMongo(force, projectName, projectPrefix, projectFile):
   projectDirectory = projectsDirectory + projectName
   command = "ls -1 "+projectDirectory+"/*.json | while read jsonfile; do mongoimport --db test --collection "+projectName+" --file $jsonfile ; done"
   os.system(command)

def makeStat(force, projectName, projectPrefix, projectFile):
   installerURL = projectsDirectory + projectName + '/' + statStFileName
   if not force and os.path.exists(installerURL):
      print('State file found. skip stat step.')
      return
   #with open(templateFile, "r") as f:
   #   template = f.read()
   #with open(installerURL, "w") as f:
   #   f.write(template.format(projectPrefix))
   #print('StatScript is made '+ installerURL)
   destinationURL = projectsDirectory + projectName
   cwd = os.getcwd()
   os.chdir(destinationURL)
   os.system(pharoVM + ' Pharo.image smallamp --stat={} > projectStat.log 2>&1'.format( projectName ) )
   #os.system(pharoVM + ' Pharo.image st '+ statStFileName +' --save --quit > projectStat.log')
   os.chdir(cwd)

def cleanup(force, projectName, projectPrefix, projectFile):
   destinationURL = projectsDirectory + projectName
   if not os.path.exists(destinationURL):
       print('Project folder not found')
       return
   cwd = os.getcwd()
   os.chdir(destinationURL)
   os.system( 'rm ./Pharo.changes' )
   os.system( 'rm ./Pharo.image' )
   os.system( 'rm ./Pharo8*.sources' )
   os.system( 'rm -rf ./pharo-local' )
   os.chdir(cwd)

def makeExtra(force, projectName, projectPrefix, projectFile):
   todoFile = projectsDirectory + projectName + '/' + todoFileName
   destinationURL = projectsDirectory + projectName
   if not os.path.exists(todoFile):
     print('todo file not found, skipping')
     return
   with open(todoFile,"r") as f:
      todo = f.readlines()

   for cname in todo:
       className = cname.strip()
       if not className:
          continue
#       if className in blackList():
#          print('Skipping ' + className + ' -- blacklist')
#          continue
       if os.path.exists(destinationURL + "/"+ className + '.json'):
         cwd = os.getcwd()
         os.chdir(destinationURL)
         #os.system(pharoVM + ' Pharo.image smallamp --xinfo={} > out/{}.xlog 2>&1'.format( className, className ) )
         os.system(pharoVM + ' Pharo.image smallamp --xinfo={} --nosave'.format( className) )
         os.chdir(cwd)
       else:
          print('Skipping: ' + className + ' -- not done yet')


   installerURL = projectsDirectory + projectName + '/' + statStFileName
   if not force and os.path.exists(installerURL):
      print('State file found. skip stat step.')
      return
   #with open(templateFile, "r") as f:
   #   template = f.read()
   #with open(installerURL, "w") as f:
   #   f.write(template.format(projectPrefix))
   #print('StatScript is made '+ installerURL)



def loadProject(force, projectName, projectPrefix, projectFile):
   loaderFile = projectsDirectory + projectName + '/' + loaderStFileName
   if not force and os.path.exists(loaderFile):
      print('loader file found. skip load step.')
      return
   os.system('cp  '+ projectFile + ' ' + loaderFile)
   destinationURL = projectsDirectory + projectName
   cwd = os.getcwd()
   os.chdir(destinationURL)
   os.system(pharoVM + ' Pharo.image st '+ loaderStFileName +' --save --quit > projectLoad.log 2>&1')
   os.chdir(cwd)


def checkDone(projectName, className):
    doneFile = projectsDirectory + projectName + '/' + doneFileName
    if not os.path.exists(doneFile):
       with open(doneFile, 'w'): pass
    with open(doneFile,"r") as f:
       dones = f.readlines()
    for cname in dones:
       if cname.strip() == className.strip():
           return True
    return False

def blackList():
    if not os.path.exists(blacklistfile):
       with open(blacklistfile, 'w'): pass
    with open(blacklistfile,"r") as f:
       blacklist = f.readlines()
    return [s.strip() for s in blacklist]

def markAsDone(projectName, className):
    doneFile = projectsDirectory + projectName + '/' + doneFileName
    with open(doneFile,"a+") as f:
        f.write(className)
        f.write(os.linesep)

def reloadSmallAmp(force, projectName):
   destinationURL = projectsDirectory + projectName
   cwd = os.getcwd()
   os.chdir(destinationURL)
   #os.system(pharoVM + " Pharo.image eval --save \"((IceRepository registry detect: [ :r | r name = 'small-amp' ]) pull) branch commits first id\"")
   os.system(pharoVM + " Pharo.image eval --save \"IceRepository registry detect: [ :r | r name = 'small-amp' ] ifFound: [ :r | r pullFrom: r remotes first. ^ r branch commits first shortId ]\"")
   os.chdir(cwd)

def runAmplificationUI(force, projectName):
    return runAmplificationBackend(pharoVMUI ,force, projectName)


def runAmplification(force, projectName):
    return runAmplificationBackend(pharoVM ,force, projectName)

def runAmplificationBackend(proc ,force, projectName):
   todoFile = projectsDirectory + projectName + '/' + todoFileName
   if not os.path.exists(todoFile):
     print('todo file not found, skipping')
     return
   with open(todoFile,"r") as f:
      todo = f.readlines()

   for cname in todo:
       className = cname.strip()
       if not className:
          continue
       if className in blackList():
          print('Skipping ' + className + ' -- blacklist')
          continue
       if force or not checkDone(projectName, className):
          print('Amplifying: ' + className)
          cwd = os.getcwd()
          os.chdir(projectsDirectory + projectName)
          if not os.path.exists('out'):
                os.makedirs('out')
          with open('/tmp/AmpCurrent.smallamp', 'w') as f:
              f.write(projectName)
              f.write(':')
              f.write(className)
          cmd = 'SmallAmp initializeDefault testCase: {} ; amplifyEval'.format( className )
          os.system(proc + ' Pharo.image eval --save \''+ cmd  +'\' > out/'+ className +'.log 2>&1')
          os.chdir(cwd)
          markAsDone(projectName, className)
       else:
          print('Skipping: ' + className)



