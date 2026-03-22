import streamlit as st
import random
import json
import os
import math
import pandas as pd
import requests
import streamlit.components.v1 as components
import re
import hashlib
import time
import plotly.express as px # NUEVO: Librería para las gráficas reales
from datetime import datetime, timedelta # NUEVO: Para gestionar el historial de 24h

try:
    from pymodbus.client import ModbusTcpClient
    MODBUS_DISPONIBLE = True
except ImportError:
    MODBUS_DISPONIBLE = False

# ==========================================
# 1. CONFIGURACIÓN INICIAL, FONDO Y ESTILOS
# ==========================================
# Usamos Wide layout para que la gráfica tenga espacio
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="wide") 

st.markdown(
    """
    <style>
    /* Fondo de granja solar */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=1920");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    /* Barra superior transparente */
    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    /* Cuadro blanco semitransparente para que se lea tu interfaz */
    [data-testid="stAppViewBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    /* Estilos para las tarjetas del Panorama */
    .tarjeta-planta {
        background-color: #ffffff;
        border-left: 5px solid #2ecc71;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .tarjeta-titulo { color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 10px; }
    .tarjeta-dato { font-size: 22px; font-weight: bold; color: #34495e; }
    .tarjeta-label { font-size: 12px; color: #7f8c8d; text-transform: uppercase; }
    </style>
    """,
    unsafe_allow_html=True
)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔒 CENTRAL GESTION DE PLANTAS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>CV INGENIERIA SAS</h3>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col_centro, col2 = st.columns([1, 2, 1]) 
    with col_centro:
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario")
            contrasena = st.text_input("🔑 Contraseña", type="password") 
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                if usuario == "admin" and contrasena == "solar123":
                    st.session_state["autenticado"] = True
                    st.rerun() 
                else:
                    st.error("❌ Credenciales incorrectas.")
    st.stop() 

# ==========================================
# 2. BASE DE DATOS Y MOTOR DE INTEGRACIÓN
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [{"nombre": "Planta Principal", "ubicacion": "Guaviare", "capacidad": "13.92 kWp", "inversores": "Híbrido Multimarca", "datalogger": "SN: CV-001", "bat_marca": "Deye/Pylontech", "bat_tipo": "Litio (LiFePO4)"}]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(inicial, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

def guardar_planta(nueva):
    plantas = cargar_plantas()
    plantas.append(nueva)
    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)

def eliminar_planta(indice):
    plantas = cargar_plantas()
    if 0 <= indice < len(plantas):
        plantas.pop(indice)
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)

# --- CREDENCIALES SOLARMAN API (DEYE) ---
SOLARMAN_APP_ID = "TU_APP_ID_AQUI"
SOLARMAN_APP_SECRET = "TU_APP_SECRET_AQUI"
SOLARMAN_EMAIL = "tu_correo@cvingenieria.com"
SOLARMAN_PASSWORD = "tu_password"

def obtener_token_solarman():
    try:
        url = "https://api.solarmanpv.com/account/v1.0/token"
        pwd_hash = hashlib.sha256(SOLARMAN_PASSWORD.encode()).hexdigest()
        payload = {"appId": SOLARMAN_APP_ID, "password": pwd_hash, "email": SOLARMAN_EMAIL}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200: return response.json().get('access_token')
        return None
    except: return None

def obtener_datos_reales(planta):
    marca = planta.get("inversores")
    ip_sn = planta.get("datalogger", "")
    
    # 1. INTEGRACIÓN FRONIUS
    if marca == "Fronius" and "." in ip_sn:
        try:
            url = f"http://{ip_sn}/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData"
            r = requests.get(url, timeout=1.2).json()
            pot_sol = r['Body']['Data'].get('PAC', {}).get('Value', 0)
            energia_diaria = round((pot_sol * 4) / 1000, 1) # Estimación rápida
            return {"solar": int(pot_sol) if pot_sol else 0, "casa": 1400, "soc": 100, "energia_diaria": energia_diaria, "status": "Online"}
        except: pass

    # 2. INTEGRACIÓN DEYE (API Solarman)
    if marca == "Deye" and "TU_APP_ID" not in SOLARMAN_APP_ID and len(ip_sn) > 6 and "." not in ip_sn:
        token = obtener_token_solarman()
        if token:
            try:
                url_device = f"https://api.solarmanpv.com/device/v1.0/currentData?appId={SOLARMAN_APP_ID}&language=en"
                headers = {"Authorization": f"bearer {token}", "Content-Type": "application/json"}
                payload = {"deviceSn": ip_sn}
                res = requests.post(url_device, json=payload, headers=headers, timeout=5)
                
                if res.status_code == 200:
                    datos_api = res.json()
                    if datos_api.get("success"):
                        parametros = datos_api.get("dataList", [])
                        pot_fv, soc_bat, pot_carga, energia_diaria = 0, 100, 1500, 0
                        for param in parametros:
                            if param.get("key") == "DC_P": pot_fv = float(param.get("value", 0))
                            elif param.get("key") == "B_SOC": soc_bat = int(float(param.get("value", 0)))
                            elif param.get("key") == "L_P": pot_carga = float(param.get("value", 0))
                            elif param.get("key") in ["E_D", "E_Today", "Daily_Generation"]: energia_diaria = float(param.get("value", 0))
                        return {"solar": int(pot_fv), "casa": int(pot_carga), "soc": int(soc_bat), "energia_diaria": energia_diaria, "status": "Online (Nube)"}
            except: pass 

    # 3. SIMULADOR INTELIGENTE
    cap_texto = str(planta.get("capacidad", "5"))
    solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
    try: cap_val = float(solo_numeros[0]) * 1000 if solo_numeros else 5000 
    except: cap_val = 5000 
    
    pot_simulada = int(cap_val * random.uniform(0.1, 0.8))
    energia_simulada = round((pot_simulada * random.uniform(3.5, 5.0)) / 1000, 1)

    estado = "Simulado (Falta configurar API)" if marca == "Deye" else "Simulado"

    return {
        "solar": pot_simulada,
        "casa": 1750 + random.randint(-40, 40),
        "soc": random.randint(50, 99),
        "energia_diaria": energia_simulada,
        "status": estado
    }

