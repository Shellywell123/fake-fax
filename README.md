# fake fax

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
Silly idea to print incoming emails on a recept printe because why not.

# Setup

- enable gmail api
- create google creds json named `token.json`
- pip install requirements
- install cups
```
		sudo apt install cups
```
- [Install Drivers](https://cosroe.com/2024/05/star-tsp-100.html)
- set gmail sender whitlist
```
echo '{"senders": "some@email.com"]}' > readWhitelist.json
```

# running

manually
```
sh fax.sh
```
or setup a cron
