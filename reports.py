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
   matches = re.findall("#(\w+)->(\d+)\.?", stat)
   matches = {tuple[0]:int(tuple[1]) for tuple in matches}
   print(projectName + '\t' + ','.join(str(x) for x in [
        1 if matches['testsFails'] ==0 and matches['testsErrors'] ==0 else 0,
        matches['packages'],
        matches['classes'],
        matches['tests'],
        matches['focousedTests'],
        matches['focousedTestsMethods']
   ]))


def reportSum(projectName):
   data = reportAmp_backend(projectName)
   if not data:
     return (projectName + ',unknown')
   max_imp = -101
   sum_imp = 0
   sum_imp_no100 = 0
   n_no100 = 0
   sum_time = 0
   n_fail = 0
   for row in data:
#      print(row['stat'])
      if row['stat'] != 'success':
         n_fail += 1
      else:
         jsonObj = row['jsonObj']
         sum_time += jsonObj['timeTotal']
         imp = jsonObj['mutationScoreAfter'] - jsonObj['mutationScoreBefore']
         sum_imp += imp
         if jsonObj['mutationScoreBefore'] < 100:
            n_no100 += 1
            sum_imp_no100 += imp
         if imp > max_imp:
            max_imp = imp
   n_cases = len(data)
   avg_imp = sum_imp / n_cases
   avg_imp_n100 = sum_imp_no100 / n_no100
   n_imp_less = 0
   n_imp_more = 0
   for row in data:
      if row['stat'] == 'success':
         jsonObj = row['jsonObj']
         imp = jsonObj['mutationScoreAfter'] - jsonObj['mutationScoreBefore']
         if imp >= avg_imp_n100:
            n_imp_more += 1
         else:
            n_imp_less += 1
   print(','.join(str(x) for x in [projectName, n_cases, max_imp, n_fail, avg_imp, n_imp_less, n_imp_more, sum_time, avg_imp_n100, n_no100 ]))


def reportAmp(projectName):
   data = reportAmp_backend(projectName)
   if not data:
      print(projectName + ',unknown')
      return
   for row in data:
      if row['stat'] == 'success':
          jsonObj = row['jsonObj']
          print(projectName + ',' + row['className'] + ',' + 'Finished successfully' + ',' + ','.join(str(x) for x in [
                  jsonObj['amplifiedClass'],
                  ' '.join(jsonObj['targetClasses']),
                  jsonObj['mutationScoreBefore'],
                  jsonObj['mutationScoreAfter'],
                  jsonObj['mutationScoreAfter'] - jsonObj['mutationScoreBefore'],
                  jsonObj['targetLoc'],
                  jsonObj['testLoc'],
                  jsonObj['testAmpLoc'],
#                 jsonObj['targetChurn'],
#                 jsonObj['testChurn'],
                  jsonObj['assertionDensityOriginal'],
                  jsonObj['assertionDensityAmplified'],
                  jsonObj['originalCoverageStatementes'],
                  jsonObj['amplifiedCoverageStatementes'],
                  jsonObj['originalCoverageBranches'],
                  jsonObj['amplifiedCoverageBranches'],
                  jsonObj['originalCoverageMethods'],
                  jsonObj['amplifiedCoverageMethods'],
                  len(jsonObj['amplifiedMethods']),
                  len(jsonObj['mutantsAliveInOriginal']),
                  len(jsonObj['killedInAmplified']),
                  len(jsonObj['stillAliveMutants']),
                  len(jsonObj['methodsNotProfiled']),
                  jsonObj['timeTotal']
               ]))
      elif row['stat'] == 'error':
          print(projectName + ',' + row['className'] + ',' + 'Finished with Error ({}) {}'.format(row['errDet'],row['lastMethod']))
      elif row['stat'] == 'fail':
          print(projectName + ',' + row['className'] + ',' + 'Unfinished Run (Image Crash?)')
      elif row['stat'] == 'blacklist':
          print(projectName + ',' + row['className'] + ',' + 'Skipped (blacklist)')
      else:
          print('shet!')


def reportAmp_backend(projectName):
   result = []
   directory = projectsDirectory + projectName
   todoFile = projectsDirectory + projectName + '/' + todoFileName
   if not os.path.exists(todoFile):
      return None

   json_files = [pos_json for pos_json in os.listdir(directory) if pos_json.endswith('.json')] # changed to .json
   with open(blacklistfile) as f:
      blacklistclasses = f.readlines()
   blacklistclasses = [s.strip() for s in blacklistclasses]
   with open(todoFile,"r") as f:
      todo = f.readlines()
   for cname in todo:
      jsonObj = None
      className = cname.strip()
      if className in blacklistclasses:
         result.append({'stat':'blacklist','className':className})
         continue
      if os.path.exists(directory + "/"+ className + '.json'):
            with open(directory + "/"+ className + '.json') as f:
               jsonStr = f.read()
            try:
                jsonObj = json.loads(jsonStr)
            except:
                pass
            if jsonObj:
               result.append({'stat':'success','className':className,'jsonObj':jsonObj})
               continue
      if not os.path.exists(directory + '/out/' + className + '.log'):
         result.append({'stat':'unknown','className':className})
         continue
      with open(directory + '/out/' + className + '.log') as f:
         log = f.read()
      if not "Run finish" in log:
         result.append({'stat':'fail','className':className})
      if "Error details" in log:
         errDet = re.findall('Error details:(.+)',log)[0]
         ampMethods = re.findall('assert amplification:(.+)',log)
         lastMethod = ampMethods[-1] if len(ampMethods) > 0 else ''
         result.append({'stat':'fail','className':className,'errDet':errDet, 'lastMethod': lastMethod})
   return result
