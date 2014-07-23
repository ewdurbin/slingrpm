from __future__ import absolute_import

from celery import Celery
import os

CELERY_APP = Celery('slingrpm',
                    broker=os.getenv('CELERY_BROKER_URI', None),
                    backend=os.getenv('CELERY_RESULT_BACKEND', None),
                    include=['slingrpm.tasks'])

if __name__ == '__main__':  # pragma: no branch
    CELERY_APP.start()  # pragma: no cover
