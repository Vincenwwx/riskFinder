#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <TFT_eSPI.h>           // Graphics and font library
#include <SPI.h>
#include <Encoder.h>            // Library used for rotary encoder

#include <ESPmDNS.h>
#include <WiFiUdp.h>
#include <ArduinoOTA.h>

#define NORMAL_SPEED
#define USE_DMA                 // ESP32 ~1.25x single frame rendering performance boost for badgers.h
                                // Note: Do not use SPI DMA if reading GIF images from SPI SD card on same bus as TFT
#include <AnimatedGIF.h>        // Library used to display animated gif
#include "robot.h"
#include "conveyorBelt.h"
#include "warehouse.h"


#define DEBUG_MODE
//#define CIRCLE_LEVEL

#define BATTERY_VOLTAGE
//#define BATTERY_PERCENTAGE

const uint8_t LEVEL_UPPER_LIMIT = 3;
const uint8_t LEVEL_LOWER_LIMIT = 1;
const uint8_t WIFI_CONNECTION_TIMEOUT = 50;

// -----------------------------------------------
// PLU Info
// -----------------------------------------------
uint8_t id = 5;
char role[20] = "undefined";
/** 
 *  States of the PLU:
 *    0: Ready
 *    1: Simulating/working
 *    2: configuring
**/
uint8_t state = 0;
uint8_t level = LEVEL_LOWER_LIMIT;
float battery_voltage = .0;
uint8_t battery_percentage = 100;

const int MAX_ANALOG_VAL = 4095;
const float MAX_BATTERY_VOLTAGE = 4.2; // Max LiPoly voltage of a 3.7 battery is 4.2

void update_battery_percentage() {
  float rawValue = analogRead(A13);
  battery_voltage = rawValue / MAX_ANALOG_VAL * 2 * 1.1 * 3.3 / MAX_BATTERY_VOLTAGE;
  battery_percentage = (int)(battery_voltage * 100);
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
const uint8_t LEVEL_X_COORDINATE = 160;
const uint8_t LEVEL_Y_COORDINATE = 15;

const uint8_t BATTERY_X_COORDINATE = 210;
const uint8_t BATTERY_Y_COORDINATE = 10;

TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h
AnimatedGIF gif;

const uint16_t iconSize = 230;
uint8_t const *roleFile = NULL;
size_t sizeOfFile = 0;

void draw_battery(uint8_t level) {
  // Clear the display by drawing a black rectangle
  tft.fillRect(BATTERY_X_COORDINATE, BATTERY_Y_COORDINATE, 
               30, 25, TFT_BLACK);
  // Change the color according to the input battery level
  int color = (level == 1) ? TFT_RED : 
              (level == 2) ? TFT_YELLOW : TFT_GREEN;
  tft.drawRect(BATTERY_X_COORDINATE, BATTERY_Y_COORDINATE, 
               20, 15, TFT_WHITE);
  tft.fillRect(BATTERY_X_COORDINATE+20, BATTERY_Y_COORDINATE+3, 
               3, 9, TFT_WHITE);
  for (int i = 0; i < level; i++) {
    tft.fillRect(BATTERY_X_COORDINATE+2+(4+2)*i, BATTERY_Y_COORDINATE+3, 
                 4, 9, color);
  }
}

void draw_level() {
  // Clear the previous level
  tft.fillRect(LEVEL_X_COORDINATE, LEVEL_Y_COORDINATE, 15, 30, TFT_BLACK);
  // Draw the latest level
  //tft.setCursor(185, 25);
  tft.setCursor(LEVEL_X_COORDINATE, LEVEL_Y_COORDINATE);
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

void render_new_display() {
  tft.fillScreen(TFT_BLACK);

  if (state == 0 || state == 1) {
    tft.setCursor(0, 0, 2);
    tft.setTextColor(TFT_WHITE);  tft.setTextSize(1);
    // Display battery
    update_battery_percentage();
    uint8_t lvl = (battery_percentage < 30) ? 1 : (battery_percentage < 60) ? 2 : 3;
    draw_battery(lvl);
  
    // Display ID
    char displayBuffer[30] = "";
    sprintf(displayBuffer, "ID    : %d", id);
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
    tft.drawCircle(LEVEL_X_COORDINATE+6, LEVEL_Y_COORDINATE+16, 22, TFT_WHITE);
    draw_level();
  
    // Display IP
#ifdef DEBUG_MODE
    tft.setTextSize(1);
    tft.print("IP: ");
    tft.println(WiFi.localIP());
    tft.print("Bat. lel: ");
    tft.print(battery_percentage);
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

  else if (state == 2) {
    tft.setCursor(1, 1, 2);
    tft.setTextColor(TFT_YELLOW); tft.setTextFont(8);
    Serial.println(id);
    tft.print(id);
  }
}

// -----------------------------------------------
// WIFI
// -----------------------------------------------
const char* ssid     = "riskFinder";
const char* password = "iasSI422";

void connect_to_WiFi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  uint8_t timeout_counter = 0;
  
  while (WiFi.status() != WL_CONNECTED) {    
    delay(200);
    Serial.print("Connection Failed! Rebooting...");
    timeout_counter++;
    if (timeout_counter >= WIFI_CONNECTION_TIMEOUT) {
      ESP.restart();
    }
  }
 
  Serial.print("Connected. IP: ");
  Serial.println(WiFi.localIP());
}

// -----------------------------------------------
// Web Server
// -----------------------------------------------
WebServer server(80); // on port 80
StaticJsonDocument<250> jsonDocument; // buffer for storing JSON data
char buffer[250];

void pack_data(int id, char *role, int battery_percentage, int simulation_level) {  
  jsonDocument.clear();  
  jsonDocument["id"] = id;
  jsonDocument["role"] = role;
  jsonDocument["batLev"] = battery_percentage;
  jsonDocument["simLev"] = simulation_level;
  serializeJson(jsonDocument, buffer);
}

void handle_info_GET() {
  update_battery_percentage();
  
  //Serial.println("Get info");
  pack_data(id, role, battery_percentage, level);
  server.send(200, "application/json", buffer);
}

void handle_config_POST() {
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
  
  render_new_display();
  // Respond to the client
  server.send(200, "text/plain", "success");
}

// setup API resources
void setup_routing() {
  server.on("/info", handle_info_GET);
  server.on("/config", HTTP_POST, handle_config_POST);
 
  // start server
  server.begin();
}

// -----------------------------------------------
// OTA function
// -----------------------------------------------
void setup_OTA() {
  ArduinoOTA
    .onStart([]() {
      String type;
      if (ArduinoOTA.getCommand() == U_FLASH)
        type = "sketch";
      else // U_SPIFFS
        type = "filesystem";
    })
    .onError([](ota_error_t error) {
      Serial.printf("Error[%u]: ", error);
      if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
      else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
      else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
      else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
      else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });

  ArduinoOTA.begin();
}

// -----------------------------------------------
// Setup
// -----------------------------------------------
void setup(void) {
  Serial.begin(9600);

  init_display();
  connect_to_WiFi();
  setup_OTA();
  setup_routing();
  render_new_display();

  pinMode(PRESS_BUTTON, INPUT_PULLUP);
  
  delay(500);
}

// -----------------------------------------------
// Loop
// -----------------------------------------------
void loop(void) {
  /** 
   *  Handle HTTP request
  **/
  server.handleClient();

  /** 
   *  Get rotary encode value
   */
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
  if (state != 2) draw_level();
  
  /** 
   *  Draw role figure
   */
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

  ArduinoOTA.handle();
}
