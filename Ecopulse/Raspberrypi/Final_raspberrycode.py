#!/usr/bin/env python3
import time
import serial
import json
import urllib.request
from flask import Flask, jsonify, render_template_string
import threading
import RPi.GPIO as GPIO
import math
from datetime import datetime

# Flask app
app = Flask(__name__)

# Global variables to store latest sensor data
latest_data = {
    'temperature': 0,
    'humidity': 0, 
    'moisture': 0,
    'light': 0,
    'mood': 'OKAY',
    'timestamp': 'Not connected',
    'battery': 85,  # Simulated battery level
    'signal': 4,    # Simulated signal strength
    'health_score': 75
}

# Calculate health score based on sensor data
def calculate_health_score(temperature, moisture, light):
    # Normalize values to 0-100 scale
    temp_score = max(0, 100 - abs(temperature - 22) * 10)  # Ideal temp ~22°C
    moisture_score = min(100, moisture * 1.2)  # Moisture directly contributes
    light_score = 100 - max(0, (light - 500) / 5)  # Lower light is better
    
    return int((temp_score + moisture_score + light_score) / 3)

# Pin definitions
DIN = 10
CLK = 11  
CS = 8

class MAX7219:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DIN, GPIO.OUT)
        GPIO.setup(CLK, GPIO.OUT)
        GPIO.setup(CS, GPIO.OUT)
        self.init_display()

    def send_byte(self, data):
        for i in range(8):
            GPIO.output(CLK, GPIO.LOW)
            GPIO.output(DIN, (data >> (7 - i)) & 0x01)
            GPIO.output(CLK, GPIO.HIGH)

    def write_reg(self, reg, data):
        GPIO.output(CS, GPIO.LOW)
        self.send_byte(reg)
        self.send_byte(data)
        GPIO.output(CS, GPIO.HIGH)

    def init_display(self):
        self.write_reg(0x0C, 0x01)
        self.write_reg(0x09, 0x00)
        self.write_reg(0x0A, 0x0F)
        self.write_reg(0x0B, 0x07)
        self.clear_display()

    def clear_display(self):
        for i in range(1, 9):
            self.write_reg(i, 0x00)

    def display_pattern(self, pattern):
        for i in range(8):
            self.write_reg(i + 1, pattern[i])

    def show_plant_mood(self, mood):
        if mood == "HAPPY":
            pattern = [0x3C, 0x42, 0xA5, 0x81, 0xA5, 0x99, 0x42, 0x3C]
        elif mood == "SAD":
            pattern = [0x3C, 0x42, 0xA5, 0x81, 0x99, 0xA5, 0x42, 0x3C]
        else:
            pattern = [0x3C, 0x42, 0xA5, 0x81, 0xBD, 0x81, 0x42, 0x3C] 
        self.display_pattern(pattern)
        print(f"🎭 Displaying {mood} mood on LED matrix")

def calculate_mood(temperature, moisture, light):
    light_good = (0 <= light <= 60)
    moisture_good = (80 <= moisture <= 100)
    light_bad = (900 <= light <= 1023) 
    moisture_bad = (0 <= moisture <= 20)
    
    if light_good and moisture_good:
        return "HAPPY"
    elif light_bad and moisture_bad:
        return "SAD"
    else:
        return "OKAY"

