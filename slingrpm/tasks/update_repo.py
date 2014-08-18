from __future__ import absolute_import

import os

from pyrpm.yum import YumPackage
from pyrpm.tools.createrepo import YumRepository

from simpleflock import SimpleFlock

from slingrpm.celery import CELERY_APP
from slingrpm.repo_config import load_private_config
from slingrpm.tasks.sync_to_s3 import sync_to_s3


@CELERY_APP.task(name="slingrpm.tasks.update_repo")
def update_repo(repository_dir):
    try:
        with SimpleFlock(os.path.join(repository_dir, '.slingrpm.lock'),
                         timeout=3):
            repo_config = load_private_config(os.path.join(repository_dir,
                                                           '.slingrpm.cfg'))
            rpms = []
            for root, dirs, files in os.walk(repository_dir):
                for filename in files:
                    if filename.endswith(".rpm"):
                        rpms.append(os.path.join(root, filename))

            repository = YumRepository(repository_dir)
            packages_keys = [key for key, value in repository.packages()]

            for rpm in rpms:
                pkg = YumPackage(file(rpm))
                if pkg.checksum not in packages_keys:
                    repository.add_package(pkg)

            repository.save()
            if repo_config.getboolean('private', 's3_sync'):
                bucket_name = repo_config.get('private', 's3_sync_bucket')
                prefix = repo_config.get('private', 's3_sync_prefix')
                job_args = (repository_dir, bucket_name, prefix)
                sync_to_s3.apply_async(args=job_args)
    except (IOError) as exc:
        raise update_repo.retry(exc=exc, max_retries=1)
