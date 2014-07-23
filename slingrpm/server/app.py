
import hashlib
import logging
import os
import tempfile

from flask import Flask
from flask import jsonify
from flask import request
from werkzeug.utils import secure_filename

from slingrpm.server.exceptions import *
from slingrpm.utils import hash_file
from slingrpm.tasks import update_repo

logging_handler = logging.StreamHandler()

APP = Flask(__name__)

STAGE_DIR = os.getenv('SLINGRPM_STAGE_DIR', tempfile.gettempdir())

@APP.errorhandler(FlaskException)
def handle_flask_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@APP.route('/', methods=['GET'])
def root_route():
    body = { "title": "slingrpm server" }
    return jsonify(body)

@APP.route('/submit', methods=['POST'])
def submit():
    repository = request.form['repository']
    package = request.files['package']
    md5hash = request.form['md5hash']
    filename = secure_filename(package.filename)
    stage_filename = os.path.join(STAGE_DIR, filename)
    target_filename = os.path.join(repository, package.filename)
    package.save(stage_filename)
    recvd_md5hash = hash_file(open(stage_filename, 'rb'))

    if md5hash != recvd_md5hash:
        raise MD5Mismatch('recieved file does not match supplied md5')
    if not os.path.isdir(repository):
        raise NoSuchRepository('the specified repository does not exist')
    if os.path.exists(target_filename):
        raise PackageExists('package name exists in specified repository')
    os.rename(stage_filename, target_filename)

    task = update_repo.apply_async(args=[repository])

    return jsonify({'response': 'got it', 'update_repo_task': task.id})

if __name__ == "__main__":
    APP.run(debug=True)
