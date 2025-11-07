#include <DHT.h>

#define DHT_PIN 8
#define DHT_TYPE DHT11
DHT dht(DHT_PIN, DHT_TYPE);

// Sensor pins
const int moisturePin = A0;
const int lightPin = A1;

// Calibration for YOUR moisture sensor
const int DRY_VALUE = 1023;    // Value when sensor is dry (in air)
const int WET_VALUE = 50;     // Value when sensor is wet (in water)

void setup() {
  Serial.begin(9600);
  dht.begin();
  
  // Wait for serial connection
  while (!Serial) {
    delay(10);
  }
  
  Serial.println("🌿 ECOPLUSE ARDUINO READY");
  Serial.println("DATA FORMAT: DATA:temp,humidity,moisture%,light,END");
}

void loop() {
  // Read sensors with error handling
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Handle sensor errors silently
  if (isnan(temperature)) temperature = 25.0;
  if (isnan(humidity)) humidity = 60.0;
  
  int moistureRaw = analogRead(moisturePin);
  int lightValue = analogRead(lightPin);
  
  // Convert moisture to percentage (HIGH raw = DRY, LOW raw = WET)
  int moisturePercent = map(moistureRaw, DRY_VALUE, WET_VALUE, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);
  
  // Send data in the exact format Pi expects
  Serial.print("DATA:");
  Serial.print(temperature, 1);  // 1 decimal place
  Serial.print(",");
  Serial.print(humidity, 1);     // 1 decimal place  
  Serial.print(",");
  Serial.print(moisturePercent); // Moisture percentage
  Serial.print(",");
  Serial.print(lightValue);      // Raw light value
  Serial.println(",END");
  
  // Optional: Print to Serial Monitor for debugging
  Serial.print("DEBUG: T=");
  Serial.print(temperature, 1);
  Serial.print("C H=");
  Serial.print(humidity, 1);
  Serial.print("% M=");
  Serial.print(moisturePercent);
  Serial.print("% L=");
  Serial.println(lightValue);
  
  delay(2000); // Send every 2 seconds
}