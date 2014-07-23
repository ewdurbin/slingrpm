from __future__ import absolute_import

import os

from slingrpm.celery import CELERY_APP

@CELERY_APP.task(name="slingrpm.tasks.stat_file")
def stat_file(file_name):
    print os.stat(file_name)
    return os.stat(file_name)
