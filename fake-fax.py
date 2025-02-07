import os
import os.path
import base64
import email
import json
from bs4 import BeautifulSoup
from datetime import datetime
from pprint import pprint
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

splash = '''
MM""""""""`M          dP                         MM""""""""`M
MM  mmmmmmmM          88                         MM  mmmmmmmM
M'      MMMM .d8888b. 88  .dP  .d8888b.          M'      MMMM .d8888b. dP.  .dP
MM  MMMMMMMM 88'  `88 88888"   88ooood8 88888888 MM  MMMMMMMM 88'  `88  `8bd8'
MM  MMMMMMMM 88.  .88 88  `8b. 88.  ...          MM  MMMMMMMM 88.  .88  .d88b.
MM  MMMMMMMM `88888P8 dP   `YP `88888P'          MM  MMMMMMMM `88888P8 dP'  `dP
MMMMMMMMMMMM                                     MMMMMMMMMMMM
'''

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def actually_print_text(msg, cpi, lpi):
    cstr = "echo '" + msg + "' | lpr" + " -o cpi=" + str(cpi) + " -o lpi=" + str(lpi) + " -o DocCutType=0NoCutDoc"
    os.system(cstr)

def actually_print_image(img):
    cstr = "lp -o fit-to-page -o DocCutType=0NoCutDoc " + path_to_img
    os.system(cstr)

def actually_cut():
    cstr = 'echo "" | lpr'
    os.system(cstr)

def actually_print_fax(fax):
    actually_print_text(fax["subject"] + "\n", 3, 3)
    actually_print_text(fax["sender"]  + "\n", 3, 3)
    actually_print_text(fax["message"] + "\n", 3, 3)

    if len (fax["attachments"]) == 0:
        # no attachments
        return 0

    actually_print_text("Attachments :\n", 3, 3)
    for attachment in fax["attachments"]:
        if attachment["id"]: # use the existence of a stored attachment id to denote images
            # todo download locally and print image then delete
            #actually_print_image(fax["attachments"])
            print("todo print picture here")
        else:
            actually_print_text(fax["attachments"]["filename"])

def import_whitelist():
    with open('sender_whitelist.json', 'r') as file:
        data = json.load(file)
    return data["senders"]

def process_email_part(payload, messages, attachments):
    main_type, sub_type = payload['mimeType'].split('/')
    if main_type == "multipart":
        parts = payload.get('parts')
        for part in parts:
            messages, attachments = process_email_part(part, messages, attachments)

    elif main_type == "text":
        messages.append(payload['body']['data'])

    elif main_type == "image":
        attachments.append({"filename": payload["filename"], "id" : payload['body']['attachmentId']})

    else:
        print("unkown mimetype: ", main_type)

    return messages, attachments

def email_to_fax(txt):
    # Get value of 'payload' from dictionary 'txt'
    payload = txt['payload']
    headers = payload['headers']

    # Look for Subject and Sender Email in the headers
    for d in headers:
        if d['name'] == 'Subject':
            subject = d['value']
        if d['name'] == 'From':
            sender = d['value']

    # The Body of the message is in Encrypted format. So, we have to decode it.
    # Get the data and decode it with base 64 decoder.

    messages, attachments = process_email_part(payload, [], [])

    message = ""

    for data in messages:
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data)

        # Now, the data obtained is in lxml. So, we will parse
        # it with BeautifulSoup library
        soup = BeautifulSoup(decoded_data, "lxml")
        body = str(soup.body())
        body = body.replace("'", "`") # this is to prevent ' escaping the print command
        message += body

    fax = { 
        "subject"     : str(subject),
        "sender"      : str(str(sender).split(' <')[0]),
        "message"     : message,
        "attachments" : attachments
    }
    return fax

def main():
    """
    Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)

    senderWhitelist = import_whitelist()

    if len(senderWhitelist) == 0:
        print("sender_whitlist.json is empty")
        return 0

    print(splash)
    print("Checking for faxing at: ", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    faxes = []

    for wSender in senderWhitelist:
        result = service.users().messages().list(userId="me",labelIds=['INBOX'], q="is:unread from:"+wSender).execute()
        messages = result.get('messages')

        if messages is None or len(messages) == 0:
            # no unread messages
            continue

        for msg in messages:
            # Get the message from its id
            email = service.users().messages().get(userId='me', id=msg['id'],).execute()

            try:
                # convert to fax
                faxes.append(email_to_fax(email))

                # mark converted emails as read
                service.users().messages().modify(userId="me", id=msg['id'], body={ 'removeLabelIds': ['UNREAD']}).execute()

            except Exception as e:
                print("Error", e)
                pass

    if len(faxes) > 0:
        print("Found " + str(len(faxes)) + " Faxes!")

        for line in splash.split('\n'):
            actually_print_text(line.replace("'","`"), 10, 10)

        actually_print_text(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 3 , 3)

        for fax in faxes:
             pprint(fax)
             actually_print_fax(fax)

        actually_cut()
        print("Done faxing.")

    else:
        print("No faxes at this time.")

if __name__ == "__main__":
    main()
