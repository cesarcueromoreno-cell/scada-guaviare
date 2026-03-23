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

# --- MANEJO DE ACCIONES DE BOTONES HTML ---
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
    background-size: cover; 
    background-position: center; 
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }

/* CONTENEDOR CENTRAL TRANSPARENTE */
.block-container, [data-testid="stMainBlockContainer"], div[data-testid="block-container"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
}

/* TEXTO BLANCO CON SOMBRA NEGRA POR DEFECTO PARA EL PAISAJE */
h1, h2, h3, h4, h5, p, .stMarkdown span {
    color: #ffffff !important;
    text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important;
}
label, label p, label div {
    color: #ffffff !important;
    text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important;
}

/* CAJAS DE INFORMACIÓN CENTRALES (ALERTAS) */
[data-testid="stAlert"] {
    background-color: rgba(255, 255, 255, 0.95) !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
}
[data-testid="stAlert"] * {
    color: #2c3e50 !important;
    text-shadow: none !important;
}

/* CORRECCIÓN: FORZAR TEXTO NEGRO DENTRO DE LOS FORMULARIOS BLANCOS (EXPANDERS) */
[data-testid="stExpanderDetails"] {
    background-color: #ffffff !important;
}
[data-testid="stExpanderDetails"] * {
    color: #2c3e50 !important;
    text-shadow: none !important;
}

