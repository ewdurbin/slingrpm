import shutil
import multiprocessing
import SimpleHTTPServer
import SocketServer
import time
import os.path
import os

import konira
from slingrpm import SlingRPM
from slingrpm import CatchRPM

def server():
  Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
  httpd = SocketServer.TCPServer(("", 65001), Handler)
  httpd.serve_forever()

def setuprepos():
  if os.path.isdir('testarea'):
    shutil.rmtree('testarea')
  os.makedirs('testarea/badrepo')
  os.makedirs('testarea/repo/repodata')
  f = open('testarea/repo/.slingrpm.conf', 'w')
  f.write('foo')
  f.close()
  f = open('testarea/repo/repodata/repomd.xml', 'w')
  f.write('foo')
  f.close()

def teardownrepos():
  if os.path.isdir('testarea'):
    shutil.rmtree('testarea')

describe "pushing a rpm package to our centralized repo":

  before all:
    setuprepos()

    self.b = multiprocessing.Process(name='serve', target=server)
    self.b.daemon = True
    self.b.start()
    
  after all:
    self.b.terminate()
    self.b.join()

    teardownrepos()

  it "throws an exception if you dont specify the repo":
    raises Exception: SlingRPM()
  it "throws an exception if the specified repo is not an http location":
    raises Exception: pusher = SlingRPM(targetrepo="/foo/bar/bazz/")
  it "throws an exception if the specified repo is not a yum repo":
    raises Exception: pusher = SlingRPM(targetrepo="http://localhost:65001/testarea/badrepo/")
  it "throws an exception if the specified repo is not setup for slingrpm":
    raises Exception: pusher = SlingRPM(targetrepo="http://localhost:65001/testarea/badrepo/")
  it "likes repos with a repmod and slingrpm":
    pusher = SlingRPM("http://localhost:65001/testarea/repo/")
    assert pusher
  it "can obtain a full path to the repository from .slingrpm.conf":
    pusher = SlingRPM("http://localhost:65001/testarea/repo/")
    assert os.path.isdir(pusher.targetpath)

describe "receiving a package":
 
  before all:
    setuprepos()
    self.badrepopath = os.path.join(os.getcwd(),'testarea/badrepo')
    self.repopath = os.path.join(os.getcwd(),'testarea/repo')

  after all:
    teardownrepos()
 
  it "needs a directory on the filesystem for a repo to live":
    catcher = CatchRPM(targetrepo=self.repopath)
    assert os.path.isdir(catcher.targetrepo)
  it "throws an exception if the target repo is not setup for slingrpm":
    raises Exception: catcher = CatchRPM(targetrepo=self.badrepopath)
