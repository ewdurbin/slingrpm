"""
Copyright (c) Django Software Foundation and individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

"""
Sync to S3
==========

Modified from the Django command that scans all files in your
settings.MEDIA_ROOT folder and uploads them to S3 with the same directory
structure.

Note: This class requires the Python boto library and valid Amazon Web
Services API keys.

"""
import datetime
import mimetypes
import os
import time

# Make sure boto is available
try:
    import boto
    import boto.exception
except ImportError:
    raise ImportError, "The boto Python library is not installed."

class S3Syncer(object):

    def __init__(self, local_path, s3_bucket, s3_prefix=None, exclude=None):
        self.AWS_BUCKET_NAME = s3_bucket
        self.DIRECTORY = local_path
        if s3_prefix is None:
            s3_prefix = ''
        self.prefix = s3_prefix
        if not self.prefix.startswith('/'):
            self.prefix = "/" + self.prefix
        if exclude is None:
            exclude = []
        self.exclude = exclude
        self.verbosity = 100
        self.upload_count = 0
        self.skip_count = 0

    def sync_s3(self):
        """
        Walks the media directory and syncs files to S3
        """
        bucket, key = self.open_s3()
        os.path.walk(self.DIRECTORY, self.upload_s3,
            (bucket, key, self.AWS_BUCKET_NAME))

    def open_s3(self):
        """
        Opens connection to S3 returning bucket and key
        """
        conn = boto.connect_s3()
        try:
            bucket = conn.get_bucket(self.AWS_BUCKET_NAME)
        except boto.exception.S3ResponseError:
            bucket = conn.create_bucket(self.AWS_BUCKET_NAME)
        return bucket, boto.s3.key.Key(bucket)

    def upload_s3(self, arg, dirname, names):
        """
        This is the callback to os.path.walk and where much of the work happens
        """
        bucket, key, bucket_name = arg # expand arg tuple

        for file in names:
            headers = {}

            filename = os.path.join(dirname, file)
            if os.path.isdir(filename):
                continue # Don't try to upload directories

            if os.path.basename(filename) in self.exclude:
                continue

            file_key = filename[len(self.DIRECTORY):]
            if self.prefix:
                file_key = os.path.join(self.prefix, file_key.lstrip('/'))

            # Check if file on S3 is older than local file, if so, upload
            s3_key = bucket.get_key(file_key)
            if s3_key:
                s3_datetime = datetime.datetime(*time.strptime(
                    s3_key.last_modified, '%a, %d %b %Y %H:%M:%S %Z')[0:6])
                local_datetime = datetime.datetime.utcfromtimestamp(
                    os.stat(filename).st_mtime)
                if local_datetime < s3_datetime:
                    self.skip_count += 1
                    if self.verbosity > 1:
                        print "File %s hasn't been modified since last " \
                            "being uploaded" % (file_key)
                    continue

            # File is newer, let's process and upload
            if self.verbosity > 0:
                print "Uploading %s..." % (file_key)

            content_type = mimetypes.guess_type(filename)[0]
            if content_type:
                headers['Content-Type'] = content_type
            file_obj = open(filename, 'rb')
            file_size = os.fstat(file_obj.fileno()).st_size
            filedata = file_obj.read()

            try:
                key.name = file_key
                key.set_contents_from_string(filedata, headers, replace=True)
                key.make_public()
            except boto.s3.connection.S3CreateError, e:
                print "Failed: %s" % e
            except Exception, e:
                print e
                raise
            else:
                self.upload_count += 1

            file_obj.close()
