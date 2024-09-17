#include <SPI.h>
#include <MFRC522.h>
#include "LiquidCrystal.h"
#include <Arduino.h>
#include <WiFi.h>
#include <NetworkClient.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <ArduinoJson.h>

#define RST_PIN 22  // Configurable, see typical pin layout above
#define SS_PIN 5    // Configurable, see typical pin layout above
#define BUZZER 4
#define RED_LED 33
#define GREEN_LED 32

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
LiquidCrystal lcd(13, 12, 25, 26, 27, 14);
const char *ssid = "Allspray solutions ";
const char *password = "Ross19791126";
const char *www_username = "admin";
const char *www_password = "esp32";
const char *apiKey = "16f7d522edbb1a7b98914ac3d5d7335a43c094443e47b17e5e3f9c471f7afa5e";
int rw_delay = 1259;       // stop reading for 2 after each reading
String mode = "reader";         // Variable to store form data
String aadharno = "aadhar no";  // Variable to store form data
String panno = "pan no";        // Variable to store form data

WebServer server(80);

TaskHandle_t Task1;

void codeForTask1(void *parameter) {
  for (;;) {
    server.handleClient();
    vTaskDelay(10 / portTICK_PERIOD_MS);  //allow the cpu to switch to other tasks
  }
}

void handleNotFound() {
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server.uri();
  message += "\nMethod: ";
  message += (server.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server.args();
  message += "\n";

  for (uint8_t i = 0; i < server.args(); i++) {
    message += " " + server.argName(i) + ": " + server.arg(i) + "\n";
  }

  server.send(404, "text/plain", message);
}

bool requestServer(HTTPClient *httpobj, String url) {
  httpobj->begin(url);                                     //HTTP
  httpobj->addHeader("Content-Type", "application/json");  // Add Content-Type header
  httpobj->addHeader("X-API-KEY", apiKey);                 // Add API Key to Authorization header
  int httpCode = httpobj->POST(" ");
  if (httpCode > 0 && httpCode == HTTP_CODE_OK) {
    String payload = httpobj->getString();
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, payload);
    bool flag = doc["flag"];
    return flag;
  } else {
    return false;
  }
}

void setup() {
  // put your setup code here, to run once:
  xTaskCreatePinnedToCore(
    codeForTask1,
    "Task1",
    20000,
    NULL,
    0,
    &Task1,
    0);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  lcd.begin(16, 2);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  SPI.begin();  // Init SPI bus
  mfrc522.PCD_Init();

  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    vTaskDelay(500);
  }
  writeScreen(WiFi.localIP().toString());
  delay(10000);

  if (MDNS.begin("esp32")) {
  }

  server.on("/get", handleGet);             // Route to display the form
  server.on("/set", HTTP_POST, handleSet);  // Route to handle form submission
  server.on("/", []() {
    server.send(200, "text/plain", "Login OK");
  });
  server.onNotFound(handleNotFound);
  const char *headerkeys[] = { "User-Agent", "Cookie", "apikey" };
  size_t headerkeyssize = sizeof(headerkeys) / sizeof(char *);
  //ask server to track these headers
  server.collectHeaders(headerkeys, headerkeyssize);
  server.begin();
  setMode();
}

