import subprocess, threading

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.timedout = False

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True)
            self.process.communicate()

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            self.timedout= True
            thread.join()

    def code(self):
        if self.process:
            return self.process.returncode
