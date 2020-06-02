import argparse
from datetime import datetime
from config import *
from steps import *
from reports import *

parser = argparse.ArgumentParser(description='Evaluate SmallAmp on selected projects.')
parser.add_argument('-p', '--project', help='Process on just specified project')
parser.add_argument('-s', '--step', help='Process only specified step' , choices=['vm', 'load', 'stat', 'amp', 'reload', 'ampui'] )
parser.add_argument('-f', '--force', help='Use force' , action='store_true')
parser.add_argument('-r', '--report', help='Generate report',  choices=['stat', 'amp'])

args = parser.parse_args()
force = args.force
step = args.step
project =args.project
report = args.report

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
   for p in projects:
     if project is None or project == p['name']:
        if step is None or step == 'vm':
           duplicateVM(force, p['name'])
        if step is None or step == 'load':
           loadProject(force, p['name'], p['prefix'], p['file'])
        if step is None or step == 'stat':
           makeStat(force, p['name'], p['prefix'], p['file'])
        if step == 'reload':
           reloadSmallAmp(force, p['name'])
        if step is None or step == 'amp':
           runAmplification(force, p['name'])
        if step == 'ampui':
           print('dup vm:')
           duplicateVM(force, p['name'])
           print('load proj:')
           loadProject(force, p['name'], p['prefix'], p['file'])
           print('make stat:')
           makeStat(force, p['name'], p['prefix'], p['file'])
           print('run:')
           runAmplificationUI(force, p['name'])

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

