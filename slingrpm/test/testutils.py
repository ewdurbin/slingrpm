import sys
import os.path
import shutil
import multiprocessing
import zmq
import SimpleHTTPServer
import SocketServer
import ConfigParser

def touch(filename, content="foo"):
  f = open(filename, 'w')
  f.write(content)
  f.close()

def setuprepos():
  os.makedirs('testarea/badrepo')
  os.makedirs('testarea/repo/repodata')
  os.makedirs('testarea/realrepo/repodata')
  os.makedirs('testarea/freshrepo')
  os.makedirs('testarea/badconfrepo')

  touch('testarea/badconfrepo/.slingrpm.conf')
  touch('testarea/repo/repodata/repomd.xml')
  touch('testarea/realrepo/repodata/repomd.xml')

  config = ConfigParser.RawConfigParser()
  config.add_section('SlingRPM')
  config.set('SlingRPM', 'repolocation', os.path.abspath('testarea/repo')) 
  config.set('SlingRPM', 'packagedir', '')
  config.set('SlingRPM', 'commport', 64666) 
  config.set('SlingRPM', 'createrepoopts', '--update --excludes .slingrpm.conf --checksum sha') 
  with open('testarea/repo/.slingrpm.conf', 'wb') as configfile:
    config.write(configfile)

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
