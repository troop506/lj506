from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials




def main():
    """Shows basic usage of the Admin SDK Directory API.
    Prints the emails and names of the first 10 users in the domain.
    """
    from google.oauth2 import service_account

    SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']
    SERVICE_ACCOUNT_FILE = 'data-connector-323916-62f0c260f9a5.json'

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES,
        subject='eric.busboom@lajollatroop506.com')

    service = build('admin', 'directory_v1', credentials=credentials)

    # Call the Admin SDK Directory API
    print('Getting the first 10 users in the domain')
    results = service.users().list(customer='my_customer', maxResults=500,
                                orderBy='email').execute()
    users = results.get('users', [])

    if not users:
        print('No users in the domain.')
    else:
        print('Users:')
        for user in users:
            print(user)
            #print(u'{0} ({1})'.format(user['primaryEmail'],
            #    user['name']['fullName']))


if __name__ == '__main__':
    main()