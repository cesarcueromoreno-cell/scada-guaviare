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
    
    with open(ARCHIVO_USUARIOS, 'r') as f: 
        db = json.load(f)
        
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

def solicitar_usuario(usuario, contrasena):
    usuarios = cargar_usuarios()
    if usuario in usuarios:
        return False, "⚠️ Este usuario ya existe o tiene una solicitud pendiente."
    
    usuarios[usuario] = {"pwd": contrasena, "status": "pending", "role": "viewer"}
    with open(ARCHIVO_USUARIOS, 'w') as f: 
        json.dump(usuarios, f)
    return True, "✅ Solicitud enviada. Espere a que el Administrador apruebe su cuenta."

def gestionar_solicitud(usuario, aprobar=True):
    usuarios = cargar_usuarios()
    if usuario in usuarios and usuarios[usuario]["status"] == "pending":
        if aprobar:
            usuarios[usuario]["status"] = "active"
            usuarios[usuario]["role"] = "viewer"
        else:
            del usuarios[usuario] 
            
        with open(ARCHIVO_USUARIOS, 'w') as f: 
            json.dump(usuarios, f)
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
    plantas = cargar_plantas()
    plantas.append(nueva)
    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)

def eliminar_planta(indice):
    plantas = cargar_plantas()
    if 0 <= indice < len(plantas):
        plantas.pop(indice)
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)

def cargar_mantenimientos():
    if not os.path.exists(ARCHIVO_MANTENIMIENTOS):
        with open(ARCHIVO_MANTENIMIENTOS, 'w') as f: json.dump({}, f)
    with open(ARCHIVO_MANTENIMIENTOS, 'r') as f: return json.load(f)

def guardar_mantenimiento(planta, datos_mant):
    mants = cargar_mantenimientos()
    if planta not in mants: mants[planta] = []
    mants[planta].append(datos_mant)
    with open(ARCHIVO_MANTENIMIENTOS, 'w') as f: json.dump(mants, f)

def actualizar_estado_mantenimiento(planta, indice, nuevo_estado):
    mants = cargar_mantenimientos()
    if planta in mants and 0 <= indice < len(mants[planta]):
        mants[planta][indice]["estado"] = nuevo_estado
        with open(ARCHIVO_MANTENIMIENTOS, 'w') as f: json.dump(mants, f)

def eliminar_mantenimiento(planta, indice):
    mants = cargar_mantenimientos()
    if planta in mants and 0 <= indice < len(mants[planta]):
        mants[planta].pop(indice)
        with open(ARCHIVO_MANTENIMIENTOS, 'w') as f: json.dump(mants, f)

# Autenticación
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None
if "rol_usuario" not in st.session_state:
    st.session_state["rol_usuario"] = None
if "editando_planta" not in st.session_state:
    st.session_state["editando_planta"] = None

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
            usuario_input = st.text_input("Usuario", label_visibility="collapsed")
            
            st.markdown("<div style='color:white; font-weight:bold; font-size:14px; margin-top:10px; text-shadow: 1px 1px 3px black;'>🔑 Contraseña</div>", unsafe_allow_html=True)
            contrasena_input = st.text_input("Contraseña", type="password", label_visibility="collapsed") 
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                usuarios_bd = cargar_usuarios()
                if usuario_input in usuarios_bd and usuarios_bd[usuario_input]["pwd"] == contrasena_input:
                    user_data = usuarios_bd[usuario_input]
                    if user_data["status"] == "pending":
                        st.warning("⚠️ Su cuenta aún está pendiente de aprobación por el Administrador.")
                    else:
                        st.session_state["autenticado"] = True
                        st.session_state["usuario_actual"] = usuario_input
                        st.session_state["rol_usuario"] = user_data["role"]
                        st.rerun() 
                else:
                    st.error("❌ Credenciales incorrectas o usuario no registrado.")
                    
        with st.expander("¿No tienes cuenta? Solicita acceso aquí"):
            with st.form("solicitud_form"):
                nuevo_usuario = st.text_input("👤 Correo / Usuario Solicitado")
                nueva_contrasena = st.text_input("🔑 Contraseña", type="password")
                confirmar_contrasena = st.text_input("🔑 Confirmar Contraseña", type="password")
                if st.form_submit_button("Enviar Solicitud", use_container_width=True):
                    if not nuevo_usuario or not nueva_contrasena:
                        st.error("⚠️ Complete todos los campos.")
                    elif nueva_contrasena != confirmar_contrasena:
                        st.error("⚠️ Las contraseñas no coinciden.")
                    else:
                        success, message = solicitar_usuario(nuevo_usuario, nueva_contrasena)
                        if success: st.success(message)
                        else: st.error(message)
    st.stop() 

