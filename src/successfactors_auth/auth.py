#!/usr/bin/env python3

'''
Authenticates to the SuccessFactors API using OAuth2 with a SAML 2.0
grant type. A SAML assertion is generated using a local template file,
then signed with a private key file before being encoded in base64 and
sent to the API via a POST request. This script is designed to be imported
into other Python scripts, which can call the auth() function to get a
Bearer token.

Derived from: https://github.com/mtrdesign/python-saml-example

This module requires the following additional files:
-Private key file for a previously created SuccessFactors OAuth2 application

Required packages:
requests
lxml
xmlsec

Example:
#!/usr/bin/env python3

import successfactors_auth

token = successfactors_auth.auth(
            SF_URL,
            SF_COMPANY_ID,
            SF_OAUTH_CLIENT_ID,
            SF_ADMIN_USER,
            SF_OAUTH_PRIVATE_KEY_FILE,
        )
'''

import base64
from datetime import datetime, timedelta
from importlib import resources as impresources
import requests
import xmlsec
from lxml import etree

from . import templates


def get_access_token(sf_url: str, company_id: str, client_id: str,
                     assertion: str) -> str:
    """
    Send POST request to SuccessFactors containing the generated
    SAML assertion and other details, then receive a token in response
    """
    # Request body
    token_request = dict(
        client_id=client_id,
        company_id=company_id,
        grant_type='urn:ietf:params:oauth:grant-type:saml2-bearer',
        assertion=assertion
    )
    response = requests.post(f"{sf_url}/oauth/token", data=token_request,
                             timeout=15)
    token_data = response.json()
    return token_data['access_token']


def generate_assertion(sf_root_url: str, user_id: str, client_id: str,
                       template_file: str) -> str:
    """
    Generate SAML assertion from the template XML
    """
    # Calculate valid time values for the assertion's validity
    issue_instant = datetime.utcnow()
    auth_instant = issue_instant
    not_valid_before = issue_instant - timedelta(minutes=10)
    not_valid_after = issue_instant + timedelta(minutes=10)

    audience = 'www.successfactors.com'

    # Define values to fill in the template with
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
    # Open the template file
    saml_template = open(template_file, encoding="utf-8").read()

    # Fill the values into the template and return in
    return saml_template.format(**context)


def sign_assertion(xml_string: str, private_key: str) -> str:
    """
    Sign the SAML assertion using a private key file
    """
    # Import key file
    key = xmlsec.Key.from_file(private_key, xmlsec.KeyFormat.PEM)

    # Find space in the SAML assertion XML to fill in the signature
    root = etree.fromstring(xml_string)
    signature_node = xmlsec.tree.find_node(root, xmlsec.Node.SIGNATURE)

    # Sign the XML
    sign_context = xmlsec.SignatureContext()
    sign_context.key = key
    sign_context.sign(signature_node)

    # Return signed XML string
    return etree.tostring(root)


def auth(sf_url: str, sf_company_id: str, sf_oauth_client_id: str,
         sf_admin_user: str, sf_saml_private_key: str) -> str:
    """
    Request an API access token by generating a signed SAML assertion
    and using it to authenticate with SuccessFactors.
    """

    template_file = impresources.files(templates) / 'sf_saml_template.xml'

    # Generate SAML assertion XML from template file
    unsigned_assertion = generate_assertion(sf_url,
                                            sf_admin_user,
                                            sf_oauth_client_id,
                                            template_file)

    # Sign the SAML assertion with the private key file
    signed_assertion = sign_assertion(unsigned_assertion, sf_saml_private_key)

    # Convert the signed XML string to base64
    signed_assertion_b64 = base64.b64encode(signed_assertion).replace(b'\n', b'')

    # Request the API token from SuccessFactors via a POST request
    access_token = get_access_token(sf_url,
                                    sf_company_id,
                                    sf_oauth_client_id,
                                    signed_assertion_b64)

    return access_token
