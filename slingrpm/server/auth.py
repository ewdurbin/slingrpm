
from functools import wraps

from flask import request
from flask import jsonify

from slingrpm.utils import iam

class NoOpAuth(object):

    def __init__(self):
        pass

    def authenticate(self, wrapped):
        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            return wrapped(*args, **kwargs)
        return wrapper

class IAMPassthroughAuth(object):

    def __init__(self, allowed_users=None, allowed_access_keys=None,
                 allowed_accounts=None):
        if allowed_users is None:
            allowed_users = []
        if allowed_access_keys is None:
            allowed_access_keys = []
        if allowed_accounts is None:
            allowed_accounts = []

        self.allowed_users = allowed_users
        self.allowed_access_keys = allowed_access_keys
        self.allowed_accounts = allowed_accounts

    def validate(self, query):
        try:
            identity = iam.execute_get_user_query(query)
            if len(self.allowed_accounts) > 0 and identity['user_account'] not in self.allowed_accounts:
                return False
            if len(self.allowed_access_keys) > 0 or len(self.allowed_users) > 0:
                key_is_authorized = self.allowed_access_keys.__contains__(identity['user_id'])
                user_is_authorized = self.allowed_users.__contains__(identity['user_name'])
                return key_is_authorized or user_is_authorized
        except (Exception) as exc:
            return False

    def authenticate(self, wrapped):
        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            auth = request.headers.get('X-IAMPassthroughAuth-Query')
            if auth is None:
                resp = jsonify({'Not Authorized': 'No X-IAMPassthroughAuth-Query supplied'})
                resp.status_code = 401
                return resp
            if not self.validate(auth):
                resp = jsonify({'Not Authorized': 'IAMPassthroughAuth Invalid'})
                resp.status_code = 401
                return resp
            return wrapped(*args, **kwargs)
        return wrapper