# --- NUEVA FUNCIÓN PARA HISTORIAL SIMULADO 24H ---
# Mientras no hay API, generamos datos creíbles para la gráfica
def simular_historico_24h(planta):
    cap_texto = str(planta.get("capacidad", "5"))
    solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
    try: cap_val = float(solo_numeros[0]) if solo_numeros else 5.0
    except: cap_val = 5.0

    hora_actual = datetime.now()
    inicio_dia = hora_actual.replace(hour=0, minute=0, second=0, microsecond=0)
    
    datos = []
    # Generamos datos cada 15 minutos
    for minutos in range(0, 24 * 60, 15):
        timestamp = inicio_dia + timedelta(minutes=minutos)
        hora = timestamp.hour
        
        # Simular Generación (Curva de campana entre 06:00 y 18:00)
        generacion = 0
        if 6 <= hora <= 18:
            x = (hora - 6) / 12 * math.pi
            generacion = (cap_val * 0.9) * math.sin(x) * random.uniform(0.95, 1.05)
            generacion = max(0, generacion)
            
        # Simular Consumo Carga (Picos mañana y noche)
        base_consumo = cap_val * 0.2
        if 7 <= hora <= 9: pico_consumo = cap_val * 0.3 * math.sin((hora-7)/2 * math.pi)
        elif 18 <= hora <= 21: pico_consumo = cap_val * 0.4 * math.sin((hora-18)/3 * math.pi)
        else: pico_consumo = 0
        
        consumo = base_consumo + pico_consumo + (cap_val * 0.05 * random.uniform(-1, 1))
        consumo = max(cap_val * 0.1, consumo)
        
        datos.append({
            "timestamp": timestamp,
            "Generación FV": round(generacion, 2),
            "Consumo Carga": round(consumo, 2)
        })
        
    return pd.DataFrame(datos)
# --------------------------------------------------

plantas_guardadas = cargar_plantas()

# ==========================================
# 3. NAVEGACIÓN
# ==========================================
st.sidebar.title("Navegación CV")
menu = st.sidebar.radio("Ir a:", ["🌐 Panorama General", "📊 Monitoreo Detallado", "🏢 Gestión de Portafolio"])
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()
st.sidebar.info("**CV INGENIERIA SAS**")

# ==========================================
# VENTANA 1: PANORAMA GENERAL (INTACTO)
# ==========================================
if menu == "🌐 Panorama General":
    st.title("🌐 PANORAMA GENERAL DEL PORTAFOLIO")
    st.markdown("**Vista global rápida - CV INGENIERIA SAS**")
    
    if not plantas_guardadas:
        st.warning("No hay plantas registradas. Ve a Gestión para agregar una.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Plantas Totales", len(plantas_guardadas))
        c2.metric("En Línea / Accediendo", "Esperando API")
        c3.metric("Desconectadas", "0")
        st.markdown("---")

        for pl in plantas_guardadas:
            datos = obtener_datos_reales(pl)
            
            cap_texto = str(pl.get("capacidad", "0"))
            solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
            cap_limpia = f"{solo_numeros[0]} kWp" if solo_numeros else "N/A"

            tarjeta = f"""
            <div class="tarjeta-planta">
                <div class="tarjeta-titulo">{pl['nombre']} <span style="float:right; font-size:12px; color:#95a5a6;">{datos['status']}</span></div>
                <div style="display: flex; justify-content: space-between; text-align: center; margin-top: 15px;">
                    <div>
                        <div class="tarjeta-dato">{datos['solar']} W</div>
                        <div class="tarjeta-label">Energía (Potencia Actual)</div>
                    </div>
                    <div>
                        <div class="tarjeta-dato">{
