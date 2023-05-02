# SuccessFactors + Python
Authenticate with and use the SAP SuccessFactors API with Python.

## Authentcation

### How to use

1. Create an OAuth application in SuccessFactors.
2. Download the private key and copy the Client ID.
3. Clone this repo and copy `sf_auth.py` and `sf_saml_template.xml` into your Python project directory.
4. Import `sf_auth` into your project.
5. Install all the requirements listed in `requirements.txt` in this repo.
6. Call the `sf_auth.auth()` function in your Python project. You'll need to pass the following parameters:
    - `sf_url`: Base API url of your SuccessFactors instance, e.g. "https://api55.sapsf.eu".
    - `sf_company_id`: SuccessFactors company ID.
    - `sf_oauth_client_id`: The Client ID for the OAuth application you created earlier.
    - `sf_admin_user`: An admin user in SuccessFactors that has access to the OAuth application.
    - `sf_saml_private_key`: Path to the private key file you downloaded when you created the OAuth application.
    - `template_file`: Path to the template file from this repo.

    Example:
    ``` python
    #!/usr/bin/env python

    import requests
    import sf_auth

    sf_url = 'https://your.base.url.com'
    sf_company_id = 'your-company-id'
    sf_oauth_client_id = 'OAUTH-CLIENT-ID'
    sf_admin_user = 'your_admin_user'
    sf_saml_private_key = 'your_app_private_key.pem'
    template_file = 'sf_saml_template.xml'

    token = sf_auth.auth(sf_url, sf_company_id, sf_oauth_client_id, sf_admin_user, sf_saml_private_key, sf_saml_template)

    headers = {
        "Accept: application/json",
        f"Authorization: {token}"
    }

    request = requests.get(f"{sf_url}/User", headers=headers)

    print(request.json())
    ```

### Using as an AWS Lambda function w/ API Gateway

Coming soon...