import argparse
from datetime import datetime
from config import *
from steps import *
from reports import *

parser = argparse.ArgumentParser(description='Evaluate SmallAmp on selected projects.')
parser.add_argument('-p', '--project', help='Process on just specified project')
parser.add_argument('-s', '--step', help='Process only specified step' , choices=['vm', 'load', 'stat', 'amp', 'reload', 'ampui', 'prepare', 'extra', 'cleanup', 'mongo', 'zip', 'ampc'] )
parser.add_argument('-f', '--force', help='Use force' , action='store_true')
parser.add_argument('-r', '--report', help='Generate report',  choices=['stat', 'amp', 'sum', 'anm'])
parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
parser.add_argument('-x', '--fix', help='fix scores', action='store_true')
parser.add_argument('-a', '--additional', help='additional required parameters')


args = parser.parse_args()
force = args.force
step = args.step
project =args.project
report = args.report
verbose = args.verbose
additional= args.additional
fix = args.fix

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

def processMain():
   projects = parseManifest(manifestFile)
   if step is None and project is None:
     parser.print_help()
     return
   if step == 'cleanup' and project is None and not force:
     print('Specify a project or use -f')
     return
   for p in projects:
     if project is None or project == p['name']:
        if step is None or step == 'vm':
           duplicateVM(force, p['name'])
        if step is None or step == 'load':
           loadProject(force, p['name'], p['prefix'], p['file'])
        if step is None or step == 'stat':
           makeStat(force, p['name'], p['prefix'], p['file'])
        if step == 'extra':
           makeExtra(force, p['name'], p['prefix'], p['file'])
        if step == 'reload':
           reloadSmallAmp(force, p['name'])
        if step is None or step == 'amp':
           runAmplification(force, p['name'])
        if step == 'ampui':
           runAmplificationUI(force, p['name'])
        if step == 'ampc':
           runAmplificationCustom(force, p['name'], additional)
        if step == 'prepare':
           print('dup vm:')
           duplicateVM(force, p['name'])
           print('load proj:')
           loadProject(force, p['name'], p['prefix'], p['file'])
           print('make stat:')
           makeStat(force, p['name'], p['prefix'], p['file'])
        if step == 'cleanup':
           cleanup(force, p['name'], p['prefix'], p['file'])
        if step == 'mongo':
           moveToMongo(force, p['name'], p['prefix'], p['file'])
        if step == 'zip':
           packResult(force, p['name'], p['prefix'], p['file'])
        if step == 'finalize':
           packResult(force, p['name'], p['prefix'], p['file'])
           moveToMongo(force, p['name'], p['prefix'], p['file'])

def reportMain():
   projects = parseManifest(manifestFile)
   for p in projects:
      if project is None or project == p['name']:
         if report == 'stat':
            reportStat(p['name'])
         elif report == 'amp':
            reportAmp(p['name'],fix)
         elif report == 'sum':
            reportSum(p['name'],fix)
         elif report == 'anm':
            reportAnomalies(p['name'],fix , verbose)

print('Script started at: ', datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
if not report is None:
   reportMain()
else:
   processMain() #default action
print('Script finished at: ', datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

