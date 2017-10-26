#include <ESP8266WiFi.h>

/*-----iSOBOT command decoding variables-----*/
#define TOTAL_CMD_LENGTH 22 //number of highs/bits 4 channel+18 command
#define CHANNEL_START_BIT 0
#define COMMAND_START_BIT 4 //bit where command starts
#define CHANNEL_LENGTH 4
#define COMMAND_LENGTH 18
#define COMMAND_FORMAT "/cmd:"

/*-----iSOBOT IR TX timing variables-----*/
/*-----determined empirically-----*/
#define TIME_HEADER_MIN 2300 //lower limit
#define TIME_HEADER_NOM 2550 //nominal
#define TIME_HEADER_MAX 2800 //upper limit
#define TIME_ZERO_MIN 300
#define TIME_ZERO_NOM 500 //380 //nominal
#define TIME_ZERO_MAX 650
#define TIME_ONE_MIN 800
#define TIME_ONE_NOM 1000//850 //nominal
#define TIME_ONE_MAX 1100
#define TIME_HIGH_NOM 630

/*-----Pin Assignments-----*/
#define IR_TX_PIN 5

/*-----Other variables-----*/
#define COUNTIN 1048576
boolean bit2[TOTAL_CMD_LENGTH];
unsigned long buttonnum;
unsigned long x = 0;
unsigned long count = COUNTIN;
unsigned long buf = 0;
String httpResponseStatus = "HTTP/1.1 ";

/*-----Wireless Settings-----*/
WiFiServer server(80);
WiFiClient client;

// Wireless network name and password
const char* ssid = "PSU_iSOBOTNET";
const char* password = "psuisobot";

void setup() {
  // open Serial port for monitoring/debug purposes.
  Serial.begin(38400);

  // Configure TX pin as output
  pinMode(IR_TX_PIN, OUTPUT);

  // Set up WiFi and launch server
  setupWiFi();
  server.begin();
}

void loop() {
  // Check if client is connected
  client = server.available();
  if (!client) {
    // No client - skip rest of loop
    return;
  }

  // Client is available - read requests
  // Read the first line of the request
  String req = client.readStringUntil('\r');
  Serial.println("Request: " + req);
  // Flush everything else, we don't need it
  client.flush();
  
  // Check command format is valid
  if (req.indexOf(COMMAND_FORMAT) != -1) {

    // Respond OK
    httpResponse(200, "OK");

    // Extract command from request
    // req will be "POST /cmd:012345%0d" (%0d = \r)
    String cmd = req.substring(10, req.length()-8);
    
    // Convert command into 7-char array
    char charBuf[7];
    cmd.toCharArray(charBuf, 7);

    // Convert char array to hex value and drive IR emitter accordingly
    buttonwrite(IR_TX_PIN, StrToHex(charBuf));
    
  } else {
    // request was not formatted properly
    httpResponse(400, "Bad Request");
  }
}

void httpResponse(int stat, String reason) {
  /*helper function for sending HTTP responses*/
  client.print("HTTP/1.1 ");
  client.print(stat);
  client.print(" " + reason + "\r\n");
}

int StrToHex(char str[]) {
  /*helper function for converting char array to integer*/
  return (int) strtol(str, 0, 16);
}

void ItoB(unsigned long integer, int length) {
  /*Convert integery to binary string*/
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

void buttonwrite(int pin, unsigned long integer) {
  //must be full integer (channel + command)
  ItoB(integer, TOTAL_CMD_LENGTH); //must have bit2[22] to hold values

  // Convert binary array to pulses on IR TX pin
  oscWrite(pin, TIME_HEADER_NOM);
  for(int i=0;i<TOTAL_CMD_LENGTH;i++){
    if (bit2[i]==0) delayMicroseconds(TIME_ZERO_NOM);
    else delayMicroseconds(TIME_ONE_NOM);
    oscWrite(pin, TIME_HIGH_NOM);
  }
  
  // minimum delay between commands
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

void setupWiFi() {
  WiFi.mode(WIFI_AP_STA);
  WiFi.disconnect();
  WiFi.softAP(ssid, password);
}

