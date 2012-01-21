import sys
import os.path
import subprocess
import shutil
import multiprocessing
import zmq
import SimpleHTTPServer
import SocketServer
import ConfigParser

def execute(cmd):
  fd = open('execute.log', 'a')
  retcode = subprocess.check_call([cmd], stderr=fd, stdout=fd, shell=True)
  fd.close()
  return retcode

def touch(filename, content="foo"):
  f = open(filename, 'w')
  f.write(content)
  f.close()

def mocketc():
  os.makedirs('testarea/etc/slingrpm')
  touch('testarea/etc/slingrpm/bad.conf')
  config = ConfigParser.RawConfigParser()
  config.add_section('SlingRPMDaemon')
  config.set('SlingRPMDaemon', 'listenport', 64666) 
  with open('testarea/etc/slingrpm/daemon.conf', 'wb') as configfile:
    config.write(configfile)

def unmocketc():
  if os.path.isdir('testarea/etc'):
    shutil.rmtree('testarea/etc')
    

def setuprepos():
  os.makedirs('testarea/repos/badrepo')
  os.makedirs('testarea/repos/repo')
  os.makedirs('testarea/repos/realrepo')
  os.makedirs('testarea/repos/freshrepo')
  os.makedirs('testarea/repos/badconfrepo')

  shutil.copyfile('slingrpm/test/empty-0-0.i386.rpm', 'testarea/repos/repo/empty-0-0.i386.rpm')
  shutil.copyfile('slingrpm/test/empty-0-0.i386.rpm', 'testarea/repos/realrepo/empty-0-0.i386.rpm')

  execute('createrepo %s' % 'testarea/repos/repo')
  execute('createrepo %s' % 'testarea/repos/realrepo')
  touch('testarea/repos/badconfrepo/.slingrpm.conf')

  config = ConfigParser.RawConfigParser()
  config.add_section('SlingRPM')
  config.set('SlingRPM', 'repolocation', os.path.abspath('testarea/repos/repo')) 
  config.set('SlingRPM', 'packagedir', '')
  config.set('SlingRPM', 'commport', 64666) 
  config.set('SlingRPM', 'createrepoopts', '--update --excludes .slingrpm.conf --checksum sha') 
  with open('testarea/repos/repo/.slingrpm.conf', 'wb') as configfile:
    config.write(configfile)

def teardownrepos():
  if os.path.isdir('testarea/repos'):
    shutil.rmtree('testarea/repos')

def send_msg_get_rsp(port, msg):
  context = zmq.Context()
  socket = context.socket(zmq.REQ)
  socket.connect('tcp://%s:%s' % ('127.0.0.1', port))
  socket.send_pyobj(msg)
  return socket.recv_pyobj()

def send_msg(port, msg):
  context = zmq.Context()
  socket = context.socket(zmq.REQ)
  socket.connect('tcp://%s:%s' % ('127.0.0.1', port))
  socket.send_pyobj(msg)

class TempHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def log_message(self, format, *args):
    with open("slingrpm/test/TempServer.log", "a") as logfile:
      logfile.write(format % args)
      logfile.write("\n")

class TempServer:

  def __init__(self):
    self.handler = TempHandler 
    port = 64000
    while port < 65000:
      try:
        self.httpd = SocketServer.TCPServer(("127.0.0.1", port), self.handler)
        break
      except:
       port = port + 1
    self.port = port

  def start(self):
    self.d = multiprocessing.Process(name='serve', target=self.httpd.serve_forever)
    self.d.daemon = True
    self.d.start()

  def stop(self):
    self.d.terminate()
    self.d.join()

if __name__ == "__main__":
  teardownrepos()
  setuprepos()
