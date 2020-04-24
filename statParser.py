import sys
import re

fileName = sys.argv[1]

with open(fileName) as f:
   data = f.read()

matches = re.findall("#(\w+)->(\d+)\.?", data)

#print(matches)
matches = {tuple[0]:int(tuple[1]) for tuple in matches}

# {'packages': 0, 'classes': 0, 'testPackages': 0, 'tests': 0, 'focousedTests': 0, 'focousedTestsMethods': 0, 'testsFails': 0, 'testsErrors': 0, 'testsPasses': 0}

# Test Green	#packages	#classes	#testClasses	#Focoused Tests	#testMethods
print(','.join(str(x) for x in [
	1 if matches['testsFails'] ==0 and matches['testsErrors'] ==0else 0,
	matches['packages'],
	matches['classes'],
	matches['tests'],
	matches['focousedTests'],
	matches['focousedTestsMethods']

]))
