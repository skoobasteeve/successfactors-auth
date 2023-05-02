#!/usr/bin/env python3

import base64
import json
import sys
import os
import requests
import xmlsec
import boto3
from lxml import etree
from datetime import datetime, timedelta


region = os.environ.get('AWS_REGION')
secret_id= os.environ.get('SECRET_ID')
template_file = 'sf_saml_template.xml'
private_keyfile = '/tmp/successfactors-private.pem'

def get_secret(region, secret_name, session):

    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )

        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']

    except Exception as x:
        print(x)
        sys.exit(1)

    return secret


def get_access_token(sf_url, company_id, client_id, assertion):

    token_request = dict(
        client_id=client_id,
        company_id=company_id,
        grant_type='urn:ietf:params:oauth:grant-type:saml2-bearer',
        assertion=assertion
    )
    response = requests.post(f"{sf_url}/oauth/token", data=token_request)
    token_data = response.json()
    return token_data['access_token']


def generate_assertion(sf_root_url, user_id, client_id, template_file):
    issue_instant = datetime.utcnow()
    auth_instant = issue_instant
    not_valid_before = issue_instant - timedelta(minutes=10)
    not_valid_after = issue_instant + timedelta(minutes=10)

    audience = 'www.successfactors.com'

    context = dict(
        issue_instant=issue_instant.isoformat(),
        auth_instant=auth_instant.isoformat(),
        not_valid_before=not_valid_before.isoformat(),
        not_valid_after=not_valid_after.isoformat(),
        sf_root_url=sf_root_url,
        audience=audience,
        user_id=user_id,
        client_id=client_id,
        session_id='mock_session_index',
    )
    saml_template = open(template_file).read()

    return saml_template.format(**context)


def sign_assertion(xml_string, private_key):
    key = xmlsec.Key.from_file(private_key, xmlsec.KeyFormat.PEM)

    root = etree.fromstring(xml_string)
    signature_node = xmlsec.tree.find_node(root, xmlsec.Node.SIGNATURE)

    sign_context = xmlsec.SignatureContext()
    sign_context.key = key
    sign_context.sign(signature_node)

    return etree.tostring(root)


def auth(sf_url, sf_company_id, sf_oauth_client_id,
         sf_admin_user, sf_saml_private_key, template_file):

    unsigned_assertion = generate_assertion(sf_url,
                                            sf_admin_user,
                                            sf_oauth_client_id,
                                            template_file)

    signed_assertion = sign_assertion(unsigned_assertion, sf_saml_private_key)
    signed_assertion_b64 = base64.b64encode(signed_assertion).replace(b'\n', b'')
    access_token = get_access_token(sf_url,
                                    sf_company_id,
                                    sf_oauth_client_id,
                                    signed_assertion_b64)

    return access_token


def lambda_handler(event, context):

    session = boto3.session.Session()

    print(event)

    if event['rawPath'] == '/token':
        body = json.loads(event['body'])
        sf_url = body['odata_url']
        sf_company_id = body['company_id']
        sf_oauth_client_id = body['oauth_client_id']
        sf_admin_user = body['admin_user']

        private_key = get_secret(region,
                                 secret_id,
                                 session)

        with open(private_keyfile, 'w') as f:
            f.write(private_key)

        token = auth(sf_url, sf_company_id, sf_oauth_client_id, sf_admin_user,
                     private_keyfile, template_file)

        payload = {
            "token": token
        }

        return {
            'statusCode': 200,
            'body': json.dumps(payload)
        }
