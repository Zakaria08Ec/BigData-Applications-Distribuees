#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAPTEUR IoT V5 (WebSockets) - "Open Cloud Smart Farm"
=====================================================
Se connecte au backend FastAPI via WebSockets.
Gère l'envoi de données et la réception d'ordres en asynchrone.
"""

import asyncio
import websockets
import json
import time
import random
import sys
import math
from datetime import datetime

# ==================== CONFIGURATION ====================
SENSOR_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 1
WS_URL = f"ws://localhost:8000/ws/sensor/{SENSOR_ID}"
SEND_INTERVAL = 5

class WebIoTSensor:
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id
        
        # Initialisation des bases selon la zone
        if sensor_id == 1:
            self.base_temp, self.base_hum = 28.0, 75.0
            self.base_co2, self.base_lux = 400, 50000
            self.name = "🌶️ Serre Tomates"
        elif sensor_id == 2:
            self.base_temp, self.base_hum = 18.0, 55.0
            self.base_co2, self.base_lux = 450, 30000
            self.name = "🍓 Serre Fraises"
        else:
            self.base_temp, self.base_hum = 22.0, 65.0
            self.base_co2, self.base_lux = 400, 80000
            self.name = f"🌾 Zone {sensor_id}"

    def generate_readings(self):
        """Génération mathématique des données"""
        cycle = 5 * math.sin(time.time() / 20)
        temp = self.base_temp + cycle + (random.random() - 0.5) * 2
        hum = max(30, min(95, self.base_hum + (random.random() - 0.5) * 5))
        co2 = max(300, self.base_co2 + random.randint(-15, 15))
        lux = max(0, self.base_lux + (cycle * 1000) + random.randint(-500, 500))
        
        return {
            'sensor_id': self.sensor_id,
            'temperature': round(temp, 2),
            'humidity': round(hum, 2),
            'co2': round(co2),
            'lux': round(lux),
            'timestamp': datetime.now().isoformat(),
            'zone': self.name
        }

    async def receive_commands(self, websocket):
        """Tâche asynchrone pour écouter les ordres du Web"""
        try:
            async for message in websocket:
                cmd = json.loads(message)
                action = cmd.get('action')
                if action == 'pump':
                    print(f"\n[ACTION WEB] 💦 POMPE ACTIVÉE SUR ZONE {self.sensor_id} ! 💦\n")
                    self.base_hum += 10
                elif action == 'fan':
                    print(f"\n[ACTION WEB] 💨 VENTILATEUR ACTIVÉ SUR ZONE {self.sensor_id} ! 💨\n")
                    self.base_temp -= 2
        except websockets.exceptions.ConnectionClosed:
            print("[SYSTÈME] Connexion fermée par le serveur.")

    async def send_data(self, websocket):
        """Tâche asynchrone pour envoyer les mesures"""
        measurement_count = 0
        try:
            while True:
                data = self.generate_readings()
                await websocket.send(json.dumps(data))
                measurement_count += 1
                print(f"[CAPTEUR {self.sensor_id}] ► T={data['temperature']}°C | H={data['humidity']}% | CO2={data['co2']}ppm")
                await asyncio.sleep(SEND_INTERVAL)
        except websockets.exceptions.ConnectionClosed:
            pass

    async def run(self):
        """Boucle principale de connexion WebSocket"""
        print(f"Tentative de connexion au Cloud Web sur {WS_URL}...")
        try:
            async with websockets.connect(WS_URL) as websocket:
                print(f"\n╔════════════════════════════════════════════╗")
                print(f"║  🌱 WEB CAPTEUR {self.sensor_id} - {self.name:<16} ║")
                print(f"╚════════════════════════════════════════════╝")
                print("✓ Connecté au Backend Web en temps réel.\n")
                
                # On lance les deux tâches (écouter et parler) en même temps !
                task_receive = asyncio.create_task(self.receive_commands(websocket))
                task_send = asyncio.create_task(self.send_data(websocket))
                
                await asyncio.gather(task_receive, task_send)
                
        except ConnectionRefusedError:
            print("✗ Erreur: Le serveur FastAPI n'est pas lancé.")

if __name__ == '__main__':
    sensor = WebIoTSensor(SENSOR_ID)
    try:
        asyncio.run(sensor.run())
    except KeyboardInterrupt:
        print("\nArrêt du capteur demandé.")