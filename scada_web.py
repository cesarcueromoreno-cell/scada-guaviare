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
# VENTANA 1: MONITOREO (INTERFAZ DEYE MANTENIDA)
# ==========================================
if menu == "📊 Monitoreo en Vivo":
    st.title("⚡ CENTRAL GESTION DE PLANTAS")
    st.markdown("**CV INGENIERIA SAS**")
    
    planta_sel = st.selectbox("Seleccione planta:", [p["nombre"] for p in plantas_guardadas])
    det = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
    
    st.markdown(f"📍 {det['ubicacion']} | ⚡ {det['capacidad']} | 📡 DL: `{det.get('datalogger','N/A')}`")
    st.markdown(f"🔋 **Batería:** {det.get('bat_marca','N/A')} ({det.get('bat_tipo','N/A')})")
    st.markdown("---")

    st
