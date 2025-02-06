import os
import os.path
import base64
import email
import json
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

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

def parse_msg(msg):
    if msg.get("payload").get("body").get("data"):
        return base64.urlsafe_b64decode(msg.get("payload").get("body").get("data").encode("ASCII")).decode("utf-8")
    return msg.get("snippet")

def actually_print(msg, cpi, lpi, cut):
    cutFlag = " -o DocCutType=0NoCutDoc"
    if cut:
        cutFlag = ""
    cstr = "echo '" + msg + "' | lpr" + " -o cpi=" + str(cpi) + " -o lpi=" + str(lpi) + cutFlag
    # print("cstr:", cstr)
    os.system(cstr)

def print_message(txt, toPrint):
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
    # TODO better switch case handling
    mimeType = payload['mimeType']

    if mimeType == "multipart/alternative":
        parts = payload.get('parts')[0]
        data = parts['body']['data']

    elif mimeType == "multipart/signed":
        parts = payload.get('parts')[0]
        data = parts['body']['data']

    elif mimeType == "text/plain":
        data = payload['body']['data']

    else:
        print("mimeType not seen before: ", mimeType)

    data = data.replace("-","+").replace("_","/")
    decoded_data = base64.b64decode(data)

    # Now, the data obtained is in lxml. So, we will parse
    # it with BeautifulSoup library
    soup = BeautifulSoup(decoded_data , "lxml")
    body = str(soup.body())
    body = body.replace("'","`") # this is to prevent ' escaping the print command
    # Printing the subject, sender's email and message

    subject_str = "Subject: " + str(subject) + "\n"
    sender_str  = "From: "    + str(sender).split('<')[0] + "\n"
    body_str    = "Message: " + str(body) + "\n\n"

    print(subject_str)
    toPrint += subject_str
    print(sender_str)
    toPrint += sender_str
    print(body_str)
    toPrint += body_str

    return toPrint

def import_whitelist():
    with open('sender_whitelist.json', 'r') as file:
        data = json.load(file)
    return data["senders"]

def main():
    """
    Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    fax = ""

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
        # json empty
        return 0

    print(splash)
    print("Checking for faxing at: ", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    for wSender in senderWhitelist:
        result = service.users().messages().list(userId="me",labelIds=['INBOX'], q="is:unread from:"+wSender).execute()
        messages = result.get('messages')

        if messages is None or len(messages) == 0:
            # no unread messages
            continue

        for msg in messages:
            # Get the message from its id
            txt = service.users().messages().get(userId='me', id=msg['id'],).execute()

            try:
                # convert to fax
                fax += print_message(txt, fax)

                # mark printed emails as read
                service.users().messages().modify(userId="me", id=msg['id'], body={ 'removeLabelIds': ['UNREAD']}).execute()

            except Exception as e:
                print("Error", e)
                pass

    if len(fax) > 0:
        print("Faxes found!")
        for line in splash.split('\n'):
            actually_print(line.replace("'","`")                   , 10, 10, False)
        actually_print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 3 , 3 , False)
        actually_print(fax                                         , 3 , 3 , True )
        print("Done faxing.")
    else:
        print("No faxes at this time.")

if __name__ == "__main__":
    main()
