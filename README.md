# Catalogue Project - Robin Edmunds 2018

## Music Collector

Web applicatoin...

## Versions
- Ubuntu 18.04
- Python 3.6.7
- Flask (1.0.2)
- httplib2 (0.9.2)
- itsdangerous (1.1.0)
- Jinja2 (2.10)
- pip (9.0.1)
- requests (2.19.1)
- simplejson (3.13.2)
- six (1.11.0)
- urllib3 (1.23)
- Werkzeug (0.14.1)
- pyOpenSSL (17.5.0)


## JSON API Endpoints

#### Entire collection: -
/api/collections/**user_id**

#### Single media item: -
/api/collections/**user_id**/media/**media_id**


## Setup

1. Install python3 package dependencies listed above using pip3
1. Clone the github repo to your local machine
1. Run __"python3 mcmodel.py"__ to generate SQLite database
1. For testing, run __"python3 mcpopulate.py"__ to populate the database with dummy data
1. Run __"python3 mcviews.py"__ to run the site in your local development environment
1. Open __https://localhost:8000__ in your web browser (note https)


## Testing

Dummy, native accounts follow the same format. The email is comprised of the first name initial, @ surname.lan. (e.g. __j@bloggs.lan__). The password for all dummy accounts is, __"secret"__. Note that in the database, only salted hashes of the passwords are stored.


## Creating and Editing Records

Music Collection records are read-only unless you are logged in as the owner of the collection. When logged in you may create new records, edit and delete existing records and also change the collection description.


## Creating a New Collection

A new Music Collection is created when a new account is registered via the registration link on the login page. Users are currently limited to one collection.

#### OAuth2
New Collections can also be made by logging in via the Google or Facebook OAuth2 buttons present on the login page. On the first successful auth of a Google or Facebook account, a new collection is created.


## Issues

- There is an unresolved conflict between the Google and Facebook OAuth2 implementation which prevents Google oauth2 working in Firefox. The workaround is to use Chrome.
- Facebook prevents callback forwarding on none https addresses and so an https Werkzeug is required for Facebook oauth2 usage in the development environment.
- On successful login using either oauth2 provider, the site does not forward to the user's collection as intended. Navigate to another page to confirm login and new collection creation.
- Logging out of a google oauth2 account successfully logs off the app, but does not log the user out from google.
