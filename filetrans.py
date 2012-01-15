#!/usr/bin/python2

import zmq 
import os.path
import os
import sys

class CatcherFilePuller:
  def __init__(self, destpath, srcpath, host, port):
    if os.path.isfile(destpath):
      raise Exception
    self.srcpath = srcpath
    self.host = host
    self.port = port
    self.destpath = destpath

  def get_file(self):
    dest = open(self.destpath, 'w+')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    buildserver = 'tcp://%s:%s' % (self.host, self.port)
    socket.connect(buildserver)
    socket.send(self.srcpath)
  
    while True:
        data = socket.recv()
        dest.write(data)
        if not socket.getsockopt(zmq.RCVMORE):
            break

class SlingerFileServer:
  def __init__(self, startingport, range):
    self.startingport = startingport
    self.range = range

  def serve(self):
    context = zmq.Context(1)
    sock = context.socket(zmq.REP)
    
    port = self.startingport
    serverstring = 'tcp://*:%s' % (port)
    maxport = self.startingport + self.range
    while port < maxport:
      try:
        sock.bind(serverstring)
        print port
        break
      except:
        port = port + 1 
  
    # Start the server loop
    while True:
      msg = sock.recv()
      if not os.path.isfile(msg):
        print "NO LUCK SIR"
        sock.send('')
        continue
      print "SERVING %s" % msg
      fn = open(msg, 'rb')
      stream = True
      # Start reading in the file
      while stream:
        # Read the file bit by bit
        stream = fn.read(128)
        if stream:
          # If the stream has more to send then send more
          sock.send(stream, zmq.SNDMORE)
        else:
            # Finish it off
            sock.send(stream)
