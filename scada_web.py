import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components
import re
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from fpdf import FPDF
import tempfile
import requests
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y ESTILO (CSS)
# ==========================================
st.set_page_config(page_title="MONISOLAR APP", page_icon="☀️", layout="wide")

css_global = """
<style>
[data-testid="stAppViewContainer"] { background-image: url("https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=1920"); background-size: cover; background-position: center; background-attachment: fixed; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.stApp > header + div > div > div > div > h1, .stApp > header + div > div > div > div > h3 { color: #ffffff !important; text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #112027 0%, #1a323c 50%, #162a33 100%) !important; border-right: 1px solid #2c5364 !important; }
[data-testid="stSidebar"] * { color: #ffffff !important; text-shadow: none !important; }
[data-testid="stSidebar"] button { background-color: rgba(255,255,255,0.1) !important; border: 1px solid rgba(255,255,255,0.3) !important; }
[data-testid="stSidebar"] button p { color: #ffffff !important; font-weight: bold !important; }
[data-testid="stSidebar"] button:hover { background-color: rgba(231, 76, 60, 0.8) !important; }
.block-container { background-color: rgba(244, 247, 249, 0.95) !important; padding: 2rem !important; border-radius: 12px; margin-top: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
.block-container h1, .block-container h2, .block-container h3, .block-container h4, .block-container h5, .block-container p, .block-container span, .block-container label, .block-container div { color: #2c3e50 !important; text-shadow: none !important; }
[data-testid="stForm"] { background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(10px) !important; border-radius: 12px !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important; }
[data-testid="stForm"] p, [data-testid="stForm"] label { color: white !important; text-shadow: 1px 1px 3px black !important; }
.block-container [data-testid="stForm"] { background: #ffffff !important; backdrop-filter: none !important; border: 1px solid #eaeaea !important; box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important; }
.block-container [data-testid="stForm"] p, .block-container [data-testid="stForm"] label, .block-container input, .block-container select { color: #2c3e50 !important; text-shadow: none !important; }
.block-container button[kind="primary"] p { color: white !important; }
div.solarman-card { background: #ffffff !important; border-radius: 8px !important; padding: 20px !important; box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important; text-align: center !important; border: 1px solid #eaeaea !important; height: 100%; display: flex; flex-direction: column; justify-content: center; }
div.solarman-card div.solarman-val { font-size: 28px !important; font-weight: bold !important; margin-bottom: 5px !important; color: #2c3e50 !important; }
div.solarman-card div.solarman-lbl { font-size: 13px !important; color: #7f8c8d !important; }
div.solarman-card span.solarman-lbl-sm { color: #7f8c8d !important; font-size: 11px !important; }
.tarjeta-dash-pro { background-color: #ffffff !important; padding: 15px !important; border-radius: 8px !important; margin-bottom: 10px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important; display: flex !important; align-items: center !important; justify-content: space-between !important; border: 1px solid #eaeaea !important;}
.tarjeta-label-pro { font-size: 11px !important; color: #7f8c8d !important; text-transform: uppercase !important; margin-bottom: 2px !important; white-space: nowrap !important; }
.tarjeta-dato-pro { font-size: 16px !important; font-weight: bold !important; color: #2c3e50 !important; white-space: nowrap !important; }
div[data-testid="stTabs"] > div[data-baseweb="tab-list"] { border-bottom: 1px solid #e0e0e0 !important; gap: 15px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"] p, div[data-testid="stTabs"] button[data-baseweb="tab"] span { color: #7f8c8d !important; font-weight: 600 !important; font-size: 16px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"] { background-color: transparent !important; border: none !important; border-bottom: 3px solid transparent !important; border-radius: 0 !important; box-shadow: none !important; padding-bottom: 10px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #e74c3c !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p, div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] span { color: #2c3e50 !important; }
div[data-testid="stButton"] button[kind="primary"] { background-color: #2d8cf0 !important; border-color: #2d8cf0 !important; border-radius: 4px !important; }
div[data-testid="stButton"] button[kind="primary"] p { color: white !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { background-color: #57a3f3 !important; }
div[data-testid="stButton"] button[kind="secondary"] { border-color: #2d8cf0 !important; border-radius: 4px !important; background-color: white !important; }
div[data-testid="stButton"] button[kind="secondary"] p { color: #2d8cf0 !important; }
.diag-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; font-size: 13px; color: #2c3e50; padding: 10px; }
.diag-grid div { margin-bottom: 10px; }
.diag-lbl { color: #7f8c8d; display: block; margin-bottom: 2px; }
</style>
"""
st.markdown(css_global, unsafe_allow_html=True)

