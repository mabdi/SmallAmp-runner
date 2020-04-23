import argparse
import os
import glob
import sys

parser = argparse.ArgumentParser(description='Evaluate SmallAmp on selected projects.')
parser.add_argument('-p', '--project', help='Process on just specified project')
parser.add_argument('-s', '--step', help='Process only specified step')
parser.add_argument('-f', '--force', help='Use force')

args = parser.parse_args()
force = args.force
step = args.step
project =args.project

home = os.path.expanduser("~")
manifestDirectory = "projects/"
manifestFile = manifestDirectory + "manifest.tsv"
templateFile = "statTemplate.txt"
baseAddress = home + '/myvms/base/'
projectsDirectory = home + '/pharo-projects/'
statStFileName = 'stats.st'
loaderStFileName = 'loader.st'

def parseManifest(manifestFile):
   manifest = []
   with open(manifestFile, "r") as f:
      lines = f.readlines()
   for line in lines:
     cols = line.split("\t")
     manifest.append({'name': cols[0].strip(), 'prefix': cols[1].strip(), 'file': manifestDirectory + cols[2].strip() })
   return manifest

def duplicateVM(projectName):
   destinationURL = projectsDirectory + projectName
   if not force and os.path.exists(destinationURL):
       print('Image folder is already exists. Skip vm step. ')
   else:
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
   os.system(home + '/pharo Pharo.image st '+ statStFileName +' --save --quit')
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
   os.system(home + '/pharo Pharo.image st '+ loaderStFileName +' --save --quit > projectLoad.log')
   os.chdir(cwd)

def main():
   projects = parseManifest(manifestFile)
   for p in projects:
     if project is None or project == p:
        if step is None or step == 'vm':
           duplicateVM(p['name'])
        if step is None or step == 'load':
           loadProject(p['name'], p['prefix'], p['file'])
        if step is None or step == 'stat':
           makeStat(p['name'], p['prefix'], p['file'])

main()

