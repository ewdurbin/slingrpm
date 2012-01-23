import konira

import testutils
import os
import os.path
import time

from slingrpm import SlingRPMDaemon
from slingrpm import Slinger

goodconf = os.path.join(os.getcwd(), 'testarea/etc/slingrpm/daemon.conf')
badconf = os.path.join(os.getcwd(), 'testarea/etc/slingrpm/bad.conf')
noconf = os.path.join(os.getcwd(), 'testarea/etc/slingrpm/no.conf')

describe "the SlingRPMDaemon":

  before all:
    testutils.mocketc()

  it "accepts a configuration file on initialization":
    daemon = SlingRPMDaemon(goodconf)
    assert daemon

  it "raises an exception if the config file DNE":
    raises Exception: daemon = SlingRPMDaemon(noconf)

  it "raises an exception if the config file sucks":
    raises Exception: daemon = SlingRPMDaemon(badconf)

  it "reads the configuration and exposes a listening port":
    daemon = SlingRPMDaemon(goodconf)
    assert int(daemon.listenport) == 64666

  after all:
    testutils.unmocketc()

describe "process tests for SlingRPMDaemon":

  before all:
    testutils.mocketc()
    self.d = SlingRPMDaemon(goodconf)
    self.d.start()

  it "opens a daemon port when start is called":
    msg = {'body': "ALIVE?"}
    resp = testutils.send_msg_get_rsp(self.d.listenport, msg)
    assert resp['body'] == "YES"

  it "can obtain a file":
    testutils.setuprepos()
    server = testutils.TempServer()
    server.start()
    
    slinger = Slinger('http://localhost:' + str(server.port) + '/testarea/repos/repo/', os.path.join(os.getcwd(), 'slingrpm/test', 'empty-0-1.i386.rpm'))
    slinger.serve()
    port = slinger.fileserver.port

    msg = {'body': "FILE TO UPLOAD",
           'host': 'localhost',
           'port': port, 
           'file': os.path.join(os.getcwd(), 'slingrpm/test', 'empty-0-1.i386.rpm'),
           'repo': os.path.join(os.getcwd(), 'testarea/repos/repo')}

    port = self.d.listenport
    resp = testutils.send_msg_get_rsp(port, msg)
    server.stop()
    assert os.path.isfile(os.path.join(os.getcwd(), 'testarea/repos/repo', 'empty-0-1.i386.rpm'))
    testutils.teardownrepos()

  after all:
    self.d.stop()
    testutils.unmocketc()
