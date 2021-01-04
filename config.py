import os


home = os.path.expanduser("~")
manifestDirectory = "projects/"
manifestFile = manifestDirectory + "manifest.tsv"
#templateFile = "statTemplate.txt"
baseAddress = home + '/Pharo-Base/'
#projectsDirectory = home + '/pharo-projects/'
projectsDirectory = home + '/pharo-projects-files/'
statStFileName = 'stats.st'
loaderStFileName = 'loader.st'
pharoVM = home + '/Pharo/pharo'
pharoVMUI = home + '/Pharo/pharo-ui'
todoFileName = 'todo.txt'
doneFileName = 'done.txt'
blacklistfile = projectsDirectory + 'blacklist.txt'
zipDirectory = 'zips/'