# ==========================================
# 2. VARIABLES DE SESIÓN
# ==========================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "usuario" not in st.session_state: st.session_state["usuario"] = None
if "rol" not in st.session_state: st.session_state["rol"] = None
if "planta_asignada" not in st.session_state: st.session_state["planta_asignada"] = "Todas"
if "editando_planta" not in st.session_state: st.session_state["editando_planta"] = None
if "mostrar_crear" not in st.session_state: st.session_state["mostrar_crear"] = False
if "red_desbloqueada" not in st.session_state: st.session_state["red_desbloqueada"] = False
if "reinicio_desbloqueado" not in st.session_state: st.session_state["reinicio_desbloqueado"] = False
if "ver_detalle_inv" not in st.session_state: st.session_state["ver_detalle_inv"] = False
if "ver_detalle_logger" not in st.session_state: st.session_state["ver_detalle_logger"] = False
if "ver_detalle_bateria" not in st.session_state: st.session_state["ver_detalle_bateria"] = False

if st.session_state["autenticado"] and st.session_state["usuario"] is None:
    st.session_state["autenticado"] = False

# ==========================================
# 4. BASE DE DATOS EN SUPABASE
# ==========================================
def init_db():
    if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
        return None, "❌ Las llaves de Supabase no se encuentran en los Secrets."
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key), "OK"
    except Exception as e:
        return None, f"❌ Error de conexión al servidor: {e}"

supabase, db_estado = init_db()

def cargar_usuarios():
    if not supabase: return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}
    try:
        res = supabase.table("usuarios").select("*").execute()
        if not res.data:
            supabase.table("usuarios").insert({"usuario": "admin", "pwd": "solar123", "rol": "admin", "estado": "active", "planta_asignada": "Todas"}).execute()
            return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}
        return {r["usuario"]: {"pwd": r["pwd"], "status": r["estado"], "role": r["rol"], "planta_asignada": r["planta_asignada"]} for r in res.data}
    except: return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}

def cargar_plantas():
    if supabase:
        try: return supabase.table("plantas").select("*").order("id").execute().data
        except: return []
    return []

def guardar_planta(nueva):
    if not supabase: return False, db_estado
    try: 
        supabase.table("plantas").insert(nueva).execute()
        return True, ""
    except Exception as e: 
        return False, str(e)

def eliminar_planta(idx):
    if supabase:
        try:
            plantas = cargar_plantas()
            if idx < len(plantas):
                supabase.table("plantas").delete().eq("id", plantas[idx]["id"]).execute()
        except: pass

# ==========================================
# 5. LOGIN
# ==========================================
if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #f1c40f !important;'>☀️ MONISOLAR APP</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white !important;'>Plataforma de Gestión - CV INGENIERÍA SAS</h3><br>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        with st.form("login"):
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                db = cargar_usuarios()
                if u in db and str(db[u]["pwd"]) == p:
                    st.session_state.update({"autenticado": True, "usuario": u, "rol": db[u]["role"], "planta_asignada": db[u].get("planta_asignada", "Todas")})
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# ==========================================
# 6. FILTRADO Y NAVEGACIÓN
# ==========================================
todas_las_plantas = cargar_plantas()
plantas_permitidas = todas_las_plantas if st.session_state['rol'] == 'admin' else [pl for pl in todas_las_plantas if pl.get("nombre") == st.session_state.get("planta_asignada")]

