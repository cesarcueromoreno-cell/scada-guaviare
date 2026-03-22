import streamlit as st
import random
import json
import os
import math
import pandas as pd
import requests
import streamlit.components.v1 as components
import re # Nueva librería para limpiar los números

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y SEGURIDAD
# ==========================================
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="centered")

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
        inicial = [{"nombre": "Planta Principal", "ubicacion": "Guaviare", "capacidad": "13.92", "inversores": "Híbrido Multimarca", "datalogger": "SN: CV-001", "bat_marca": "Deye/Pylontech", "bat_tipo": "Litio (LiFePO4)"}]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(inicial, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

def guardar_planta(nueva):
    plantas = cargar_plantas()
    plantas.append(nueva)
    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)

def obtener_datos_reales(planta):
    marca = planta.get("inversores")
    ip_sn = planta.get("datalogger", "")
    
    # Intento de conexión real para FRONIUS
    if marca == "Fronius" and "." in ip_sn:
        try:
            url = f"http://{ip_sn}/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData"
            r = requests.get(url, timeout=1.5).json()
            pot_sol = r['Body']['Data'].get('PAC', {}).get('Value', 0)
            return {
                "solar": int(pot_sol) if pot_sol is not None else 0,
                "casa": 1200 + random.randint(-50, 50),
                "soc": 100,
                "status": "Online"
            }
        except:
            pass

    # --- CORRECCIÓN DEL ERROR DE VALOR (VALUEERROR) ---
    cap_raw = str(planta.get("capacidad", "5"))
    # Esta línea extrae solo los números y puntos, ignorando "kWp" o espacios
    cap_limpia = re.sub(r'[^\d.]', '', cap_raw) 
    
    try:
        cap_val = float(cap_limpia) * 1000
    except:
        cap_val = 5000 # Valor por defecto si todo falla

    fator_sol = random.uniform(0.1, 0.85) 
    
    return {
        "solar": int(cap_val * fator_sol),
        "casa": random.randint(300, 1800),
        "soc": random.randint(45, 98),
        "status": "Simulado"
    }

plantas_guardadas = cargar_plantas()

# ==========================================
# 3. NAVEGACIÓN
# ==========================================
st.sidebar.title("Navegación CV")
menu = st.sidebar.radio("Ir a:", ["📊 Monitoreo", "🏢 Gestión"])
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()
st.sidebar.info("**CV INGENIERIA SAS**")

# ==========================================
# VENTANA 1: MONITOREO
# ==========================================
if menu == "📊 Monitoreo":
    st.title("⚡ CENTRAL GESTIÓN DE PLANTAS")
    st.markdown("**CV INGENIERIA SAS**")
    
    if not plantas_guardadas:
        st.warning("No hay plantas registradas.")
    else:
        planta_sel = st.selectbox("Seleccione Planta:", [p["nombre"] for p in plantas_guardadas])
        d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
        
        datos_act = obtener_datos_reales(d)
        pot_solar = datos_act["solar"]
        pot_casa = datos_act["casa"]
        pot_bat = pot_solar - pot_casa
        soc = datos_act["soc"]
        color_bat = "#2ecc71" if soc > 20 else "#e74c3c"

        st.write(f"📍 {d['ubicacion']} | ⚡ {d['capacidad']} | 📡 Estado: `{datos_act['status']}`")
        st.write(f"🔋 **Batería:** {d.get('bat_marca','N/A')} ({soc}%)")
        st.markdown("---")

        st.markdown("### 🔄 Flujo de Energía en Tiempo Real")
        
        diagrama_svg = f"""
        <div style="background: #fdfdfd; padding: 20px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); width: 100%; max-width: 500px; margin: auto; font-family: sans-serif;">
            <svg viewBox="0 0 400 350" width="100%">
                <path d="M 100 85 V 150 H 170" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                <path d="M 300 85 V 150 H 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                <path d="M 170 150 H 100 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                <path d="M 230 150 H 300 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                
                <circle r="6" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 85 V 150 H 170" /></circle>
                <circle r="6" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>
                <circle r="6" fill="#e67e22"><animateMotion dur="1.5s"
