import slingrpm
import zmq

import sys
import os.path
import time
import optparse
import socket

from urlparse import urlparse
from urllib import urlopen

class Slinger:

  def get_serve_ip(self, rhost, rport):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((rhost, rport))
    host = s.getsockname()[0]
    s.close()
    return host

  def __init__(self, targetrepo='http://foobah.baz:75000/repo', file='/dev/null/null'):
    self.parse_cli()

    if self.file == '/dev/null/null':
      raise Exception('must specify file')
    if self.targetrepo == 'http://foobah.baz:75000/repo':
      raise Exception('must specify target repository')

    repomd = urlopen(self.targetrepo + 'repodata/repomd.xml')
    if repomd.getcode() != 200:
      raise Exception('Not a valid Yum Repository')

    if not os.path.isfile(self.file):
      raise Exception('No such file %s to serve' % self.file)

    parsed = urlparse(self.targetrepo)

    self.repohost = parsed.hostname
    self.repoport = parsed.port

    self.slinghost = self.get_serve_ip(self.repohost, self.repoport)

    self.config = slingrpm.SlingConfig(self.targetrepo + '.slingrpm.conf')

    self.servedir = os.path.dirname(self.file)
    self.fileserver = slingrpm.SlingerFileServer(self.servedir)

  def serve(self):
    self.fileserver.start()

  def stop(self):
    self.fileserver.proc.terminate()
    self.fileserver.proc.join()

  def parse_cli(self):
    parser = optparse.OptionParser()
    parser.add_option('-r', '--repository', dest='repo', default=None, help='Repository to push to')
    parser.add_option('-p', '--package', dest='package', default=None, help='Package to publish')
    options, args = parser.parse_args()

    if options.package:
      self.file = os.path.abspath(os.path.expandvars(options.package))
    
    self.targetrepo = options.repo

  def setup_comm_connection(self):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.REQ)
    self.socket.connect('tcp://%s:%s' % (self.repohost, self.config.commport))

  def sling(self):
    print "setting up for publication"
    self.serve()

    self.slingport = self.fileserver.port

    msg = {'body': "FILE TO UPLOAD",
           'host': self.slinghost, 
           'port': self.slingport, 
           'path': self.file,
           'repo': self.config.repolocation} 

    self.setup_comm_connection()
    self.socket.send_pyobj(msg)
    poller = zmq.Poller()
    poller.register(self.socket, zmq.POLLIN)
    resp = None
    if poller.poll(10*1000):
      resp = self.socket.recv_pyobj()
    else:
      print "Daemon did not respond within 10s"

    if resp:
      if resp['body'] == "ERROR":
        print resp['exception']
        raise Exception('ERROR on server, see stacktrace above')
    
      if resp['body'] == "UNKNOWN":
        print resp['body']
        return 1
   
      print "connected to slingrpmdaemon, pushing file..." 

    while self.fileserver.done_queue.empty():
      time.sleep(.1)
    
    status = self.fileserver.done_queue.get()
    if status == "SUCCESS":
      print "published %s to repo %s" % (self.file, self.targetrepo)
      return 0
    if status == "FAILURE":
      print "failed to publish"
      return 1

