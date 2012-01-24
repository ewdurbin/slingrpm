import ConfigParser
import zmq

import os.path
from multiprocessing import Process

import time
import sys
import threading
import zlib
from slingconfig import SlingConfig

from catcher import Catcher

class SlingRPMDaemonProcess(Process):

  def __init__(self, config):
    super(SlingRPMDaemonProcess, self).__init__()
    self.config = config
    self.listenport = self.config.get('SlingRPMDaemon', 'listenport')

  def worker_routine(self, worker_url, context):
    socket = context.socket(zmq.REP)
    socket.connect(worker_url)
    while True:
      msg = socket.recv_pyobj()
      ret = {}

      if msg['body'] == "ALIVE?":
        ret['body'] = "YES"

      if msg['body'] == "FILE TO UPLOAD":
        try:
          host = msg['host']
          port = msg['port']
          repo = msg['repo']
          file = msg['path']
          config = SlingConfig(os.path.join(repo, '.slingrpm.conf'))
          catcher = Catcher(config, host, port, file)
          ret['body'] = "PULLING FILE"
          catcher.get_file()
        except:
          import traceback
          ret['body'] = "ERROR"
          ret['exception'] = traceback.format_exc()

      if ret == {}:
        ret['body'] = "UNKNOWN"

      socket.send_pyobj(ret)

  def run(self):
    self.context = zmq.Context(1)
    self.clients = self.context.socket(zmq.ROUTER)
    self.workers = self.context.socket(zmq.DEALER)

    try:
      self.clients.bind('tcp://*:%s' % self.listenport)
      self.workers.bind('inproc://workers')
    except:
      raise

    for i in range(4):
      thread = threading.Thread(target=self.worker_routine, args=('inproc://workers', self.context, ))
      thread.start()

    zmq.device(zmq.QUEUE, self.clients, self.workers)

class SlingRPMDaemon:

  def __init__(self, conf='/etc/slingrpm/daemon.conf'):
    self.read(conf)

  def read(self, conf):
    if not os.path.isfile(conf):
      raise Exception
    self.conf = conf

    try:
      config = ConfigParser.RawConfigParser()
      config.read(self.conf)
      self.config = config

      self.listenport = self.config.get('SlingRPMDaemon', 'listenport')
    except:
      raise

  def start(self):
    self.proc = SlingRPMDaemonProcess(self.config)
    self.proc.start()

  def stop(self):
    if self.proc.is_alive():
      self.proc.terminate()
      self.proc.join(timeout=10)

if __name__ == "__main__":
  import slingrpm
  daemon = SlingRPMDaemon()
  try:
    arg = sys.argv[1]
  except:
    arg = None
  if arg == "-d":
    slingrpm.daemonize()
  daemon.start()
