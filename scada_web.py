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
import plotly.express as px
from datetime import datetime, timedelta

try:
    from pymodbus.client import ModbusTcpClient
    MODBUS_DISPONIBLE = True
except ImportError:
    MODBUS_DISPONIBLE = False

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y FONDO
# ==========================================
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="wide") 

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=1920");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    [data-testid="stAppViewBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 15px; padding: 2rem; margin-top: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .tarjeta-planta {
        background-color: #ffffff; border-left: 5px solid #2ecc71;
        padding: 15px; border-radius: 8px; margin-bottom: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .tarjeta-titulo { color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 10px; }
    .tarjeta-dato { font-size: 22px; font-weight: bold; color: #34495e; }
    .tarjeta-label { font-size: 12px; color: #7f8c8d; text-transform: uppercase; }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. BASE DE DATOS (PLANTAS Y USUARIOS)
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'
ARCHIVO_USUARIOS = 'usuarios.json'

def cargar_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'w') as f: json.dump({"admin": "solar123"}, f)
    with open(ARCHIVO_USUARIOS, 'r') as f: return json.load(f)

def guardar_usuario(usuario, contrasena):
    usuarios = cargar_usuarios()
    usuarios[usuario] = contrasena
    with open(ARCHIVO_USUARIOS, 'w') as f: json.dump(usuarios, f)

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

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔒 CENTRAL GESTIÓN DE PLANTAS</h1>", unsafe_allow_html=True)
    col1, col_centro, col2 = st.columns([1, 2, 1]) 
    with col_centro:
        with st.form("login_form"):
            usuario_input = st.text_input("👤 Usuario")
            contrasena_input = st.text_input("🔑 Contraseña", type="password") 
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                usuarios_bd = cargar_usuarios()
                if usuario_input in usuarios_bd and usuarios_bd[usuario_input] == contrasena_input:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_actual"] = usuario_input
                    st.rerun() 
                else:
                    st.error("❌ Credenciales incorrectas.")
    st.stop() 

# --- MOTOR DE INTEGRACIÓN SOLARMAN ---
SOLARMAN_APP_ID = "TU_APP_ID_AQUI"
SOLARMAN_APP_SECRET = "TU_APP_SECRET_AQUI"
SOLARMAN_EMAIL = "tu_correo@
