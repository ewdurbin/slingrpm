
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

    def __init__(self, user_ids=None, user_names=None, accounts=None):
        self.valid_user_ids = user_ids
        self.valid_user_names = user_names
        self.valid_accounts = accounts

        self.check_user_ids = True
        self.check_user_names = True
        self.check_accounts = True

        if len(self.valid_user_ids) == 0 or self.valid_user_ids is None:
            self.check_user_ids = False
        if len(self.valid_user_names) == 0 or self.valid_user_names is None:
            self.check_user_names = False
        if len(self.valid_accounts) == 0 or self.valid_accounts is None:
            self.check_accounts = False

    def validate(self, query):
        try:
            identity = iam.execute_get_user_query(query)
            account_good = True
            user_name_good = True
            user_id_good = True
            if self.check_accounts:
                account_good = identity['account'] in self.valid_accounts
            if self.check_user_ids or self.check_user_names:
                user_id_good = identity['user_id'] in self.valid_user_ids
                user_name_good = identity['user_name'] in self.valid_user_names
            return account_good and (user_id_good or user_name_good)
        except (Exception):
            return False

    def authenticate(self, wrapped):
        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            auth = request.headers.get('X-IAMPassthroughAuth-Query')
            if auth is None:
                resp = jsonify({'Not Authorized':
                                'No X-IAMPassthroughAuth-Query supplied'})
                resp.status_code = 401
                return resp
            if not self.validate(auth):
                resp = jsonify({'Not Authorized':
                                'IAMPassthroughAuth Invalid'})
                resp.status_code = 401
                return resp
            return wrapped(*args, **kwargs)
        return wrapper
