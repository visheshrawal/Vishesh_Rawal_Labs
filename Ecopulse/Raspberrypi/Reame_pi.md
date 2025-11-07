# 🌿 EcoPulse - Raspberry Pi Setup Guide

## 🔌 GPIO Connections (BCM Mode)

| Component | GPIO Pin | Physical Pin |
|-----------|----------|--------------|
| MAX7219 DIN | GPIO 10 | Pin 19 |
| MAX7219 CS | GPIO 8 | Pin 24 |
| MAX7219 CLK | GPIO 11 | Pin 23 |
| VCC | 5V | Pin 2 |
| GND | GND | Pin 6 |

## 🐍 Installation Steps

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt