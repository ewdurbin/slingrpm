import sys
import os.path
import shutil
import multiprocessing
import SimpleHTTPServer
import SocketServer

def touch(filename, content="foo"):
  f = open(filename, 'w')
  f.write(content)
  f.close()

def setuprepos():
  os.makedirs('testarea/badrepo')
  os.makedirs('testarea/repo/repodata')
  os.makedirs('testarea/realrepo/repodata')
  os.makedirs('testarea/freshrepo')

  touch('testarea/repo/.slingrpm.conf')
  touch('testarea/repo/repodata/repomd.xml')
  touch('testarea/realrepo/repodata/repomd.xml')

def teardownrepos():
  if os.path.isdir('testarea'):
    shutil.rmtree('testarea')

class TempHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def log_message(self, format, *args):
    with open("slingrpm/test/TempServer.log", "a") as logfile:
      logfile.write(format % args)
      logfile.write("\n")

class TempServer:

  def __init__(self):
    self.handler = TempHandler 
    self.httpd = SocketServer.TCPServer(("127.0.0.1", 65001), self.handler)

  def start(self):
    self.d = multiprocessing.Process(name='serve', target=self.httpd.serve_forever)
    self.d.daemon = True
    self.d.start()

  def stop(self):
    self.d.terminate()
    self.d.join()
 
