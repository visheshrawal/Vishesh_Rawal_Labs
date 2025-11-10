# 🌿 EcoPulse - Arduino Setup Guide

## 🔧 Hardware Connections

### Sensors Connected:
- **DHT11** → Pin 8
- **Soil Moisture** → A0
- **LM393 Light** → A1

## ⚙️ Calibration Steps

1. **Upload `sensor_calibration.ino`**
2. **Open Serial Monitor** (9600 baud)
3. **Note the values:**
   - Sensor in AIR → DRY_VALUE
   - Sensor in WATER → WET_VALUE
4. **Update in main code:**
   ```cpp
   const int DRY_VALUE = 1023;    // Your measured dry value
   const int WET_VALUE = 50;      // Your measured wet value
