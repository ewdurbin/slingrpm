from __future__ import absolute_import

import os

from pyrpm.yum import YumPackage
from pyrpm.tools.createrepo import YumRepository

from simpleflock import SimpleFlock

from slingrpm.celery import CELERY_APP


@CELERY_APP.task(name="slingrpm.tasks.update_repo")
def update_repo(repository_dir):
    try:
        with SimpleFlock(os.path.join(repository_dir, 'lock'), timeout=3):
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
    except (IOError) as exc:
        raise update_repo.retry(exc=exc, max_retries=1)
