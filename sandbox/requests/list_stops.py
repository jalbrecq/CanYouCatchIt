# importing requests
import requests
from config import access_token

# The STIB API url
url = "https://opendata-api.stib-mivb.be/NetworkDescription/1.0/PointByLine/2"

# Payload
payload = {}

# Headers
headers = {
  'Authorization': 'Bearer ' + access_token,
  'Cookie': 'f5avraaaaaaaaaaaaaaaa_session_=OEEDFHADHAIPEDCPACGJLMHJJHFCELBIFFONKBJEDPDLCCOBLCPONHDHNEIJOKPPCGMDMAGEOMALHLHIHJAAAPLKCGFPGILCLCEFENJHMMCPOAADADGOKJFHONBMHBKE; TS010ea478=0136df15ed8891ae979df14d59421064adc5f7e78b2404e3b7caf5821294aa2c57d1d2895669a6cd21601587f50dccb5d83071c806cc8031eb583a663cc797365ea3a8aa2b'
}

# Start speaking with the STIB API
response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
