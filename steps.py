import argparse
import os
import glob
import sys
from datetime import datetime
import re
import json
from config import *

def duplicateVM(force, projectName):
   destinationURL = projectsDirectory + projectName
   if not force and os.path.exists(destinationURL):
       print('Image folder is already exists. Skip vm step. ')
   else:
       if os.path.exists(destinationURL):
          os.system('rm -rf ' + destinationURL)
       os.system('cp -r '+ baseAddress + ' ' + destinationURL)
       print('Image duplicated: '+ destinationURL)

def makeStat(force, projectName, projectPrefix, projectFile):
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

def loadProject(force, projectName, projectPrefix, projectFile):
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

def runAmplification(force, projectName):
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
