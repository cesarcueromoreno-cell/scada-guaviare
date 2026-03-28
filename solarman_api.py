import hashlib
import time
import requests
import logging

class MotorSolarmanAPI:
    def __init__(self, app_id, app_secret, email, password):
        self.app_id = app_id
        self.app_secret = app_secret
        self.email = email
        # Solarman exige que la contraseña viaje encriptada en SHA256
        self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        # URL oficial para cuentas Business Internacionales
        self.base_url = "https://globalapi.solarmanpv.com" 
        self.token = None
        self.headers = {"Content-Type": "application/json"}

    def _generar_firma(self, timestamp):
        """Genera la firma de seguridad criptográfica requerida por Solarman"""
        token_str = f"{self.app_id}{self.app_secret}{timestamp}"
        return hashlib.sha256(token_str.encode('utf-8')).hexdigest()

    def autenticar(self):
        """Solicita el Token de Acceso (Access Token) al servidor"""
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
                print("✅ [API] Autenticación exitosa. Token obtenido.")
                return True
            else:
                print(f"❌ [API] Error de autenticación: {response.text}")
                return False
        except Exception as e:
            print(f"❌ [API] Error de red: {e}")
            return False

    def obtener_datos_planta(self, station_id):
        """Extrae la telemetría en tiempo real de una planta específica"""
        if not self.token:
            if not self.autenticar(): return None

        url = f"{self.base_url}/station/v1.0/realTime"
        payload = {"stationId": station_id}
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    "solar": data.get("generationPower", 0), # Potencia de paneles
                    "casa": data.get("consumptionPower", 0), # Consumo de la casa
                    "red": data.get("gridPower", 0),         # Inyección/Compra a red
                    "bateria": data.get("batteryPower", 0),  # Carga/Descarga
                    "soc": data.get("soc", 0),               # Porcentaje de batería
                    "hoy": data.get("dailyGeneration", 0)    # Energía generada hoy (kWh)
                }
            return None
        except Exception as e:
            print(f"❌ [API] Error obteniendo datos de planta {station_id}: {e}")
            return None
