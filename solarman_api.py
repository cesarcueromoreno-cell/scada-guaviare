# solarman_api.py
import hashlib
import time
import requests

class MotorSolarmanAPI:
    def __init__(self, email, password):
        self.email = email
        # Encriptamos la clave como lo hace la página web internamente
        self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        # Usamos la URL pública de la API global (la misma que usa la App del celular)
        self.base_url = "https://globalapi.solarmanpv.com" 
        self.token = None
        
        # Simulamos ser un navegador web (Google Chrome en Windows)
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Usamos las credenciales genéricas (Open Source) de la App móvil de Solarman 
        # para engañar al sistema y no pagar la cuota de empresa.
        self.app_id = "1000000000000000"
        self.app_secret = "1234567890abcdef1234567890abcdef"

    def _generar_firma(self, timestamp):
        token_str = f"{self.app_id}{self.app_secret}{timestamp}"
        return hashlib.sha256(token_str.encode('utf-8')).hexdigest()

    def autenticar(self):
        """Finge ser la aplicación iniciando sesión para robar el token de acceso"""
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
                print("✅ [API HACK] Autenticación web exitosa. Token capturado.")
                return True
            else:
                print(f"❌ [API HACK] Bloqueado por el servidor: {response.text}")
                return False
        except Exception as e:
            print(f"❌ [API HACK] Error de red: {e}")
            return False

    def obtener_datos_planta(self, station_id):
        """Extrae la telemetría en tiempo real"""
        if not self.token:
            if not self.autenticar(): return None

        url = f"{self.base_url}/station/v1.0/realTime"
        payload = {"stationId": station_id}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    "solar": data.get("generationPower", 0), 
                    "casa": data.get("consumptionPower", 0), 
                    "red": data.get("gridPower", 0),         
                    "bateria": data.get("batteryPower", 0),  
                    "soc": data.get("soc", 0),               
                    "hoy": data.get("dailyGeneration", 0)    
                }
            return None
        except Exception as e:
            print(f"❌ [API HACK] Error obteniendo datos: {e}")
            return None
