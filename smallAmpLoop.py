from command import Command
import json

def read_json(fname):
   with open(fname) as f:
      jsonStr = f.read()
   try:
      jsonObj = json.loads(jsonStr)
   except:
      pass
   return jsonObj

class MainLoop:

   def __init__(self, vm, imgFile, className, logFile, inputAmpIter = 3, config = '(SAConfig default)'):
     self._vm = vm
     self._img = imgFile
     self._cls = className
     self._cnf = config
     self._n_input = inputAmpIter
     self._logFile = logFile
     self._ts = []

   def runSmallAmp(self, cmdtxt, t = 60):
     cmd = self._vm + ' ' + self._img + ' smallamp ' + cmdtxt + ' >> ' + self._logFile + ' 2>&1'
     print('RUN: ', cmd, flush=True)
     c = Command(cmd) 
     c.run(timeout=t)
     # TODO: add onTimeout, onCrash events to Command

   def amplify(self):
     self.setup_class()
     for testSelector in self._ts:
          self.setup_method(testSelector)
          self.assert_amp()
          self.selection()
          for n in range(self._n_input):
              self.input_amp()
              self.assert_amp()
              self.selection()
              self.finalize_method()
     self.finalize_class()

   def setup_class(self):
     self.runSmallAmp(' --ciAmplifyClass={}'.format(self._cls))
     self._ts = read_json('_smallamp_theTS.json')

   def setup_method(self, selector):
     self.runSmallAmp(' --ciAmplifyTest={}'.format(selector))

   def finalize_method(self):
     self.runSmallAmp(' --ciFinalizeTest')

   def finalize_class(self):
     self.runSmallAmp(' --ciFinalizeClass')

   def selection(self):
     self.runSmallAmp(' --ciSelectionInit')
     uncovered = read_json('_smallamp_uncovered.json')
     for i in range(len(uncovered)):
        self.runSmallAmp(' --ciSelectionMutantIndex={}'.format(i+1))
        # TODO onCrash: log <uncovered[i], content of _mutalk_lasttest.txt> in crashes, remove i from uncovereds
     self.runSmallAmp(' --ciSelectionFinalize')

   def assert_amp(self):
     v = read_json('_smallamp_theV.json')
     for selector in v:
        self.runSmallAmp(' --ciAssertionAmplification={}'.format(selector)) 
        # TODO   onCrash: log selector in crashes, ignore selector.

   def input_amp(self): 
      self.runSmallAmp(' --ciInputAmplification')
