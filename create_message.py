import datetime, time
import requests, json

#const
busURL = "http://futar.bkk.hu/api/query/v1/ws/otp/api/where/arrivals-and-departures-for-stop.json?stopId=BKK_F03299&minutesBefore=1&minutesAfter=240"
message_file = "/var/www/html/message.html"
timetable_file = "/var/www/html/timetable.html"
aq_file = "/var/www/html/aq.html"
weekdays = {0:"Hetfo",1:"Kedd",2:"Szerda",3:"Csut",4:"Pentek",5:"Szombat",6:"Vasarnap"}

#variables
now = datetime.datetime.now()
today_day_string = now.strftime("%Y.%m.%d")
yesterday__day_string = yesterday_day_string = (now - datetime.timedelta(days=1)).strftime("%Y.%m.%d")
weatherfilename_today = "/home/pi/sensors/data/" + today_day_string
weatherfilename_yesterday = "/home/pi/sensors/data/" + yesterday_day_string

mytime = datetime.datetime.now().strftime("%m.%d %H:%M")
now = datetime.datetime.now() + datetime.timedelta(hours = 0)
currenttime = now.hour*3600 + now.minute*60 + now.second

def temp_trend(old, new):
    diff = float(new) - float(old)
    sign = ("", "+") [diff > 0]
    return sign + str(round(diff,1))
      
def pres_trend(old, new):
   diff = float(new) - float(old)
   if diff < -4: 
      return "V"
   elif diff > 4:
      return "^"
   else:
      return "~"

def get_remaining_time(nextbussec, nowsec):
   totalsec = (nextbussec % (3600*24)) - time.timezone #current UTC offset (always negative)
   remainingminutes = (totalsec- nowsec) // 60 + 1
   return remainingminutes

def get_time():
   weekday = weekdays.get(now.weekday())
   return weekday + " " + mytime

def get_hevstr():
   try:
      with open(timetable_file, "r") as f:
         content = f.readlines()
      content = [x.strip() for x in content]
      nexttrains = [i for i in content if int(i)-60  > currenttime]
      nexttrains.append("None")
      if nexttrains[0] != "None":
         remainingminutes = (int(nexttrains[0]) - currenttime) // 60 + 1
      else:
         remainingminutes = "-"
      return "H" + str(remainingminutes) + "p"
   except:
      return "hiba"
      
def get_busstr():
   busminutes = []
   r = requests.get(busURL)
   parsed = json.loads(r.text)
   if not parsed['data']['limitExceeded']:
      for i in range(2):
         for entry in ['predictedDepartureTime', 'departureTime']:
            try:
               time = parsed["data"]["entry"]["stopTimes"][i][entry]
               remainingmin = get_remaining_time(time, currenttime)
               busminutes.append(remainingmin)
            except:
               busminutes.append(-1)
      busstr  = "B" + str(busminutes[0]) + "p(" + str(busminutes[1]) + "-" + str(busminutes[3]) + "p)"
   else:
      busstr = "limitexceeded"
   return busstr
   
def get_weather():
   try:
      today_data = []
      with open(weatherfilename_today, "r") as today_file_handle:
         today_data = today_file_handle.readlines()
   
      time, today_temp, today_pres, tempin, hum = today_data[-1].split(",")
      timeindex = yesterday_day_string + datetime.datetime.now().strftime(" %H:")
      with open(weatherfilename_yesterday, "r") as yesterday_file_handle:
         yesterday_data = yesterday_file_handle.readlines()
   
      indexes = [i for i, j in enumerate(yesterday_data) if timeindex in j]
      time2, yesterday_temp, yesterday_pres, tempin2, hum2 = yesterday_data[indexes[0]].split(",")
      ttrend = "" + temp_trend(yesterday_temp, today_temp) + "" 
      ptrend = pres_trend(yesterday_pres, today_pres)
      return [today_temp + "C (" + ttrend + "C)", ptrend + today_pres + "hPa"]
   except:
      return ["hiba","hiba"]

def get_aq():
   with open(aq_file, "r") as f:
      return "AQ " + f.read()
   

def write_out(timestr, hevstr, busstr, khom, lnyom, aq):
   with open(message_file, "w") as f:
      # Datum ido, HEV (min), 31-es (min), C kint, C bent, hPa, aq 	
      # 04.02 18:18 20p, 5p ,16.8C-8.9  21C ~1009.5, 64(30)
      f.write(timestr + "," + hevstr + "," + busstr + "," + khom + "," + lnyom + "," + aq)

# Script

timestr = get_time()
hevstr = get_hevstr()
busstr = get_busstr()
khom, lnyom = get_weather()
aq = get_aq()

write_out(timestr, hevstr, busstr, khom, lnyom, aq)
