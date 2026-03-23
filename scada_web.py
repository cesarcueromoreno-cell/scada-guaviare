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
# 1. CONFIGURACIÓN INICIAL Y FONDO VISUAL
# ==========================================
st.set_page_config(page_title="MOMISOLAR APP", page_icon="☀️", layout="wide") 

# --- MANEJO DE ACCIONES DE BOTONES HTML (LÁPIZ Y PAPELERA) ---
if "delete" in st.query_params:
    try:
        idx = int(st.query_params["delete"])
        def eliminar_planta_directo(indice):
            if os.path.exists('plantas.json'):
                with open('plantas.json', 'r') as f: plantas = json.load(f)
                if 0 <= indice < len(plantas):
                    plantas.pop(indice)
                    with open('plantas.json', 'w') as f: json.dump(plantas, f)
        eliminar_planta_directo(idx)
        st.query_params.clear()
    except: pass

if "edit" in st.query_params:
    try:
        idx = int(st.query_params["edit"])
        st.session_state["editando_planta"] = idx
        st.query_params.clear()
    except: pass
# -------------------------------------------------------------

css_global = """
<style>
/* FONDO DE LA APLICACIÓN */
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=1920");
    background-size: cover; background-position: center; background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }

/* CONTENEDOR CENTRAL TRANSPARENTE */
.block-container, [data-testid="stMainBlockContainer"], div[data-testid="block-container"] {
    background-color: transparent !important; border: none !important; box-shadow: none !important; backdrop-filter: none !important;
}

/* TEXTOS POR DEFECTO PARA EL PAISAJE */
h1, h2, h3, h4, h5, p, .stMarkdown span { color: #ffffff !important; text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important; }
label, label p, label div { color: #ffffff !important; text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important; }
[data-testid="stAlert"] { background-color: rgba(255, 255, 255, 0.95) !important; border-radius: 10px !important; box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important; }
[data-testid="stAlert"] * { color: #2c3e50 !important; text-shadow: none !important; }
[data-testid="stExpanderDetails"] { background-color: #ffffff !important; }
[data-testid="stExpanderDetails"] * { color: #2c3e50 !important; text-shadow: none !important; }

/* MENÚ LATERAL (OSCURO) */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #112027 0%, #1a323c 50%, #162a33 100%) !important;
    border-right: 1px solid #2c5364 !important; box-shadow: 4px 0 15px rgba(0,0,0,0.5) !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; text-shadow: none !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] div:first-child { background-color: transparent !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div { background-color: #e74c3c !important; border-color: #e74c3c !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div div { background-color: #e74c3c !important; }
[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p { font-weight: bold !important; font-size: 15px !important; }
[data-testid="stSidebar"] [data-testid="stAlert"] { background-color: rgba(0, 0, 0, 0.3) !important; border: 1px solid #f1c40f !important; border-left: 5px solid #f1c40f !important; border-radius: 8px !important; }
[data-testid="stSidebar"] [data-testid="stAlert"] * { color: #f1c40f !important; font-weight: bold !important; letter-spacing: 1px !important; }

/* ESTILIZAR EL FORMULARIO DE LOGIN COMO CRISTAL */
[data-testid="stForm"] { background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(10px) !important; border-radius: 12px !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important; }
.tarjeta-planta *, input, select, textarea, button span { color: #2c3e50 !important; text-shadow: none !important; }

/* ESTILO DASHBOARD LISTA */
.dashboard-dash-base { background-color: #f0f2f5 !important; border-radius: 15px !important; padding: 25px !important; margin-bottom: 20px !important; }
.dashboard-dash-base h1, .dashboard-dash-base h2, .dashboard-dash-base h3, .dashboard-dash-base p { color: #2c3e50 !important; text-shadow: none !important; }
.tarjeta-dash-pro { background-color: #ffffff !important; padding: 15px !important; border-radius: 8px !important; margin-bottom: 10px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important; display: flex !important; align-items: center !important; justify-content: space-between !important; }
.tarjeta-dash-item { margin: 0 15px !important; }
.tarjeta-label-pro { font-size: 11px !important; color: #7f8c8d !important; text-transform: uppercase !important; margin-bottom: 2px !important; white-space: nowrap !important; }
.tarjeta-dato-pro { font-size: 16px !important; font-weight: bold !important; color: #2c3e50 !important; white-space: nowrap !important; }
</style>
"""
st.markdown(css_global, unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'
ARCHIVO_USUARIOS = 'usuarios.json'
ARCHIVO_MANTENIMIENTOS = 'mantenimientos.json'

def cargar_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'w') as f: json.dump({"admin": {"pwd": "solar123", "status": "active", "role": "admin"}}, f)
    with open(ARCHIVO_USUARIOS, 'r') as f: db = json.load(f)
    datos_actualizados = False
    for user, data in db.items():
        if isinstance(data, str):
            db[user] = {"pwd": data, "status": "active", "role": "admin" if user == "admin" else "viewer"}
            datos_actualizados = True
    if "admin" in db and isinstance(db["admin"], dict):
        if db["admin"].get("role") != "admin" or db["admin"].get("status") != "active":
            db["admin"]["role"] = "admin"
            db["admin"]["status"] = "active"
            datos_actualizados = True
    if datos_actualizados:
        with open(ARCHIVO_USUARIOS, 'w') as f: json.dump(db, f)
    return db

