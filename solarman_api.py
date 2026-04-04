import hashlib
import time
import requests
import streamlit as st

class MotorSolarmanAPI:
    def __init__(self, email, password):
        # El .strip() elimina espacios accidentales al inicio o al final
        self.email = str(email).strip()
        self.password_hash = hashlib.sha256(str(password).strip().encode('utf-8')).hexdigest()
        self.base_url = "https://globalapi.solarmanpv.com" 
        self.token = None
        
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "SolarmanSmart/1.0.0 (Android)"
        }
        
        # App ID universal de la comunidad Home Assistant (muy estable)
        self.app_id = "1789785894395813340"
        self.app_secret = "04820123565842880812903422031383"

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
            "password": self.password_hash,
            "orgId": ""  # <-- El parámetro que a veces bloquea si no está
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code == 200 and response.json().get("success"):
                self.token = response.json().get("access_token")
                self.headers["Authorization"] = f"bearer {self.token}"
                return True
            else:
                st.error(f"🛑 Error interno de Solarman: {response.text}")
                return False
        except Exception as e:
            st.error(f"🛑 Error de red: {str(e)}")
            return False

    def obtener_datos_planta(self, station_id):
        if not self.token:
            if not self.autenticar(): return None

        url = f"{self.base_url}/station/v1.0/realTime"
        payload = {"stationId": str(station_id).strip()}
        
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
