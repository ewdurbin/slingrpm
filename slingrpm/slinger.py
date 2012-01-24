from urlparse import urlparse
from urllib import urlopen
import sys
import os.path
import time

import slingrpm

class Slinger:

  def __init__(self, targetrepo="", file=""):
    repomd = urlopen(targetrepo + 'repodata/repomd.xml')
    if repomd.getcode() != 200:
      raise Exception

    if not os.path.isfile(file):
      raise Exception

    self.file = os.path.abspath(file)
    self.targetrepo = targetrepo
    self.config = slingrpm.SlingConfig()
    self.config.read(self.targetrepo + '.slingrpm.conf')

    self.servedir = os.path.dirname(self.file)

    self.fileserver = slingrpm.SlingerFileServer(self.servedir)

  def serve(self):
    self.fileserver.start()

  def stop(self):
    self.fileserver.proc.terminate()
    self.fileserver.proc.join()

if __name__ == "__main__":
  import sys
  import zmq

  slinger = Slinger(sys.argv[1], sys.argv[2])
  slinger.serve()

  host = 'localhost'
  port = slinger.fileserver.port

  msg = {'body': "FILE TO UPLOAD",
         'host': host, 
         'port': port, 
         'path': slinger.file,
         'repo': slinger.config.repolocation} 

  context = zmq.Context()
  socket = context.socket(zmq.REQ)
  socket.connect('tcp://%s:%s' % (host, 64666))

  socket.send_pyobj(msg)
  resp = socket.recv_pyobj()

  if resp['body'] == "ERROR":
    print resp['exception']
    sys.exit(1)

  if resp['body'] == "UNKNOWN":
    print resp['body']
    sys.exit(1)

  while slinger.fileserver.done_queue.empty():
    time.sleep(.1)

  print slinger.fileserver.done_queue.get()