/* DISEÑO DEL MENÚ LATERAL (OSCURO) */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #112027 0%, #1a323c 50%, #162a33 100%) !important;
    border-right: 1px solid #2c5364 !important;
    box-shadow: 4px 0 15px rgba(0,0,0,0.5) !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
    text-shadow: none !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] div:first-child {
    background-color: transparent !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div {
    background-color: #e74c3c !important; 
    border-color: #e74c3c !important;
}
[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] input:checked + div div {
    background-color: #e74c3c !important; 
}
[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
    font-weight: bold !important;
    font-size: 15px !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background-color: rgba(0, 0, 0, 0.3) !important;
    border: 1px solid #f1c40f !important;
    border-left: 5px solid #f1c40f !important;
    border-radius: 8px !important;
    box-shadow: 0 0 10px rgba(241, 196, 15, 0.1) !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] * {
    color: #f1c40f !important; 
    font-weight: bold !important;
    letter-spacing: 1px !important;
}

/* ELEMENTOS DE INPUT NATIVOS */
.tarjeta-planta *, input, select, textarea, button span {
    color: #2c3e50 !important;
    text-shadow: none !important;
}

/* ESTILIZAR EL FORMULARIO DE LOGIN COMO CRISTAL */
[data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
}

/* ESTILO DASHBOARD PRO (LISTA DE PLANTAS) */
.dashboard-dash-base {
    background-color: #f0f2f5 !important; 
    border-radius: 15px !important;
    padding: 25px !important;
    box-shadow: inset 0 0 15px rgba(0,0,0,0.1) !important;
    margin-bottom: 20px !important;
}
.dashboard-dash-base h1, .dashboard-dash-base h2, .dashboard-dash-base h3, .dashboard-dash-base p {
    color: #2c3e50 !important;
    text-shadow: none !important;
}
.tarjeta-dash-pro {
    background-color: #ffffff !important; 
    padding: 15px !important; 
    border-radius: 8px !important; 
    margin-bottom: 10px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
}
.tarjeta-dash-item { margin: 0 15px !important; }
.tarjeta-label-pro {
    font-size: 11px !important; color: #7f8c8d !important; text-transform: uppercase !important;
    margin-bottom: 2px !important; white-space: nowrap !important;
}
.tarjeta-dato-pro {
    font-size: 16px !important; font-weight: bold !important; color: #2c3e50 !important; white-space: nowrap !important;
}

/* DISEÑO PARA ICONOS GRISES (LÁPIZ Y PAPELERA) */
.iconos-accion .stButton button {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    color: #7f8c8d !important; 
    font-size: 20px !important;
    transition: transform 0.2s ease, color 0.2s ease !important;
}
.iconos-accion .stButton button:hover {
    color: #2c3e50 !important; 
    transform: scale(1.1) !important;
}
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
        with open(ARCHIVO_USUARIOS, 'w') as f: 
            json.dump({"admin": {"pwd": "solar123", "status": "active", "role": "admin"}}, f)
    with open(ARCHIVO_USUARIOS, 'r') as f: db = json.load(f)
    datos_actualizados = False
    for user, data in db.items():
        if isinstance(data, str):
            rol_asignado = "admin" if user == "admin" else "viewer"
            db[user] = {"pwd": data, "status": "active", "role": rol_asignado}
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
        inicial = [{
            "nombre": "Planta Principal", "ubicacion": "Guaviare", "capacidad": "13.92 kWp", 
            "inversores": "Híbrido Multimarca", "datalogger": "SN: CV-001", 
            "bat_marca": "Deye/Pylontech", "bat_tipo": "Litio (LiFePO4)"
        }]
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

def simular_historico_24h(planta):
    cap_texto = str(planta.get("capacidad", "5"))
    solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
    try: cap_val = float(solo_numeros[0]) if solo_numeros else 5.0
    except: cap_val = 5.0
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
# CSS DINÁMICO
# ==========================================
if menu == "📊 Panel de Planta":
    st.markdown("""
    <style>
    .block-container { background-color: #f4f7f9 !important; backdrop-filter: none !important; border-radius: 0px !important; }
    [data-testid="stMainBlockContainer"] * { text-shadow: none !important; }
    [data-testid="stMainBlockContainer"] h1, [data-testid="stMainBlockContainer"] h2, [data-testid="stMainBlockContainer"] h3, [data-testid="stMainBlockContainer"] h4, [data-testid="stMainBlockContainer"] h5, [data-testid="stMainBlockContainer"] p, [data-testid="stMainBlockContainer"] span, [data-testid="stMainBlockContainer"] label, [data-testid="stMainBlockContainer"] div { color: #2c3e50 !important; }
    div[data-testid="stTabs"] > div[data-baseweb="tab-list"] { background-color: transparent !important; border-bottom: 1px solid #e0e0e0 !important; gap: 15px !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"] p, div[data-testid="stTabs"] button[data-baseweb="tab"] span { color: #7f8c8d !important; font-weight: 600 !important; font-size: 15px !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"] { border: none !important; border-bottom: 3px solid transparent !important; border-radius: 0 !important; box-shadow: none !important; padding-bottom: 10px !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #e74c3c !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p, div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] span { color: #2c3e50 !important; }
    .solarman-card { background: #ffffff !important; border-radius: 8px !important; padding: 20px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important; text-align: center !important; border: 1px solid #eaeaea !important; }
    .solarman-val { font-size: 26px !important; font-weight: bold !important; margin-bottom: 5px !important; }
    .solarman-lbl { font-size: 13px !important; text-transform: uppercase !important; }
    .iconos-accion .stButton button { border: none !important; background: transparent !important; box-shadow: none !important; padding: 0 !important; color: #7f8c8d !important; font-size: 20px !important; }
    .iconos-accion .stButton button:hover { color: #2c3e50 !important; transform: scale(1.1) !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# VENTANA 1: PANORAMA GENERAL
# ==========================================
if menu == "🌐 Panorama General":
    st.title("🌐 PANORAMA GENERAL")
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
                n_inv = c2.selectbox("Marca", ["Deye", "GoodWe", "Huawei", "Sylvania"], index=0)
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
        c_bus = st.text_input("🔍 Buscar planta", placeholder="Ingrese nombre o ciudad...", label_visibility="collapsed")
        filtradas = [pl for pl in plantas_guardadas if c_bus.lower() in pl['nombre'].lower() or c_bus.lower() in pl['ubicacion'].lower()]
        st.markdown('<div style="overflow-x: auto; padding-bottom: 15px;"><div style="min-width: 1050px;">', unsafe_allow_html=True)
        for i, pl in enumerate(filtradas):
            dat = obtener_datos_reales(pl)
            col_card, col_btns = st.columns([11, 1])
            with col_card:
                st.markdown(f"""<div class="tarjeta-dash-pro" style="position:relative;">
                <div style="display:flex; align-items:center; width: 320px; flex-shrink: 0;"><img src="https://img.icons8.com/color/48/solar-panel.png" style="width: 32px; margin-right:15px;"/><div style="font-size: 15px; font-weight: bold; color: #2c3e50;">{pl['nombre']}</div></div>
                <div class="tarjeta-dash-item"><div class="tarjeta-label-pro">Potencia Solar</div><div class="tarjeta-dato-pro">{dat['solar']} W</div></div>
                <div class="tarjeta-dash-item"><div class="tarjeta-label-pro">Energía Hoy</div><div class="tarjeta-dato-pro" style="color:#27ae60 !important;">{dat['energia_diaria']} kWh</div></div>
                </div>""", unsafe_allow_html=True)
            with col_btns:
                if r_act == "admin":
                    st.markdown("<div class='iconos-accion'>", unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    if b1.button("✎", key=f"ed_{i}"): st.session_state["editando_planta"] = i; st.rerun()
                    if b2.button("🗑", key=f"dl_{i}"):
                        plantas_guardadas.pop(i)
                        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas_guardadas, f)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

# ==========================================
# VENTANA 2: PANEL DE PLANTA
# ==========================================
elif menu == "📊 Panel de Planta":
    if not plantas_guardadas: st.warning("No hay plantas.")
    else:
        pl_sel = st.selectbox("Planta:", [p["nombre"] for p in plantas_guardadas], label_visibility="collapsed")
        d = next(p for p in plantas_guardadas if p["nombre"] == pl_sel)
        dat = obtener_datos_reales(d)
        st.markdown(f"<h2>{d['nombre']} <span style='font-size:14px; color:#7f8c8d;'>| SN: {d.get('datalogger', 'N/A')}</span></h2><hr>", unsafe_allow_html=True)
        
        # KPIS
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#3498db;'>{dat['energia_diaria']} kWh</div><div class='solarman-lbl'>Solar</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#e67e22;'>{round(dat['energia_diaria']*0.45, 1)} kWh</div><div class='solarman-lbl'>Consumo</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='solarman-card'><div style='font-size:14px; font-weight:bold;'>🔋 {round(dat['energia_diaria']*0.2, 1)} kWh Cargar</div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='solarman-card'><div style='font-size:14px; font-weight:bold;'>⚡ 0 kWh Red</div></div>", unsafe_allow_html=True)

        if r_act == "admin":
            tabs = st.tabs(["📈 Gráfica", "⚙️ Control Remoto", "📄 Reportes", "🛠️ O&M"])
            with tabs[1]:
                st.info(f"⚙️ Configurando inversor **{d['inversores']}**")
                sub_tabs = st.tabs([
                    "🔋 Configuración Baterías", "🔄 Modos de operación-1", "🔄 Modos de operación-2", 
                    "⚡ Configuración de la red", "🧠 Carga inteligente", "⚙️ Configuración Básica", 
                    "🛠️ Funciones Avanzadas-1", "🛠️ Funciones Avanzadas-2"
                ])
                
                # --- PESTAÑA 1: Config Baterías ---
                with sub_tabs[0]:
                    st.markdown("<div style='font-size:12px; color:#7f8c8d; margin-bottom:15px;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</div>", unsafe_allow_html=True)
                    cb1, cb2, cb3, cb4, cb5 = st.columns(5)
                    cb1.selectbox("* Tipo de Batería", ["Modo Litio", "Plomo-Ácido"], index=0)
                    cb2.number_input("* Capacidad (Ah)", value=100)
                    cb3.number_input("* Max A Carga", value=50)
                    cb4.number_input("* Max A Descarga", value=50)
                    cb5.number_input("* Desconexión %", value=10)
                
                # --- PESTAÑA 2: Modos 1 ---
                with sub_tabs[1]:
                    st.markdown("<div style='font-size:12px; color:#7f8c8d; margin-bottom:15px;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</div>", unsafe_allow_html=True)
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.selectbox("* Modos de Operación", ["Seleccione", "Autoconsumo"])
                    with m2:
                        st.markdown("<div style='font-size: 14px;'>* Configuración</div>", unsafe_allow_html=True)
                        st.checkbox("Lunes"); st.checkbox("Martes"); st.checkbox("Miércoles")
                    m3.number_input("* Máxima Potencia Solar (W)", value=5000)
                    m4.number_input("* Máx Inyección Red (W)", value=5000)
                    m5.selectbox("* Patrón de Energía", ["Seleccione", "Prioridad Carga"])

                # --- PESTAÑA 3: Modos 2 ---
                with sub_tabs[2]:
                    st.toggle("* FuncionamientoporPeriodos", value=False)

                # --- PESTAÑA 4: Red ---
                with sub_tabs[3]:
                    st.markdown("<div style='color:#f39c12; font-weight:bold;'>🔒 Para configurar la red, introduzca la contraseña</div>", unsafe_allow_html=True)
                    st.text_input("Contraseña", type="password", label_visibility="collapsed")
                    st.button("Desbloquear")

                # --- PESTAÑA 5: SmartLoad ---
                with sub_tabs[4]:
                    cs1, cs2, cs3 = st.columns(3)
                    cs1.selectbox("* Configuración de SmartLoad", ["Seleccione", "SmartLoad"])
                    cs2.selectbox("* Par de CA red", ["Seleccione", "Habilitar"])
                    cs3.selectbox("* Par de CA carga", ["Seleccione", "Habilitar"])

                # --- PESTAÑA 8: FUNCIONES AVANZADAS-2 (CLONADA DE TU FOTO) ---
                with sub_tabs[7]:
                    st.markdown("<div style='font-size:12px; color:#7f8c8d; margin-bottom:15px;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</div>", unsafe_allow_html=True)
                    st.markdown("<div style='color: #2c3e50; font-weight: bold;'>Configuración Baterías</div>", unsafe_allow_html=True)
                    av2_1, av2_2, av2_3 = st.columns([1, 1, 2])
                    av2_1.selectbox("* DC 1 para turbina eólica", ["Seleccione", "Habilitado", "Deshabilitado"])
                    av2_2.empty()
                    av2_3.empty()

                # BOTONES INFERIORES COMO EN SOLARMAN
                st.markdown("<br>", unsafe_allow_html=True)
                b_esp, b_mira, b_conf = st.columns([8, 1, 1])
                with b_mira: st.button("Mirada lasciva")
                with b_conf: st.button("Configurar", type="primary")

elif menu == "🚨 Centro de Alertas":
    st.title("🚨 ALERTAS")
    st.success("Sistemas operando con normalidad.")
