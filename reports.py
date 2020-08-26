import os
import glob
import sys
import re
import json
from config import *
from collections import Counter

#this = sys.modules[__name__]

def mut_to_string(mut):
    return '-'.join([mut['operatorDescription'], mut['class'], mut['operatorClass'], mut['method'], str(mut['mutationStart']), str(mut['mutationEnd'])])

#this.current_n = -1

def number_of_changes(list_of_methods):
    return [ re.search(r"_amp(.*)$", txt).group(1).count('_') for txt in list_of_methods]

def count_killed_mutants(lst):
   return Counter([ mut['operatorClass'] for mut in lst])

def mutation_list_compare_covered_list(covered, mutatans):
   return [ mut for mut in mutants if mut['class']+'>>#'+mut['method'] in covered]

def an_print(msg, more_det=None, verbose=False):
   """this.current_n += 1
   if n_anomaly == -1:
      print(str(this.current_n) + ': ' + msg)
   if n_anomaly > -1 and n_anomaly == this.current_n:
      print(str(this.current_n) + ': ' + msg)
      print('--more details--' + str(more_det))"""
   print( msg)
   if verbose:
      print('--more details--' + str(more_det))

def get_median(lst):
   idx = (len(lst) - 1) // 2
   if len(lst) % 2:
      return lst[idx], idx
   else:
      return ((lst[idx] + lst[idx+1]) / 2.0), idx

def get_boxplot_infor(alist):
   if len(alist)<4:
     return {"out_min": -1, "out_min":-1, "minimum":-1, "maximum":-1, "iqr":-1, "q1":-1, "q3":-1, "median":-1}
   alist.sort()
   #print(alist)
   median, mid_idx = get_median(alist)
   q1, q1_idx = get_median(alist[:mid_idx])
   q3, q3_idx = get_median(alist[mid_idx:])
   iqr = q3 - q1
   minimum = max(min(alist), q1 - 1.5 * iqr)
   maximum = min(max(alist), q3 + 1.5 * iqr)
   out_min = [x for x in alist if x < minimum]
   out_max = [x for x in alist if x > maximum]

   return {"out_min": out_min, "out_min":out_min, "minimum":minimum, "maximum":maximum, "iqr":iqr, "q1":q1, "q3":q3, "median":median}

def reportAnomalies(projectName, fix, verbose):
   data = reportAmp_backend(projectName, fix)
   if not data:
     return (projectName + ',unknown')
   for row in data:
      if row['stat'] == 'success':
          jsonObj = row['jsonObj']
          imp = jsonObj['mutationScoreAfter'] - jsonObj['mutationScoreBefore']
          before = {mut_to_string(x) for x in jsonObj['mutantsAliveInOriginal']}
          after_killed = {mut_to_string(x) for x in jsonObj['killedInAmplified']}
          after_alive = {mut_to_string(x) for x in jsonObj['stillAliveMutants']}

          if  imp <  0:
             an_print(projectName + ',' + row['className'] + ',' + 'negative amplification')
          if len(jsonObj['amplifiedMethods'])== 0 and imp != 0:
             an_print(projectName + ',' + row['className'] + ',' + 'no new method but change in score')
          if len(jsonObj['killedInAmplified']) + len(jsonObj['stillAliveMutants']) !=  len(jsonObj['mutantsAliveInOriginal']):
             an_print(projectName + ',' + row['className'] + ',' + 'mutation stat size mismatch')
          an1 = after_killed.union(after_alive) - before
          if len(an1)>0:
             an_print(projectName + ',' + row['className'] + ',' + 'new mutation after', str(an1), verbose)
          an2 = before - after_killed.union(after_alive) 
          if len(an2)>0:
             an_print(projectName + ',' + row['className'] + ',' + 'new mutation before', str(an2), verbose)
      else:
          if 'className' in row.keys():
             an_print(projectName + ',' + row['className'] + ',' + row['stat'])
          else:
             an_print(projectName + ',' + row['stat'], json.dumps(row), verbose)


def reportStat(projectName):
   d = reportStat_backend(projectName)
   if d:
      print(','.join(str(x) for x in reportStat_backend(projectName) ))

def reportStat_backend(projectName):
   statFile = projectsDirectory + projectName + '/' + projectName + '.stat'
   if not os.path.exists(statFile):
      #print('file not found: '+ statFile)
      return []
   with open(statFile) as f:
      stat = f.read()
   matches = re.findall("#(\w+)->(true|false|\d+|'[0-9a-z]+')\.?", stat)
   matches = {tuple[0]:tuple[1] for tuple in matches}
   if 'commitId' not in matches.keys():
      matches['commitId'] = 'NA'
   return [str(x) for x in [
        projectName,
        matches['allGreen'],
        matches['classes'],
        matches['tests'],
        matches['targetedTests'],
        matches['targetedTestsMethods'],
        matches['commitId']
   ]]


def reportSum(projectName, fix):
   data = reportAmp_backend(projectName,fix )
   stat = reportStat_backend(projectName)
   if not data:
     return (projectName + ',unknown')
   max_imp = -101
   sum_imp = 0
   sum_imp_no100 = 0
   n_no100 = 0
   all_new_killed = 0
   all_new_methods = 0
   sum_time = 0
   n_fail = 0
   imps_no100 = []
   for row in data:
#      print(row['stat'])
      if row['stat'] != 'success':
         n_fail += 1
      else:
         jsonObj = row['jsonObj']
         sum_time += jsonObj['timeTotal']
         imp = jsonObj['mutationScoreAfter'] - jsonObj['mutationScoreBefore']
         if imp < 0:
           continue 
         sum_imp += imp
         all_new_killed += len(jsonObj['killedInAmplified'])
         all_new_methods += len(jsonObj['amplifiedMethods'])
         if jsonObj['mutationScoreBefore'] < 100:
            imps_no100.append(imp)
            n_no100 += 1
            sum_imp_no100 += imp
         if imp > max_imp:
            max_imp = imp
   #print(imps_no100)
   bpi = get_boxplot_infor(imps_no100)
   n_cases = len(data)
   avg_imp = sum_imp / n_cases if n_cases != 0 else 0
   avg_imp_n100 = sum_imp_no100 / n_no100 if n_no100 != 0 else 0
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

   print(','.join(str(x) for x in [projectName, n_cases, max_imp, n_fail, avg_imp, n_imp_less, 
            n_imp_more, sum_time, avg_imp_n100, n_no100, all_new_methods, all_new_killed, 
            bpi['q1'],bpi['q3'],bpi['minimum'],bpi['maximum'],bpi['median'],
            stat[1], stat[2],stat[3],stat[4],stat[5],stat[6]
         ]))

def do_fix(result):
   for row in result:
      if row['stat'] == 'success':
         jsonObj = row['jsonObj']
         if len(jsonObj['amplifiedMethods']) == 0:
            jsonObj['mutationScoreAfter'] = jsonObj['mutationScoreBefore']
         row['jsonObj'] = jsonObj
   return result


def reportAmp(projectName, fix):
   data = reportAmp_backend(projectName, fix)
   if not data:
      print(projectName + ',,unknown')
      return
   for row in data:
      if row['stat'] == 'success':
          jsonObj = row['jsonObj']
          xjson = row['xjson']
          if not xjson:
             xjson = {'targetChurn': 'NA',
			'testChurn': 'NA',
			'assertionDensityOriginal': 'NA',
			'assertionDensityAmplified': 'NA',
			'originalCoverageStatementes': 'NA',
			'amplifiedCoverageStatementes': 'NA',
			'originalCoverageBranches': 'NA',
			'amplifiedCoverageBranches': 'NA',
			'originalCoverageMethods': 'NA',
			'amplifiedCoverageMethods': 'NA',
			'directTestingOriginal': 'NA'
		}
          print(projectName + ',' + row['className'] + ',' + 'Finished successfully' + ',' + ','.join(str(x) for x in [
                  jsonObj['amplifiedClass'],
                  ' '.join(jsonObj['targetClasses']),
                  jsonObj['mutationScoreBefore'],
                  jsonObj['mutationScoreAfter'],
                  jsonObj['mutationScoreAfter'] - jsonObj['mutationScoreBefore'],
                  jsonObj['targetLoc'],
                  jsonObj['testLoc'],
                  jsonObj['testAmpLoc'],
                  xjson['assertionDensityOriginal'],
                  xjson['assertionDensityAmplified'],
                  xjson['originalCoverageStatementes'],
                  xjson['amplifiedCoverageStatementes'],
                  xjson['originalCoverageBranches'],
                  xjson['amplifiedCoverageBranches'],
                  xjson['originalCoverageMethods'],
                  xjson['amplifiedCoverageMethods'],
                  len(jsonObj['amplifiedMethods']),
                  len(jsonObj['mutantsAliveInOriginal']),
                  len(jsonObj['killedInAmplified']),
                  len(jsonObj['stillAliveMutants']),
                  len(jsonObj['methodsNotProfiled']),
                  jsonObj['timeTotal'],
                  xjson['targetChurn'],
                  xjson['testChurn'],
                  xjson['directTestingOriginal'],
                  max(number_of_changes(jsonObj['amplifiedMethods']) or [0])

               ]))
      elif row['stat'] == 'error':
          print(projectName + ',' + row['className'] + ',' + 'Finished with Error ({}) {}'.format(row['errDet'],row['lastMethod']))
      elif row['stat'] == 'fail':
          print(projectName + ',' + row['className'] + ',' + 'Unfinished Run (Image Crash?)')
      elif row['stat'] == 'blacklist':
          print(projectName + ',' + row['className'] + ',' + 'Skipped (blacklist)')
      else:
          print('shet!' + json.dumps(row))


def reportAmp_backend(projectName, fix):
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
      xjson = None
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
            if os.path.exists(directory + "/"+ className + '.xjson'):
               with open(directory + "/"+ className + '.xjson') as f:
                   jsonStrx = f.read()
               try:
                   xjson = json.loads(jsonStrx)
               except:
                   pass

            if jsonObj:
               result.append({'stat':'success','className':className,'jsonObj':jsonObj,'xjson': xjson})
               continue
      if not os.path.exists(directory + '/out/' + className + '.log'):
         result.append({'stat':'unknown','className':className})
         continue
      try:
         with open(directory + '/out/' + className + '.log') as f:
            log = f.read()
      except:
         print('cannot read file: ', directory + '/out/' + className + '.log')
         result.append({'stat':'fail','className':className})
         continue
      if not "Run finish" in log:
         result.append({'stat':'fail','className':className})
      if "Error details" in log:
         errDet = re.findall('Error details:(.+)',log)[0]
         ampMethods = re.findall('assert amplification:(.+)',log)
         lastMethod = ampMethods[-1] if len(ampMethods) > 0 else ''
         result.append({'stat':'fail','className':className,'errDet':errDet, 'lastMethod': lastMethod})
   if fix:
      return do_fix(result)
   return result
