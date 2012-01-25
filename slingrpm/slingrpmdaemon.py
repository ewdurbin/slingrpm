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
from yumrepo import YumRepo

class SlingRPMDaemonProcess(Process):

  def __init__(self, config):
    super(SlingRPMDaemonProcess, self).__init__()
    self.config = config
    self.listenport = self.config.get('SlingRPMDaemon', 'listenport')
    self.filequeue = []

  def catcher_routine(self, catcher_url, catcher_context, catcherout_url, catcherout_context):
    print "starting catcher"
    socket = catcher_context.socket(zmq.REP)
    socket.connect(catcher_url)
    socket1 = catcherout_context.socket(zmq.PUSH)
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
          outmsg = {'body': 'FILE ADDED', 'repo': msg['repo']}
          socket1.send_pyobj(outmsg)
        except:
          import traceback
          ret['body'] = "ERROR"
          ret['exception'] = traceback.format_exc()

      if ret == {}:
        ret['body'] = "UNKNOWN"

      socket.send_pyobj(ret)

  def repoupdater_routine(self, repoupdater_url, repoupdater_context):
    print "starting repoupdater"
    socket = repoupdater_context.socket(zmq.PULL)
    socket.connect(repoupdater_url)
    poller = zmq.core.poll.Poller()
    poller.register(socket, flags=zmq.POLLIN)
    while True:
      if poller.poll(timeout=100):
        msg = socket.recv_pyobj()
        if msg['body'] == "FILE ADDED":
          self.filequeue.append((time.time(), msg['repo']))
        elif msg['body'] == "ALIVE?":
          print "ping recieved"
          continue

      """ check condition """
      if len(self.filequeue) > 0:
        mintime = min(self.filequeue, key=lambda x: x[0])
        if len(self.filequeue) >= 15 or time.time() - mintime[0] >= 10 and not poller.poll(timeout=10):
          print "updating repo"
          repos = []
          for item in self.filequeue:
            repos.append(item[1])
          for repo in set(repos):
            yumrepo = YumRepo(repo)
            yumrepo.updatemetadata()
          self.filequeue = []
      time.sleep(.1)
 

  def run(self):
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

    repoupdater = ThreadDevice(zmq.STREAMER, zmq.PULL, zmq.PUSH)
    repoupdater.daemon = False
    repoupdater.setsockopt_in(zmq.IDENTITY, 'repoPUSH')
    repoupdater.bind_in(self.catchersout_url)
    repoupdater.setsockopt_out(zmq.IDENTITY, 'repoPULL')
    repoupdater.bind_out(self.repoupdater_url)
    repoupdater.start()

    for i in range(4):
 
      thread = threading.Thread(target=self.catcher_routine,
                                args=(self.catchers_url,
                                      catchers.context_factory(),
                                      self.catchersout_url,
                                      repoupdater.context_factory(), ))
      thread.start()

    thread = threading.Thread(target=self.repoupdater_routine,
                              args=(self.repoupdater_url,
                                    repoupdater.context_factory(), ))
    thread.start()

    while True:
      time.sleep(5)

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
