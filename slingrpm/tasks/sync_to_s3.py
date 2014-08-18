from __future__ import absolute_import

import os

from simpleflock import SimpleFlock

from slingrpm.celery import CELERY_APP
from slingrpm.utils.s3 import S3Syncer


@CELERY_APP.task(name="slingrpm.tasks.sync_to_s3")
def sync_to_s3(repository_dir, bucket_name, prefix):
    logger = sync_to_s3.get_logger()
    logger.info("Syncing %s to %s/%s", repository_dir, bucket_name, prefix)
    try:
        with SimpleFlock(os.path.join(repository_dir, '.slingrpm.lock'), timeout=3):
            exclude_list = ['.slingrpm.cfg', '.slingrpm.lock']
            syncer = S3Syncer(repository_dir, bucket_name, prefix,
                              exclude=exclude_list)
            syncer.sync_s3()
        logger.info("Successfully synced %s to %s/%s", repository_dir,
                    bucket_name, prefix)
    except (IOError) as exc:
        logger.warn("Unable to lock repo %s, retrying...", repository_dir)
        raise update_repo.retry(exc=exc, max_retries=1)
