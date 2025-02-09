# Fake-Fax

```
MM""""""""`M          dP                         MM""""""""`M                   
MM  mmmmmmmM          88                         MM  mmmmmmmM                   
M'      MMMM .d8888b. 88  .dP  .d8888b.          M'      MMMM .d8888b. dP.  .dP 
MM  MMMMMMMM 88'  `88 88888"   88ooood8 88888888 MM  MMMMMMMM 88'  `88  `8bd8'  
MM  MMMMMMMM 88.  .88 88  `8b. 88.  ...          MM  MMMMMMMM 88.  .88  .d88b.  
MM  MMMMMMMM `88888P8 dP   `YP `88888P'          MM  MMMMMMMM `88888P8 dP'  `dP 
MMMMMMMMMMMM                                     MMMMMMMMMMMM           
```
![](./fake-fax.png)

A silly idea to print incoming emails on a receipt printer to mimic a fax because why not.\
Using the gmail api we can check unread emails from specific senders and then print those.

# Setup

1. [configure gmail api](https://developers.google.com/gmail/api/quickstart/python) and create google creds json named `credentials.json`
2. pip install requirements
3. install cups
```
sudo apt install cups
```
5. Install Drivers for your printer ([Drivers or Mine](https://cosroe.com/2024/05/star-tsp-100.html))
6. Set gmail sender whitelist (who's unread emails to print)
```
echo '{"senders": ["some@email.com"]}' > sender_whitelist.json
```

# Running

Manually:
```
python3 fake-fax.py
```
or setup a cron
