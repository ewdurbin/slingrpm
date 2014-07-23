from slinger import Slinger
from catcher import Catcher
from slingconfig import SlingConfig
from slingsetup import SlingSetup
from slingerfileserver import SlingerFileServer
from slingerfileserver import SlingerFileServerProcess
from slingerfileserver import FileHandler
from yumrepo import YumRepo
from slingrpmdaemon import SlingRPMDaemon
from exceptions import NoRepoException
from exceptions import AlreadySlingEnabledException 

import os
import sys

def daemonize():
    '''
    Daemonize a process
    '''
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError as exc:
        print "first fork failed"
        sys.exit(1)

    # decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(022)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as exc:
        print "second fork failed"
        sys.exit(1)

    dev_null = open('/dev/null', 'rw')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())
    os.dup2(dev_null.fileno(), sys.stdout.fileno())
    os.dup2(dev_null.fileno(), sys.stderr.fileno())
