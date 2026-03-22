import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y SEGURIDAD (LOGIN)
# ==========================================
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="centered")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔒 CENTRAL GESTION DE PLANTAS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>CV INGENIERIA SAS</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Ingrese sus credenciales para acceder al panel de control.</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    col_vacia1, col_centro, col_vacia2 = st.columns([1, 2, 1]) 
    
    with col_centro:
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario")
            contrasena = st.text_input("🔑 Contraseña", type="password") 
            submit_login = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit_login:
                if usuario == "admin" and contrasena == "solar123":
                    st.session_state["autenticado"] = True
                    st.rerun() 
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop() 

# ==========================================
# 2. BASE DE DATOS Y MOTOR SOLAR
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        plantas_iniciales = [{
            "nombre": "Planta Principal", "ubicacion": "San José del Guaviare", 
            "capacidad": "13.92 kWp", "inversores": "Fronius + GoodWe", 
            "datalogger": "SN: 240.123456", "bat_marca": "GoodWe Lynx", "bat_tipo": "Litio (LiFePO4)"
        }]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas_iniciales, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

def guardar_planta(nueva_planta):
    plantas = cargar_plantas()
    plantas.append(nueva_planta)
    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)

plantas_guardadas = cargar_plantas()

def generar_curva_solar(nombre_planta):
    random.seed(nombre_planta) 
    pico_max = random.randint(4000, 15000) 
    horas = [f"{h:02d}:00" for h in range(6, 19)] 
    energia = [max(0, int(pico_max * math.sin(math.pi * (h - 6) / 12) + random.randint(-400, 400))) for h in range(6, 19)]
    random.seed() 
    return pd.DataFrame({"Hora": horas, "Generación (W)": energia}).set_index("Hora")

# ==========================================
# 3. MENÚ LATERAL
# ==========================================
st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["📊 Monitoreo en Vivo", "🏢 Gestión de Plantas"])
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()
st.sidebar.info("Plataforma Oficial \n**CV INGENIERIA SAS**")

# ==========================================
# VENTANA 1: MONITOREO (DISEÑO DE INTERFAZ ORIGINAL)
# ==========================================
if menu == "📊 Monitoreo en Vivo":
    st.title("⚡ CENTRAL GESTION DE PLANTAS")
    st.markdown("**CV INGENIERIA SAS**")
    
    planta_sel = st.selectbox("Seleccione planta:", [p["nombre"] for p in plantas_guardadas])
    det = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
    
    st.markdown(f"📍 {det['ubicacion']} | ⚡ {det['capacidad']} | 📡 DL: `{det.get('datalogger','N/A')}`")
    st.markdown(f"🔋 **Batería:** {det.get('bat_marca','N/A')} ({det.get('bat_tipo','N/A')})")
    st.markdown("---")

    st.markdown("### 📈 Curva de Generación Diaria")
    datos_h = generar_curva_solar(planta_sel)
    st.area_chart(datos_h, color="#f1c40f")

    # Cálculos para diagrama en tiempo real
    pot_solar = max(0, datos_h.iloc[-1]["Generación (W)"] + random.randint(-100, 100))
    pot_load = 1800 + random.randint(-50, 50)
    pot_bat = pot_solar - pot_load
    soc = random.randint(40, 100)

    st.markdown("### 🔄 Flujo de Energía en Tiempo Real")
    diagrama_svg = f"""
    <div style="background-color: #f9f9f9; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 500px; margin: auto; font-family: sans-serif;">
        <svg viewBox="0 0 400 330" width="100%" height="100%">
            <path d="M 100 80 H 170" fill="none" stroke="#ddd" stroke-width="3"/>
            <path d="M 230 150 H 300 V 80" fill="none" stroke="#ddd" stroke-width="3"/>
            <path d="M 170 150 H 100 V 220" fill="none" stroke="#ddd" stroke-width="3"/>
            <path d="M 230 150 H 300 V 220" fill="none" stroke="#ddd" stroke-width="3"/>
            
            <circle r="5" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 80 H 170" /></circle>
            <circle r="5" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 220" /></circle>
            <circle r="5" fill="#e67e2
