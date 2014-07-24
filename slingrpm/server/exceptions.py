

class FlaskException(Exception):

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class MD5Mismatch(FlaskException):

    def __init__(self, message, status_code=None, payload=None):
        FlaskException.__init__(self, message, status_code=507, payload=None)


class NoSuchRepository(FlaskException):

    def __init__(self, message, status_code=None, payload=None):
        FlaskException.__init__(self, message, status_code=404, payload=None)


class PackageExists(FlaskException):

    def __init__(self, message, status_code=None, payload=None):
        FlaskException.__init__(self, message, status_code=409, payload=None)