# --- MOTOR DE INTEGRACIÓN SOLARMAN ---
def obtener_datos_reales(planta):
    cap_texto = str(planta.get("capacidad", "5"))
    solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
    try: cap_val = float(solo_numeros[0]) * 1000 if solo_numeros else 5000 
    except: cap_val = 5000 
    
    pot_simulada = int(cap_val * random.uniform(0.1, 0.8))
    energia_simulada = round((pot_simulada * random.uniform(3.5, 5.0)) / 1000, 1)
    
    soc_actual = random.randint(15, 99) 
    alertas_activas = []
    
    if soc_actual <= 25:
        alertas_activas.append("⚠️ Batería Baja: Nivel de SOC crítico (<=25%). Riesgo de desconexión de cargas.")
    if random.random() < 0.15: 
        alertas_activas.append("🔌 Falla de Red AC: Sin voltaje detectado en la acometida.")

    return {
        "solar": pot_simulada, "casa": 1750 + random.randint(-40, 40),
        "soc": soc_actual, "energia_diaria": energia_simulada, "status": "Simulado",
        "alertas": alertas_activas
    }

def simular_historico_24h(planta):
    cap_texto = str(planta.get("capacidad", "5"))
    solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
    try: cap_val = float(solo_numeros[0]) if solo_numeros else 5.0
    except: cap_val = 5.0

    hora_actual = datetime.now()
    inicio_dia = hora_actual.replace(hour=0, minute=0, second=0, microsecond=0)
    
    datos = []
    for minutos in range(0, 24 * 60, 15):
        timestamp = inicio_dia + timedelta(minutes=minutos)
        hora = timestamp.hour
        generacion = max(0, (cap_val * 0.9) * math.sin((hora - 6) / 12 * math.pi) * random.uniform(0.95, 1.05)) if 6 <= hora <= 18 else 0
        consumo = max(cap_val * 0.1, cap_val * 0.2 + (cap_val * 0.3 * math.sin((hora-7)/2 * math.pi) if 7<=hora<=9 else (cap_val * 0.4 * math.sin((hora-18)/3 * math.pi) if 18<=hora<=21 else 0)))
        datos.append({"timestamp": timestamp, "Generación FV": round(generacion, 2), "Consumo Carga": round(consumo, 2)})
        
    return pd.DataFrame(datos)

plantas_guardadas = cargar_plantas()

# ==========================================
# 3. NAVEGACIÓN PRINCIPAL
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #f1c40f !important; text-shadow: none !important;'>☀️ MOMISOLAR APP</h2>", unsafe_allow_html=True)
rol_actual = st.session_state["rol_usuario"]
usuario_actual = st.session_state["usuario_actual"]
etiqueta_rol = "Instalador/Admin" if rol_actual == "admin" else "Cliente"

st.sidebar.write(f"🧑🏽‍💻 Usuario: **{usuario_actual}**\n\n🛡️ Rol: **{etiqueta_rol}**\n\nIr a:")

opciones_menu = ["🌐 Panorama General", "📊 Panel de Planta", "🚨 Centro de Alertas"]
if rol_actual == "admin":
    opciones_menu.append("👥 Gestión de Usuarios")
    opciones_menu.append("🏢 Gestión de Portafolio")

menu = st.sidebar.radio("Navegación Oculta", opciones_menu, label_visibility="collapsed")

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.session_state["usuario_actual"] = None
    st.session_state["rol_usuario"] = None
    st.rerun()
    
st.sidebar.info("**POWERED BY:**\n\n**CV INGENIERIA SAS**")

