
import datetime, time
import requests, json

def get_departures(URL):
  r = requests.get(URL)
  parsed = json.loads(r.text)
  departures  = []
  #print(parsed)
  for departure in parsed["data"]["entry"]["stopTimes"]:
     #'stopHeadsign': 'Örs vezér tere'
     destination = departure["stopHeadsign"]
     if destination != "Csömör":
        totalseconds = (departure["departureTime"] % (3600*24)) - time.timezone  # - current utc offset in seconds
        departures.append(str(totalseconds)) 
  return departures


#Const

URL = "http://futar.bkk.hu/api/query/v1/ws/otp/api/where/arrivals-and-departures-for-stop.json?stopId=BKK_F03409&minutesBefore=1&minutesAfter=240"
timetable_file = "/var/www/html/timetable.html"

try:
   with open(timetable_file, "r") as f:
      content = f.readlines()
   content = [x.strip() for x in content] 
except:
  content = []


with open(timetable_file, "a") as f:
   for departure in get_departures(URL):
      if (departure not in content):
         f.write(departure + "\n")