@app.route('/')
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌿 EcoPulse - Premium Plant Intelligence</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            :root {
                --primary: #00d4aa;
                --primary-dark: #00b894;
                --secondary: #667eea;
                --danger: #ff6b6b;
                --warning: #ffd93d;
                --dark: #2d3436;
                --light: #f8f9fa;
                --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                --glass: rgba(255,255,255,0.1);
                --shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                min-height: 100vh;
                padding: 20px;
                color: var(--dark);
                overflow-x: hidden;
            }
            
            .container {
                max-width: 450px;
                margin: 0 auto;
                position: relative;
            }
            
            /* Header with animated background */
            .header {
                text-align: center;
                margin-bottom: 30px;
                position: relative;
            }
            
            .header-content {
                background: var(--glass);
                backdrop-filter: blur(20px);
                border-radius: 25px;
                padding: 25px;
                border: 1px solid rgba(255,255,255,0.2);
                box-shadow: var(--shadow);
            }
            
            .logo {
                font-size: 3.5rem;
                margin-bottom: 10px;
                animation: float 3s ease-in-out infinite;
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
            }
            
            .header h1 {
                font-size: 2.2rem;
                font-weight: 800;
                background: linear-gradient(135deg, #fff 0%, #00d4aa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 5px;
            }
            
            .header p {
                color: rgba(255,255,255,0.8);
                font-weight: 400;
            }
            
            /* Status Bar */
            .status-bar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: var(--glass);
                backdrop-filter: blur(20px);
                border-radius: 15px;
                padding: 12px 20px;
                margin-bottom: 20px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            
            .status-item {
                display: flex;
                align-items: center;
                color: white;
                font-size: 0.9rem;
            }
            
            .status-item i {
                margin-right: 8px;
                font-size: 1rem;
            }
            
            .battery {
                width: 40px;
                height: 18px;
                background: rgba(255,255,255,0.2);
                border-radius: 4px;
                position: relative;
                margin-left: 8px;
            }
            
            .battery-level {
                height: 100%;
                background: var(--primary);
                border-radius: 3px;
                width: {{ data.battery }}%;
                transition: width 0.5s ease;
            }
            
            .signal-bars {
                display: flex;
                align-items: end;
                gap: 2px;
                margin-left: 8px;
            }
            
            .signal-bar {
                width: 3px;
                background: rgba(255,255,255,0.3);
                border-radius: 1px;
            }
            
            .signal-bar.active {
                background: var(--primary);
            }
            
            /* Main Mood Card */
            .mood-card {
                background: white;
                border-radius: 25px;
                padding: 30px;
                margin-bottom: 25px;
                box-shadow: var(--shadow);
                text-align: center;
                position: relative;
                overflow: hidden;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }
            
            .mood-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--primary), var(--secondary));
            }
            
            .mood-card:hover {
                transform: translateY(-8px) scale(1.02);
                box-shadow: 0 30px 60px rgba(0,0,0,0.15);
            }
            
            .mood-emoji {
                font-size: 5rem;
                margin-bottom: 15px;
                animation: bounce 2s infinite;
            }
            
            @keyframes bounce {
                0%, 100% { transform: scale(1) rotate(0deg); }
                25% { transform: scale(1.1) rotate(5deg); }
                75% { transform: scale(1.1) rotate(-5deg); }
            }
            
            .mood-text {
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 10px;
                background: linear-gradient(135deg, var(--dark), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .mood-description {
                color: #666;
                font-size: 1rem;
                line-height: 1.5;
            }
            
            /* Health Score */
            .health-score {
                background: var(--glass);
                backdrop-filter: blur(20px);
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid rgba(255,255,255,0.2);
                text-align: center;
                color: white;
            }
            
            .score-circle {
                width: 100px;
                height: 100px;
                margin: 0 auto 15px;
                position: relative;
            }
            
            .score-value {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 1.8rem;
                font-weight: 700;
                color: white;
            }
            
            /* Sensor Grid */
            .sensor-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 25px;
            }
            
            .sensor-card {
                background: white;
                border-radius: 20px;
                padding: 20px;
                text-align: center;
                box-shadow: var(--shadow);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .sensor-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: var(--primary);
            }
            
            .sensor-card:hover {
                transform: translateY(-5px);
            }
            
            .sensor-icon {
                font-size: 2.2rem;
                margin-bottom: 10px;
                opacity: 0.8;
            }
            
            .sensor-value {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 5px;
                color: var(--dark);
            }
            
            .sensor-label {
                font-size: 0.85rem;
                color: #666;
                font-weight: 500;
            }
            
            /* Recommendations */
            .recommendations {
                background: white;
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: var(--shadow);
            }
            
            .recommendation-item {
                display: flex;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid #f0f0f0;
            }
            
            .recommendation-item:last-child {
                border-bottom: none;
            }
            
            .rec-icon {
                width: 35px;
                height: 35px;
                background: var(--primary);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 15px;
                color: white;
                font-size: 1rem;
            }
            
            /* Footer */
            .footer {
                text-align: center;
            }
            
            .refresh-btn {
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: white;
                border: none;
                padding: 15px 35px;
                border-radius: 25px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                display: inline-flex;
                align-items: center;
                gap: 10px;
            }
            
            .refresh-btn:hover {
                transform: translateY(-3px) scale(1.05);
                box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            }
            
            .last-update {
                color: rgba(255,255,255,0.7);
                margin-top: 15px;
                font-size: 0.9rem;
            }
            
            /* Pulse animation for critical alerts */
            .pulse-alert {
                animation: pulse-red 2s infinite;
            }
            
            @keyframes pulse-red {
                0% { box-shadow: 0 0 0 0 rgba(255,107,107,0.4); }
                70% { box-shadow: 0 0 0 15px rgba(255,107,107,0); }
                100% { box-shadow: 0 0 0 0 rgba(255,107,107,0); }
            }
            
            /* Mobile Responsive */
            @media (max-width: 480px) {
                .container {
                    padding: 10px;
                }
                
                .header h1 {
                    font-size: 1.8rem;
                }
                
                .sensor-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Animated Header -->
            <div class="header">
                <div class="header-content">
                    <div class="logo">🌿</div>
                    <h1>EcoPulse Pro</h1>
                    <p>AI-Powered Plant Emotion Intelligence</p>
                </div>
            </div>
            
            <!-- Status Bar -->
            <div class="status-bar">
                <div class="status-item">
                    <i class="fas fa-satellite"></i>
                    Signal:
                    <div class="signal-bars">
                        {% for i in range(5) %}
                        <div class="signal-bar {{ 'active' if i < data.signal else '' }}" style="height: {{ (i+1)*4 }}px"></div>
                        {% endfor %}
                    </div>
                </div>
                <div class="status-item">
                    <i class="fas fa-battery-three-quarters"></i>
                    <div class="battery">
                        <div class="battery-level"></div>
                    </div>
                </div>
            </div>
            
            <!-- Health Score -->
            <div class="health-score">
                <h3 style="margin-bottom: 15px; opacity: 0.9;">Plant Health Score</h3>
                <div class="score-circle">
                    <svg width="100" height="100" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="8"/>
                        <circle cx="50" cy="50" r="45" fill="none" stroke="var(--primary)" stroke-width="8" 
                                stroke-dasharray="283" stroke-dashoffset="{{ 283 - (283 * data.health_score / 100) }}"
                                stroke-linecap="round" transform="rotate(-90 50 50)"/>
                    </svg>
                    <div class="score-value">{{ data.health_score }}</div>
                </div>
                <div style="font-size: 0.9rem; opacity: 0.8;">
                    {% if data.health_score >= 80 %} Excellent!
                    {% elif data.health_score >= 60 %} Good
                    {% else %} Needs Attention {% endif %}
                </div>
            </div>
            
            <!-- Main Mood Card -->
            <div class="mood-card {{ 'pulse-alert' if data.mood == 'SAD' else '' }}">
                <div class="mood-emoji">
                    {% if data.mood == 'HAPPY' %} 😊
                    {% elif data.mood == 'SAD' %} 😢
                    {% else %} 😐 {% endif %}
                </div>
                <div class="mood-text">
                    {% if data.mood == 'HAPPY' %} THRIVING! 
                    {% elif data.mood == 'SAD' %} NEEDS HELP!
                    {% else %} STABLE {% endif %}
                </div>
                <div class="mood-description">
                    {% if data.mood == 'HAPPY' %} 
                    Perfect conditions! Your plant is absolutely loving life! 🌟
                    {% elif data.mood == 'SAD' %} 
                    Immediate attention required! Check water and light levels! 🚨
                    {% else %} 
                    Your plant is comfortable. Minor adjustments could make it happier! 💫
                    {% endif %}
                </div>
            </div>
            
            <!-- Sensor Grid -->
            <div class="sensor-grid">
                <div class="sensor-card">
                    <div class="sensor-icon">🌡️</div>
                    <div class="sensor-value">{{ data.temperature }}°C</div>
                    <div class="sensor-label">Temperature</div>
                </div>
                
                <div class="sensor-card">
                    <div class="sensor-icon">💧</div>
                    <div class="sensor-value">{{ data.humidity }}%</div>
                    <div class="sensor-label">Humidity</div>
                </div>
                
                <div class="sensor-card">
                    <div class="sensor-icon">🌱</div>
                    <div class="sensor-value">{{ data.moisture }}%</div>
                    <div class="sensor-label">Soil Moisture</div>
                </div>
                
                <div class="sensor-card">
                    <div class="sensor-icon">☀️</div>
                    <div class="sensor-value">{{ data.light }}</div>
                    <div class="sensor-label">Light Level</div>
                </div>
            </div>
            
            <!-- Smart Recommendations -->
            <div class="recommendations">
                <h3 style="margin-bottom: 15px; color: var(--dark);">💡 Smart Recommendations</h3>
                {% if data.mood == 'SAD' %}
                <div class="recommendation-item">
                    <div class="rec-icon">💧</div>
                    <div>Water your plant immediately - soil moisture is low</div>
                </div>
                <div class="recommendation-item">
                    <div class="rec-icon">☀️</div>
                    <div>Move to better lighting conditions</div>
                </div>
                {% elif data.mood == 'OKAY' %}
                <div class="recommendation-item">
                    <div class="rec-icon">🌡️</div>
                    <div>Maintain current temperature range</div>
                </div>
                <div class="recommendation-item">
                    <div class="rec-icon">💫</div>
                    <div>Consider slight increase in watering frequency</div>
                </div>
                {% else %}
                <div class="recommendation-item">
                    <div class="rec-icon">⭐</div>
                    <div>Perfect conditions! Maintain current care routine</div>
                </div>
                <div class="recommendation-item">
                    <div class="rec-icon">🎉</div>
                    <div>Your plant is thriving! Great job!</div>
                </div>
                {% endif %}
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <button class="refresh-btn" onclick="location.reload()">
                    <i class="fas fa-sync-alt"></i>
                    Refresh Data
                </button>
                <div class="last-update">
                    <i class="far fa-clock"></i>
                    Last updated: {{ data.timestamp }}
                </div>
            </div>
        </div>
        
        <script>
            // Auto-refresh with smooth transition
            setTimeout(() => {
                document.body.style.opacity = '0.7';
                setTimeout(() => {
                    location.reload();
                }, 500);
            }, 10000); // Refresh every 10 seconds
            
            // Add entrance animations
            document.addEventListener('DOMContentLoaded', function() {
                const elements = document.querySelectorAll('.header-content, .mood-card, .sensor-card, .recommendations');
                elements.forEach((el, index) => {
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(30px)';
                    
                    setTimeout(() => {
                        el.style.transition = 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                        el.style.opacity = '1';
                        el.style.transform = 'translateY(0)';
                    }, index * 150);
                });
                
                // Animate health score circle
                const scoreCircle = document.querySelector('.score-circle circle:nth-child(2)');
                if (scoreCircle) {
                    setTimeout(() => {
                        scoreCircle.style.transition = 'stroke-dashoffset 2s ease-in-out';
                    }, 1000);
                }
            });
            
            // Add interactive hover effects
            document.querySelectorAll('.sensor-card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-8px) scale(1.05)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(-5px)';
                });
            });
        </script>
    </body>
    </html>
    ''', data=latest_data)

@app.route('/data')
def get_data():
    return jsonify(latest_data)


def sensor_reader():
    global latest_data
    
    try:
        print("🌿 Starting EcoPulse Pro Sensor Reader...")
        
        # Initialize display
        print("🔧 Initializing LED display...")
        display = MAX7219()
        print("✅ LED Display initialized successfully!")
        
      
        moods = ["HAPPY", "OKAY", "SAD", "OKAY"]
        for mood in moods:
            display.show_plant_mood(mood)
            time.sleep(0.8)
        
        # Connect to Arduino
        arduino_ports = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyUSB0']
        ser = None
        
        for port in arduino_ports:
            try:
                ser = serial.Serial(port, 9600, timeout=1)
                ser.reset_input_buffer()
                print(f"✅ Connected to Arduino on {port}!")
                break
            except:
                print(f"❌ Failed to connect on {port}")
                continue
        
        if ser is None:
            print("❌ Could not connect to Arduino!")
            display.show_plant_mood("SAD")
            return
        
        print("🚀 EcoPulse Pro System Ready! AI Monitoring Activated...")
        
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line.startswith("DATA:"):
                    data_str = line.replace("DATA:", "").replace(",END", "")
                    parts = data_str.split(",")
                    
                    if len(parts) == 4:
                        try:
                            temperature = float(parts[0])
                            humidity = float(parts[1])
                            moisture = int(parts[2])
                            light = int(parts[3])
                            
                            # Calculate mood and health score
                            mood = calculate_mood(temperature, moisture, light)
                            health_score = calculate_health_score(temperature, moisture, light)
                            
                            # Update display
                            display.show_plant_mood(mood)
                            
                            # Update global data with enhanced info
                            latest_data = {
                                'temperature': temperature,
                                'humidity': humidity,
                                'moisture': moisture,
                                'light': light,
                                'mood': mood,
                                'health_score': health_score,
                                'battery': max(10, min(100, 100 - (time.time() % 100))),  # Simulated battery
                                'signal': 4 if health_score > 50 else 3,  # Simulated signal
                                'timestamp': datetime.now().strftime('%H:%M:%S')
                            }
                            
                            # Enhanced console output
                            light_status = "🟢 GOOD" if (0 <= light <= 60) else "🔴 BAD" if (900 <= light <= 1023) else "🟡 OKAY"
                            moisture_status = "🟢 GOOD" if (80 <= moisture <= 100) else "🔴 BAD" if (0 <= moisture <= 20) else "🟡 OKAY"
                            print(f"🌡 {temperature:.1f}C | 💧 {moisture}% {moisture_status} | ☀️ {light} {light_status}")
                            print(f"😊 {mood} | ⭐ Health: {health_score}% | 🕒 {latest_data['timestamp']}")
                            print("─" * 50)
                            
                        except ValueError as e:
                            print(f"Error parsing data: {e}")
            
            time.sleep(0.1)
            
    except Exception as e:
        print(f"❌ Sensor reader error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    try:
        sensor_thread = threading.Thread(target=sensor_reader, daemon=True)
        sensor_thread.start()
        
        print("🌐 Starting EcoPulse Pro Web Server on http://192.168.0.xx:5000")
        print("📱 PREMIUM UI Activated with AI Features!")
        print("✨ Features: Health Scoring, Smart Recommendations, Animated UI")
        app.run(host='192.168.0.xx', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down EcoPulse Pro...")
        GPIO.cleanup()
    except Exception as e:
        print(f"❌ Main error: {e}")
        GPIO.cleanup()