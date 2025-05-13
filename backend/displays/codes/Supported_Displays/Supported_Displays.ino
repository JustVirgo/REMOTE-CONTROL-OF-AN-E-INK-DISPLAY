#include <Arduino.h>
#include "Display.h"

#include <WiFiManager.h>
#include <HTTPClient.h>
#include <Preferences.h>

#define uS_TO_S_FACTOR 1000000

String getScreenCommand = "/api/get-screen-picture-bin/";
String getSleepCommand  = "/api/get-sleep/";

Preferences prefs;

WiFiManager wifiManager;
WiFiManagerParameter server_address;
WiFiManagerParameter screen_id;
String addr;
String screenid;

int   sleepTime        = 300;
bool  saveConfigCalled = false;


bool tryUpdateImageData() {
  HTTPClient http;
  String      url = addr + getScreenCommand + screenid +"/"+ DISPLAY_ID;
  Serial.println("URL is:" + url);

  if (!http.begin(url)) {
    Serial.println("DBG HTTP: Failed to initialize HTTP connection");
    return false;
  }

  int httpCode = http.GET();
  if (httpCode != HTTP_CODE_OK) {
    Serial.printf("ERR: HTTP GET failed: %s\n",
                  http.errorToString(httpCode).c_str());
    http.end();
    return false;
  }

  String stream = http.getString();
  http.end();

  // allocate
#ifdef BOARD_HAS_PSRAM
  uint8_t *dataBuffer = (uint8_t *)ps_malloc(stream.length());
#else
  uint8_t *dataBuffer = (uint8_t *)malloc(stream.length());
#endif
  if (!dataBuffer) {
    Serial.println("ERR: Failed to allocate memory");
    return false;
  }

  // copy & display
  for (int i = 0; i < stream.length(); i++) {
    dataBuffer[i] = stream[i];
  }
  printToDisplay(dataBuffer, stream.length());
  free(dataBuffer);

#ifdef GET_DYNAMIC_SLEEP
  HTTPClient sleepHttp;
  if (sleepHttp.begin(addr + getSleepCommand + screenid)) {
    httpCode = sleepHttp.GET();
    if (httpCode == HTTP_CODE_OK) {
      sleepTime = sleepHttp.getString().toInt();
      Serial.printf("Got sleep %d\n", sleepTime);
    }
    sleepHttp.end();
  }
#endif

  return true;
}

// called when user hits “Save” in the portal
void saveCallback() {
  Serial.println("Save was pressed");
  saveConfigCalled = true;
}

void configCallback() {
  String newAddr = String(server_address.getValue());
  String newId = String(screen_id.getValue());
  Serial.println(">>> configCallback: " + newAddr + ", " + newId);

  prefs.begin("config", false);
  prefs.putString("serveraddr", newAddr);
  prefs.putString("screenid", newId);
  prefs.end();

  addr = newAddr;
  screenid = newId;
}

void setup() {
  Serial.begin(115200);
  Serial.println("BEGIN");
  InitDisplay();

  prefs.begin("config", true);
  String savedAddr = prefs.getString("serveraddr", "http://");
  prefs.end();
  Serial.println("Loaded saved serveraddr: " + savedAddr);

  addr = savedAddr;

  new (&server_address)
    WiFiManagerParameter("serveraddr",
                         "Server Address and port",
                         "http://",
                         64,
                         "placeholder=\"enter server URL\"");

  new (&screen_id)
    WiFiManagerParameter("screenid",
                         "Screen ID",
                         "",
                         64,
                         "placeholder=\"enter display ID\"");

  wifiManager.addParameter(&server_address);
  wifiManager.addParameter(&screen_id);

  wifiManager.setSaveConfigCallback(configCallback);

  wifiManager.setBreakAfterConfig(true);

  wifiManager.setConnectRetries(3);
  wifiManager.setConnectTimeout(10);
  wifiManager.autoConnect();

  Serial.println("WiFi up, IP: " + WiFi.localIP().toString());
  if(String(server_address.getValue()) != "http://" && String(server_address.getValue()) != "")
  {
    prefs.begin("config", false);
    prefs.putString("serveraddr", String(server_address.getValue()));
    prefs.end();
    Serial.println("Saved server address:" + String(server_address.getValue()));
  }

  if(String(screen_id.getValue()) != ""){
    prefs.begin("config", false);
    prefs.putString("screenid", String(screen_id.getValue()));
    prefs.end();
    Serial.println("Saved display id:" + String(screen_id.getValue()));
  }

  prefs.begin("config", true);
  addr = prefs.getString("serveraddr", "http://");
  screenid = prefs.getString("screenid", "");
  prefs.end();

  Serial.println("Using server: " + addr);
  Serial.println("Using id: " + screenid);
}

void loop() {
  bool success = false;
  while (!success) {
    for(int i = 0; i < 4; i++){
      success = tryUpdateImageData();
      if(success) {
        break;
      }
      delay(500);
    }

    if(!success) {
      Serial.println("Fetch failed; popping up config portal…");
      wifiManager.startConfigPortal();
      Serial.println("New serveraddr: " + addr);
    }
  }

  // printed image, go to sleep
  Serial.println("Success! Sleeping for " + String(sleepTime) + "s");
  esp_sleep_enable_timer_wakeup(sleepTime * uS_TO_S_FACTOR);
  esp_deep_sleep_start();
}