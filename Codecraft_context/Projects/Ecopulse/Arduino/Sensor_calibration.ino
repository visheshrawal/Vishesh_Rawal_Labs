/**
 * 🌿 EcoPulse - Sensor Calibration Tool
 * Use this to calibrate your moisture sensor for accurate readings
 */

const int moisturePin = A0;
const int lightPin = A1;

void setup() {
  Serial.begin(9600);
  Serial.println("🌿 ECOPLUSE SENSOR CALIBRATION TOOL");
  Serial.println("====================================");
  Serial.println("Instructions:");
  Serial.println("1. Place moisture sensor in AIR - note DRY value");
  Serial.println("2. Place moisture sensor in WATER - note WET value");
  Serial.println("3. Update these values in main ecopulse_arduino.ino");
  Serial.println();
}

void loop() {
  int moistureRaw = analogRead(moisturePin);
  int lightValue = analogRead(lightPin);
  
  // Calculate moisture percentage (example calibration)
  int moisturePercent = map(moistureRaw, 1023, 50, 0, 100);
  moisturePercent = constrain(moisturePercent, 0, 100);
  
  Serial.print("💧 Moisture Raw: ");
  Serial.print(moistureRaw);
  Serial.print(" | Percent: ");
  Serial.print(moisturePercent);
  Serial.print("%");
  
  Serial.print(" | ☀️ Light: ");
  Serial.println(lightValue);
  
  // Provide calibration guidance
  if (moistureRaw > 1000) {
    Serial.println("   → Sensor is DRY (in air) - This is your DRY_VALUE");
  } else if (moistureRaw < 100) {
    Serial.println("   → Sensor is WET (in water) - This is your WET_VALUE");
  }
  
  delay(2000);
}