void loop() {
  if (mode == "reader") {
    if ((WiFi.status() == WL_CONNECTED)) {
      HTTPClient http;
      http.setTimeout(100000);  // Timeout in milliseconds (100 seconds)
      if (!mfrc522.PICC_IsNewCardPresent()) {
        digitalWrite(BUZZER, LOW);
        digitalWrite(GREEN_LED, LOW);  // turn the LED off by making the voltage LOW
        digitalWrite(RED_LED, LOW);    // turn the LED off by making the voltage LOW
        return;
      }
      if (!mfrc522.PICC_ReadCardSerial()) {
        digitalWrite(BUZZER, LOW);
        digitalWrite(GREEN_LED, LOW);  // turn the LED off by making the voltage LOW
        digitalWrite(RED_LED, LOW);    // turn the LED off by making the voltage LOW
        return;
      }
      String userid;
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        userid += String(mfrc522.uid.uidByte[i], HEX);
      }
      // Serial.println(userid);
      writeScreen("Verifing        ");
      String url = ("http://192.168.1.106:8000/api/doexists/" + userid + "");
      bool flag = requestServer(&http, url);
      if (flag) {
        writeScreen("Email Sent    ");
        url = "http://192.168.1.106:8000/api/is_authenticated/" + userid + "";
        bool isVerified = requestServer(&http, url);
        if (isVerified) {
          digitalWrite(GREEN_LED, HIGH);
          digitalWrite(BUZZER, HIGH);
          delay(300);
          digitalWrite(GREEN_LED, LOW);
          digitalWrite(BUZZER, LOW);
        }
        else {
          writeScreen("Failed !    ");
          digitalWrite(RED_LED, HIGH);
          digitalWrite(BUZZER, HIGH);
          delay(300);
          digitalWrite(RED_LED, LOW);
          digitalWrite(BUZZER, LOW);
        }
      } 
      else {
        digitalWrite(RED_LED, HIGH);
        digitalWrite(BUZZER, HIGH);
        delay(300);
        digitalWrite(RED_LED, LOW);
        digitalWrite(BUZZER, LOW);
      }
      http.end();
    }
    else {
      writeScreen("No connection   ");
    }
  } else if (mode == "writer") {
    MFRC522::MIFARE_Key key;
    for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
    server.handleClient();
    if (!mfrc522.PICC_IsNewCardPresent()) {
      return;
    }

    // Select one of the cards
    if (!mfrc522.PICC_ReadCardSerial()) {
      return;
    }
    lcd.setCursor(0, 1);
    writeScreen("Writing in 7secs");
    vTaskDelay(7000);
    writeScreen("                ");
    byte buffer[34];
    byte block;
    MFRC522::StatusCode status;
    aadharno.getBytes(buffer, sizeof(buffer));  // Extract bytes into buffer
    block = 1;

    status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      return;
    }

    status = mfrc522.MIFARE_Write(block, buffer, 16);
    if (status != MFRC522::STATUS_OK) {
      return;
    }

    block = 2;
    //Serial.println(F("Authenticating using key A..."));
    status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      return;
    }

    // Write block
    status = mfrc522.MIFARE_Write(block, &buffer[16], 16);
    if (status != MFRC522::STATUS_OK) {
      return;
    }

    panno.getBytes(buffer, sizeof(buffer));  // Extract bytes into buffer

    block = 4;
    //Serial.println(F("Authenticating using key A..."));
    status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      return;
    }

    // Write block
    status = mfrc522.MIFARE_Write(block, buffer, 16);
    if (status != MFRC522::STATUS_OK) {
      return;
    }

    block = 5;
    //Serial.println(F("Authenticating using key A..."));
    status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
      return;
    }

    // Write block
    status = mfrc522.MIFARE_Write(block, &buffer[16], 16);
    if (status != MFRC522::STATUS_OK) {
      return;
    }
    writeScreen("Data written    ");
    // mfrc522.PICC_HaltA(); // Halt PICC
    mfrc522.PCD_StopCrypto1();  // Stop encryption on PCD
    vTaskDelay(3000);
  }
  writeScreen("                ");
  vTaskDelay(10 / portTICK_PERIOD_MS);  //allow the cpu to switch to other tasks
  delay(rw_delay);
}

void handleGet() {

  if (server.header("apikey") == apiKey) {
    StaticJsonDocument<200> jsonDoc;
    jsonDoc["Mode"] = mode;
    // Serialize JSON to a string
    String jsonString;
    serializeJson(jsonDoc, jsonString);

    // Send JSON response
    server.sendHeader("Access-Control-Allow-Origin", "*");  // Allow all origins
    server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    server.sendHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
    server.send(200, "application/json", jsonString);
  } else {
    server.sendHeader("Access-Control-Allow-Origin", "*");  // Allow all origins
    server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    server.sendHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
    server.send(401, "application/json", "{\"message\":\"Unauthorized: API key missing or invalid\"}");
  }
}

void handleSet() {
  if (server.method() == HTTP_POST && server.header("apikey") == apiKey) {
    if (server.hasArg("value") && server.hasArg("aadharno") && server.hasArg("panno") && (server.arg("value") == "reader" || server.arg("value") == "writer")) {
      mode = server.arg("value");         // Get the value from the form
      aadharno = server.arg("aadharno");  // Get the value from the form
      panno = server.arg("panno");        // Get the value from the form
      server.send(200, "application/json", "{\"message\":\"Updated\"}");
      setMode();
    } else {
      server.send(401, "application/json", "{\"message\":\"Missing parameters or bad request\"}");
    }
  } else {
    server.send(405, "application/json", "{\"message\":\"Unauthorized: API key missing or invalid or bad request\"}");
  }
}

void setMode() {
  if (mode == "reader") {
    lcd.begin(16, 2);
    lcd.print("Reading Mode    ");
  } else if (mode == "writer") {
    lcd.begin(16, 2);
    lcd.print("Writing Mode    ");
  }
}

void writeScreen(String text) {
  lcd.setCursor(0, 1);
  lcd.print(text);
}