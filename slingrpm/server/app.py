from flask import Flask, jsonify

from slingrpm.tasks import stat_file

APP = Flask(__name__)

@APP.route('/')
def root_route():
    body = { "title": "slingrpm server" }
    return jsonify(body)

@APP.route('/stat/<file_name>')
def stat_file_route(file_name):
    stat_file.delay(file_name)
    return jsonify({'response': 'got it'})

if __name__ == "__main__":
    APP.run(debug=True)
