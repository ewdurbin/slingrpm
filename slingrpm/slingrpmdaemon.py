import ConfigParser
import zmq
from zmq.devices.basedevice import ThreadDevice

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

  def catcher_routine(self, catcher_url, catcher_context, catcherout_url, catcherout_context):
    socket = catcher_context.socket(zmq.REP)
    socket.connect(catcher_url)
    socket1 = catcherout_context.socket(zmq.REQ)
    socket1.connect(catcherout_url)
    while True:
      msg = socket.recv_pyobj()
      ret = {}

      if msg['body'] == "ALIVE?":
        ret['body'] = "YES"

      if msg['body'] == "FILE TO UPLOAD":
        try:
          config = SlingConfig(os.path.join(msg['repo'], '.slingrpm.conf'))
          catcher = Catcher(config, msg['host'], msg['port'], msg['path'])
          ret['body'] = "PULLING FILE"
          catcher.get_file()
          outmsg = {'body': 'FILE ADDED'}
          socket1.send_pyobj(outmsg)
          print socket1.recv_pyobj()
        except:
          import traceback
          ret['body'] = "ERROR"
          ret['exception'] = traceback.format_exc()

      if ret == {}:
        ret['body'] = "UNKNOWN"

      socket.send_pyobj(ret)

  def repoupdater_routine(self, catcherout_url, repoupdater_url, context):
    socket = context.socket(zmq.REP)
    socket.connect(catcherout_url)
    while True:
      msg = socket.recv_pyobj()
      ret = {}

      if msg['body'] == "ALIVE?":
        ret['body'] = "YES"

      if msg['body'] == "FILE ADDED":
        print msg
        ret['body'] = "KTHNKXBYE"

      if ret == {}:
        ret['body'] = "UNKNOWN"

      socket.send_pyobj(ret)

  def run(self):
#    self.context = zmq.Context(1)
#    self.clients = self.context.socket(zmq.ROUTER)
#    self.catchers = self.context.socket(zmq.DEALER)
#    self.context0 = zmq.Context(1)
#    self.catchersout = self.context0.socket(zmq.ROUTER)
#    self.repoupdater = self.context0.socket(zmq.DEALER)

    self.clients_url = 'tcp://*:%s' % self.listenport
    self.catchers_url = 'ipc:///var/run/slingrpm/catchers'

    catchers = ThreadDevice(zmq.QUEUE, zmq.ROUTER, zmq.DEALER)
    catchers.setsockopt_in(zmq.IDENTITY, 'catcherROUTER')
    catchers.bind_in(self.clients_url)
    catchers.setsockopt_out(zmq.IDENTITY, 'catcherDEALER')
    catchers.bind_out(self.catchers_url)
    catchers.start()

    self.catchersout_url = 'ipc:///var/run/slingrpm/catchersout'
    self.repoupdater_url = 'ipc:///var/run/slingrpm/repoupdater'

    repoupdater = ThreadDevice(zmq.QUEUE, zmq.ROUTER, zmq.DEALER)
    repoupdater.setsockopt_in(zmq.IDENTITY, 'repoROUTER')
    repoupdater.bind_in(self.catchersout_url)
    repoupdater.setsockopt_out(zmq.IDENTITY, 'repoDEALER')
    repoupdater.bind_out(self.repoupdater_url)
    repoupdater.start()

#    try:
#      self.clients.bind(self.clients_url)
#      self.catchers.bind(self.catchers_url)
#      self.catchersout.bind(self.catchersout_url)
#      self.repoupdater.bind(self.repoupdater_url)
#    except:
#      raise

#    zmq.device(zmq.QUEUE, self.clients, self.catchers)
#    zmq.device(zmq.QUEUE, self.catchersout, self.repoupdater)

    for i in range(4):
 
      thread = threading.Thread(target=self.catcher_routine,
                                args=(self.catchers_url,
                                      catchers.context_factory(),
                                      self.catchersout_url,
                                      repoupdater.context_factory(), ))
      thread.start()

    thread = threading.Thread(target=self.repoupdater_routine,
                              args=(self.catchersout_url,
                                    self.repoupdater_url,
                                    repoupdater.context_factory(), ))

    while True:
      time.sleep(1)

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
