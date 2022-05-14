#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <TFT_eSPI.h> // Graphics and font library for ST7735 driver chip
#include <SPI.h>

const char* ssid     = "Midea 5. Floor";
const char* password = "20#MIDEA#22";

// ----------------- Display -----------------
TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h

void init_display() {
  tft.init();
  tft.setRotation(1);
  // Fill screen with grey so we can see the effect of printing with and without 
  // a background colour defined
  tft.fillScreen(TFT_BLACK);
  
  // Set "cursor" at top left corner of display (0,0) and select font 2
  // (cursor will move to next line automatically during printing with 'tft.println'
  //  or stay on the line is there is room for the text with tft.print)
  tft.setCursor(0, 0, 2);
  // Set the font colour to be white with a black background, set text size multiplier to 1
  tft.setTextColor(TFT_WHITE);  tft.setTextSize(1);
  // We can now plot text on screen using the "print" class
  tft.println("System init...");
}

// JSON data buffer
StaticJsonDocument<250> jsonDocument;
char buffer[250];

// ----------------- Node Info ------------------
char role[20] = "undefined";
int id = 1;

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

// ----------------- Web Server ------------------
// Web server running on port 80
WebServer server(80);

// setup API resources
void setup_routing() {
  server.on("/role", getRole);
  server.on("/config", HTTP_POST, handlePost);
 
  // start server
  server.begin();
}

void getRole() {
  Serial.println("Get role");
  create_json("Role", role, "");
  server.send(200, "application/json", buffer);
}

void handlePost() {
  if (server.hasArg("plain") == false) {
    //handle error here
  }
  String body = server.arg("plain");
  DeserializationError error = deserializeJson(jsonDocument, body);
  // Test if parsing succeeds.
  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    return;
  }

  if (strcmp(jsonDocument["role"], role) != 0) {
    strcpy(role, jsonDocument["role"]);
    renderNewDisplay();
  }

  Serial.print("Role: ");
  Serial.print(role);
  // Respond to the client
  server.send(200, "application/json", "{}");
}

// ----------------- JSON helper ------------------
void create_json(char *tag, char *value, char *unit) {  
  jsonDocument.clear();  
  jsonDocument["type"] = tag;
  jsonDocument["value"] = value;
  jsonDocument["unit"] = unit;
  serializeJson(jsonDocument, buffer);
}


void setup(void) {
  Serial.begin(9600);

  connectToWiFi();
  setup_routing();

  tft.init();
  tft.setRotation(1);
  // Fill screen with grey so we can see the effect of printing with and without 
  // a background colour defined
  tft.fillScreen(TFT_BLACK);
  
  // Set "cursor" at top left corner of display (0,0) and select font 2
  // (cursor will move to next line automatically during printing with 'tft.println'
  //  or stay on the line is there is room for the text with tft.print)
  tft.setCursor(0, 0, 2);
  // Set the font colour to be white with a black background, set text size multiplier to 1
  tft.setTextColor(TFT_WHITE);  tft.setTextSize(1);
  // We can now plot text on screen using the "print" class
  tft.println("System init...");
  
  char idBuffer[9] = "";
  sprintf(idBuffer, "ID: %d", id);
  tft.println(idBuffer);
  delay(1000);
}

void renderNewDisplay() {
  tft.fillScreen(TFT_BLACK);
  tft.setCursor(0, 0, 2);
  
  char idBuffer[9] = "";
  sprintf(idBuffer, "ID: %d", id);
  tft.println(idBuffer);
  
  char roleBuffer[30] = "";
  sprintf(roleBuffer, "Role: %s", role);
  tft.println(roleBuffer);
}

void loop() {

  
  server.handleClient();
}
