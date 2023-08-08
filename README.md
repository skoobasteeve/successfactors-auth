# SuccessFactors Auth
Authenticate with the SAP SuccessFactors API with OAuth2 and Python.

## Dependencies

- xmlsec
- requests

## System Requirements

- libxml2 >= 2.9.1
- libxmlsec1 >= 1.2.18

## How to use

1. Create an OAuth application in SuccessFactors.
2. Download the private key and copy the Client ID.
3. Install the Python module:
   ``` shell
   pip install successfactors_auth
   ```
   Depending on your OS, you may need to install additional system packages, see [xmlsec documentation](https://pypi.org/project/xmlsec/).  
   **Note for macOS users:** There is a bug that prevents you from installing xmlsec with Homebrew, currently tracked in a [Github issue](https://github.com/xmlsec/python-xmlsec/issues/254). There are some workaround you can try, but in the mean time it may be easier to install within a container or VM.
4. Import `successfactors_auth` into your Python >=3.9 project.
5. Call the `successfactors_auth.get_token()` function in your Python project. You'll need to pass the following parameters:
    - `sf_url`: Base API url of your SuccessFactors instance, e.g. "https://api55.sapsf.eu".
    - `sf_company_id`: SuccessFactors company ID.
    - `sf_oauth_client_id`: The Client ID for the OAuth application you created earlier.
    - `sf_admin_user`: An admin user in SuccessFactors that has access to the OAuth application.
    - `sf_saml_private_key`: Path to the private key file you downloaded when you created the OAuth application.

### Example

``` python
#!/usr/bin/env python

import requests
import successfactors_auth as sf

sf_url = 'https://your.base.url.com'
sf_company_id = 'your-company-id'
sf_oauth_client_id = 'your_app_client_id'
sf_admin_user = 'your_admin_user'
sf_saml_private_key = 'app_private_key_file.pem'

token = sf.get_token(
    sf_company_id=company_id,
    sf_oauth_client_id=oauth_client_id,
    sf_admin_user=admin_api_user,
    sf_saml_private_key=oauth_private_key,
    sf_url=url
)

headers = {
    "Accept: application/json",
    f"Authorization: {token}"
}

request = requests.get(f"{sf_url}/User", headers=headers)
user = request.json()

print(user)
```

## Background

I wrote this module because I was forced to deal with the *horrific* SAP SuccessFactors API at my job, and I wanted to make sure other devs/sysadmins wouldn't have to feel the pain that I felt.  

Once you get authenticated, getting the information you want is a whole new level of suffering. I hope to publish some more examples in the form of a blog post or docs in this repo.

## Contributing

All contributions welcome! Feel free to file an [issue](https://github.com/skoobasteeve/successfactors_auth/issues) or open a [pull request](https://github.com/skoobasteeve/successfactors_auth/pulls).
