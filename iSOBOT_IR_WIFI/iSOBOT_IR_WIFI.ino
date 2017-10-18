#include <ESP8266WiFi.h>

//-------------------info about bits-------------------------------
#define totallength 22 //number of highs/bits 4 channel+18 command
#define channelstart 0
#define commandstart 4 //bit where command starts
#define channellength 4
#define commandlength 18
//---------determined empirically--------------
#define headerlower 2300 //lower limit
#define headernom 2550 //nominal
#define headerupper 2800 //upper limit
#define zerolower 300
#define zeronom 500 //380 //nominal
#define zeroupper 650
#define onelower 800
#define onenom 1000//850 //nominal
#define oneupper 1100
#define highnom 630
//---------------------pin assignments--------------
//#define TXpin 7
#define TXpin 5
//----------------------variables----------------------
#define countin 1048576
boolean bit2[totallength];
unsigned long buttonnum;
unsigned long x = 0;
unsigned long count = countin;
unsigned long buf = 0;

const char WiFiAPPSK[] = "psuisobot";

WiFiServer server(80);
WiFiClient client;

String httpResponseStatus = "HTTP/1.1 ";

void setup() {
  Serial.begin(38400);
  pinMode(TXpin, OUTPUT);

  setupWiFi();
  server.begin();
}

void loop() {

  // Check if client is connected
  client = server.available();
  if (!client) {
    return;
  }

  // Read the first line of the request
  String req = client.readStringUntil('\r');
  client.flush();

  String cmd = req.substring(10, req.length()-8);
  if (req.indexOf("/cmd:") != -1) {
    httpResponse(200, "OK");
    
    
    char charBuf[7];
    cmd.toCharArray(charBuf, 7);
    
    Serial.print("cmd: ");
    Serial.println(cmd);
    Serial.print("charBuf: ");
    Serial.println(charBuf);
    Serial.print("charBufToHex: ");
    Serial.println(StrToHex(charBuf));
    
    buttonwrite(TXpin, StrToHex(charBuf));
  } else {
    httpResponse(400, "Bad Request");
  }
}

void httpResponse(int stat, String reason) {
  client.print("HTTP/1.1 ");
  client.print(stat);
  client.print(" " + reason + "\r\n");
}

int StrToHex(char str[]) {
  return (int) strtol(str, 0, 16);
}

int SerialReadHexDigit(char digit){
  byte c = (byte) digit;
  if (c >= '0' && c <= '9') {
    return c - '0';
  } else if (c >= 'a' && c <= 'f') {
    return c - 'a' + 10;
  } else if (c >= 'A' && c <= 'F') {
    return c - 'A' + 10;
  } else {
    return -1; // non-hexadecimal digit
  }
}

void ItoB(unsigned long integer, int length) {
  //needs bit2[length]
  Serial.println("ItoB");
  for (int i=0; i<length; i++){
    if ((integer / power2(length-1-i)) == 1){
      integer -= power2(length-1-i);
      bit2[i] = 1;
    }
    else {
      bit2[i] = 0;
    }
    Serial.print(bit2[i]);
  }
  Serial.println();
}

unsigned long power2(int power) { //gives 2 to the (power)
  unsigned long integer=1; //apparently both bitshifting and pow functions had problems
  for (int i=0; i<power; i++){ //so I made my own
    integer*=2;
  }
  return integer;
}

void buttonwrite(int txpin, unsigned long integer) {
  //must be full integer (channel + command)
  ItoB(integer, 22); //must have bit2[22] to hold values
  oscWrite(txpin, headernom);
  for(int i=0;i<totallength;i++){
    if (bit2[i]==0) delayMicroseconds(zeronom);
    else delayMicroseconds(onenom);
    oscWrite(txpin, highnom);
  }
  delay(205);
}

void oscWrite(int pin, int time) { //writes at approx 38khz
  for(int i = 0; i < (time / 26) - 1; i++) {
    //prescaler at 26 for 16mhz, 52 at 8mhz, ? for 20mhz
    digitalWrite(pin, HIGH);
    delayMicroseconds(10);
    digitalWrite(pin, LOW);
    delayMicroseconds(10);
  }
}

void setupWiFi()
{
  WiFi.mode(WIFI_AP);

  // Do a little work to get a unique-ish name. Append the
  // last two bytes of the MAC (HEX'd) to "Thing-":
  uint8_t mac[WL_MAC_ADDR_LENGTH];
  WiFi.softAPmacAddress(mac);
  String macID = String(mac[WL_MAC_ADDR_LENGTH - 2], HEX) +
                 String(mac[WL_MAC_ADDR_LENGTH - 1], HEX);
  macID.toUpperCase();
  String AP_NameString = "ESP8266 ISOBOT " + macID;

  char AP_NameChar[AP_NameString.length() + 1];
  memset(AP_NameChar, 0, AP_NameString.length() + 1);

  for (int i=0; i<AP_NameString.length(); i++)
    AP_NameChar[i] = AP_NameString.charAt(i);

  WiFi.softAP(AP_NameChar, WiFiAPPSK);
}