def solicitar_usuario(u, p):
    db = cargar_usuarios()
    if u in db: return False, "⚠️ Usuario existente o pendiente."
    db[u] = {"pwd": p, "status": "pending", "role": "viewer"}
    with open(ARCHIVO_USUARIOS, 'w') as f: json.dump(db, f)
    return True, "✅ Solicitud enviada. Espere aprobación."

def gestionar_solicitud(u, aprobar=True):
    db = cargar_usuarios()
    if u in db and db[u]["status"] == "pending":
        if aprobar: db[u]["status"], db[u]["role"] = "active", "viewer"
        else: del db[u]
        with open(ARCHIVO_USUARIOS, 'w') as f: json.dump(db, f)
        return True
    return False

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [{"nombre": "Cancha las malvinas off grid", "ubicacion": "Barranquilla", "capacidad": "30 kWp", "inversores": "Deye", "datalogger": "2412120039", "bat_marca": "Deye", "bat_tipo": "Modo Litio"}]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(inicial, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

def guardar_planta(nueva):
    pl = cargar_plantas()
    pl.append(nueva)
    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(pl, f)

def cargar_mantenimientos():
    if not os.path.exists(ARCHIVO_MANTENIMIENTOS):
        with open(ARCHIVO_MANTENIMIENTOS, 'w') as f: json.dump({}, f)
    with open(ARCHIVO_MANTENIMIENTOS, 'r') as f: return json.load(f)

def guardar_mantenimiento(pl, d):
    m = cargar_mantenimientos()
    if pl not in m: m[pl] = []
    m[pl].append(d)
    with open(ARCHIVO_MANTENIMIENTOS, 'w') as f: json.dump(m, f)

def actualizar_estado_mantenimiento(pl, i, est):
    m = cargar_mantenimientos()
    if pl in m and 0 <= i < len(m[pl]):
        m[pl][i]["estado"] = est
        with open(ARCHIVO_MANTENIMIENTOS, 'w') as f: json.dump(m, f)

def eliminar_mantenimiento(pl, i):
    m = cargar_mantenimientos()
    if pl in m and 0 <= i < len(m[pl]):
        m[pl].pop(i)
        with open(ARCHIVO_MANTENIMIENTOS, 'w') as f: json.dump(m, f)

if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "usuario_actual" not in st.session_state: st.session_state["usuario_actual"] = None
if "rol_usuario" not in st.session_state: st.session_state["rol_usuario"] = None
if "editando_planta" not in st.session_state: st.session_state["editando_planta"] = None

# ==========================================
# PANTALLA DE LOGIN
# ==========================================
if not st.session_state["autenticado"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #f1c40f !important; text-shadow: 2px 2px 5px rgba(0,0,0,1) !important;'>☀️ MOMISOLAR APP</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white !important; text-shadow: 2px 2px 5px rgba(0,0,0,1) !important;'>Plataforma de Gestión - CV INGENIERÍA SAS</h3><br>", unsafe_allow_html=True)
    col1, col_centro, col2 = st.columns([1, 1.5, 1]) 
    with col_centro:
        with st.form("login_form"):
            st.markdown("<div style='color:white; font-weight:bold; font-size:14px; text-shadow: 1px 1px 3px black;'>👤 Correo / Usuario</div>", unsafe_allow_html=True)
            u_in = st.text_input("Usuario", label_visibility="collapsed")
            st.markdown("<div style='color:white; font-weight:bold; font-size:14px; margin-top:10px; text-shadow: 1px 1px 3px black;'>🔑 Contraseña</div>", unsafe_allow_html=True)
            p_in = st.text_input("Contraseña", type="password", label_visibility="collapsed") 
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                db = cargar_usuarios()
                if u_in in db and db[u_in]["pwd"] == p_in:
                    if db[u_in]["status"] == "pending": st.warning("⚠️ Cuenta pendiente de aprobación.")
                    else:
                        st.session_state.update({"autenticado": True, "usuario_actual": u_in, "rol_usuario": db[u_in]["role"]})
                        st.rerun() 
                else: st.error("❌ Credenciales incorrectas.")
        with st.expander("¿No tienes cuenta? Solicita acceso aquí"):
            with st.form("sol_form"):
                n_u = st.text_input("👤 Correo / Usuario")
                n_p = st.text_input("🔑 Contraseña", type="password")
                c_p = st.text_input("🔑 Confirmar Contraseña", type="password")
                if st.form_submit_button("Enviar Solicitud", use_container_width=True):
                    if not n_u or not n_p: st.error("⚠️ Complete campos.")
                    elif n_p != c_p: st.error("⚠️ Contraseñas no coinciden.")
                    else:
                        s, m = solicitar_usuario(n_u, n_p)
                        if s: st.success(m)
                        else: st.error(m)
    st.stop() 

# --- MOTOR SIMULADOR ---
def obtener_datos_reales(planta):
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(planta.get("capacidad", "5")))[0]) * 1000 if re.findall(r"[-+]?\d*\.\d+|\d+", str(planta.get("capacidad", "5"))) else 5000
    p_sol = int(cap * random.uniform(0.1, 0.8))
    e_dia = round((p_sol * random.uniform(3.5, 5.0)) / 1000, 1)
    soc = random.randint(15, 99) 
    al = ["⚠️ Batería Baja (SOC<=25%)"] if soc <= 25 else []
    return {"solar": p_sol, "casa": 1750 + random.randint(-40, 40), "soc": soc, "energia_diaria": e_dia, "status": "Simulado", "alertas": al}