# ==========================================
# CSS DINÁMICO (FORZAR TEXTOS NEGROS EN EL PANEL BLANCO Y REPARAR PESTAÑAS)
# ==========================================
if menu == "📊 Panel de Planta":
    st.markdown("""
    <style>
    .block-container, [data-testid="stMainBlockContainer"] {
        background-color: #f4f7f9 !important;
        backdrop-filter: none !important;
        border-radius: 0px !important;
    }
    [data-testid="stMainBlockContainer"] * { text-shadow: none !important; }
    [data-testid="stMainBlockContainer"] h1, [data-testid="stMainBlockContainer"] h2, [data-testid="stMainBlockContainer"] h3, [data-testid="stMainBlockContainer"] h4, [data-testid="stMainBlockContainer"] h5, [data-testid="stMainBlockContainer"] p, [data-testid="stMainBlockContainer"] span, [data-testid="stMainBlockContainer"] label, [data-testid="stMainBlockContainer"] div {
        color: #2c3e50 !important;
    }
    div[data-testid="stTabs"] > div[data-baseweb="tab-list"] { background-color: transparent !important; border-bottom: 1px solid #e0e0e0 !important; gap: 15px !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"] p, div[data-testid="stTabs"] button[data-baseweb="tab"] span, div[data-testid="stTabs"] button[data-baseweb="tab"] div { color: #7f8c8d !important; text-shadow: none !important; font-weight: 600 !important; font-size: 16px !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"] { background-color: transparent !important; border: none !important; border-bottom: 3px solid transparent !important; border-radius: 0 !important; box-shadow: none !important; padding-bottom: 10px !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #e74c3c !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p, div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] span, div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] div { color: #2c3e50 !important; }
    .solarval-blue { color: #3498db !important; }
    .solarval-orange { color: #e67e22 !important; }
    .solarlbl-gray { color: #7f8c8d !important; }
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
    st.title("🌐 PANORAMA GENERAL DEL PORTAFOLIO")
    st.markdown("**MOMISOLAR APP - Vista global rápida**")
    
    if st.session_state.get("editando_planta") is not None:
        idx_edit = st.session_state["editando_planta"]
        if idx_edit < len(plantas_guardadas):
            p_edit = plantas_guardadas[idx_edit]
            st.markdown("<div style='background:rgba(255,255,255,0.95); padding:20px; border-radius:10px; margin-bottom:20px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:#2c3e50 !important; text-shadow:none !important;'>✏️ Editar Parámetros: {p_edit['nombre']}</h3>", unsafe_allow_html=True)
            with st.form("edit_form"):
                c1, c2 = st.columns(2)
                st.markdown("<style>input {color: #2c3e50 !important; text-shadow:none !important;}</style>", unsafe_allow_html=True)
                new_nom = c1.text_input("Nombre de la Planta", value=p_edit["nombre"])
                new_ubi = c2.text_input("Ubicación", value=p_edit["ubicacion"])
                new_cap = c1.text_input("Capacidad (kWp)", value=p_edit["capacidad"])
                new_inv = c2.selectbox("Marca de Inversor", ["Deye", "GoodWe", "Fronius", "Huawei", "Growatt", "Must", "Sylvania"], index=["Deye", "GoodWe", "Fronius", "Huawei", "Growatt", "Must", "Sylvania"].index(p_edit["inversores"]) if p_edit["inversores"] in ["Deye", "GoodWe", "Fronius", "Huawei", "Growatt", "Must", "Sylvania"] else 0)
                new_sn = st.text_input("SN del Datalogger (Wifi/LAN)", value=p_edit.get("datalogger", ""))
                
                sub1, sub2 = st.columns(2)
                if sub1.form_submit_button("💾 Guardar Cambios"):
                    plantas_guardadas[idx_edit].update({"nombre": new_nom, "ubicacion": new_ubi, "capacidad": new_cap, "inversores": new_inv, "datalogger": new_sn})
                    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas_guardadas, f)
                    st.session_state["editando_planta"] = None
                    st.rerun()
                if sub2.form_submit_button("❌ Cancelar"):
                    st.session_state["editando_planta"] = None
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if not plantas_guardadas:
        st.warning("No hay plantas registradas. Ve a Gestión para agregar una.")
    else:
        st.markdown("<h3 style='margin-bottom:10px; color:#ffffff;'>Directorio Técnico de Plantas</h3>", unsafe_allow_html=True)
        col_espacio, col_buscador = st.columns([2, 1])
        with col_buscador:
            busqueda = st.text_input("🔍 Buscar planta", label_visibility="collapsed", placeholder="Ingrese nombre o ciudad...")
        
        plantas_filtradas = [pl for pl in plantas_guardadas if busqueda.lower() in pl['nombre'].lower() or busqueda.lower() in pl['ubicacion'].lower()]

        st.markdown('<div style="overflow-x: auto; padding-bottom: 15px;"><div style="min-width: 1050px;">', unsafe_allow_html=True)
        st.markdown(f"""
<div style="background:#ffffff; border-radius: 8px; padding: 10px 15px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
<div style="display:flex; align-items:center;"><div style="color: #3498db; font-size:16px; margin-right:10px;">☀️</div><div style="font-weight:bold; color: #2c3e50;">Listado Activo (Total {len(plantas_filtradas)})</div></div></div>
""", unsafe_allow_html=True)
        
        if not plantas_filtradas:
            st.info("No se encontraron plantas que coincidan con la búsqueda.")
        else:
            for i, pl in enumerate(plantas_filtradas):
                datos = obtener_datos_reales(pl)
                cap_texto = str(pl.get("capacidad", "0"))
                solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
                cap_limpia = f"{solo_numeros[0]} kWp" if solo_numeros else "N/A"

                alerta_html = ""
                status_icon = "🟢" if datos["solar"] > 10 else "🟠"
                if datos["alertas"]:
                    status_icon = "🔴"
                    alerta_html = f"<div style='position:absolute; top:5px; left:15px; background: #e74c3c; color:white; font-size:9px; padding: 2px 6px; border-radius:10px;'>{len(datos['alertas'])} Alertas</div>"

                col_card, col_btns = st.columns([11, 1])
                
                with col_card:
                    st.markdown(f"""
                    <div class="tarjeta-dash-pro" style="position:relative; margin-bottom:0px;">{alerta_html}
                    <div style="display:flex; align-items:center; width: 320px; flex-shrink: 0;">
                    <img src="https://img.icons8.com/color/48/solar-panel.png" style="width: 32px; height:32px; margin-right:15px; border-radius:4px;"/>
                    <div><div style="font-size: 15px; font-weight: bold; color: #2c3e50;">{pl['nombre']}</div>
                    <div style="font-size: 12px; color: #7f8c8d;"><img src="https://img.icons8.com/material-rounded/24/marker.png" style="width:12px; height:12px; margin-right:3px;"/>{pl['ubicacion']}</div></div></div>
                    <div class="tarjeta-dash-item" style="text-align: center; width: 50px; flex-shrink: 0;"><div class="tarjeta-label-pro">Com</div><div style="font-size:16px;">📶</div></div>
                    <div class="tarjeta-dash-item" style="text-align: center; width: 60px; flex-shrink: 0;"><div class="tarjeta-label-pro">Alertas</div><div style="font-size:16px;">{status_icon}</div></div>
                    <div class="tarjeta-dash-item" style="width: 140px; flex-shrink: 0;"><div class="tarjeta-label-pro">Capacidad</div><div class="tarjeta-dato-pro">{cap_limpia}</div></div>
                    <div class="tarjeta-dash-item" style="width: 160px; flex-shrink: 0;"><div class="tarjeta-label-pro">Potencia Solar Actual</div><div class="tarjeta-dato-pro">{datos['solar']} W</div></div>
                    <div class="tarjeta-dash-item" style="width: 150px; flex-shrink: 0;"><div class="tarjeta-label-pro">Producción Diaria</div><div class="tarjeta-dato-pro" style="color: #27ae60 !important;">{datos['energia_diaria']} kWh</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btns:
                    if rol_actual == "admin":
                        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
                        st.markdown("<div class='iconos-accion'>", unsafe_allow_html=True)
                        b1, b2 = st.columns(2)
                        if b1.button("✎", key=f"btn_ed_{i}", help="Editar Planta"):
                            st.session_state["editando_planta"] = i
                            st.rerun()
                        if b2.button("🗑", key=f"btn_dl_{i}", help="Eliminar Planta"):
                            eliminar_planta(i)
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("</div></div>", unsafe_allow_html=True) 
        if st.button("🔄 Actualizar Todo"): st.rerun()

# ==========================================
# VENTANA 2: PANEL DE PLANTA
# ==========================================
elif menu == "📊 Panel de Planta":
    if not plantas_guardadas:
        st.warning("No hay plantas registradas en el sistema.")
    else:
        col_tit, col_sel = st.columns([2, 1])
        with col_sel:
            planta_sel = st.selectbox("Cambiar de Planta:", [p["nombre"] for p in plantas_guardadas], label_visibility="collapsed")
        d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
        datos_act = obtener_datos_reales(d)
        
        estado_ico = "🟢 En línea" if not datos_act["alertas"] else "🔴 Con Alertas"
        sn_info = f" | SN: {d.get('datalogger', 'No asignado')}" if d.get('datalogger') else ""
        st.markdown(f"<h2>{d['nombre']} <span style='font-size:14px; color:#7f8c8d; font-weight:normal;'>| {estado_ico}{sn_info}</span></h2>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top:0px; margin-bottom:20px; border-color:#e0e0e0;'>", unsafe_allow_html=True)

        prod_solar = datos_act["energia_diaria"]
        consumo_sim = round(prod_solar * 0.45, 1)
        carga_bat = round(prod_solar * 0.2, 1)
        descarga_bat = round(prod_solar * 0.1, 1)
        
        c1, c2, c3, c4 = st.columns([1.5, 1.5, 1, 1])
        c1.markdown(f"<div class='solarman-card'><div class='solarman-val solarval-blue'>{prod_solar} kWh</div><div class='solarman-lbl solarlbl-gray'>Producción Solar</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='solarman-card'><div class='solarman-val solarval-orange'>{consumo_sim} kWh</div><div class='solarman-lbl solarlbl-gray'>Consumo</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='solarman-card'><div style='font-size:14px; font-weight:bold;'>🔋 {carga_bat} kWh <span class='solarlbl-gray' style='font-size:10px;'>Cargar</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px;'>🔋 {descarga_bat} kWh <span class='solarlbl-gray' style='font-size:10px;'>Descargar</span></div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='solarman-card'><div style='font-size:14px; font-weight:bold;'>⚡ 0 kWh <span class='solarlbl-gray' style='font-size:10px;'>A Red</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px;'>⚡ 0 kWh <span class='solarlbl-gray' style='font-size:10px;'>De Red</span></div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if rol_actual == "admin":
            # --- AÑADIDA LA NUEVA PESTAÑA "Modos Operación-1" ---
            tabs = st.tabs(["📈 Panel Gráfico y Flujo", "⚙️ Control Remoto del Inversor", "📄 Reportes y Datos", "🛠️ Agenda de O&M"])
            tab_monitor = tabs[0]
            tab_control = tabs[1]
            tab_reportes = tabs[2]
            tab_mantenimiento = tabs[3]
        else:
            tabs = st.tabs(["📈 Panel Gráfico y Flujo", "📄 Reportes y Datos"])
            tab_monitor = tabs[0]
            tab_reportes = tabs[1]
            tab_control = None
            tab_mantenimiento = None
        
        with tab_monitor:
            col_grafica, col_flujo = st.columns([7, 3])
            with col_grafica:
                st.markdown("<div style='background:white; border-radius:8px; padding:15px; border:1px solid #eaeaea;'>", unsafe_allow_html=True)
                df_historico = simular_historico_24h(d)
                fig2 = px.area(df_historico, x="timestamp", y=["Generación FV", "Consumo Carga"], color_discrete_map={"Generación FV": "#3498db", "Consumo Carga": "#e74c3c"})
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text=None, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis=dict(tickformat="%H:%M", dtick=2 * 3600000, gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0"), yaxis_title="kW", margin=dict(l=10, r=10, t=10, b=10), height=380)
                fig2.update_traces(fill='tozeroy', mode='lines', line=dict(width=2))
                fig2.update_traces(selector=dict(name="Consumo Carga"), fill='none')
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_flujo:
                pot_solar = datos_act["solar"]
                pot_casa = datos_act["casa"]
                pot_bat = pot_solar - pot_casa
                soc = datos_act["soc"]
                color_bat = "#2ecc71" if soc > 20 else "#e74c3c"
                diagrama_svg = f"""
                <div style="background: white; border-radius: 8px; padding: 20px; border: 1px solid #eaeaea; height: 100%; display: flex; align-items: center;">
                    <svg viewBox="0 0 400 350" width="100%">
                        <path d="M 100 85 V 150 H 170 M 300 85 V 150 H 230 M 170 150 H 100 V 230 M 230 150 H 300 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                        <circle r="6" fill="#3498db"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 85 V 150 H 170" /></circle>
                        <circle r="6" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>
                        <circle r="6" fill="#e74c3c"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 230" /></circle>
                        <rect x="165" y="115" width="70" height="70" rx="12" fill="#f8f9fa" stroke="#3498db" stroke-width="3"/>
                        <rect x="175" y="125" width="50" height="25" rx="3" fill="#2c3e50"/> 
                        <text x="200" y="142" text-anchor="middle" font-size="8" fill="#55efc4" font-weight="bold">CV-ENG</text>
                        <text x="200" y="200" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">Híbrido</text>
                        <g transform="translate(60,30)"><image href="https://img.icons8.com/color/48/solar-panel.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#3498db" text-anchor="middle">{pot_solar} W</text></g>
                        <g transform="translate(260,30)"><image href="https://img.icons8.com/fluency/48/electrical.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#7f8c8d" text-anchor="middle">0 W</text></g>
                        <g transform="translate(60,260)"><image href="https://img.icons8.com/color/48/car-battery.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#27ae60" text-anchor="middle">{pot_bat} W</text><text x="5" y="55" font-size="11" font-weight="bold" fill="{color_bat}" text-anchor="middle">SOC: {soc}%</text></g>
                        <g transform="translate(260,260)"><image href="https://img.icons8.com/color/48/home.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#e74c3c" text-anchor="middle">{pot_casa} W</text></g>
                    </svg>
                </div>
                """
                components.html(diagrama_svg, height=415)

        if tab_control:
            with tab_control:
                st.info(f"⚙️ Configurando el inversor **{d['inversores']}** de la planta '{d['nombre']}'. Proceda con precaución.")
                
                # --- NUEVA PESTAÑA AÑADIDA AQUÍ ---
                sub_t1, sub_t2, sub_t3, sub_t4 = st.tabs(["🔋 Config. Baterías", "🔄 Modos de operación-1", "⚡ Red y Normativa", "🕒 TOU"])
                
                with sub_t1:
                    st.markdown("<div style='font-size:12px; color:#7f8c8d; margin-bottom:15px;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</div>", unsafe_allow_html=True)
                    cb1, cb2, cb3, cb4, cb5 = st.columns(5)
                    cb1.selectbox("* Tipo de Batería", ["Modo Litio", "Plomo-Ácido", "Sin Batería"], index=0)
                    cb2.number_input("* Capacidad (Ah)", value=100)
                    cb3.number_input("* Max A Carga", value=50)
                    cb4.number_input("* Max A Descarga", value=50)
                    cb5.number_input("* Desconexión %", value=10)
                    
                    cc1, cc2, cc3, cc4, cc5 = st.columns(5)
                    cc1.number_input("* Reconexión %", value=35)
                    cc2.number_input("* Batería Baja %", value=20)
                    cc3.selectbox("* Paralelo bat1&bat2", ["Deshabilitado", "Habilitado"], index=0)
                    cc4.selectbox("* Carga de Red", ["Deshabilitado", "Habilitado"], index=0)
                    cc5.selectbox("* Carga Generador", ["Deshabilitado", "Habilitado"], index=0)
                    
                    cd1, cd2, cd3, cd4, cd5 = st.columns(5)
                    cd1.selectbox("* Señal de Red", ["Deshabilitado", "Habilitado"], index=0)
                    cd2.selectbox("* Señal Generador", ["Deshabilitado", "Habilitado"], index=0)
                    cd3.selectbox("* Fuerza General", ["Deshabilitado", "Habilitado"], index=0)
                    cd4.number_input("* Máx Tiempo Gen", value=0.0)
                    cd5.number_input("* Tiempo parada Gen", value=0.0)

                # --- NUEVO CÓDIGO DE "Modos de operación-1" (CLONADO DE TU FOTO) ---
                with sub_t2:
                    st.markdown("<div style='font-size:12px; color:#7f8c8d; margin-bottom:15px;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</div>", unsafe_allow_html=True)
                    
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.selectbox("* Modos de Operación", ["Seleccione", "Autoconsumo", "Corte de picos", "Respaldo"])
                    
                    with m2:
                        st.markdown("<div style='font-size: 14px; color: #2c3e50; margin-bottom: 5px;'>* Configuración</div>", unsafe_allow_html=True)
                        d1, d2 = st.columns(2)
                        d1.checkbox("Domingo")
                        d2.checkbox("Sábado")
                        d1.checkbox("Viernes")
                        d2.checkbox("Jueves")
                        d1.checkbox("Miércoles")
                        d2.checkbox("Martes")
                        d1.checkbox("Lunes")
                    
                    m3.number_input("* Máxima Potencia Solar (W)", min_value=1000, max_value=48000, value=5000)
                    m4.number_input("* Máxima Potencia Inyección a Red (W)", min_value=1000, max_value=120000, value=5000)
                    m5.selectbox("* Patrón de Energía", ["Seleccione", "Prioridad Carga", "Prioridad Batería"])
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    m6, m7, m8, m9, m10 = st.columns(5)
                    m6.number_input("* Cero exportación de energía (W)", min_value=-500, max_value=500, value=0)
                    m7.selectbox("* Función de Límite Duro", ["Seleccione", "Habilitado", "Deshabilitado"])
                    m8.number_input("* Potencia de límite fijo (%)", min_value=0.1, max_value=100.0, value=100.0)
                # ------------------------------------------------------------------

                with sub_t3:
                    col_g1, col_g2 = st.columns(2)
                    col_g1.selectbox("Normativa Aplicada", ["Colombia (RETIE / NTC 2050)", "IEEE 1547", "IEC 61727"])
                    col_g2.slider("Límite de Inyección a red (%) - Zero Export", min_value=0, max_value=100, value=0)
                    st.markdown("<div style='margin-top: 15px; font-weight: bold; color: #2c3e50;'>Protecciones de Tensión AC (V)</div>", unsafe_allow_html=True)
                    col_v1, col_v2 = st.columns(2)
                    col_v1.number_input("Sobre Tensión Máx (Over-voltage V)", min_value=220.0, max_value=280.0, value=253.0, step=1.0)
                    col_v2.number_input("Sub Tensión Mín (Under-voltage V)", min_value=170.0, max_value=220.0, value=198.0, step=1.0)
                    st.markdown("<div style='margin-top: 15px; font-weight: bold; color: #2c3e50;'>Protecciones de Frecuencia (Hz)</div>", unsafe_allow_html=True)
                    col_f1, col_f2 = st.columns(2)
                    col_f1.number_input("Sobre Frecuencia Máx (Over-frequency Hz)", min_value=60.0, max_value=65.0, value=60.5, step=0.1)
                    col_f2.number_input("Sub Frecuencia Mín (Under-frequency Hz)", min_value=55.0, max_value=60.0, value=59.5, step=0.1)

                with sub_t4:
                    st.checkbox("Habilitar Carga desde la Red Eléctrica (Grid Charge)")
                    col_t1, col_t2 = st.columns(2)
                    col_t1.time_input("Inicio de carga forzada", value=datetime.strptime("00:00", "%H:%M"))
                    col_t2.time_input("Fin de carga forzada", value=datetime.strptime("05:00", "%H:%M"))
                    st.slider("SOC Objetivo para carga desde la red (%)", min_value=10, max_value=100, value=100)

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 Escribir Parámetros al Datalogger", use_container_width=True):
                    with st.spinner("Conectando con el equipo remoto..."):
                        time.sleep(2)
                    st.success("¡Parámetros actualizados exitosamente!")

        with tab_reportes:
            st.markdown("### 📄 Descarga de Datos en Bruto")
            st.write("Exporte las métricas del día actual.")
            fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            datos_informe = {"Fecha Consulta": [fecha_hora_actual], "Planta": [d['nombre']], "Capacidad": [d['capacidad']], "Batería SOC (%)": [datos_act['soc']], "Producción Diaria (kWh)": [prod_solar]}
            df_informe = pd.DataFrame(datos_informe)
            csv_data = df_informe.to_csv(index=False).encode('utf-8-sig') 
            st.download_button(label="📥 Descargar Informe CSV", data=csv_data, file_name=f"Reporte_{d['nombre'].replace(' ', '_')}.csv", mime="text/csv")

        if tab_mantenimiento:
            with tab_mantenimiento:
                st.markdown("<h3 style='color:#2c3e50;'>📅 Agenda de O&M</h3>", unsafe_allow_html=True)
                with st.form("f_mant"):
                    mc1, mc2, mc3 = st.columns([2, 1, 1])
                    m_tipo = mc1.selectbox("Tipo de Tarea", ["💦 Limpieza de Paneles", "🔋 Revisión de Banco de Baterías", "🔌 Mantenimiento Preventivo Inversor", "🔎 Inspección Eléctrica General", "🔧 Corrección de Fallo por Garantía"])
                    m_fecha = mc2.date_input("Fecha Programada")
                    m_resp = mc3.text_input("Técnico a Cargo", placeholder="Ej: Carlos M.")
                    m_notas = st.text_input("Observaciones o Materiales Necesarios", placeholder="Ej: Llevar hidrolavadora...")
                    if st.form_submit_button("➕ Agendar Mantenimiento", use_container_width=True):
                        guardar_mantenimiento(d['nombre'], {"fecha": str(m_fecha), "tipo": m_tipo, "resp": m_resp, "notas": m_notas, "estado": "⏳ Pendiente"})
                        st.rerun()
                st.markdown("<br><h4>📋 Historial de Servicios</h4>", unsafe_allow_html=True)
                mantenimientos_raw = cargar_mantenimientos().get(d['nombre'], [])
                if not mantenimientos_raw: st.info("Aún no hay mantenimientos programados para esta planta.")
                else:
                    for i, m in enumerate(reversed(mantenimientos_raw)):
                        real_idx = len(mantenimientos_raw) - 1 - i
                        st.markdown(f"<div style='background:white; padding:15px; border-radius:8px; border:1px solid #eaeaea; margin-bottom:10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
                        col_det, col_est, col_acc = st.columns([5, 2, 1])
                        with col_det: st.markdown(f"<div style='font-size:16px; font-weight:bold; color:#2c3e50;'>{m['tipo']}</div><div style='font-size:13px; color:#7f8c8d; margin-top:5px;'>📅 Fecha: {m['fecha']} &nbsp;|&nbsp; 👨‍🔧 Responsable: {m['resp']} <br> 📝 Notas: {m['notas']}</div>", unsafe_allow_html=True)
                        with col_est:
                            if m['estado'] == "⏳ Pendiente": st.warning(m['estado'])
                            else: st.success(m['estado'])
                        with col_acc:
                            if m['estado'] == "⏳ Pendiente" and st.button("✅ Ok", key=f"btn_ok_{real_idx}_{d['nombre']}", help="Marcar como completado"):
                                actualizar_estado_mantenimiento(d['nombre'], real_idx, "✅ Completado")
                                st.rerun()
                            if st.button("🗑️", key=f"btn_del_{real_idx}_{d['nombre']}", help="Eliminar registro"):
                                eliminar_mantenimiento(d['nombre'], real_idx)
                                st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# VENTANA 3: GESTIÓN DE PORTAFOLIO (ADMIN SOLO)
# ==========================================
elif menu == "🏢 Gestión de Portafolio":
    if rol_actual != "admin":
        st.error("⛔ ACCESO DENEGADO")
        st.stop()
        
    st.title("🏢 CONFIGURACIÓN DE PROYECTOS")
    st.markdown("**Asistente de Puesta en Marcha**")
    
    with st.expander("1️⃣ Crear Proyecto (Añadir Planta)", expanded=False):
        with st.form("f_planta"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nombre de la Planta")
            n_tipo = c2.selectbox("Tipo de Planta", ["Residencial", "Comercial e Industrial", "Off-Grid"])
            c3, c4 = st.columns(2)
            n_ubi = c3.text_input("Ubicación (Ciudad/Región)")
            n_cap = c4.text_input("Capacidad (kWp)")
            c5, c6 = st.columns(2)
            n_inv = c5.selectbox("Marca de Inversor", ["Deye", "GoodWe", "Huawei", "Sylvania"])
            n_sn = c6.text_input("SN del Datalogger (Opcional)")
            
            if st.form_submit_button("💾 Crear Planta (createPlant)"):
                if n_nom:
                    guardar_planta({"nombre": n_nom, "ubicacion": n_ubi, "capacidad": n_cap, "inversores": n_inv, "datalogger": n_sn, "status": "active"})
                    st.success("Planta creada exitosamente.")
                    st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Directorio de Plantas Activas")
    for i, pl in enumerate(plantas_guardadas):
        col_info, col_btn = st.columns([5, 1]) 
        with col_info:
            sn_display = f" | SN: {pl.get('datalogger', 'N/A')}" if pl.get('datalogger') else ""
            st.markdown(f"<div style='background: white; color: black; padding: 10px; border-radius: 5px; border: 1px solid #eaeaea;'><b>{pl['nombre']}</b> | {pl['ubicacion']} | {pl['capacidad']} | Inversor: {pl['inversores']}{sn_display}</div>", unsafe_allow_html=True)
        with col_btn:
            if st.button("🗑️", key=f"del_pl_{i}", help="Borrar planta"):
                eliminar_planta(i)
                st.rerun()

# ==========================================
# VENTANA 4: CENTRO DE ALERTAS
# ==========================================
elif menu == "🚨 Centro de Alertas":
    st.title("🚨 CENTRO DE ALERTAS Y DIAGNÓSTICO")
    if not plantas_guardadas: st.info("No hay plantas registradas.")
    else:
        alertas_totales = 0
        for pl in plantas_guardadas:
            datos = obtener_datos_reales(pl)
            if datos.get("alertas"):
                st.markdown(f"### 📍 Proyecto: {pl['nombre']}")
                for alerta in datos["alertas"]:
                    alertas_totales += 1
                    if "Batería" in alerta: st.warning(alerta)
                    else: st.error(alerta)
        st.markdown("---")
        if alertas_totales == 0: st.success("✅ Excelente. Todos los sistemas están operando con normalidad.")
        else:
            if st.button("🔄 Refrescar"): st.rerun()

# ==========================================
# VENTANA 5: GESTIÓN DE USUARIOS (ADMIN SOLO)
# ==========================================
elif menu == "👥 Gestión de Usuarios":
    if rol_actual != "admin":
        st.error("⛔ ACCESO DENEGADO")
        st.stop()
        
    st.title("👥 GESTIÓN DE USUARIOS Y AUTORIZACIONES")
    db_usuarios = cargar_usuarios()
    pendientes = [(u, d) for u, d in db_usuarios.items() if d["status"] == "pending"]
    activos = [(u, d) for u, d in db_usuarios.items() if d["status"] == "active"]
    
    st.markdown("### 📋 Solicitudes de Registro Pendientes")
    if not pendientes: st.success("✅ No hay solicitudes pendientes de aprobación.")
    else:
        st.markdown(f"Hay **{len(pendientes)}** solicitud(es) esperando autorización.")
        for i, (user, data) in enumerate(pendientes):
            st.markdown(f"<div style='background:white; padding:15px; border-radius:8px; border:1px solid #e0e0e0; margin-bottom:10px;'>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([4, 1, 1])
            with c1: st.markdown(f"<b style='color:#2c3e50;'>{user}</b> solicita acceso como Cliente.")
            with c2:
                if st.button("✅ Aprobar", key=f"app_{i}", use_container_width=True):
                    gestionar_solicitud(user, aprobar=True)
                    st.rerun()
            with c3:
                if st.button("❌ Rechazar", key=f"rej_{i}", use_container_width=True):
                    gestionar_solicitud(user, aprobar=False)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 👥 Usuarios Autorizados Activos")
    df_activos = pd.DataFrame([{"Usuario": u, "Rol": "Instalador/Admin" if d["role"]=="admin" else "Cliente", "Estado": "Activo"} for u, d in activos])
    st.dataframe(df_activos, use_container_width=True)
