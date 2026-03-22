import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. SEGURIDAD Y LOGIN
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
# 2. BASE DE DATOS DE PLANTAS
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [{"nombre": "Planta Principal", "ubicacion": "San José del Guaviare", "capacidad": "13.92 kWp", "inversores": "Fronius + GoodWe", "datalogger": "SN: 240.123", "bat_marca": "GoodWe Lynx", "bat_tipo": "Litio (LiFePO4)"}]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(inicial, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

def guardar_planta(nueva):
    plantas = cargar_plantas()
    plantas.append(nueva)
    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)

plantas_guardadas = cargar_plantas()

# ==========================================
# 3. NAVEGACIÓN
# ==========================================
st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["📊 Monitoreo", "🏢 Gestión"])
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()
st.sidebar.info("**CV INGENIERIA SAS**")

# ==========================================
# VENTANA: MONITOREO
# ==========================================
if menu == "📊 Monitoreo":
    st.title("⚡ MONITOREO EN VIVO")
    planta_sel = st.selectbox("Seleccione Planta:", [p["nombre"] for p in plantas_guardadas])
    p = next(item for item in plantas_guardadas if item["nombre"] == planta_sel)
    
    st.write(f"📍 **{p['ubicacion']}** | 📡 DL: `{p.get('datalogger','N/A')}`")
    st.write(f"🔋 **Batería:** {p.get('bat_marca','N/A')} ({p.get('bat_tipo','N/A')})")
    
    # Simulación de datos
    pot_solar = random.randint(3000, 8000)
    pot_casa = 2000 + random.randint(-100, 100)
    pot_bat = pot_solar - pot_casa
    
    # Diagrama de Flujo SVG
    diagrama = f"""
    <div style="background: #f0f2f6; padding: 20px; border-radius: 15px; font-family: sans-serif;">
        <svg viewBox="0 0 400 300" width="100%">
            <path d="M 100 50 H 200 V 150" fill="none" stroke="#ccc" stroke-width="3"/>
            <path d="M 300 50 H 200 V 150" fill="none" stroke="#ccc" stroke-width="3"/>
            <path d="M 200 150 V 250 H 100" fill="none" stroke="#ccc" stroke-width="3"/>
            <path d="M 200 150 V 250 H 300" fill="none" stroke="#ccc" stroke-width="3"/>
            <circle r="5" fill="yellow"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 50 H 200 V 150" /></circle>
            <rect x="165" y="120" width="70" height="60" rx="10" fill="#1f77b4"/><text x="200" y="155" text-anchor="middle" fill="white">Inv</text>
            <text x="100" y="40" text-anchor="middle">☀️ {pot_solar}W</text>
            <text x="300" y="40" text-anchor="middle">🗼 Red: 0W</text>
            <text x="100" y="280" text-anchor="middle">🔋 Bat: {pot_bat}W</text>
            <text x="300" y="280" text-anchor="middle">🏠 Casa: {pot_casa}W</text>
        </svg>
    </div>
    """
    components.html(diagrama, height=400)
    if st.button("🔄 Actualizar"): st.rerun()

# ==========================================
# VENTANA: GESTIÓN
# ==========================================
else:
    st.title("🏢 GESTIÓN DE PROYECTOS")
    with st.form("nueva_planta"):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre Planta")
        ubi = c2.text_input("Ubicación")
        inv = c1.selectbox("Inversor", ["Fronius", "GoodWe", "Deye", "Huawei", "Growatt"])
        cap = c2.text_input("Capacidad (kWp)")
        st.markdown("---")
        b_marca = c1.selectbox("Batería", ["Ninguna", "Pylontech", "Deye", "GoodWe", "BYD", "AGM/Gel"])
        b_tipo = c2.selectbox("Tecnología", ["Litio (LiFePO4)", "Plomo-Ácido", "AGM", "Gel"])
        dl = st.text_input("📡 SN Datalogger / IP")
        
        if st.form_submit_button("💾 Registrar Planta"):
            if nombre:
                guardar_planta({"nombre": nombre, "ubicacion": ubi, "capacidad": cap, "inversores": inv, "datalogger": dl, "bat_marca": b_marca, "bat_tipo": b_tipo})
                st.success("Planta Guardada")
                st.rerun()

    st.markdown("### 📋 Directorio")
