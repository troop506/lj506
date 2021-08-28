from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

subject='eric.busboom@lajollatroop506.com'

scopes = {
    'gmail': ['https://www.googleapis.com/auth/gmail.settings.basic',
              'https://www.googleapis.com/auth/gmail.settings.sharing',
              'https://www.googleapis.com/auth/gmail.modify'
              ],
    'admin': ['https://www.googleapis.com/auth/admin.directory.user']
}

def get_credentials(service_name, subject=None):

    from google.oauth2 import service_account

    SCOPES = scopes[service_name]
    SERVICE_ACCOUNT_FILE = 'data-connector-323916-62f0c260f9a5.json'

    if subject is not None:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES,
            subject=subject)
    else:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    return credentials

def get_service(service_name, version, subject):

    credentials = get_credentials(service_name, subject)

    service = build(service_name, version, credentials=credentials)

    return service

def main():
    """Shows basic usage of the Admin SDK Directory API.
    Prints the emails and names of the first 10 users in the domain.
    """

    bobson_id = 106829057542664179550

    dir_srv = get_service('admin', 'directory_v1', subject)

    results = dir_srv.users().list(customer='my_customer', maxResults=500,
                                orderBy='email').execute()
    users = results.get('users', [])

    for user in users:

        if  int(user['id']) == bobson_id:
            # print(user)
            print(f"{user['kind']}  {user['id']}  {user['name']}  {user.get('emails','NA')}")

    print('-------')

    gmail_src = get_service('gmail', 'v1', 'billy.bobson@lajollatroop506.com')

    results = gmail_src.users().settings().forwardingAddresses().list(userId='me').execute()
    if not results:
        address = {'forwardingEmail': 'eric+bobson@busboom.org'}
        result = gmail_src.users().settings().forwardingAddresses().create(userId='me', body=address).execute()

    results = gmail_src.users().settings().forwardingAddresses().list(userId='me').execute()

    print(results)

    print('-------')



if __name__ == '__main__':
    main()