st.sidebar.markdown("<h2 style='text-align: center; color: #f1c40f !important;'>☀️ MONISOLAR APP</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("Ir a:", ["🌐 Panorama General", "📊 Panel de Planta", "🚨 Centro de Alertas"] if st.session_state['rol'] == 'admin' else ["📊 Panel de Mi Planta"])

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.update({"autenticado": False})
    st.rerun()

# ==========================================
# VISTAS
# ==========================================
if menu == "🌐 Panorama General":
    st.title("🌐 PANORAMA GENERAL")
    
    if st.session_state.get("mostrar_crear"):
        with st.form("crear"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nombre de la Planta")
            n_ubi = c2.text_input("Ubicación")
            n_cap = c1.text_input("Capacidad (Solo número)")
            n_sn = c2.text_input("SN Datalogger")
            if st.form_submit_button("💾 Guardar"):
                num_cap = float(re.findall(r"\d+\.?\d*", str(n_cap))[0]) if re.findall(r"\d+\.?\d*", str(n_cap)) else 0.0
                guardar_planta({"nombre": str(n_nom), "ubicacion": str(n_ubi), "capacidad": num_cap, "datalogger": str(n_sn), "tipo_sistema": "Híbrido"})
                st.session_state["mostrar_crear"] = False
                st.rerun()
    
    if st.button("Crear una planta", type="primary"):
        st.session_state["mostrar_crear"] = True
        st.rerun()

    for i, pl in enumerate(plantas_permitidas):
        st.markdown(f"""<div class="tarjeta-dash-pro"><b>{pl['nombre']}</b> | {pl['ubicacion']} | {pl['capacidad']} kW</div>""", unsafe_allow_html=True)

elif "Panel" in menu:
    if not plantas_permitidas: st.warning("Sin plantas asignadas.")
    else:
        sel = st.selectbox("Seleccionar:", [p['nombre'] for p in plantas_permitidas])
        p = next(x for x in plantas_permitidas if x['nombre'] == sel)
        d = {"solar": random.randint(1000, 15000), "casa": random.randint(500, 8000), "soc": random.randint(20, 100), "hoy": random.uniform(10, 50)}

        # --- TARJETAS ---
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='solarman-card'><h3>{d['hoy']:.1f} kWh</h3><p>Generación Hoy</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='solarman-card'><h3>{d['hoy']*0.4:.1f} kWh</h3><p>Consumo Hoy</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='solarman-card'><h3>{d['soc']}%</h3><p>SOC Batería</p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='solarman-card'><h3>0 W</h3><p>Red Eléctrica</p></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- FILA SUPERIOR: GRÁFICA DE FLUJO DETALLADA (IZQ) Y DIAGRAMA EN VIVO (DER) ---
        col_grafica, col_flujo = st.columns([7.5, 2.5])
        
        with col_grafica:
            st.markdown("<div style='background:white; border-radius:8px; padding:15px; border:1px solid #eaeaea; box-shadow: 0 4px 10px rgba(0,0,0,0.03);'>", unsafe_allow_html=True)
            t = pd.date_range(start="00:00", end="23:45", freq="15min")
            g = [max(0, 20000 * math.sin(i/len(t) * math.pi) * random.uniform(0.8, 1.1)) for i in range(len(t))]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t, y=g, fill='tozeroy', line=dict(color='#3498db'), name='Potencia solar'))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_flujo:
            # BLOQUE UNIFICADO: CUADRO BLANCO + DIAGRAMA SVG (Arreglado para el espacio amarillo)
            html_flujo = f"""
            <div style="background:white; border-radius:8px; padding:15px; border:1px solid #eaeaea; box-shadow: 0 4px 10px rgba(0,0,0,0.03); display: flex; align-items: center; justify-content: center; height: 400px; box-sizing: border-box;">
                <svg viewBox="0 0 400 400" width="100%" height="100%" style="max-height: 380px;">
                    <path d="M 80 130 V 180 H 130" fill="none" stroke="#7f8c8d" stroke-width="3" stroke-dasharray="5,5"/>
                    <path d="M 320 130 V 180 H 270" fill="none" stroke="#7f8c8d" stroke-width="3" stroke-dasharray="5,5"/>
                    <path d="M 80 230 V 220 H 130" fill="none" stroke="#7f8c8d" stroke-width="3" stroke-dasharray="5,5"/>
                    <path d="M 320 230 V 220 H 270" fill="none" stroke="#7f8c8d" stroke-width="3" stroke-dasharray="5,5"/>
                    
                    <image href="https://img.icons8.com/color/48/solar-panel--v1.png" x="50" y="70" width="60" height="60"/>
                    <text x="80" y="60" text-anchor="middle" font-size="14" font-weight="bold" fill="#2c3e50">Producción</text>
                    <text x="80" y="150" text-anchor="middle" font-size="12" fill="#3498db">{d['solar']} W</text>
                    
                    <image href="https://img.icons8.com/ios/48/576574/transmission-tower.png" x="290" y="70" width="60" height="60"/>
                    <text x="320" y="60" text-anchor="middle" font-size="14" font-weight="bold" fill="#2c3e50">Red</text>
                    <text x="320" y="150" text-anchor="middle" font-size="12" fill="#7f8c8d">0 W</text>
                    
                    <image href="https://img.icons8.com/color/48/home.png" x="290" y="240" width="60" height="60"/>
                    <text x="320" y="320" text-anchor="middle" font-size="14" font-weight="bold" fill="#2c3e50">Consumo</text>
                    <text x="320" y="340" text-anchor="middle" font-size="12" fill="#e74c3c">{d['casa']} W</text>

                    <rect x="135" y="170" width="130" height="80" rx="5" fill="#ffffff" stroke="#2c3e50" stroke-width="2"/>
                    <text x="200" y="215" text-anchor="middle" font-size="14" font-weight="bold" fill="#2c3e50">Deye HV</text>
                    
                    <rect x="55" y="240" width="50" height="30" rx="3" fill="#2ecc71"/>
                    <text x="80" y="290" text-anchor="middle" font-size="14" font-weight="bold" fill="#2c3e50">Batería</text>
                    <text x="80" y="310" text-anchor="middle" font-size="12" fill="#27ae60">{d['soc']}%</text>
                </svg>
            </div>
            """
            components.html(html_flujo, height=420)

        # --- FILA INFERIOR: RESUMEN Y MANTENIMIENTO ---
        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Mantenimiento", "Exportar"])
        with tab1: st.write("Programar limpieza de paneles.")
        with tab2: st.button("Generar PDF")

elif menu == "🚨 Centro de Alertas":
    st.title("🚨 CENTRO DE ALERTAS")
    st.success("✅ Todo operando normal.")
