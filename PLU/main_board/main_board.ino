  #include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <TFT_eSPI.h> // Graphics and font library for ST7735 driver chip
#include <SPI.h>

#define NORMAL_SPEED
#define USE_DMA       // ESP32 ~1.25x single frame rendering performance boost for badgers.h
                        // Note: Do not use SPI DMA if reading GIF images from SPI SD card on same bus as TFT
// Load GIF library
#include <AnimatedGIF.h>
AnimatedGIF gif;

#include "robot.h"
#include "conveyorBelt.h"

#define HOME
//#define RASP
//#define DEBUG_MODE

// -----------------------------------------------
// PLU Info
// -----------------------------------------------
char role[20] = "undefined";
uint8_t id = 1;
// States of the node
//  0: Ready
//  1: Simulating/working
uint8_t state = 0;
uint8_t battery_level = 100;

// -----------------------------------------------
// Display
// -----------------------------------------------
TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h
const uint16_t iconSize = 230;
uint8_t const *roleFile = NULL;
size_t sizeOfFile = 0;

void init_display() {
  tft.init();
#ifdef USE_DMA
  tft.initDMA();
#endif
  tft.setRotation(0);
  // Fill screen with grey so we can see the effect of printing with and without 
  // a background colour defined
  tft.fillScreen(TFT_BLACK);
  // Swap the colour byte order when rendering
  //tft.setSwapBytes(true);
  gif.begin(BIG_ENDIAN_PIXELS);
  
  // Set "cursor" at top left corner of display (0,0) and select font 2
  // (cursor will move to next line automatically during printing with 'tft.println'
  //  or stay on the line is there is room for the text with tft.print)
  tft.setCursor(0, 0, 2);
  // Set the font colour to be white with a black background, set text size multiplier to 1
  tft.setTextColor(TFT_WHITE);  tft.setTextSize(1);
  // We can now plot text on screen using the "print" class
  tft.println("System init...");
}

void renderNewDisplay() {
  tft.fillScreen(TFT_BLACK);
  tft.setCursor(0, 0, 2);

  // Display ID
  char displayBuffer[30] = "";
  sprintf(displayBuffer, "ID   : %d", id);
  tft.println(displayBuffer);
  
  // Display role
  sprintf(displayBuffer, "ROLE : %s", role);
  tft.println(displayBuffer);

  // Display state
  char s[11] = "";
  if (state == 0) {
    strcpy(s, "ready");
  } else {
    strcpy(s, "simulating");
  }
  sprintf(displayBuffer, "STATE: %s", s);
  tft.println(displayBuffer);

  // Display IP
#ifdef DEBUG_MODE
  tft.print("IP: ");
  tft.println(WiFi.localIP());
#endif
  
  if (strcmp(role, "robot") == 0) {
    roleFile = robot;
    sizeOfFile = sizeof(robot);
  } else if (strcmp(role, "conveyor belt") == 0) {
    roleFile = conveyorBelt;
    sizeOfFile = sizeof(conveyorBelt);
  }
}

// -----------------------------------------------
// WIFI
// -----------------------------------------------
#ifdef RASP
const char* ssid     = "vincen_MA";
const char* password = "wwxwwx183";
#endif
#ifdef HOME
const char* ssid     = "Google Cloud";
const char* password = "wwxwwx183";
#endif

void connectToWiFi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
    // we can even make the ESP32 to sleep
  }
 
  Serial.print("Connected. IP: ");
  Serial.println(WiFi.localIP());
}

// -----------------------------------------------
// Web Server
// -----------------------------------------------
// Web server running on port 80
WebServer server(80);
// JSON data buffer
StaticJsonDocument<250> jsonDocument;
char buffer[250];

void create_json(int id, char *role, int battery_level) {  
  jsonDocument.clear();  
  jsonDocument["id"] = id;
  jsonDocument["role"] = role;
  jsonDocument["batLel"] = battery_level;
  serializeJson(jsonDocument, buffer);
}

void getInfo() {
  Serial.println("Get role");
  create_json(id, role, battery_level);
  server.send(200, "application/json", buffer);
}

void handlePost() {
  if (server.hasArg("plain") == false) {}
    //handle error here
  
  String body = server.arg("plain");
  DeserializationError error = deserializeJson(jsonDocument, body);
  // Test if parsing succeeds.
  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    //server.send(404, "text/plain", "Error, unknown role...");
    return;
  }
  // role updates
  if (strcmp(jsonDocument["role"], role) != 0) {
    strcpy(role, jsonDocument["role"]);
  }
  // state updates
  state = jsonDocument["state"];

  renderNewDisplay();
  // Respond to the client
  server.send(200, "text/plain", "success");
}

// setup API resources
void setup_routing() {
  server.on("/info", getInfo);
  server.on("/config", HTTP_POST, handlePost);
 
  // start server
  server.begin();
}

// -----------------------------------------------
// Setup
// -----------------------------------------------
void setup(void) {
  Serial.begin(9600);

  init_display();
  connectToWiFi();
  setup_routing();
  renderNewDisplay();
  
  delay(1000);
}

// -----------------------------------------------
// Loop
// -----------------------------------------------
void loop(void) {
  server.handleClient();
  if(roleFile != NULL) {
#ifdef DEBUG_MODE
    Serial.print("Not null");
#endif
    if (gif.open((uint8_t *)roleFile, sizeOfFile, GIFDraw)) {
#ifdef DEBUG_MODE
      Serial.print("read file");
#endif
      tft.startWrite(); // For DMA the TFT chip slect is locked low
      while (gif.playFrame(false, NULL))
      {
        if (state==0) break;  // not simulating then only play the first frame
        // Each loop renders one frame
        yield();
      }
      gif.close();
      tft.endWrite(); // Release TFT chip select for other SPI devices
    }
  }

  //delay(43);
}
