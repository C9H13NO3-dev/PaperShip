#include <Inkplate.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <SD.h>

Inkplate display(INKPLATE_3BIT);

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* imageUrl = "https://example.com/latest.png";

const unsigned long UPDATE_INTERVAL_MS = 60UL * 60UL * 1000UL; // one hour
unsigned long lastUpdate = 0;

void setup() {
    Serial.begin(115200);
    display.begin();
    display.rotate(1); // portrait mode

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected");

    if (!SD.begin(13)) {
        Serial.println("SD card initialization failed!");
    }

    fetchAndDisplay();
    lastUpdate = millis();
}

void loop() {
    if (millis() - lastUpdate > UPDATE_INTERVAL_MS) {
        fetchAndDisplay();
        lastUpdate = millis();
    }
    delay(1000);
}

void fetchAndDisplay() {
    HTTPClient http;
    http.begin(imageUrl);
    int httpCode = http.GET();
    if (httpCode == HTTP_CODE_OK) {
        File file = SD.open("/latest.png", FILE_WRITE);
        if (file) {
            WiFiClient *stream = http.getStreamPtr();
            uint8_t buff[128];
            int len = http.getSize();
            while (http.connected() && (len > 0 || len == -1)) {
                size_t c = stream->readBytes(buff, sizeof(buff));
                if (c) file.write(buff, c);
                if (len > 0) len -= c;
            }
            file.close();
            display.clearDisplay();
            display.drawPngFile(SD, "/latest.png", 0, 0);
            display.display();
        } else {
            Serial.println("Failed to open file on SD");
        }
    } else {
        Serial.printf("HTTP GET failed: %d\n", httpCode);
    }
    http.end();
}

