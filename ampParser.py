import sys
import re
import os
import json

my_path = os.path.abspath(os.path.dirname(__file__))


if len(sys.argv) != 2:
    print('missing argument')
    sys.exit()

def number_of_changes(list_of_methods):
    return [ re.search(r"_amp(.*)$", txt).group(1).count('_') for txt in list_of_methods]

xjson = None
jsonObj = None

jsonFile = os.path.join(my_path,sys.argv[1])
xjsonFile = os.path.join(my_path,jsonFile[:-4]+'xjson')


with open(jsonFile) as f:
   jsonStr = f.read()
   try:
      jsonObj = json.loads(jsonStr)
   except:
      pass
if os.path.exists(xjsonFile):
   with open(xjsonFile) as f:
       jsonStrx = f.read()
   try:
       xjson = json.loads(jsonStrx)
   except:
       pass

if not jsonObj:
   print('no file')
   sys.exit()

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


print('Finished successfully' + ',' + ','.join(str(x) for x in [
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
                  len(jsonObj['notCoveredInOriginal']),
                  len(jsonObj['newCovered']),
                  len(jsonObj['notCoveredInAmplified']),
                  len(jsonObj['methodsNotProfiled']),
                  jsonObj['timeTotal'],
                  xjson['targetChurn'],
                  xjson['testChurn'],
                  xjson['directTestingOriginal'],
                  max(number_of_changes(jsonObj['amplifiedMethods']) or [0])

               ]))
