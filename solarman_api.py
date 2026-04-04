import hashlib
import time
import requests
import streamlit as st

class MotorSolarmanAPI:
    def __init__(self, email, password):
        self.email = email
        self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        self.base_url = "https://globalapi.solarmanpv.com" 
        self.token = None
        
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "SolarmanSmart/1.0.0 (Android)"
        }
        
        # App ID y Secret públicos de la aplicación residencial
        self.app_id = "1227361424750919680"
        self.app_secret = "29b82fc2d2aa93e7f9f2509192ce26e3"

    def _generar_firma(self, timestamp):
        token_str = f"{self.app_id}{self.app_secret}{timestamp}"
        return hashlib.sha256(token_str.encode('utf-8')).hexdigest()

    def autenticar(self):
        timestamp = str(int(time.time() * 1000))
        url = f"{self.base_url}/account/v1.0/token"
        
        payload = {
            "appId": self.app_id,
            "signature": self._generar_firma(timestamp),
            "timestamp": timestamp,
            "email": self.email,
            "password": self.password_hash
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code == 200 and response.json().get("success"):
                self.token = response.json().get("access_token")
                self.headers["Authorization"] = f"bearer {self.token}"
                return True
            else:
                # AQUÍ ESTÁ LA MAGIA: Imprime la respuesta real del servidor en rojo
                st.error(f"🛑 Error interno de Solarman: {response.text}")
                return False
        except Exception as e:
            st.error(f"🛑 Error de red: {str(e)}")
            return False

    def obtener_datos_planta(self, station_id):
        if not self.token:
            if not self.autenticar(): return None

        url = f"{self.base_url}/station/v1.0/realTime"
        payload = {"stationId": station_id}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {
                        "solar": data.get("generationPower", 0), 
                        "casa": data.get("consumptionPower", 0), 
                        "red": data.get("gridPower", 0),         
                        "bateria": data.get("batteryPower", 0),  
                        "soc": data.get("soc", 0),               
                        "hoy": data.get("dailyGeneration", 0)    
                    }
                else:
                    st.error(f"🛑 Error al pedir datos de la planta: {response.text}")
                    return None
            return None
        except Exception as e:
            return None
