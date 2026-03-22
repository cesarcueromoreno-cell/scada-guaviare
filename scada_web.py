import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURACIÓN Y SEGURIDAD (LOGIN)
# ==========================================
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="centered")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔒 CENTRAL GESTIÓN DE PLANTAS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>CV INGENIERIA SAS</h3>", unsafe_allow_html=True)
    
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
                    st.error("❌ Credenciales incorrectas")
    st.stop()

# ==========================================
# 2. BASE DE DATOS
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [{"nombre": "Planta Principal", "ubicacion": "San José del Guaviare", "capacidad": "13.92 kWp", "inversores": "Deye", "datalogger": "N/A", "bat_marca": "Pylontech", "bat_tipo": "Litio"}]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(inicial, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

def guardar_planta(nueva):
    plantas = cargar_plantas()
    plantas.append(nueva)
    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)

plantas_guardadas = cargar_plantas()

# ==========================================
# 3. INTERFAZ DE MONITOREO (DISEÑO REALISTA)
# ==========================================
st.sidebar.title("Navegación CV")
menu = st.sidebar.radio("Ir a:", ["📊 Monitoreo", "🏢 Gestión"])
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()

if menu == "📊 Monitoreo":
    st.title("⚡ MONITOREO EN VIVO")
    st.markdown("#### CV INGENIERIA SAS")
    
    planta_sel = st.selectbox("Seleccione Planta:", [p["nombre"] for p in plantas_guardadas])
    d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
    
    st.write(f"📍 {d['ubicacion']} | ⚡ {d['capacidad']} | 📡 DL: {d.get('datalogger','N/A')}")
    st.markdown("---")

    # Simulación de datos
    pot_solar = random.randint(4000, 5000)
    pot_load = 1800
    pot_bat = pot_solar - pot_load
    soc = random.randint(75, 95)
    color_soc = "#2ecc71" if soc > 20 else "#e74c3c"

    st.markdown("### 🔄 Flujo de Energía en Tiempo Real")
    
    # SVG DIBUJADO (Panel, Torre, Casa, Batería Rack)
    diagrama_svg = f"""
    <div style="background: #f4f7f6; padding: 20px; border-radius: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); width: 100%; max-width: 500px; margin: auto; font-family: sans-serif;">
        <svg viewBox="0 0 400 350" width="100%">
            <path d="M 100 80 V 150 H 170" fill="none" stroke="#cfd8dc" stroke-width="4" stroke-linecap="round"/>
            <path d="M 300 80 V 150 H 230" fill="none" stroke="#cfd8dc" stroke-width="4" stroke-linecap="round"/>
            <path d="M 170 150 H 100 V 230" fill="none" stroke="#cfd8dc" stroke-width="4" stroke-linecap="round"/>
            <path d="M 230 150 H 300 V 230" fill="none" stroke="#cfd8dc" stroke-width="4" stroke-linecap="round"/>
            
            <circle r="5" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 80 V 150 H 170" /></circle>
            <circle r="5" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>
            <circle r="5" fill="#e67e22"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 230" /></circle>
            
            <rect x="165" y="115" width="70" height="75" rx="10" fill="white" stroke="#3498db" stroke-width="2"/>
            <rect x="172" y="122" width="56" height="30" rx="3" fill="#2c3e50"/>
            <text x="200" y="142" text-anchor="middle" font-size="8" fill="#00e676" font-weight="bold">DEYE</text>
            <text x="200" y="175" text-anchor="middle" font-size="10" font-weight="bold" fill="#34495e">Inversor</text>

            <g transform="translate(30,20)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eceff1" stroke-width="1"/>
                <rect x="10" y="12" width="45" height="60" fill="#1a237e" rx="2"/>
                <path d="M 10 27 H 55 M 10 42 H 55 M 10 57 H 55 M 21 12 V 72 M 32 12 V 72 M 43 12 V 72" stroke="#afb42b" stroke-width="0.5"/>
                <text x="65" y="35" font-size="11" fill="#607d8b" font-weight="bold">FV TOTAL</text>
                <text x="65" y="65" font-size="18" font-weight="bold" fill="#263238">{pot_solar} W</text>
            </g>
            
            <g transform="translate(230,20)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eceff1" stroke-width="1"/>
                <path d="M 35 70 L 25 15 L 45 15 L 35 70 Z M 20 25 H 50 M 15 45 H 55" fill="none" stroke="#78909c" stroke-width="2.5"/>
                <text x="65" y="35" font-size="11" fill="#607d8b" font-weight="bold">RED ELÉC.</text>
                <text x="65" y="65" font-size="18" font-weight="bold" fill="#d32f2f">0 W</text>
            </g>

            <g transform="translate(30,230)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eceff1" stroke-width="1"/>
                <rect x="10" y="10" width="45" height="65" rx="4" fill="#546e7a"/>
                <rect x="15" y="18" width="35" height="8" rx="1" fill="#263238"/>
                <rect x="15" y="55" width="35" height="15" rx="2" fill="white"/>
                <text x="32" y="67" text-anchor="middle" font-size="10" font-weight="bold" fill="{color_soc}">{soc}%</text>
                <text x="65" y="35" font-size="11" fill="#607d8b" font-weight="bold">BATERÍA</text>
                <text x="65" y="65" font-size="18" font-weight="bold" fill="#388e3c">{pot_bat} W</text>
            </g>
            
            <g transform="translate(230,230)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eceff1" stroke-width="1"/>
                <path d="M 35 15 L 10 35 V 75 H 60 V
