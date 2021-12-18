import requests, json, datetime, traceback

#Const
url = "https://api.ambeedata.com/latest/by-postal-code"
querystring = {"postalCode":"1162","countryCode":"HU"}
headers = {'x-api-key': "FlPffZbCYA3v6I7069W773pC8YAEwAAi988eJBUa",'Content-type': "application/json"}
aq_file = "/var/www/html/aq.html"

try:
   response = requests.request("GET", url, headers=headers, params=querystring)
   d = json.loads(response.text)
   aqi = d.get("stations")[0].get("AQI")
   timestamp = d.get("stations")[0].get('updatedAt')
   delta = datetime.datetime.now() - datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
   passedhours = delta.days * 24 + int(delta.seconds / 3600)
   output = str(aqi) + "(" + str(passedhours) + ")"
   
except:
   output = "ERROR"

with open(aq_file, "w") as f:
   f.write(output)
