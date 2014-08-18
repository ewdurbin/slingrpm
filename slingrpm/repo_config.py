
import StringIO

from ConfigParser import SafeConfigParser

PUBLIC_DEFAULTS = {
    'submission_url': None,
    'repository_dir': None,
    }

PRIVATE_DEFAULTS = {
    'iam_auth': False,
    'iam_auth_user_ids': None,
    'iam_auth_user_names': None,
    'iam_auth_accounts': None,
    's3_sync': False,
    's3_sync_bucket': None,
    's3_sync_prefix': None,
    }


def parse_public_config(config_string):
    """Read public configuration from a string"""
    config_file = StringIO.StringIO(config_string)
    config = SafeConfigParser(PUBLIC_DEFAULTS)
    config.add_section('public')
    config.readfp(config_file)
    return config

def parse_private_config(config_string):
    """Read private configuration from a string"""
    config_file = StringIO.StringIO(config_string)
    config = SafeConfigParser(PRIVATE_DEFAULTS)
    config.add_section('private')
    config.readfp(config_file)
    return config

def load_public_config(config_path):
    """Read public configuration from a file."""
    with open(config_path) as config_file:
        return parse_public_config(config_file.read())

def load_private_config(config_path):
    """Read private configuration from a file."""
    with open(config_path) as config_file:
        return parse_private_config(config_file.read())
