import os
import glob
import sys
import re
import json
from config import *

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
      jsons = [jsFile for jsFile in json_files if className in jsFile]
      if not jsons:
         print('check me@ ' + projectName + ',' + className)
      for jsFile in jsons:
            with open(directory + "/"+ jsFile) as f:
               jsonStr = f.read()
            jsonObj = json.loads(jsonStr)
            print(projectName + ',' + className + ',' + 'Finished successfully' + ',' + ','.join(str(x) for x in [
               jsonObj['mutationScoreBefore'],
               jsonObj['mutationScoreAfter'],
               jsonObj['timeTotal'],
               len(jsonObj['amplifiedMethods'])
            ]))
