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

# TODO print this nicely
splash = '''
MM""""""""`M          dP                         MM""""""""`M
MM  mmmmmmmM          88                         MM  mmmmmmmM
M'      MMMM .d8888b. 88  .dP  .d8888b.          M'      MMMM .d8888b. dP.  .dP
MM  MMMMMMMM 88'  `88 88888"   88ooood8 88888888 MM  MMMMMMMM 88'  `88  `8bd8'
MM  MMMMMMMM 88.  .88 88  `8b. 88.  ...          MM  MMMMMMMM 88.  .88  .d88b.
MM  MMMMMMMM `88888P8 dP   `YP `88888P'          MM  MMMMMMMM `88888P8 dP'  `dP
MMMMMMMMMMMM                                     MMMMMMMMMMMM
'''

with open('sender_whitelist.json', 'r') as file:
    data = json.load(file)

senderWhitelist = data["senders"]

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

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """

    toPrint = ""

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

    if len(senderWhitelist) == 0:
        # json empty
        return 0

    for wSender in senderWhitelist:
        result = service.users().messages().list(userId="me",labelIds=['INBOX'], q="is:unread from:"+wSender).execute()
        messages = result.get('messages')

        if messages is None or len(messages) == 0:
            # no unread messages
            continue

        for msg in messages:
        # Get the message from its id

            txt = service.users().messages().get(userId='me', id=msg['id'],).execute()
            # Use try-except to avoid any Errors
            try:
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

                try:
                    parts = payload.get('parts')[0]
                    data = parts['body']['data']
                except:
                    data = payload['body']['data']

                data = data.replace("-","+").replace("_","/")
                decoded_data = base64.b64decode(data)

                # Now, the data obtained is in lxml. So, we will parse
                # it with BeautifulSoup library
                soup = BeautifulSoup(decoded_data , "lxml")
                body = soup.body()

                # Printing the subject, sender's email and message

                toPrint += "Subject: " + str(subject) + "\n"
                toPrint += "From: " + str(sender).split('<')[0] + "\n"
                toPrint += "Message: " + str(body) + "\n\n"

                # print("Subject: ", subject)
                # print("From: ", sender)
                # print("Message: ", body) #TODO can we reformat?
                # print('\n')

                # mark printed emails as read
                service.users().messages().modify(userId="me", id=msg['id'], body={ 'removeLabelIds': ['UNREAD']}).execute()

            except Exception as e:
                print("Error", e)
                pass

    print(splash)
    print("Checking for faxing at: ", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    if len(toPrint) >0:
        #for line in splash.split('\n'):
        #    actually_print(line,                                    10, 10, False)
        os.system("cat splash.md | lp -o cpi=10 -o lpi=10 -o DocCutType=0NoCutDoc")
        actually_print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),3 , 3 , False)
        actually_print(toPrint                                     ,3 , 3 , True)

        print("Done faxing.")
    else:
        print("No faxes at this time.")

if __name__ == "__main__":
    main()
