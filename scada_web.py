import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. ESTILO CORPORATIVO Y FONDO REAL
# ==========================================
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="centered")

fondo_solar_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1509391366360-fe5ace4a1012?auto=format&fit=crop&w=1920&q=80");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.main .block-container {
    background-color: rgba(255, 255, 255, 0.9);
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    margin-top: 1rem;
}
h1, h2, h3, p, label { color: #0d47a1 !important; font-weight: bold; }
</style>
"""
st.markdown(fondo_solar_css, unsafe_allow_html=True)

# ==========================================
# 2. SEGURIDAD (LOGIN)
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔒 CENTRAL GESTIÓN DE PLANTAS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>CV INGENIERIA SAS</h3>", unsafe_allow_html=True)
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
# 3. BASE DE DATOS Y LÓGICA
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
# 4. INTERFAZ DE MONITOREO
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

    # Variables para el diagrama (Aquí estaba el error)
    pot_solar = random.randint(4000, 4800)
    pot_load = random.randint(1500, 2000)
    pot_bat = pot_solar - pot_load
    soc = random.randint(70, 98)
    color_soc = "#2ecc71" if soc > 20 else "#e74c3c"

    st.markdown("### 🔄 Flujo de Energía en Tiempo Real")
    
    diagrama_svg = f"""
    <div style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #eee;">
        <svg viewBox="0 0 400 350" width="100%">
            <path d="M 100 85 V 150 H 170" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            <path d="M 300 85 V 150 H 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            <path d="M 170 150 H 100 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            <path d="M 230 150 H 300 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            
            <circle r="6" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 85 V 150 H 170" /></circle>
            <circle r="6" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>
            <circle r="6" fill="#e67e22"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 230" /></circle>
            
            <rect x="165" y="115" width="70" height="70" rx="12" fill="white" stroke="#3498db" stroke-width="3"/>
            <text x="200" y="155" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">Deye</text>

            <g transform="translate(30,20)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eee" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72" font-weight="bold">FV TOTAL</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold" fill="#2d3436">{pot_solar} W</text>
            </g>
            <g transform="translate(230,20)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eee" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72" font-weight="bold">RED</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold" fill="#d63031">0 W</text>
            </g>
            <g transform="translate(30,230)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eee" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72" font-weight="bold">BATERÍA ({soc}%)</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold" fill="#27ae60">{pot_bat} W</text>
            </g>
            <g transform="translate(230,230)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eee" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72" font-weight="bold">CARGA</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold" fill="#e67e22">{pot_load} W</text>
            </g>
        </svg>
    </div>
    """
    components.html(diagrama_svg, height=520)
    if st.button("🔄 Actualizar Datos"): st.rerun()

# ==========================================
# 5. GESTIÓN DE PLANTAS
# ==========================================
else:
    st.title("🏢 GESTIÓN DE PORTAFOLIO")
    with st.form("f_planta"):
        n_nom = st.text_input("Nombre Planta")
        n_ubi = st.text_input("Ubicación")
        n_cap = st.text_input("Capacidad (kWp)")
        if st.form_submit_button("💾 Guardar Planta"):
            if n_nom:
                guardar_planta({"nombre": n_nom, "ubicacion": n_ubi, "capacidad": n_cap})
                st.success("Planta Guardada!")
                st.rerun()

    st.markdown("### 📋 Directorio de Plantas")
    for pl in plantas_guardadas:
        st.info(f"**{pl['nombre']}** | 📍 {pl['ubicacion']} | ⚡ {pl.get('capacidad','')}")
