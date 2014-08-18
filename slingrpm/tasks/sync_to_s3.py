from __future__ import absolute_import

import os

from simpleflock import SimpleFlock

from slingrpm.celery import CELERY_APP
from slingrpm.utils.s3 import S3Syncer


@CELERY_APP.task(name="slingrpm.tasks.sync_to_s3")
def sync_to_s3(repository_dir, bucket_name, prefix):
    try:
        with SimpleFlock(os.path.join(repository_dir, '.slingrpm.lock'), timeout=3):
            exclude_list = ['.slingrpm.cfg', '.slingrpm.lock']
            syncer = S3Syncer(repository_dir, bucket_name, prefix,
                              exclude=exclude_list)
            syncer.sync_s3()
    except (IOError) as exc:
        raise update_repo.retry(exc=exc, max_retries=1)
