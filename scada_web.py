import streamlit as st
import random
import json
import os
import math
import pandas as pd
import requests
import streamlit.components.v1 as components
import re

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
    
    # 1. Lógica Fronius
    if marca == "Fronius" and "." in ip_sn:
        try:
            url = f"http://{ip_sn}/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData"
            r = requests.get(url, timeout=1.2).json()
            pot_sol = r['Body']['Data'].get('PAC', {}).get('Value', 0)
            return {"solar": int(pot_sol) if pot_sol else 0, "casa": 1100, "soc": 100, "status": "Online"}
        except:
            pass

    # 2. LIMPIEZA DE CAPACIDAD (SOLUCIÓN AL ERROR DE TU IMAGEN)
    cap_texto = str(planta.get("capacidad", "5"))
    # Extrae solo números y puntos (ej: "13.92 kWp" -> "13.92")
    solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
    
    try:
        cap_num = float(solo_numeros[0]) if solo_numeros else 5.0
        cap_val = cap_num * 1000
    except:
        cap_val = 5000 

    return {
        "solar": int(cap_val * random.uniform(0.1, 0.8)),
        "casa": random.randint(400, 1500),
        "soc": random.randint(40, 99),
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
        st.info("No hay plantas. Ve a Gestión para agregar una.")
    else:
        planta_sel = st.selectbox("Seleccione Planta:", [p["nombre"] for p in plantas_guardadas])
        d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
        
        datos = obtener_datos_reales(d)
        pot_solar, pot_casa, soc = datos["solar"], datos["casa"], datos["soc"]
        pot_bat = pot_solar - pot_casa
        color_bat = "#2ecc71" if soc > 20 else "#e74c3c"

        st.write(f"📍 {d['ubicacion']} | ⚡ {d['capacidad']} | 📡 Status: `{datos['status']}`")
        st.markdown("---")

        # SVG PROFESIONAL CON FLUJO
        diagrama_svg = f"""
        <div style="background: #fdfdfd; padding: 20px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); width: 100%; max-width: 500px; margin: auto; font-family: sans-serif;">
            <svg viewBox="0 0 400 350" width="100%">
                <path d="M 100 85 V 150 H 170" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                <path d="M 300 85 V 150 H 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                <path d="M 170 150 H 100 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                <path d="M 230 150 H 300 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                <circle r="6" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 85 V 150 H 170" /></circle>
                <circle r="6" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>
                <circle r="6" fill="#e67e22"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 230" /></circle>
                <rect x="165" y="115" width="70" height="70" rx="12" fill="#ffffff" stroke="#3498db" stroke-width="3"/>
                <text x="200" y="142" text-anchor="middle" font-size="8" fill="#2c3e50" font-weight="bold">CV-ENG</text>
                <text x="200" y="200" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">{d['inversores']}</text>
                <g transform="translate(30,20)">
                    <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                    <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72" font-weight="bold">FV TOTAL</text>
                    <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold" fill="#2d3436">{pot_solar} W</text>
                </g>
                <g transform="translate(230,20)">
                    <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                    <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72" font-weight="bold">RED ELÉC.</text>
                    <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold" fill="#d63031">0 W</text>
                </g>
                <g transform="translate(30,230)">
                    <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                    <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72" font-weight="bold">BATERÍA {soc}%</text>
                    <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold" fill="#27ae60">{pot_bat} W</text>
                </g>
                <g transform="translate(230,230)">
                    <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                    <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72" font-weight="bold">CARGA</text>
                    <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold" fill="#e67e22">{pot_casa} W</text>
                </g>
            </svg>
        </div>
        """
        components.html(diagrama_svg, height=520) 
        if st.button("🔄 Actualizar Datos"): st.rerun()

# ==========================================
# VENTANA 2: GESTIÓN DE PORTAFOLIO
# ==========================================
else:
    st.title("🏢 GESTIÓN DE PORTAFOLIO")
    st.markdown("**CV INGENIERIA SAS**")
    
    with st.expander("➕ Registrar Nueva Planta", expanded=False):
        with st.form("f_planta"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nombre Planta")
            n_ubi = c2.text_input("Ubicación")
            n_inv = c1.selectbox("Inversor", ["Deye", "Fronius", "Huawei", "Must", "GoodWe"])
            n_cap = c2.text_input("Capacidad (ej: 13.92)")
            st.markdown("---")
            n_b_m = st.selectbox("Marca Batería", ["Pylontech", "Deye", "Huawei", "Ninguna"])
            n_dl = st.text_input("📡 IP o Serial Datalogger")
            
            if st.form_submit_button("💾 Guardar"):
                if n_nom:
                    guardar_planta({"nombre": n_nom, "ubicacion": n_ubi, "capacidad": n_cap, "inversores": n_inv, "datalogger": n_dl, "bat_marca": n_b_m})
                    st.success("¡Planta guardada!")
                    st.rerun()

    st.markdown("### 📋 Directorio de Plantas")
    for pl in plantas_guardadas:
        st.info(f"**{pl['nombre']}** | {pl['ubicacion']} | {pl['inversores']}")