def simular_historico_24h(cap_val):
    inicio_dia = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    datos = []
    for m in range(0, 24 * 60, 15):
        t = inicio_dia + timedelta(minutes=m)
        h = t.hour
        gen = max(0, (cap_val * 0.9) * math.sin((h - 6) / 12 * math.pi) * random.uniform(0.95, 1.05)) if 6 <= h <= 18 else 0
        con = max(cap_val * 0.1, cap_val * 0.2 + (cap_val * 0.3 * math.sin((h-7)/2 * math.pi) if 7<=h<=9 else (cap_val * 0.4 * math.sin((h-18)/3 * math.pi) if 18<=h<=21 else 0)))
        datos.append({"timestamp": t, "Generación FV": round(gen, 2), "Consumo Carga": round(con, 2)})
    return pd.DataFrame(datos)

plantas_guardadas = cargar_plantas()

# ==========================================
# 3. NAVEGACIÓN PRINCIPAL
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #f1c40f !important; text-shadow: none !important;'>☀️ MOMISOLAR APP</h2>", unsafe_allow_html=True)
r_act, u_act = st.session_state["rol_usuario"], st.session_state["usuario_actual"]
st.sidebar.write(f"🧑🏽‍💻 Usuario: **{u_act}**\n\n🛡️ Rol: **{'Instalador/Admin' if r_act == 'admin' else 'Cliente'}**\n\nIr a:")

opc = ["🌐 Panorama General", "📊 Panel de Planta", "🚨 Centro de Alertas"]
if r_act == "admin": opc += ["👥 Gestión de Usuarios", "🏢 Gestión de Portafolio"]
menu = st.sidebar.radio("Navegación", opc, label_visibility="collapsed")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.update({"autenticado": False, "usuario_actual": None, "rol_usuario": None})
    st.rerun()
st.sidebar.info("**POWERED BY:**\n\n**CV INGENIERIA SAS**")

