
import base64
import datetime
import hashlib
import hmac
import os
import sys
import urllib

import xmltodict
import requests

method = 'GET'
service = 'iam'
host = 'iam.amazonaws.com'
region = 'us-east-1'
endpoint = 'https://iam.amazonaws.com'

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def generate_get_user_query(access_key=None, secret_key=None):
    if access_key is None or secret_key is None:
        raise Exception

    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')

    canonical_uri = '/'

    canonical_headers = 'host:%s\n' % (host)
    signed_headers = 'host'

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = '/'.join([datestamp, region, service, 'aws4_request'])

    x_amz_credential = urllib.quote_plus(access_key + '/' + credential_scope)
    canonical_querystring = 'Action=GetUser&Version=2010-05-08'
    canonical_querystring += '&X-Amz-Algorithm=AWS4-HMAC-SHA256'
    canonical_querystring += '&X-Amz-Credential=' + x_amz_credential
    canonical_querystring += '&X-Amz-Date=' + amz_date
    canonical_querystring += '&X-Amz-Expires=30'
    canonical_querystring += '&X-Amz-SignedHeaders=' + signed_headers

    payload_hash = hashlib.sha256('').hexdigest()

    canonical_request = '\n'.join([method, canonical_uri,
                                   canonical_querystring, canonical_headers,
                                   signed_headers, payload_hash])

    string_to_sign = '\n'.join([algorithm, amz_date, credential_scope,
                                hashlib.sha256(canonical_request).hexdigest()])

    signing_key = getSignatureKey(secret_key, datestamp, region, service)

    signature = hmac.new(signing_key, (string_to_sign).encode("utf-8"),
                         hashlib.sha256).hexdigest()

    canonical_querystring += '&X-Amz-Signature=' + signature

    request_url = endpoint + "?" + canonical_querystring

    return request_url

def execute_get_user_query(query):
    r = requests.get(query)
    if r.status_code != 200:
        raise Exception
    response = xmltodict.parse(r.text)
    user_name = response['GetUserResponse']['GetUserResult']['User']['UserName']
    user_id = response['GetUserResponse']['GetUserResult']['User']['UserId']
    arn = response['GetUserResponse']['GetUserResult']['User']['Arn']
    return {'user_name': user_name, 'user_id': user_id, 'arn': arn}
