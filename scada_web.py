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

# --- IMPORTACIÓN ROBUSTA ---
try:
    from pymodbus.client import ModbusTcpClient
    MODBUS_DISPONIBLE = True
except ImportError:
    MODBUS_DISPONIBLE = False

# ==========================================
# 1. CONFIGURACIÓN, FONDO Y ESTILOS
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
        padding: 15px; border-radius: 8px; margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .tarjeta-titulo { color: #2c3e50; font-size: 18px; font-weight: bold; }
    .tarjeta-dato { font-size: 22px; font-weight: bold; color: #34495e; }
    .tarjeta-label { font-size: 12px; color: #7f8c8d; text-transform: uppercase; }
    </style>
    """,
    unsafe_allow_html=True
)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔒 CENTRAL CV INGENIERÍA</h1>", unsafe_allow_html=True)
    col1, col_centro, col2 = st.columns([1, 2, 1]) 
    with col_centro:
        with st.form("login_form"):
            u = st.text_input("👤 Usuario")
            p = st.text_input("🔑 Contraseña", type="password") 
            if st.form_submit_button("Entrar", use_container_width=True):
                if u == "admin" and p == "solar123":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else: st.error("❌ Error")
    st.stop() 

# ==========================================
# 2. MOTOR DE DATOS Y PERSISTENCIA
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [{"nombre": "Planta Principal", "ubicacion": "Guaviare", "capacidad": "13.92", "inversores": "Deye", "datalogger": "SN: CV-001"}]
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

def obtener_datos_reales(planta):
    # Simulador inteligente mientras llega la API
    cap_t = str(planta.get("capacidad", "5"))
    solo_n = re.findall(r"[-+]?\d*\.\d+|\d+", cap_t)
    cap_v = float(solo_n[0]) * 1000 if solo_n else 5000
    
    pot_sol = int(cap_v * random.uniform(0.1, 0.8))
    e_dia = round((pot_sol * 4.2) / 1000, 1)
    return {
        "solar": pot_sol, "casa": 1700 + random.randint(-50, 50),
        "soc": random.randint(45, 98), "energia_diaria": e_dia,
        "status": "Simulado" if planta.get("inversores") == "Deye" else "Online"
    }

def simular_historico(planta):
    inicio = datetime.now().replace(hour=0, minute=0, second=0)
    datos = []
    for i in range(0, 96): # Cada 15 min
        t = inicio + timedelta(minutes=i*15)
        h = t.hour
        gen = max(0, 5000 * math.sin((h-6)/12 * math.pi)) if 6 <= h <= 18 else 0
        con = 1200 + 400 * math.sin((h-18)/6 * math.pi) if 18 <= h <= 24 else 1000
        datos.append({"Tiempo": t, "Generación (W)": gen, "Consumo (W)": con})
    return pd.DataFrame(datos)

plantas_guardadas = cargar_plantas()

# ==========================================
# 3. INTERFAZ Y NAVEGACIÓN
# ==========================================
st.sidebar.title("Navegación CV")
menu = st.sidebar.radio("Ir a:", ["🌐 Panorama", "📊 Monitoreo", "🏢 Gestión"])

if menu == "🌐 Panorama":
    st.title("🌐 PANORAMA DE PLANTAS")
    for pl in plantas_guardadas:
        d = obtener_datos_reales(pl)
        # CORRECCIÓN DE SINTAXIS EN HTML
        html_card = f"""
        <div class="tarjeta-planta">
            <div class="tarjeta-titulo">{pl['nombre']}</div>
            <div style="display: flex; justify-content: space-between; margin-top:10px;">
                <div><div class="tarjeta-dato">{d['solar']} W</div><div class="tarjeta-label">Potencia</div></div>
                <div><div class="tarjeta-dato">{d['energia_diaria']} kWh</div><div class="tarjeta-label">Hoy</div></div>
                <div><div class="tarjeta-dato">{pl['capacidad']} kWp</div><div class="tarjeta-label">Instalado</div></div>
            </div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)

elif menu == "📊 Monitoreo":
    st.title("📊 MONITOREO DETALLADO")
    p_sel = st.selectbox("Seleccione Planta:", [p["nombre"] for p in plantas_guardadas])
    pl = next(p for p in plantas_guardadas if p["nombre"] == p_sel)
    d = obtener_datos_reales(pl)
    
    # SVG Original sin cambios
    svg = f"""
    <div style="background:white; border-radius:15px; padding:15px; text-align:center;">
        <svg viewBox="0 0 400 350" width="100%">
            <path d="M 100 85 V 150 H 170 M 300 85 V 150 H 230 M 170 150 H 100 V 230 M 230 150 H 300 V 230" fill="none" stroke="#dfe6e9" stroke-width="4"/>
            <circle r="5" fill="#f1c40f"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 100 85 V 150 H 170" /></circle>
            <rect x="165" y="120" width="70" height="60" rx="10" fill="#3498db"/>
            <text x="200" y="155" text-anchor="middle" fill="white" font-size="10" font-weight="bold">CV-ENG</text>
            <g transform="translate(30,20)"><text x="0" y="0" font-size="10" fill="gray">FV</text><text x="0" y="25" font-size="18" font-weight="bold">{d['solar']}W</text></g>
            <g transform="translate(260,20)"><text x="0" y="0" font-size="10" fill="gray">RED</text><text x="0" y="25" font-size="18" font-weight="bold">0W</text></g>
            <g transform="translate(30,240)"><text x="0" y="0" font-size="10" fill="gray">BATERÍA {d['soc']}%</text><text x="0" y="25" font-size="18" font-weight="bold">{d['solar']-d['casa']}W</text></g>
            <g transform="translate(260,240)"><text x="0" y="0" font-size="10" fill="gray">CARGA</text><text x="0" y="25" font-size="18" font-weight="bold">{d['casa']}W</text></g>
        </svg>
    </div>"""
    components.html(svg, height=380)
    
    # Gráfica de Comportamiento Real
    df = simular_historico(pl)
    fig = px.area(df, x="Tiempo", y=["Generación (W)", "Consumo (W)"], 
                  color_discrete_map={"Generación (W)": "#f1c40f", "Consumo (W)": "#e74c3c"})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.title("🏢 GESTIÓN")
    with st.form("nueva_p"):
        c1, c2 = st.columns(2)
        n = c1.text_input("Nombre")
        cap = c2.text_input("Capacidad (kWp)")
        if st.form_submit_button("Guardar"):
            guardar_planta({"nombre": n, "capacidad": cap, "inversores": "Deye"})
            st.rerun()
    for i, p in enumerate(plantas_guardadas):
        c1, c2 = st.columns([4,1])
        c1.info(f"**{p['nombre']}** - {p['capacidad']} kWp")
        if c2.button("🗑️", key=f"d_{i}"):
            eliminar_planta(i)
            st.rerun()