# ==========================================
# CSS DINÁMICO PARA PANEL BLANCO
# ==========================================
if menu == "📊 Panel de Planta":
    st.markdown("""
    <style>
    .block-container { background-color: #f4f7f9 !important; backdrop-filter: none !important; border-radius: 0px !important; }
    [data-testid="stMainBlockContainer"] * { text-shadow: none !important; }
    [data-testid="stMainBlockContainer"] h1, h2, h3, h4, h5, p, span, label, div { color: #2c3e50 !important; }
    div[data-testid="stTabs"] > div[data-baseweb="tab-list"] { background-color: transparent !important; border-bottom: 1px solid #e0e0e0 !important; gap: 15px !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"] p, div[data-testid="stTabs"] button[data-baseweb="tab"] span { color: #7f8c8d !important; font-weight: 600 !important; font-size: 15px !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"] { border: none !important; border-bottom: 3px solid transparent !important; border-radius: 0 !important; box-shadow: none !important; padding-bottom: 10px !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #e74c3c !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p, div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] span { color: #2c3e50 !important; }
    .solarman-card { background: #ffffff !important; border-radius: 8px !important; padding: 20px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important; text-align: center !important; border: 1px solid #eaeaea !important; }
    .solarman-val { font-size: 26px !important; font-weight: bold !important; margin-bottom: 5px !important; }
    .solarman-lbl { font-size: 13px !important; text-transform: uppercase !important; }
    
    /* DETALLES DE INVERSOR Y TABLAS INTERNAS */
    .detalles-box { background: white; border: 1px solid #eaeaea; border-radius: 6px; padding: 15px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .detalles-title { font-size: 16px; font-weight: bold; border-bottom: 1px solid #eaeaea; padding-bottom: 10px; margin-bottom: 10px; color:#2c3e50; }
    .detalles-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }
    .det-item { display: flex; flex-direction: column; }
    .det-lbl { font-size: 12px; color: #7f8c8d; }
    .det-val { font-size: 14px; font-weight: 500; color: #2c3e50; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# VENTANA 1: PANORAMA GENERAL
# ==========================================
if menu == "🌐 Panorama General":
    st.title("🌐 PANORAMA GENERAL")
    st.markdown("**MOMISOLAR APP - Vista global rápida**")
    
    if st.session_state.get("editando_planta") is not None:
        idx = st.session_state["editando_planta"]
        if idx < len(plantas_guardadas):
            p_edit = plantas_guardadas[idx]
            st.markdown("<div style='background:rgba(255,255,255,0.95); padding:20px; border-radius:10px; margin-bottom:20px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:#2c3e50 !important; text-shadow:none !important;'>✏️ Editar Parámetros: {p_edit['nombre']}</h3>", unsafe_allow_html=True)
            with st.form("edit_form"):
                c1, c2 = st.columns(2)
                st.markdown("<style>input {color: #2c3e50 !important; text-shadow:none !important;}</style>", unsafe_allow_html=True)
                n_nom = c1.text_input("Nombre", value=p_edit["nombre"])
                n_ubi = c2.text_input("Ubicación", value=p_edit["ubicacion"])
                n_cap = c1.text_input("Capacidad", value=p_edit["capacidad"])
                n_inv = c2.selectbox("Marca", ["Deye", "GoodWe", "Fronius", "Sylvania"], index=0)
                n_sn = st.text_input("SN Datalogger", value=p_edit.get("datalogger", ""))
                s1, s2 = st.columns(2)
                if s1.form_submit_button("💾 Guardar"):
                    plantas_guardadas[idx].update({"nombre": n_nom, "ubicacion": n_ubi, "capacidad": n_cap, "inversores": n_inv, "datalogger": n_sn})
                    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas_guardadas, f)
                    st.session_state["editando_planta"] = None
                    st.rerun()
                if s2.form_submit_button("❌ Cancelar"):
                    st.session_state["editando_planta"] = None
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if not plantas_guardadas: st.warning("No hay plantas.")
    else:
        c_esp, c_bus = st.columns([2, 1])
        busqueda = c_bus.text_input("🔍 Buscar planta", label_visibility="collapsed")
        filtradas = [pl for pl in plantas_guardadas if busqueda.lower() in pl['nombre'].lower() or busqueda.lower() in pl['ubicacion'].lower()]

        st.markdown('<div style="overflow-x: auto; padding-bottom: 15px;"><div style="min-width: 1050px;">', unsafe_allow_html=True)
        st.markdown(f'<div style="background:#ffffff; border-radius: 8px; padding: 10px 15px; margin-bottom: 10px; display: flex; align-items: center; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);"><div style="color: #3498db; font-size:16px; margin-right:10px;">☀️</div><div style="font-weight:bold; color: #2c3e50;">Listado Activo (Total {len(filtradas)})</div></div>', unsafe_allow_html=True)
        
        for i, pl in enumerate(filtradas):
            dat = obtener_datos_reales(pl)
            cap = f"{re.findall(r'[-+]?\d*\.\d+|\d+', str(pl.get('capacidad', '0')))[0]} kWp" if re.findall(r'[-+]?\d*\.\d+|\d+', str(pl.get('capacidad', '0'))) else "N/A"
            icon_al = f"<div style='position:absolute; top:5px; left:15px; background: #e74c3c; color:white; font-size:9px; padding: 2px 6px; border-radius:10px;'>{len(dat['alertas'])} Alertas</div>" if dat["alertas"] else ""
            btn_acc = f'<div style="display: flex; gap: 8px; width: 60px; flex-shrink: 0;"><a href="?edit={i}" title="Editar"><img src="https://img.icons8.com/material-rounded/24/edit.png" style="width:20px; opacity:0.7;"/></a><a href="?delete={i}" title="Eliminar"><img src="https://img.icons8.com/material-rounded/24/filled-trash.png" style="width:20px; opacity:0.7;"/></a></div>' if r_act == "admin" else "<div style='width: 60px; flex-shrink: 0;'></div>"
            
            st.markdown(f"""
            <div class="tarjeta-dash-pro" style="position:relative;">{icon_al}
                <div style="display:flex; align-items:center; width: 320px; flex-shrink: 0;">
                    <img src="https://img.icons8.com/color/48/solar-panel.png" style="width: 32px; margin-right:15px; border-radius:4px;"/>
                    <div><div style="font-size: 15px; font-weight: bold; color: #2c3e50;">{pl['nombre']}</div><div style="font-size: 12px; color: #7f8c8d;">📍 {pl['ubicacion']}</div></div>
                </div>
                <div class="tarjeta-dash-item" style="text-align: center; width: 50px; flex-shrink: 0;"><div class="tarjeta-label-pro">Com</div><div style="font-size:16px;">📶</div></div>
                <div class="tarjeta-dash-item" style="text-align: center; width: 60px; flex-shrink: 0;"><div class="tarjeta-label-pro">Alertas</div><div style="font-size:16px;">{'🔴' if dat['alertas'] else '🟢'}</div></div>
                <div class="tarjeta-dash-item" style="width: 140px; flex-shrink: 0;"><div class="tarjeta-label-pro">Capacidad</div><div class="tarjeta-dato-pro">{cap}</div></div>
                <div class="tarjeta-dash-item" style="width: 160px; flex-shrink: 0;"><div class="tarjeta-label-pro">Potencia Solar Actual</div><div class="tarjeta-dato-pro">{dat['solar']} W</div></div>
                <div class="tarjeta-dash-item" style="width: 150px; flex-shrink: 0;"><div class="tarjeta-label-pro">Producción Diaria</div><div class="tarjeta-dato-pro" style="color: #27ae60 !important;">{dat['energia_diaria']} kWh</div></div>
                {btn_acc}
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True) 

