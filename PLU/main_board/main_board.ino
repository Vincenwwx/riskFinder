#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <TFT_eSPI.h>           // Graphics and font library
#include <SPI.h>
#include <Encoder.h>            // Library used for rotary encoder

#define NORMAL_SPEED
#define USE_DMA                 // ESP32 ~1.25x single frame rendering performance boost for badgers.h
                                // Note: Do not use SPI DMA if reading GIF images from SPI SD card on same bus as TFT
#include <AnimatedGIF.h>        // Library used to display animated gif
#include "robot.h"
#include "conveyorBelt.h"
#include "warehouse.h"

#define HOME
//#define RASP

#define DEBUG_MODE
//#define CIRCLE_LEVEL

const uint8_t LEVEL_UPPER_LIMIT = 3;
const uint8_t LEVEL_LOWER_LIMIT = 1;

// -----------------------------------------------
// PLU Info
// -----------------------------------------------
uint8_t id = 1;
char role[20] = "undefined";
// States of the node
//  0: Ready
//  1: Simulating/working
uint8_t state = 0;
uint8_t level = LEVEL_LOWER_LIMIT;
uint8_t battery_level = 100;

const int MAX_ANALOG_VAL = 4095;
const float MAX_BATTERY_VOLTAGE = 4.2; // Max LiPoly voltage of a 3.7 battery is 4.2

void update_battery_level() {
  float rawValue = analogRead(A13);
  battery_level = (int)(rawValue / MAX_ANALOG_VAL * 2 * 1.1 * 3.3 / MAX_BATTERY_VOLTAGE * 100);
}


// -----------------------------------------------
// Rotary Encoder
// -----------------------------------------------
const uint8_t BUTTON_A = 33;
const uint8_t BUTTON_B = 15;
const uint8_t PRESS_BUTTON = 14;

Encoder rotary_encoder(BUTTON_A, BUTTON_B);
long pos = -999;

void update_level(uint8_t &level, int num) {
#ifdef CIRCLE_LEVEL
  if (level == LEVEL_LOWER_LIMIT && num == -1)
    level = LEVEL_UPPER_LIMIT;
  else if (level == LEVEL_UPPER_LIMIT && num == 1) {
    level = LEVEL_LOWER_LIMIT;
  }
#else
  if ((level == LEVEL_LOWER_LIMIT && num == -1) ||
      (level == LEVEL_UPPER_LIMIT && num == 1))
  { 
    // do nothing 
  }
#endif
  else 
    level += num;
}

// -----------------------------------------------
// Display
// -----------------------------------------------
// Change the position of the elements here
const uint8_t level_x_coordinate = 160;
const uint8_t level_y_coordinate = 15;

const uint8_t battery_x_coordinate = 210;
const uint8_t battery_y_coordinate = 10;

TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h
AnimatedGIF gif;

const uint16_t iconSize = 230;
uint8_t const *roleFile = NULL;
size_t sizeOfFile = 0;

void draw_battery(uint8_t level) {
  //assert(level < 3);
  tft.fillRect(battery_x_coordinate, battery_y_coordinate, 30, 25, TFT_BLACK);

  int color;
  if (level == 1) color = TFT_RED;
  else if (level == 2) color = TFT_YELLOW;
  else color = TFT_GREEN;
  tft.drawRect(battery_x_coordinate, battery_y_coordinate, 20, 15, TFT_WHITE);
  tft.fillRect(battery_x_coordinate+20, battery_y_coordinate+3, 3, 9, TFT_WHITE);
  for (int i = 0; i < level; i++) {
    tft.fillRect(battery_x_coordinate+2+(4+2)*i, battery_y_coordinate+3, 4, 9, color);
  }
}

void draw_level() {
  // Clear the previous level
  tft.fillRect(level_x_coordinate, level_y_coordinate, 15, 30, TFT_BLACK);
  // Draw the latest level
  //tft.setCursor(185, 25);
  tft.setCursor(level_x_coordinate, level_y_coordinate);
  tft.setTextSize(2);
  tft.println(level);
}

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
  //  or stay on the line if there is room for the text with tft.print)
  tft.setCursor(0, 0, 2);
  // Set the font colour to be white with a black background, set text size multiplier to 1
  tft.setTextColor(TFT_WHITE);  tft.setTextSize(1);
  // We can now plot text on screen using the "print" class
  tft.println("System init...");
}

void renderNewDisplay() {
  tft.fillScreen(TFT_BLACK);
  tft.setCursor(0, 0, 2);
  tft.setTextSize(1);

  // Display battery
  update_battery_level();
  uint8_t lvl = (battery_level < 30) ? 1 : (battery_level < 60) ? 2 : 3;
  draw_battery(lvl);

  // Display ID
  char displayBuffer[30] = "";
  sprintf(displayBuffer, "ID   : %d", id);
  tft.println(displayBuffer);
  
  // Display role
  sprintf(displayBuffer, "ROLE : %s", role);
  tft.println(displayBuffer);

  // Display simulation state
  char s[11] = "";
  if (state == 0) {
    strcpy(s, "ready");
  } else {
    strcpy(s, "simulating");
  }
  sprintf(displayBuffer, "STATE: %s", s);
  tft.println(displayBuffer);

  // Display simulation parameter
  tft.drawCircle(level_x_coordinate+6, level_y_coordinate+16, 22, TFT_WHITE);
  draw_level();

  // Display IP
#ifdef DEBUG_MODE
  tft.setTextSize(1);
  tft.print("IP: ");
  tft.println(WiFi.localIP());
  tft.print("Bat. lel: ");
  tft.print(battery_level);
  tft.println("%");
#endif
  
  if (strcmp(role, "robot") == 0) {
    roleFile = robot;
    sizeOfFile = sizeof(robot);
  } else if (strcmp(role, "conveyor belt") == 0) {
    roleFile = conveyorBelt;
    sizeOfFile = sizeof(conveyorBelt);
  } else if (strcmp(role, "warehouse") == 0) {
    roleFile = warehouse;
    sizeOfFile = sizeof(warehouse);
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
  jsonDocument["batLev"] = battery_level;
  serializeJson(jsonDocument, buffer);
}

void getInfo() {
  update_battery_level();
  
  Serial.println("Get info");
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
  if (jsonDocument.containsKey("role")) {
    if (strcmp(jsonDocument["role"], role) != 0) {
      strcpy(role, jsonDocument["role"]);
    }
  }
  // state updates
  if (jsonDocument.containsKey("state")) {
    state = jsonDocument["state"];
  }

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

  pinMode(PRESS_BUTTON, INPUT_PULLUP);
  
  delay(1000);
}

// -----------------------------------------------
// Loop
// -----------------------------------------------
void loop(void) {
  // handle HTTP request
  server.handleClient();

  // Get rotary encode value
  long pos = rotary_encoder.read();
  delay(70);
  if (pos < 8) {
    level = 1;
  }
  else if (pos < 20) {
    //Serial.println(newPos);
    level = 2;
  } else {
    level = 3;
  }
  draw_level();
  
  // Draw role figure
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

  if(digitalRead(PRESS_BUTTON) == LOW) { // If the button of rotary encode is pressed
    rotary_encoder.write(0);             // set the current position as default
  }
  //delay(43);
}
