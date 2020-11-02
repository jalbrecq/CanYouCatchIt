# Run the file to download the STIB's GTFS file
# importing requests
import requests
from config import access_token

# The STIB API url
url = "https://opendata-api.stib-mivb.be/Files/2.0/Gtfs"

# Payload
payload = {}

# Headers
# You need to secure this token be carefull it's fragile
headers = {
  'Authorization': 'Bearer ' + access_token,
  'Cookie': 'f5avraaaaaaaaaaaaaaaa_session_=BPOOJGFBBJPIMMAHACNEOHEANDKJHMGACDPAKLHDECJOMBLIPLEKJFMNNCGBDCGOEGADNNHONIMMGNBKHNJAJPHGPLIOINDLKKFFFMIKOCILDDJKBAILGEIDGPFKBMIL; TS010ea478=0136df15ed0d91af286203f1c7d86d59410783d4ae9eb3b4bc8d95aae5824d3137de240009aeb4e805f3e4f462ed99601f93313f0278a8e96410eace08261ced15935c38f2'
}

# Start speaking with the STIB API
response = requests.request("GET", url, headers=headers, data = payload)

with open('sandbox/data/gtfs.zip', 'wb') as f:
  f.write(response.content)
