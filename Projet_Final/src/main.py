#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
import google.generativeai as genai
from pydantic import BaseModel

# ==================== CONFIGURATION IA ====================
# Configure ton API Gemini ICI
genai.configure(api_key="your API")
model = genai.GenerativeModel('gemini-2.5-flash')

class ChatRequest(BaseModel):
    message: str

# ==================== INITIALISATION API ====================
app = FastAPI(title="Smart Farm API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ÉTAT EN MÉMOIRE ====================
sensor_data = {}
active_sensors = {}
active_dashboards = []

# ==================== ROUTES REST ====================
@app.get("/")
def read_root():
    return {"status": "Le Cloud Smart Farm est en ligne !"}

@app.get("/api/sensors")
def get_current_data():
    return {"sensors": sensor_data}

@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    """Reçoit la question, injecte le contexte de la ferme, et interroge Gemini."""
    user_message = request.message
    farm_context = json.dumps(sensor_data, ensure_ascii=False)
    
    system_prompt = f"""
    Tu es AgriBot, l'assistant IA expert de la plateforme 'Smart Farm'.
    Ton rôle est d'aider le gestionnaire de la ferme en répondant de manière concise, 
    professionnelle et directe.
    
    Voici les données EN TEMPS RÉEL des capteurs de la ferme :
    {farm_context}
    
    Règles :
    - Si une température dépasse 30°C ou l'humidité descend sous 40%, signale-le comme une alerte critique et propose d'activer la pompe ou le ventilateur.
    - Sois bref (maximum 3 phrases).
    - Réponds toujours en anglais, car l'interface de la plateforme est en anglais.
    
    Question de l'utilisateur : {user_message}
    """
    
    try:
        response = model.generate_content(system_prompt)
        return {"reply": response.text}
    except Exception as e:
        # On affiche l'erreur exacte dans le terminal d'Uvicorn pour le débogage !
        print(f"\n[ERREUR CRITIQUE GEMINI] : {str(e)}\n") 
        
        error_msg = str(e)
        if "429" in error_msg or "Resource Exhausted" in error_msg:
            return {"reply": "⚠️ API Quota limit reached for this specific model. Please wait a moment before asking again."}
        return {"reply": f"⚠️ System error: Unable to contact the AI model."}

# ==================== WEBSOCKETS ====================
@app.websocket("/ws/dashboard")
async def dashboard_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_dashboards.append(websocket)
    try:
        await websocket.send_json({"sensors": sensor_data})
        while True:
            msg = await websocket.receive_text()
            payload = json.loads(msg)
            if payload.get("command") == "actuate":
                target_id = payload.get("sensor_id")
                action = payload.get("action")
                if target_id in active_sensors:
                    await active_sensors[target_id].send_json({"action": action})
                    print(f"[ROUTAGE WEB] 🚀 Ordre '{action}' envoyé à la Zone {target_id}")
    except WebSocketDisconnect:
        active_dashboards.remove(websocket)

@app.websocket("/ws/sensor/{sensor_id}")
async def sensor_endpoint(websocket: WebSocket, sensor_id: int):
    await websocket.accept()
    active_sensors[sensor_id] = websocket
    print(f"[CONNEXION] Capteur {sensor_id} connecté au Web Cloud.")
    try:
        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)
            data['last_update'] = datetime.now().isoformat()
            data['online'] = True
            sensor_data[sensor_id] = data
            
            for dashboard_ws in active_dashboards:
                try:
                    await dashboard_ws.send_json({"sensors": sensor_data})
                except:
                    pass
    except WebSocketDisconnect:
        print(f"[DÉCONNEXION] Capteur {sensor_id} hors ligne.")
        del active_sensors[sensor_id]
        if sensor_id in sensor_data:
            sensor_data[sensor_id]['online'] = False
        for dashboard_ws in active_dashboards:
            try:
                await dashboard_ws.send_json({"sensors": sensor_data})
            except:
                pass