# ==========================================
# VENTANA 2: PANEL DE PLANTA (EL MONSTRUO)
# ==========================================
elif menu == "📊 Panel de Planta":
    if not plantas_guardadas: st.warning("No hay plantas registradas.")
    else:
        col_tit, col_sel = st.columns([2, 1])
        planta_sel = col_sel.selectbox("Planta:", [p["nombre"] for p in plantas_guardadas], label_visibility="collapsed")
        d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
        dat = obtener_datos_reales(d)
        
        # 1. ENCABEZADO IDÉNTICO A SOLARMAN
        st.markdown(f"<h2>{d['nombre']} <span style='font-size:14px; color:#7f8c8d; font-weight:normal;'>| 🟢 En línea | SN: {d.get('datalogger', '2412120039')}</span></h2><hr style='margin-top:0px; margin-bottom:20px; border-color:#e0e0e0;'>", unsafe_allow_html=True)

        # 2. KPIS SUPERIORES (4 CAJAS BLANCAS)
        p_sol, c_sim = dat["energia_diaria"], round(dat["energia_diaria"] * 0.45, 1)
        c_bat, d_bat = round(p_sol * 0.2, 1), round(p_sol * 0.1, 1)
        
        c1, c2, c3, c4 = st.columns([1.5, 1.5, 1, 1])
        c1.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#2c3e50;'>{p_sol} kWh</div><div class='solarman-lbl' style='color:#7f8c8d;'>Producción Solar</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#2c3e50;'>{c_sim} kWh</div><div class='solarman-lbl' style='color:#7f8c8d;'>Consumo</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='solarman-card'><div style='font-size:14px; font-weight:bold; color:#2c3e50;'>🔋 {c_bat} kWh <span style='color:#7f8c8d; font-size:10px;'>Cargar</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>🔋 {d_bat} kWh <span style='color:#7f8c8d; font-size:10px;'>Descargar</span></div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='solarman-card'><div style='font-size:14px; font-weight:bold; color:#2c3e50;'>⚡ 0 kWh <span style='color:#7f8c8d; font-size:10px;'>A Red</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>⚡ 0 kWh <span style='color:#7f8c8d; font-size:10px;'>De Red</span></div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 3. DEFINICIÓN DINÁMICA DE TABS SEGÚN FOTOS
        if r_act == "admin":
            tabs = st.tabs(["📈 Panel Gráfico y Flujo", "💻 Dispositivos y Detalles", "⚙️ Control Remoto del Inversor", "📄 Reportes y Datos", "🛠️ Agenda de O&M"])
            t_graf, t_disp, t_ctrl, t_rep, t_om = tabs
        else:
            tabs = st.tabs(["📈 Panel Gráfico y Flujo", "💻 Dispositivos y Detalles", "📄 Reportes y Datos"])
            t_graf, t_disp, t_rep = tabs
            t_ctrl, t_om = None, None

        # --- TAB 1: GRÁFICO Y FLUJO (COMO EN LA FOTO) ---
        with t_graf:
            cg1, cg2 = st.columns([7, 3])
            with cg1:
                st.markdown("<div style='background:white; border-radius:8px; padding:15px; border:1px solid #eaeaea;'>", unsafe_allow_html=True)
                df_h = simular_historico_24h(d)
                fig = px.area(df_h, x="timestamp", y=["Generación FV", "Consumo Carga"], color_discrete_map={"Generación FV": "#3498db", "Consumo Carga": "#e74c3c"})
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text=None, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis=dict(tickformat="%H:%M", dtick=2 * 3600000, gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0"), margin=dict(l=10, r=10, t=10, b=10), height=380)
                fig.update_traces(fill='tozeroy', mode='lines', line=dict(width=2))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with cg2:
                # Flujo y Beneficios
                svg = f"""<div style="background: white; border-radius: 8px; padding: 20px; border: 1px solid #eaeaea; height: 100%; display: flex; align-items: center; justify-content:center; margin-bottom:15px;"><svg viewBox="0 0 300 300" width="100%">
                <path d="M 150 70 V 130 M 150 170 V 230 M 90 150 H 130 M 170 150 H 210" fill="none" stroke="#e8eaec" stroke-width="3"/>
                <circle r="4" fill="#3498db"><animateMotion dur="1s" repeatCount="indefinite" path="M 150 70 V 130" /></circle>
                <circle r="4" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 130 150 H 90" /></circle>
                <rect x="130" y="130" width="40" height="40" rx="4" fill="#2c3e50"/> 
                <g transform="translate(130, 20)"><image href="https://img.icons8.com/color/48/solar-panel.png" width="40" height="40"/><text x="20" y="55" font-size="12" font-weight="bold" fill="#3498db" text-anchor="middle">{dat['solar']} W</text></g>
                <g transform="translate(230, 130)"><image href="https://img.icons8.com/fluency/48/electrical.png" width="40" height="40" opacity="0.5"/><text x="20" y="55" font-size="12" font-weight="bold" fill="#7f8c8d" text-anchor="middle">0 W</text></g>
                <g transform="translate(30, 130)"><image href="https://img.icons8.com/color/48/car-battery.png" width="40" height="40"/><text x="20" y="55" font-size="12" font-weight="bold" fill="#27ae60" text-anchor="middle">{dat['solar'] - dat['casa']} W</text><text x="20" y="-5" font-size="11" font-weight="bold" fill="#2c3e50" text-anchor="middle">SOC: {dat['soc']}%</text></g>
                <g transform="translate(130, 240)"><image href="https://img.icons8.com/color/48/home.png" width="40" height="40"/><text x="20" y="55" font-size="12" font-weight="bold" fill="#e74c3c" text-anchor="middle">{dat['casa']} W</text></g></svg></div>"""
                components.html(svg, height=300)
                
                st.markdown("""<div style="background:white; border:1px solid #eaeaea; border-radius:8px; padding:15px;"><div style="font-size:14px; font-weight:bold; color:#2c3e50; margin-bottom:10px;">Beneficios ambientales 🌍</div><div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span style="color:#7f8c8d; font-size:12px;">Ahorro de carbón</span><span style="font-weight:bold; color:#2c3e50; font-size:13px;">0.54 t</span></div><div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span style="color:#7f8c8d; font-size:12px;">Reducción CO2</span><span style="font-weight:bold; color:#2c3e50; font-size:13px;">1.42 t</span></div><div style="display:flex; justify-content:space-between;"><span style="color:#7f8c8d; font-size:12px;">Árboles plantados</span><span style="font-weight:bold; color:#2c3e50; font-size:13px;">97.6 u</span></div></div>""", unsafe_allow_html=True)

        # --- TAB 2: DISPOSITIVOS Y DETALLES (NUEVO CLON DE FOTO) ---
        with t_disp:
            st.markdown("<h4 style='color:#2c3e50;'>Lista de Dispositivos en Planta</h4>", unsafe_allow_html=True)
            tb_d = f"""
            <table style="width:100%; border-collapse:collapse; background:white; border:1px solid #eaeaea; border-radius:8px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.05); text-align:left;">
                <tr style="background:#f8f9fa; border-bottom:1px solid #eaeaea; color:#7f8c8d; font-size:13px;"><th style="padding:10px;">Nombre/SN</th><th style="padding:10px;">Estado</th><th style="padding:10px;">Sistema</th><th style="padding:10px;">Potencia solar(kW)</th></tr>
                <tr style="border-bottom:1px solid #eaeaea; color:#2c3e50; font-size:14px;"><td style="padding:12px;"><b>inversor 1.1</b><br><span style="color:#7f8c8d; font-size:11px;">{d.get('datalogger', '2412120039')}</span></td><td style="padding:12px; color:#27ae60;">🟢 En línea</td><td style="padding:12px;">{d['nombre']}</td><td style="padding:12px;">{round(dat['solar']/1000, 2)}</td></tr>
            </table><br>
            """
            st.markdown(tb_d, unsafe_allow_html=True)

            st.markdown("<h4 style='color:#2c3e50;'>Detalles del Inversor Seleccionado</h4>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="detalles-box">
                <div class="detalles-title">Información básica</div>
                <div class="detalles-grid">
                    <div class="det-item"><span class="det-lbl">NS (Número de Serie)</span><span class="det-val">{d.get('datalogger', '2412120039')}</span></div>
                    <div class="det-item"><span class="det-lbl">Tipo de inversor</span><span class="det-val">Híbrido HV trifásico ({d['inversores']})</span></div>
                    <div class="det-item"><span class="det-lbl">Potencia nominal</span><span class="det-val">{d['capacidad']}</span></div>
                </div>
            </div>
            
            <div class="detalles-box">
                <div class="detalles-title">Información de versión</div>
                <div class="detalles-grid">
                    <div class="det-item"><span class="det-lbl">Versión protocolo</span><span class="det-val">0104</span></div>
                    <div class="det-item"><span class="det-lbl">PRINCIPAL</span><span class="det-val">3103-1086-1E10</span></div>
                    <div class="det-item"><span class="det-lbl">HMI</span><span class="det-val">2001-C036</span></div>
                    <div class="det-item"><span class="det-lbl">Arc Board Firmware Version</span><span class="det-val">F204</span></div>
                    <div class="det-item"><span class="det-lbl">Número de versión de batería de litio</span><span class="det-val">4101</span></div>
                </div>
            </div>
            
            <div class="detalles-box">
                <div class="detalles-title">Generación eléctrica en tiempo real</div>
                <table style="width:100%; border-collapse:collapse; text-align:center;">
                    <tr style="color:#7f8c8d; font-size:12px; border-bottom:1px solid #eaeaea;"><th>Canal</th><th>Voltaje (V)</th><th>Corriente (A)</th><th>Potencia (W)</th><th>Estado</th></tr>
                    <tr style="color:#3498db; font-size:14px; font-weight:bold; padding-top:10px;"><td style="padding-top:10px;">PV1</td><td style="padding-top:10px;">467.70 V</td><td style="padding-top:10px;">{(dat['solar']/467.7):.2f} A</td><td style="padding-top:10px;">{dat['solar']} W</td><td style="padding-top:10px;">✔️</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

        # --- TAB 3: CONTROL REMOTO (CONFIGURACIÓN PROFUNDA DE FOTO) ---
        if t_ctrl:
            with t_ctrl:
                st.info(f"⚙️ Configurando inversor **{d['inversores']}** de la planta '{d['nombre']}'. Proceda con precaución.")
                
                s_t1, s_t2, s_t3 = st.tabs(["🔋 Configuración Baterías", "⚡ Configuración de la red", "🕒 Funciones Avanzadas"])
                
                with s_t1:
                    st.markdown("<div style='font-size:12px; color:#7f8c8d; margin-bottom:15px;'>* El grupo de comandos actual debe configurarse como un todo.</div>", unsafe_allow_html=True)
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.selectbox("* Tipo de Batería", ["Modo Litio", "Plomo-Ácido", "Sin Batería"], index=0)
                    c2.number_input("* Capacidad de la Batería (Ah)", value=100)
                    c3.number_input("* Max A Carga (A)", value=50)
                    c4.number_input("* Max A Descarga (A)", value=50)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    c5, c6, c7, c8 = st.columns(4)
                    c5.number_input("* Batería Desconexión %", value=10)
                    c6.number_input("* Batería Reconexión %", value=35)
                    c7.number_input("* Batería Baja %", value=20)
                    c8.selectbox("* Paralelo bat1&bat2", ["Deshabilitado", "Habilitado"], index=0)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    c9, c10, c11, c12 = st.columns(4)
                    c9.selectbox("* Carga de Red", ["Deshabilitado", "Habilitado"], index=0)
                    c10.selectbox("* Carga de Generador", ["Deshabilitado", "Habilitado"], index=0)
                    c11.selectbox("* Señal de Red", ["Deshabilitado", "Habilitado"], index=0)
                    c12.selectbox("* Señal de Generador", ["Deshabilitado", "Habilitado"], index=0)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    c13, c14, c15, c16 = st.columns(4)
                    c13.selectbox("* Fuerza General", ["Deshabilitado", "Habilitado"], index=0)
                    c14.number_input("* Máx Tiempo de Operación Gen (h)", value=0.0)
                    c15.number_input("* Tiempo parada Gen (h)", value=0.0)

                with s_t2:
                    col_g1, col_g2 = st.columns(2)
                    col_g1.selectbox("* Normativa Aplicada", ["Colombia (RETIE / NTC 2050)", "IEEE 1547", "IEC 61727"])
                    col_g2.slider("* Límite de Inyección a red (%) - Zero Export", min_value=0, max_value=100, value=0)
                    st.markdown("<br><b>Protecciones AC (V y Hz)</b>", unsafe_allow_html=True)
                    cv1, cv2, cf1, cf2 = st.columns(4)
                    cv1.number_input("Sobre Tensión (V)", value=253.0)
                    cv2.number_input("Sub Tensión (V)", value=198.0)
                    cf1.number_input("Sobre Frecuencia (Hz)", value=60.5)
                    cf2.number_input("Sub Frecuencia (Hz)", value=59.5)

                with s_t3:
                    st.checkbox("Habilitar Carga Inteligente")
                    ct1, ct2 = st.columns(2)
                    ct1.time_input("Inicio de carga forzada", value=datetime.strptime("00:00", "%H:%M"))
                    ct2.time_input("Fin de carga forzada", value=datetime.strptime("05:00", "%H:%M"))
                    st.slider("SOC Objetivo para carga desde la red (%)", min_value=10, max_value=100, value=100)

                st.markdown("<br>", unsafe_allow_html=True)
                b1, b2 = st.columns([8, 2])
                with b2:
                    if st.button("Configurar (Enviar Comando)", type="primary", use_container_width=True):
                        with st.spinner("Estableciendo conexión..."): time.sleep(2)
                        st.success("¡Comandos enviados correctamente!")

        # --- TAB 4: REPORTES ---
        with t_rep:
            st.markdown("### 📄 Descarga de Datos Históricos")
            df_i = pd.DataFrame({"Fecha Consulta": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")], "Planta": [d['nombre']], "SOC %": [dat['soc']], "Producción Diaria (kWh)": [p_sol]})
            st.download_button("📥 Exportar Datos (CSV)", data=df_i.to_csv(index=False).encode('utf-8-sig'), file_name=f"Reporte_{d['nombre']}.csv", mime="text/csv")

        # --- TAB 5: MANTENIMIENTO ---
        if t_om:
            with t_om:
                st.markdown("<h3 style='color:#2c3e50;'>📅 Agenda de O&M</h3>", unsafe_allow_html=True)
                with st.form("f_mant"):
                    mc1, mc2, mc3 = st.columns([2, 1, 1])
                    m_tipo = mc1.selectbox("Tipo de Tarea", ["Limpieza de Paneles", "Revisión Baterías", "Mantenimiento Inversor", "Garantía"])
                    m_fecha = mc2.date_input("Fecha")
                    m_resp = mc3.text_input("Técnico", placeholder="Ej: Carlos M.")
                    m_notas = st.text_input("Observaciones")
                    if st.form_submit_button("➕ Agendar Mantenimiento", use_container_width=True):
                        guardar_mantenimiento(d['nombre'], {"fecha": str(m_fecha), "tipo": m_tipo, "resp": m_resp, "notas": m_notas, "estado": "⏳ Pendiente"})
                        st.rerun()
                
                st.markdown("<br><h4>📋 Historial</h4>", unsafe_allow_html=True)
                mants = cargar_mantenimientos().get(d['nombre'], [])
                if not mants: st.info("Sin mantenimientos.")
                else:
                    for i, m in enumerate(reversed(mants)):
                        r_idx = len(mants) - 1 - i
                        st.markdown(f"<div style='background:white; padding:15px; border-radius:8px; border:1px solid #eaeaea; margin-bottom:10px;'><b>{m['tipo']}</b> - {m['estado']}<br><span style='font-size:12px; color:#7f8c8d;'>📅 {m['fecha']} | 👨‍🔧 {m['resp']} | 📝 {m['notas']}</span></div>", unsafe_allow_html=True)
                        c_btn1, c_btn2, _ = st.columns([1,1,8])
                        if m['estado'] == "⏳ Pendiente" and c_btn1.button("✅", key=f"ok_{r_idx}"):
                            actualizar_estado_mantenimiento(d['nombre'], r_idx, "✅ Completado")
                            st.rerun()
                        if c_btn2.button("🗑️", key=f"del_{r_idx}"):
                            eliminar_mantenimiento(d['nombre'], r_idx)
                            st.rerun()

# ==========================================
# VENTANAS 3, 4, 5 (RESTO DE MÓDULOS)
# ==========================================
elif menu == "🏢 Gestión de Portafolio" and r_act == "admin":
    st.title("🏢 CONFIGURACIÓN DE PROYECTOS")
    with st.expander("1️⃣ Añadir Planta", expanded=True):
        with st.form("f_planta"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nombre de Planta")
            n_ubi = c2.text_input("Ubicación")
            n_cap = c1.text_input("Capacidad (kWp)")
            n_inv = c2.selectbox("Inversor", ["Deye", "GoodWe", "Huawei", "Sylvania"])
            n_sn = c1.text_input("SN Datalogger")
            if st.form_submit_button("Crear Planta"):
                if n_nom:
                    guardar_planta({"nombre": n_nom, "ubicacion": n_ubi, "capacidad": n_cap, "inversores": n_inv, "datalogger": n_sn})
                    st.success("Planta creada.")

elif menu == "🚨 Centro de Alertas":
    st.title("🚨 ALERTAS")
    al_tot = 0
    for pl in plantas_guardadas:
        dat = obtener_datos_reales(pl)
        if dat["alertas"]:
            st.warning(f"**{pl['nombre']}**: {', '.join(dat['alertas'])}")
            al_tot += 1
    if al_tot == 0: st.success("Todo en orden.")

elif menu == "👥 Gestión de Usuarios" and r_act == "admin":
    st.title("👥 GESTIÓN DE USUARIOS")
    db_u = cargar_usuarios()
    pendientes = [(u, d) for u, d in db_u.items() if d["status"] == "pending"]
    activos = [(u, d) for u, d in db_u.items() if d["status"] == "active"]
    
    st.markdown("### Solicitudes Pendientes")
    for i, (u, d) in enumerate(pendientes):
        c1, c2, c3 = st.columns([4,1,1])
        c1.write(f"**{u}** solicita acceso.")
        if c2.button("Aprobar", key=f"ap_{i}"):
            gestionar_solicitud(u, True)
            st.rerun()
        if c3.button("Rechazar", key=f"re_{i}"):
            gestionar_solicitud(u, False)
            st.rerun()
    st.markdown("---")
    st.dataframe(pd.DataFrame([{"Usuario": u, "Rol": d["role"], "Estado": d["status"]} for u, d in activos]), use_container_width=True)
