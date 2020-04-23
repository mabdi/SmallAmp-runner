import os
import glob
import sys

home = os.path.expanduser("~")
manifestFile = "projects/manifest.tsv"
templateFile = "installerTemplate.txt"
baseAddress = home + '/myvms/base/'
regenerateImages = False
projectsDirectory = home + '/pharo-projects/'
installerName = 'installer.st'

def parseManifest(manifestFile):
   manifest = []
   with open(manifestFile, "r") as f:
      lines = f.readlines()
   for line in lines:
     cols = line.split("\t")
     manifest.append({'name': cols[0], 'prefix': cols[1], 'file': cols[2]})

def duplicateVM(projectName):
   destinationURL = projectsDirectory + projectName
   if not regenerateImages and os.path.exists(destinationURL):
       print('Image is already exists. remove manually if you like to regenerate or set regenerateImages to true: '+ destinationURL)
   else:
       os.system('cp -r '+ baseAddress + ' ' + destinationURL)
       print('Image duplicated: '+ destinationURL)

def makeInstaller(projectName, projectPrefix, projectFile):
   installerURL = projectsDirectory + projectName + '/' + installerName
   with open(projectFile,"r") as f:
       loadingCode = f.read()
   with open(templateFile, "r") as f:
      template = f.read()
   with open(installerURL, "w") as f:
      f.write(template.format(projectPrefix, loadingCode))
   print('Installer is made '+ installerURL)

def installOnVM(projectName):
   destinationURL = projectsDirectory + projectName
   os.chdir(destinationURL)
   os.system(home + '/pharo Pharo.image st '+ installerName +' --save --quit')


def main():
   projects = parseManifest(manifestFile)
   for project in projects:
     duplicateVM(project['name'])
     makeInstaller(project['name'], project['prefix'], project['file'])
     installOnVM(project['name'])

main()
