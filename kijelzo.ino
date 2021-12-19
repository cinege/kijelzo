// library from https://github.com/finitespace/BME280
// D2-SDA // D1-SCL  3v-vcc gnd-gnd
// library found https://robojax.com/learn/arduino/?vid=robojax-LCD2004-I2C
// library from https://github.com/fdebrabander/Arduino-LiquidCrystal-I2C-library
// TESTED ON WEMOS D1 R1 mini SDA-D2 SCL-D1


#include <BME280I2C.h>
#include <Wire.h>
#include <ESP8266WiFi.h> 
#include <LiquidCrystal_I2C.h>

const char* ssid = "bekey-wifi"; //replace with your own wifi ssid 
const char* password = "Gtmy5q4h"; //replace with your own //wifi ssid password 
const char* host = "192.168.100.7";


BME280I2C bme;    // Default : forced mode, standby time = 1000 ms
                  // Oversampling = pressure ×1, temperature ×1, humidity ×1, filter off,
LiquidCrystal_I2C lcd(0x27,20,4); 

void setup() {
  lcd.begin();
  lcd.backlight();
  Serial.begin(9600);
  while(!Serial) {} // Wait
  Wire.begin();

  while(!bme.begin())
  {
    Serial.println("Could not find BME280 sensor!");
    delay(1000);
  } 
  delay(10); // We start by connecting to a WiFi network Serial.println();
  Serial.println(); 
  Serial.print("Connecting to ");
  Serial.println(ssid);
  /* Explicitly set the ESP8266 to be a WiFi-client, otherwise, it by default, would try to act as both a client and an access-point and could cause network-issues with your other WiFi-devices on your WiFi-network. */
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    lcd.setCursor(0,0);
    lcd.print("Kapcsolodas..."); 
  }
  Serial.println("");
  Serial.println("WiFi connected"); Serial.println("IP address: "); 
  Serial.println(WiFi.localIP()); 
  lcd.setCursor(0,0);
  lcd.print("A Wifi kapcsolat"); 
  lcd.setCursor(0,1);
  lcd.print("letrejott");
} 
int value = 0; 


void loop() { 
  delay(10000); 
  ++value;
  Serial.print("connecting to ");
  Serial.println(host); // Use WiFiClient class to create TCP connections
  WiFiClient client;
  const int httpPort = 8081;
  if (!client.connect(host, httpPort)) {
    Serial.println("connection failed");
    return;
  }
  // We now create a URI for the request
  //this url contains the informtation we want to send to the server
  //if esp8266 only requests the website, the url is empty
  String url = "/message.html";

  Serial.println(url); // This will send the request to the server
  client.print(String("GET ") + url + " HTTP/1.1\r\n" + "Host: " + host + "\r\n" + "Connection: close\r\n\r\n");
  unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > 5000){ 
      Serial.println(">>> Client Timeout !");
      client.stop(); return; 
    } 
  } // Read all the lines of the reply from server and print them to Serial
  String line;
  while (client.available()) {
    line = client.readStringUntil('\r');
  }
  
  float temp(NAN), hum(NAN), pres(NAN);
  BME280::TempUnit tempUnit(BME280::TempUnit_Celsius);
  BME280::PresUnit presUnit(BME280::PresUnit_Pa);
  bme.read(pres, temp, hum, tempUnit, presUnit);
  
  String inf = line;
  String inf0 = getValue(inf,',',0);
  String inf1 = getValue(inf,',',1);
  String inf2 = getValue(inf,',',2);
  String inf3 = getValue(inf,',',3);
  String inf4 = getValue(inf,',',4);
  String inf5 = getValue(inf,',',5);
  String tempstr = String(round(temp*10)/10);
  String strr = tempstr.substring(0, tempstr.length() - 1);
  String inf6 = strr + "C";
  
  inf0.trim();
  inf1.trim();
  inf2.trim();
  inf3.trim();
  inf4.trim();
  inf5.trim();

  String  message0 = inf0;
  String  message1 = inf1 + ' ' + inf2;
  String  message2 = inf6 + ' ' + inf3;
  String  message3 = inf4 + ' ' + inf5;
  
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(message0);
  lcd.setCursor(0,1);
  lcd.print(message1);
  lcd.setCursor(0,2);
  lcd.print(message2);
  lcd.setCursor(0,3);
  lcd.print(message3);
  
  Serial.println(message0);
  Serial.println(message1);
  Serial.println(message2);
  Serial.println(message3);
  Serial.println();
 }

String getValue(String data, char separator, int index) {
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}
