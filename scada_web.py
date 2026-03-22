import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y SEGURIDAD (LOGIN) - NO TOCAR
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
# 2. BASE DE DATOS DE PLANTAS - NO TOCAR
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
# VENTANA 1: MONITOREO (NUEVO DISEÑO DIBUJADO)
# ==========================================
if menu == "📊 Monitoreo":
    st.title("⚡ CENTRAL GESTIÓN DE PLANTAS")
    st.markdown("**CV INGENIERIA SAS**")
    
    planta_sel = st.selectbox("Seleccione Planta:", [p["nombre"] for p in plantas_guardadas])
    d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
    
    st.write(f"📍 {d['ubicacion']} | ⚡ {d['capacidad']} | 📡 DL: `{d.get('datalogger','N/A')}`")
    st.write(f"🔋 **Batería:** {d.get('bat_marca','N/A')} ({d.get('bat_tipo','N/A')})")
    st.markdown("---")

    # Datos en tiempo real
    pot_solar = 4200 + random.randint(-100, 100)
    pot_casa = 1750 + random.randint(-40, 40)
    pot_bat = pot_solar - pot_casa
    soc = random.randint(50, 99)
    color_bat = "#2ecc71" if soc > 20 else "#e74c3c"

    st.markdown("### 🔄 Flujo de Energía en Tiempo Real")
    
    # EL DIBUJO PROFESIONAL (SVG NATIVO)
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
            <rect x="175" y="125" width="50" height="25" rx="3" fill="#2c3e50"/> <circle cx="185" cy="160" r="3" fill="#2ecc71"/> <text x="200" y="142" text-anchor="middle" font-size="8" fill="#55efc4" font-weight="bold">CV-ENG</text>
            <text x="200" y="200" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">Híbrido</text>

            <g transform="translate(30,20)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                <rect x="10" y="10" width="45" height="65" fill="#1a237e" rx="2"/> <path d="M 10 25 H 55 M 10 40 H 55 M 10 55 H 55 M 21 10 V 75 M 32 10 V 75 M 43 10 V 75" stroke="#f1c40f" stroke-width="0.5"/>
                <text x="65" y="35" font-size="11" fill="#636e72" font-weight="bold">FV TOTAL</text>
                <text x="65" y="65" font-size="18" font-weight="bold" fill="#2d3436">{pot_solar} W</text>
            </g>
            
            <g transform="translate(230,20)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                <path d="M 35 75 L 25 15 L 45 15 L 35 75 Z M 20 25 H 50 M 15 45 H 55" fill="none" stroke="#b2bec3" stroke-width="2.5"/> <text x="65" y="35" font-size="11" fill="#636e72" font-weight="bold">RED ELÉC.</text>
                <text x="65" y="65" font-size="18" font-weight="bold" fill="#d63031">0 W</text>
            </g>

            <g transform="translate(30,230)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                <rect x="10" y="10" width="45" height="65" rx="4" fill="#636e72"/> <rect x="15" y="15" width="35" height="8" rx="1" fill="#2d3436"/>
                <rect x="15" y="30" width="35" height="8" rx="1" fill="#2d3436"/>
                <rect x="15" y="55" width="35" height="15" rx="1" fill="white"/> <text x="32" y="67" text-anchor="middle" font-size="10" font-weight="bold" fill="{color_bat}">{soc}%</text>
                <text x="65" y="35" font-size="11" fill="#636e72" font-weight="bold">BATERÍA</text>
                <text x="65" y="65" font-size="18" font-weight="bold" fill="#27ae60">{pot_bat} W</text>
            </g>
            
            <g transform="translate(230,230)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                <path d="M 35 15 L 10 35 V 75 H 60 V 35 Z" fill="#dfe6e9"/> <path d="M 35 10 L 5 35 H 65 Z" fill="#636e72"/> <rect x="28" y="55" width="14" height="20" fill="#a1887f"/> <text x="75" y="35" font-size="11" fill="#636e72" font-weight="bold">CARGA</text>
                <text x="75" y="65" font-size="18" font-weight="bold" fill="#e67e22">{pot_casa} W</text>
            </g>
        </svg>
    </div>
    """
    
    components.html(diagrama_svg, height=520) 
    if st.button("🔄 Actualizar Datos"): st.rerun()

# ==========================================
# VENTANA 2: GESTIÓN DE PORTAFOLIO - NO TOCAR
# ==========================================
else:
    st.title("🏢 GESTIÓN DE PORTAFOLIO")
    st.markdown("**CV INGENIERIA SAS**")
    
    with st.expander("➕ Registrar Nueva Planta", expanded=False):
        with st.form("f_planta"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nombre Planta")
            n_ubi = c2.text_input("Ubicación")
            n_inv = c1.selectbox("Inversor", ["Deye", "GoodWe", "Fronius", "Huawei", "Growatt"])
            n_cap = c2.text_input("Capacidad (kWp)")
            st.markdown("---")
            c3, c4 = st.columns(2)
            n_b_m = c3.selectbox("Batería", ["Ninguna", "Pylontech", "Deye", "BYD", "Trojan"])
            n_b_t = c4.selectbox("Tecnología", ["Litio (LiFePO4)", "Plomo-Ácido", "AGM", "Gel"])
            n_dl = st.text_input("📡 SN Datalogger / IP")
            if st.form_submit_button("💾 Guardar"):
                if n_nom:
                    guardar_planta({"nombre": n_nom, "ubicacion": n_ubi, "capacidad": n_cap, "inversores": n_inv, "datalogger": n_dl, "bat_marca": n_b_m, "bat_tipo": n_b_t})
                    st.success("Planta Guardada")
                    st.rerun()

    st.markdown("### 📋 Directorio de Plantas")
    for pl in plantas_guardadas:
        st.info(f"**{pl['nombre']}** | {pl['ubicacion']} | 🔋 {pl.get('bat_marca','N/A')}")
