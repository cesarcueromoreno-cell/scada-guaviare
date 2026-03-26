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
import gspread
from google.oauth2.service_account import Credentials
from fpdf import FPDF
import tempfile
import requests

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

if st.session_state["autenticado"] and st.session_state["usuario"] is None:
    st.session_state["autenticado"] = False

# ==========================================
# 3. BASE DE DATOS EN GOOGLE SHEETS
# ==========================================
@st.cache_resource(ttl=600)
def init_gsheets():
    if "GOOGLE_JSON" in st.secrets:
        try:
            creds_dict = json.loads(st.secrets["GOOGLE_JSON"], strict=False)
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            return gspread.authorize(creds).open("BD_MONISOLAR")
        except Exception as e:
            st.error(f"⚠️ Error conectando a Google Sheets: {e}")
    return None

db_sheet = init_gsheets()

def check_headers(sheet, headers):
    if not sheet.row_values(1): sheet.append_row(headers)

def cargar_usuarios():
    if not db_sheet: return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}
    try:
        sheet = db_sheet.worksheet("usuarios")
        check_headers(sheet, ["usuario", "pwd", "status", "role", "planta_asignada"])
        records = sheet.get_all_records()
        if not records:
            sheet.append_row(["admin", "solar123", "active", "admin", "Todas"])
            return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}
        return {str(r["usuario"]): {"pwd": str(r["pwd"]), "status": str(r["status"]), "role": str(r["role"]), "planta_asignada": str(r.get("planta_asignada", "Todas"))} for r in records}
    except: return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}

def solicitar_usuario(usuario, contrasena):
    db = cargar_usuarios()
    if usuario in db: return False, "⚠️ Este usuario ya existe o tiene una solicitud pendiente."
    if db_sheet:
        try:
            db_sheet.worksheet("usuarios").append_row([usuario, contrasena, "pending", "viewer", "Pendiente Asignar"])
            return True, "✅ Solicitud enviada. Espere a que el Administrador apruebe su cuenta."
        except: pass
    return False, "❌ Error de conexión a la base de datos."

def actualizar_usuario_bd(usuario_id, nuevo_estado, nuevo_rol, nueva_planta, nueva_pwd=None):
    if db_sheet:
        try:
            sheet = db_sheet.worksheet("usuarios")
            records = sheet.get_all_records()
            for i, r in enumerate(records):
                if str(r["usuario"]) == usuario_id:
                    if nueva_pwd: sheet.update_cell(i + 2, 2, nueva_pwd)
                    sheet.update_cell(i + 2, 3, nuevo_estado)
                    sheet.update_cell(i + 2, 4, nuevo_rol)
                    sheet.update_cell(i + 2, 5, nueva_planta)
                    break
        except Exception as e: st.error(f"Error actualizando usuario: {e}")

def eliminar_usuario_bd(usuario_id):
    if db_sheet:
        try:
            sheet = db_sheet.worksheet("usuarios")
            records = sheet.get_all_records()
            for i, r in enumerate(records):
                if str(r["usuario"]) == usuario_id:
                    sheet.delete_rows(i + 2)
                    break
        except Exception as e: pass

def cargar_plantas():
    if not db_sheet: return []
    try:
        sheet = db_sheet.worksheet("plantas")
        check_headers(sheet, ["nombre", "ubicacion", "capacidad", "inversores", "datalogger", "tipo_sistema", "smart_meter"])
        return sheet.get_all_records()
    except: return []

def guardar_planta(nueva):
    if db_sheet:
        try: 
            db_sheet.worksheet("plantas").append_row([
                nueva.get("nombre",""), nueva.get("ubicacion",""), nueva.get("capacidad",""), 
                nueva.get("inversores",""), nueva.get("datalogger",""), 
                nueva.get("tipo_sistema","Híbrido"), nueva.get("smart_meter","Ninguno")
            ])
        except: pass

def actualizar_planta(idx, p_edit):
    if db_sheet:
        try:
            sheet = db_sheet.worksheet("plantas")
            row_idx = idx + 2
            cell_list = sheet.range(f"A{row_idx}:G{row_idx}")
            vals = [
                p_edit.get("nombre",""), p_edit.get("ubicacion",""), p_edit.get("capacidad",""), 
                p_edit.get("inversores",""), p_edit.get("datalogger",""),
                p_edit.get("tipo_sistema","Híbrido"), p_edit.get("smart_meter","Ninguno")
            ]
            for i, val in enumerate(vals): cell_list[i].value = str(val)
            sheet.update_cells(cell_list)
        except: pass

def eliminar_planta(idx):
    if db_sheet:
        try: db_sheet.worksheet("plantas").delete_rows(idx + 2)
        except: pass

def cargar_mantenimientos():
    if not db_sheet: return {}
    try:
        sheet = db_sheet.worksheet("mantenimientos")
        check_headers(sheet, ["planta", "fecha", "tipo", "resp", "notas", "estado"])
        records = sheet.get_all_records()
        mants = {}
        for r in records:
            planta = str(r["planta"])
            if planta not in mants: mants[planta] = []
            mants[planta].append({"fecha": str(r["fecha"]), "tipo": str(r["tipo"]), "resp": str(r["resp"]), "notas": str(r["notas"]), "estado": str(r["estado"])})
        return mants
    except: return {}

def guardar_mantenimiento(planta, datos_mant):
    if db_sheet:
        try: db_sheet.worksheet("mantenimientos").append_row([planta, datos_mant["fecha"], datos_mant["tipo"], datos_mant["resp"], datos_mant["notas"], datos_mant["estado"]])
        except: pass

def actualizar_estado_mantenimiento(planta, indice, nuevo_estado):
    if db_sheet:
        try:
            sheet = db_sheet.worksheet("mantenimientos")
            records = sheet.get_all_records()
            count = 0
            for i, r in enumerate(records):
                if str(r["planta"]) == planta:
                    if count == indice:
                        sheet.update_cell(i + 2, 6, nuevo_estado)
                        break
                    count += 1
        except: pass

def eliminar_mantenimiento(planta, indice):
    if db_sheet:
        try:
            sheet = db_sheet.worksheet("mantenimientos")
            records = sheet.get_all_records()
            count = 0
            for i, r in enumerate(records):
                if str(r["planta"]) == planta:
                    if count == indice:
                        sheet.delete_rows(i + 2)
                        break
                    count += 1
        except: pass

if "delete" in st.query_params:
    try:
        idx = int(st.query_params["delete"])
        eliminar_planta(idx)
        st.query_params.clear()
    except: pass
if "edit" in st.query_params:
    try:
        idx = int(st.query_params["edit"])
        st.session_state["editando_planta"] = idx
        st.query_params.clear()
    except: pass

# ==========================================
# 4. LOGIN
# ==========================================
if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #f1c40f !important;'>☀️ MONISOLAR APP</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white !important;'>Plataforma de Gestión - CV INGENIERÍA SAS</h3><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        with st.form("login"):
            st.markdown("<div style='color:white; font-weight:bold; font-size:14px; text-shadow: 1px 1px 3px black;'>Usuario</div>", unsafe_allow_html=True)
            u = st.text_input("Usuario", label_visibility="collapsed")
            st.markdown("<div style='color:white; font-weight:bold; font-size:14px; margin-top:10px; text-shadow: 1px 1px 3px black;'>Contraseña</div>", unsafe_allow_html=True)
            p = st.text_input("Contraseña", type="password", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                db = cargar_usuarios()
                if u in db and str(db[u]["pwd"]) == p:
                    if db[u].get("status") == "pending": st.warning("⚠️ Su cuenta está pendiente de aprobación.")
                    else:
                        st.session_state.update({"autenticado": True, "usuario": u, "rol": db[u]["role"], "planta_asignada": db[u].get("planta_asignada", "Todas")})
                        st.rerun()
                else: st.error("❌ Credenciales incorrectas.")
        with st.expander("¿No tienes cuenta? Solicita acceso aquí"):
            with st.form("solicitud_form"):
                nuevo_usuario = st.text_input("👤 Correo / Usuario Solicitado")
                nueva_contrasena = st.text_input("🔑 Contraseña", type="password")
                confirmar_contrasena = st.text_input("🔑 Confirmar Contraseña", type="password")
                if st.form_submit_button("Enviar Solicitud", use_container_width=True):
                    if not nuevo_usuario or not nueva_contrasena: st.error("⚠️ Complete todos los campos.")
                    elif nueva_contrasena != confirmar_contrasena: st.error("⚠️ Las contraseñas no coinciden.")
                    else:
                        success, message = solicitar_usuario(nuevo_usuario, nueva_contrasena)
                        if success: st.success(message)
                        else: st.error(message)
    st.stop()

# ==========================================
# 5. FILTRADO DE SEGURIDAD Y NAVEGACIÓN
# ==========================================
todas_las_plantas = cargar_plantas()

if st.session_state['rol'] == 'admin':
    plantas_permitidas = todas_las_plantas
else:
    planta_user = st.session_state.get("planta_asignada", "Ninguna")
    plantas_permitidas = [pl for pl in todas_las_plantas if pl.get("nombre") == planta_user]

st.sidebar.markdown("<h2 style='text-align: center; color: #f1c40f !important; text-shadow: none !important;'>☀️ MONISOLAR APP</h2>", unsafe_allow_html=True)
st.sidebar.write(f"👤 **{st.session_state.get('usuario', '')}** | Rol: {'Instalador/Admin' if st.session_state.get('rol') == 'admin' else 'Cliente'}")

opciones_menu = []
if st.session_state.get('rol') == 'admin':
    opciones_menu = ["🌐 Panorama General", "📊 Panel de Planta", "🚨 Centro de Alertas", "👥 Gestión de Usuarios"]
else:
    opciones_menu = ["📊 Panel de Mi Planta"]

menu = st.sidebar.radio("Ir a:", opciones_menu)

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.update({"autenticado": False, "usuario": None, "rol": None, "planta_asignada": "Todas", "red_desbloqueada": False, "reinicio_desbloqueado": False})
    st.rerun()

# ==========================================
# 6. FUNCIONES DE SIMULACIÓN / EXTRACCIÓN Y PDF
# ==========================================
def get_data(pl):
    cap_val = pl.get("capacidad", "5")
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val))[0]) * 1000 if re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val)) else 5000
    id_planta = str(pl.get("datalogger", "")).strip()
    
    if "SOLARMAN_USER" in st.secrets and "SOLARMAN_PWD" in st.secrets and id_planta != "":
        try:
            sesion = requests.Session()
            sesion.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json, text/plain, */*"
            })
            url_login = "https://pro.solarmanpv.com/api/v1.0/pwd/login"
            payload = {"email": st.secrets["SOLARMAN_USER"], "password": st.secrets["SOLARMAN_PWD"]}
            res_login = sesion.post(url_login, json=payload, timeout=3)
            if res_login.status_code == 200:
                url_datos = f"https://pro.solarmanpv.com/api/v1.0/station/{id_planta}/flow"
                res_datos = sesion.get(url_datos, timeout=3)
                if res_datos.status_code == 200:
                    pass
        except Exception as e:
            pass 

    p_sol = int(cap * random.uniform(0.1, 0.8))
    e_dia = round((p_sol * random.uniform(3.5, 5.0)) / 1000, 1)
    soc = random.randint(15, 99) 
    return {"solar": p_sol, "casa": int(p_sol*0.4) + random.randint(500, 1500), "soc": soc, "hoy": e_dia, "alertas": []}

def simular_historico_24h_avanzado(planta):
    cap_val = planta.get("capacidad", "5")
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val))[0]) if re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val)) else 5.0
    inicio_dia = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    datos = []
    soc_actual = 65.0
    
    for m in range(0, 24 * 60, 15):
        t = inicio_dia + timedelta(minutes=m)
        h = t.hour
        gen = max(0, (cap * 0.9) * math.sin((h - 6) / 12 * math.pi) * random.uniform(0.95, 1.05)) if 6 <= h <= 18 else 0
        con = max(cap * 0.1, cap * 0.2 + (cap * 0.3 * math.sin((h-7)/2 * math.pi) if 7<=h<=9 else (cap * 0.4 * math.sin((h-18)/3 * math.pi) if 18<=h<=21 else 0)))
        diff = gen - con
        bat_power = 0
        if diff > 0 and soc_actual < 100:
            bat_power = min(diff, cap * 0.5) 
            soc_actual = min(100, soc_actual + (bat_power * 0.25 / (cap*2)) * 100)
        elif diff < 0 and soc_actual > 20:
            bat_power = max(diff, -cap * 0.5) 
            soc_actual = max(20, soc_actual + (bat_power * 0.25 / (cap*2)) * 100)
            
        red = 0 if planta.get('tipo_sistema', 'Híbrido') == 'Off-Grid' else max(0, con - gen + bat_power)

        datos.append({
            "timestamp": t,
            "Potencia Solar": round(gen, 2),
            "Consumo": round(con, 2),
            "Batería": round(bat_power, 2),
            "Red": round(red, 2),
            "SOC": round(soc_actual, 1)
        })
    return pd.DataFrame(datos)

def generar_pdf(planta, datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, "CV INGENIERIA SAS", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(52, 152, 219)
    pdf.cell(0, 10, "REPORTE DE GENERACION SOLAR", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(50, 10, "Planta:")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(planta.get('nombre', 'N/A')), ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Ubicacion:")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(planta.get('ubicacion', 'N/A')), ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Tipo de Sistema:")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(planta.get('tipo_sistema', 'Híbrido')), ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Fecha de Reporte:")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, datetime.now().strftime("%Y-%m-%d %H:%M"), ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "  Resumen de Rendimiento (Hoy)", ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.cell(80, 10, "Energia Solar Generada:")
    pdf.set_text_color(39, 174, 96) 
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"{datos['hoy']} kWh", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(80, 10, "Consumo Aproximado:")
    pdf.set_text_color(230, 126, 34) 
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"{round(datos['hoy']*0.45,1)} kWh", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    if planta.get('tipo_sistema', 'Híbrido') in ['Híbrido', 'Off-Grid']:
        pdf.set_font("Arial", '', 12)
        pdf.cell(80, 10, "Nivel de Baterias (SOC):")
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{datos['soc']} %", ln=True)
        
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(127, 140, 141)
    pdf.cell(0, 10, "Este es un documento generado automaticamente por MONISOLAR APP.", ln=True, align='C')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            pdf_bytes = f.read()
    return pdf_bytes

# ==========================================
# 7. VISTAS (ADMINISTRADOR Y CLIENTE)
# ==========================================

OPCIONES_SISTEMA = ["Híbrido", "On-Grid", "Off-Grid"]
OPCIONES_METERS = ["Ninguno", "Deye/Chint Meter", "Fronius Smart Meter", "Eastron SDM", "GoodWe HomeKit", "Huawei Smart Power"]

if menu == "👥 Gestión de Usuarios":
    st.title("👥 GESTIÓN DE USUARIOS")
    db_usuarios = cargar_usuarios()
    nombres_plantas = ["Todas", "Pendiente Asignar"] + [p['nombre'] for p in todas_las_plantas]
    
    st.markdown("<br>", unsafe_allow_html=True)
    for usr, datos in db_usuarios.items():
        if usr == "admin": continue
        estado_color = "#27ae60" if datos['status'] == 'active' else "#f39c12"
        estado_texto = "🟢 Activo" if datos['status'] == 'active' else "⏳ Pendiente"
        st.markdown(f"""
        <div style="background: white; border-radius: 8px; padding: 15px; border: 1px solid #eaeaea; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: #2c3e50;">👤 {usr}</h4>
                    <span style="font-size: 13px; color: {estado_color}; font-weight: bold;">{estado_texto}</span> | 
                    <span style="font-size: 13px; color: #7f8c8d;">Rol: {datos['role']}</span> | 
                    <span style="font-size: 13px; color: #2980b9; font-weight: bold;">Planta: {datos.get('planta_asignada', 'Ninguna')}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        with st.form(f"form_{usr}"):
            c1, c2, c3, c4 = st.columns([1.5, 1.5, 2, 2])
            nuevo_est = c1.selectbox("Estado", ["active", "pending"], index=0 if datos['status'] == 'active' else 1, key=f"est_{usr}")
            nuevo_rol = c2.selectbox("Rol", ["viewer", "admin"], index=0 if datos['role'] == 'viewer' else 1, key=f"rol_{usr}")
            idx_planta = nombres_plantas.index(datos.get('planta_asignada', 'Todas')) if datos.get('planta_asignada', 'Todas') in nombres_plantas else 0
            nueva_planta = c3.selectbox("Asignar Planta", nombres_plantas, index=idx_planta, key=f"pl_{usr}")
            c4_a, c4_b = c4.columns([3, 1])
            nueva_pwd = c4_a.text_input("Cambiar Contraseña", type="password", placeholder="Dejar en blanco para no cambiar")
            sub_col1, sub_col2 = c4_b.columns(2)
            if sub_col1.form_submit_button("💾"):
                actualizar_usuario_bd(usr, nuevo_est, nuevo_rol, nueva_planta, nueva_pwd if nueva_pwd else None)
                st.success(f"Usuario {usr} actualizado.")
                time.sleep(1)
                st.rerun()
            if sub_col2.form_submit_button("🗑️"):
                eliminar_usuario_bd(usr)
                st.warning(f"Usuario {usr} eliminado.")
                time.sleep(1)
                st.rerun()

elif menu == "🌐 Panorama General":
    st.title("🌐 PANORAMA GENERAL")
    
    if st.session_state["editando_planta"] is not None:
        idx = st.session_state["editando_planta"]
        p_edit = plantas_permitidas[idx]
        st.markdown(f"<h3>✏️ Editar Parámetros: {p_edit['nombre']}</h3>", unsafe_allow_html=True)
        with st.form("edit"):
            c1, c2, c3 = st.columns([2, 2, 1])
            n = c1.text_input("Nombre", p_edit['nombre'])
            u = c2.text_input("Ubicación", p_edit['ubicacion'])
            c = c3.text_input("Capacidad", str(p_edit.get('capacidad', '')))
            
            c4, c5, c6 = st.columns(3)
            sn = c4.text_input("SN Datalogger", str(p_edit.get('datalogger', '')))
            idx_tipo = OPCIONES_SISTEMA.index(p_edit.get('tipo_sistema', 'Híbrido')) if p_edit.get('tipo_sistema', 'Híbrido') in OPCIONES_SISTEMA else 0
            n_tipo = c5.selectbox("Tipo de Sistema", OPCIONES_SISTEMA, index=idx_tipo)
            idx_meter = OPCIONES_METERS.index(p_edit.get('smart_meter', 'Ninguno')) if p_edit.get('smart_meter', 'Ninguno') in OPCIONES_METERS else 0
            n_meter = c6.selectbox("Smart Meter (Medidor Inteligente)", OPCIONES_METERS, index=idx_meter)

            if st.form_submit_button("💾 Guardar Cambios"):
                p_edit.update({"nombre": n, "ubicacion": u, "capacidad": c, "datalogger": sn, "tipo_sistema": n_tipo, "smart_meter": n_meter})
                actualizar_planta(idx, p_edit)
                st.session_state["editando_planta"] = None
                st.rerun()

    if st.session_state.get("mostrar_crear"):
        st.markdown("<h3>➕ Crear Nueva Planta</h3>", unsafe_allow_html=True)
        with st.form("crear_planta_form"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nombre de la Planta")
            n_ubi = c2.text_input("Ubicación")
            n_cap = c1.text_input("Capacidad (Ej: 30 kWp)")
            n_inv = c2.selectbox("Marca de Inversor", ["Deye", "Fronius", "GoodWe", "Huawei", "Sylvania"])
            
            c3, c4 = st.columns(2)
            n_tipo = c3.selectbox("Tipo de Sistema", OPCIONES_SISTEMA)
            n_meter = c4.selectbox("Smart Meter a Instalar", OPCIONES_METERS)
            n_sn = st.text_input("SN del Datalogger (ID Solarman)")
            
            s1, s2 = st.columns(2)
            if s1.form_submit_button("💾 Guardar Nueva Planta"):
                if n_nom:
                    guardar_planta({"nombre": n_nom, "ubicacion": n_ubi, "capacidad": n_cap, "inversores": n_inv, "datalogger": n_sn, "tipo_sistema": n_tipo, "smart_meter": n_meter})
                    st.session_state["mostrar_crear"] = False
                    st.rerun()
            if s2.form_submit_button("❌ Cancelar"):
                st.session_state["mostrar_crear"] = False
                st.rerun()

    col_bus, col_btn = st.columns([8, 2])
    with col_bus: c_bus = st.text_input("🔍 Buscar planta", placeholder="Buscar por nombre o ciudad", label_visibility="collapsed")
    with col_btn:
        if st.button("Crear una planta", type="primary", use_container_width=True):
            st.session_state["mostrar_crear"] = not st.session_state.get("mostrar_crear", False)
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    if not plantas_permitidas: st.warning("No hay plantas registradas o no tiene plantas asignadas.")
    else:
        filtradas = [pl for pl in plantas_permitidas if c_bus.lower() in str(pl.get('nombre','')).lower() or c_bus.lower() in str(pl.get('ubicacion','')).lower()]
        st.markdown('<div style="overflow-x: auto;"><div style="min-width: 1050px;">', unsafe_allow_html=True)
        for i, pl in enumerate(filtradas):
            dat = get_data(pl)
            tipo_etiqueta = pl.get('tipo_sistema', 'Híbrido')
            col_card, col_btns = st.columns([11, 1])
            with col_card:
                st.markdown(f"""
                <div class="tarjeta-dash-pro" style="margin-bottom:0px;">
                <div style="display:flex; align-items:center; width: 320px; flex-shrink: 0;">
                    <img src="https://img.icons8.com/color/48/solar-panel.png" style="width: 32px; margin-right:15px;"/>
                    <div>
                        <div style="font-size: 15px; font-weight: bold;">{pl.get('nombre','N/A')}</div>
                        <div style="font-size: 11px; color: #7f8c8d; font-weight: bold;">{tipo_etiqueta}</div>
                    </div>
                </div>
                <div class="tarjeta-dash-item"><div class="tarjeta-label-pro">Potencia Solar</div><div class="tarjeta-dato-pro">{dat['solar']} W</div></div>
                <div class="tarjeta-dash-item"><div class="tarjeta-label-pro">Energía Hoy</div><div class="tarjeta-dato-pro" style="color:#27ae60 !important;">{dat['hoy']} kWh</div></div>
                </div>""", unsafe_allow_html=True)
            with col_btns:
                st.markdown("<div style='height:15px;'></div><div style='display:flex; gap:10px;'>", unsafe_allow_html=True)
                st.markdown(f'<a href="?edit={i}" title="Editar"><img src="https://img.icons8.com/material-rounded/24/7f8c8d/edit.png" width="24"/></a> <a href="?delete={i}" title="Eliminar"><img src="https://img.icons8.com/material-rounded/24/7f8c8d/filled-trash.png" width="24"/></a>', unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

elif menu in ["📊 Panel de Planta", "📊 Panel de Mi Planta"]:
    if not plantas_permitidas:
        st.warning("No tiene plantas asignadas. Contacte a CV Ingeniería.")
        st.stop()
        
    pl_sel = st.selectbox("Seleccionar Planta:", [p["nombre"] for p in plantas_permitidas], label_visibility="collapsed")
    p = next(x for x in plantas_permitidas if x["nombre"] == pl_sel)
    d = get_data(p)
    
    tipo_sistema_actual = p.get('tipo_sistema', 'Híbrido')
    smart_meter_actual = p.get('smart_meter', 'Ninguno')
    
    st.markdown(f"<h2>{p['nombre']} <span style='font-size:14px; color:#7f8c8d; font-weight:normal;'>| 🟢 En línea | Tipo: {tipo_sistema_actual} | SN: {p.get('datalogger', 'N/A')}</span></h2><hr style='margin-top:0px; margin-bottom:20px; border-color:#e0e0e0;'>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
    c1.markdown(f"<div class='solarman-card' style='border-top: 4px solid #3498db;'><div class='solarman-val'>{d['hoy']} kWh</div><div class='solarman-lbl'>Producción Solar</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='solarman-card' style='border-top: 4px solid #e74c3c;'><div class='solarman-val'>{round(d['hoy']*0.45,1)} kWh</div><div class='solarman-lbl'>Consumo</div></div>", unsafe_allow_html=True)
    
    if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
        c3.markdown(f"<div class='solarman-card' style='border-top: 4px solid #2ecc71;'><div style='font-size:14px; font-weight:bold; color:#2c3e50;'>🔋 {round(d['hoy']*0.2,1)} kWh <span class='solarman-lbl-sm'>Cargar</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>🔋 {round(d['hoy']*0.1,1)} kWh <span class='solarman-lbl-sm'>Descargar</span></div></div>", unsafe_allow_html=True)
    else:
        c3.markdown(f"<div class='solarman-card' style='border-top: 4px solid #bdc3c7;'><div style='font-size:20px; font-weight:bold; color:#bdc3c7;'>--</div><div class='solarman-lbl'>Sin Baterías</div></div>", unsafe_allow_html=True)

    if tipo_sistema_actual in ["Híbrido", "On-Grid"]:
        c4.markdown(f"<div class='solarman-card' style='border-top: 4px solid #f1c40f;'><div style='font-size:14px; font-weight:bold; color:#2c3e50;'>⚡ 0 kWh <span class='solarman-lbl-sm'>A Red</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>⚡ 0 kWh <span class='solarman-lbl-sm'>De Red</span></div></div>", unsafe_allow_html=True)
    else:
        c4.markdown(f"<div class='solarman-card' style='border-top: 4px solid #bdc3c7;'><div style='font-size:20px; font-weight:bold; color:#bdc3c7;'>--</div><div class='solarman-lbl'>Aislado (Off-Grid)</div></div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state['rol'] == 'admin':
        t_graf, t_disp, t_ctrl, t_rep, t_om = st.tabs(["📈 Panel Gráfico", "🔌 Dispositivos", "⚙️ Control Remoto", "📄 Reportes PDF", "🛠️ O&M"])
    else:
        t_graf, t_disp, t_rep = st.tabs(["📈 Panel Gráfico", "🔌 Dispositivos", "📄 Reportes PDF"])
        t_ctrl, t_om = None, None
    
    with t_graf:
        col_grafica, col_flujo = st.columns([7, 3])
        with col_grafica:
            st.markdown("<div style='background:white; border-radius:8px; padding:15px; border:1px solid #eaeaea;'>", unsafe_allow_html=True)
            
            df_historico = simular_historico_24h_avanzado(p)
            fig2 = make_subplots(specs=[[{"secondary_y": True}]])
            
            if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                fig2.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['Batería'], fill='tozeroy', mode='lines', line=dict(color='#2ecc71', width=1), name='Batería (Carga/Descarga)'), secondary_y=False)
            
            fig2.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['Potencia Solar'], fill='tozeroy', mode='lines', line=dict(color='#3498db', width=2), name='Potencia Solar'), secondary_y=False)
            fig2.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['Consumo'], mode='lines', line=dict(color='#e74c3c', width=2), name='Consumo'), secondary_y=False)
            
            if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                fig2.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['SOC'], mode='lines', line=dict(color='#34495e', width=2, dash='dot'), name='SOC %'), secondary_y=True)

            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=10, r=10, t=10, b=10), height=410
            )
            fig2.update_yaxes(title_text="kW", secondary_y=False, gridcolor="#f0f0f0")
            fig2.update_yaxes(title_text="%", secondary_y=True, range=[0, 105], showgrid=False)
            fig2.update_xaxes(tickformat="%H:%M", dtick=3 * 3600000, gridcolor="#f0f0f0")
            
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_flujo:
            pot_bat = d["solar"] - d["casa"]
            color_bat = "#2ecc71" if d["soc"] > 20 else "#e74c3c"
            
            svg_paths = ""
            svg_circles = ""
            svg_icons = ""
            
            svg_paths += '<path d="M 100 85 V 150 H 170" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>'
            svg_circles += '<circle r="6" fill="#3498db"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 85 V 150 H 170" /></circle>'
            svg_icons += f'<g transform="translate(60,30)"><image href="https://img.icons8.com/color/48/solar-panel.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#3498db" text-anchor="middle">{d["solar"]} W</text></g>'
            
            svg_paths += '<path d="M 230 150 H 300 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>'
            svg_circles += '<circle r="6" fill="#e74c3c"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 230" /></circle>'
            svg_icons += f'<g transform="translate(260,260)"><image href="https://img.icons8.com/color/48/home.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#e74c3c" text-anchor="middle">{d["casa"]} W</text></g>'
            
            if tipo_sistema_actual in ["Híbrido", "On-Grid"]:
                svg_paths += '<path d="M 300 85 V 150 H 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>'
                svg_circles += '<circle r="6" fill="#7f8c8d"><animateMotion dur="2s" repeatCount="indefinite" path="M 300 85 V 150 H 230" /></circle>'
                txt_meter = f'<text x="5" y="55" font-size="9" font-weight="bold" fill="#95a5a6" text-anchor="middle">{smart_meter_actual}</text>' if smart_meter_actual != "Ninguno" else ""
                svg_icons += f'<g transform="translate(260,30)"><image href="https://img.icons8.com/fluency/48/electrical.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#7f8c8d" text-anchor="middle">0 W</text>{txt_meter}</g>'
            
            if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                svg_paths += '<path d="M 170 150 H 100 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>'
                svg_circles += '<circle r="6" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>'
                svg_icons += f'<g transform="translate(60,260)"><image href="https://img.icons8.com/color/48/car-battery.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#27ae60" text-anchor="middle">{pot_bat} W</text><text x="5" y="55" font-size="11" font-weight="bold" fill="{color_bat}" text-anchor="middle">SOC: {d["soc"]}%</text></g>'

            svg_inversor = f"""
            <rect x="165" y="115" width="70" height="70" rx="12" fill="#f8f9fa" stroke="#3498db" stroke-width="3"/>
            <rect x="175" y="125" width="50" height="25" rx="3" fill="#2c3e50"/> 
            <text x="200" y="142" text-anchor="middle" font-size="8" fill="#55efc4" font-weight="bold">CV-ENG</text>
            <text x="200" y="200" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">{tipo_sistema_actual}</text>
            """

            diagrama_svg = f"""
            <div style="background: white; border-radius: 8px; padding: 20px; border: 1px solid #eaeaea; display: flex; align-items: center;">
                <svg viewBox="0 0 400 350" width="100%">
                    {svg_paths}
                    {svg_circles}
                    {svg_inversor}
                    {svg_icons}
                </svg>
            </div>
            """
            components.html(diagrama_svg, height=300)
            
            st.markdown(f"""
            <div style="background: white; border-radius: 8px; padding: 15px; border: 1px solid #eaeaea; margin-top: 15px;">
                <h4 style="margin-top:0; margin-bottom:15px; color:#2c3e50; font-size:14px;">Beneficios ambientales y económicos ❔</h4>
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <div style="display:flex; align-items:center;"><img src="https://img.icons8.com/color/24/coal.png" style="margin-right:10px;"/><span style="color:#7f8c8d; font-size:13px;">Ahorro de carbón estándar</span></div>
                    <div style="font-weight:bold; color:#2c3e50;">{round(d['hoy'] * 0.026, 2)} t</div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <div style="display:flex; align-items:center;"><img src="https://img.icons8.com/color/24/carbon-dioxide.png" style="margin-right:10px;"/><span style="color:#7f8c8d; font-size:13px;">Reducción de emisiones CO2</span></div>
                    <div style="font-weight:bold; color:#2c3e50;">{round(d['hoy'] * 0.068, 2)} t</div>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <div style="display:flex; align-items:center;"><img src="https://img.icons8.com/color/24/deciduous-tree.png" style="margin-right:10px;"/><span style="color:#7f8c8d; font-size:13px;">Árboles plantados</span></div>
                    <div style="font-weight:bold; color:#2c3e50;">{round(d['hoy'] * 4.7, 2)} Árboles</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with t_disp:
        st.markdown("### 🔌 Lista de Dispositivos Registrados")
        
        sn_logger = str(p.get('datalogger', 'N/A'))
        marca_inv = str(p.get('inversores', 'Genérico'))
        
        rows_html = f"""<tr style="border-bottom: 1px solid #ecf0f1;">
    <td style="padding: 12px;"><b>Inversor {marca_inv}</b><br><span style="color:#7f8c8d; font-size:12px;">{sn_logger}</span></td>
    <td style="padding: 12px;">Inversor</td>
    <td style="padding: 12px; color: #27ae60; font-weight: bold;">🟢 En línea</td>
    <td style="padding: 12px; color: #27ae60;">Normal</td>
    <td style="padding: 12px;">{round(d['solar']/1000, 2)}</td>
    <td style="padding: 12px;">{d['hoy']}</td>
</tr>
<tr style="border-bottom: 1px solid #ecf0f1;">
    <td style="padding: 12px;"><b>Datalogger WiFi</b><br><span style="color:#7f8c8d; font-size:12px;">{sn_logger}</span></td>
    <td style="padding: 12px;">Registrador</td>
    <td style="padding: 12px; color: #27ae60; font-weight: bold;">🟢 En línea</td>
    <td style="padding: 12px; color: #27ae60;">Normal</td>
    <td style="padding: 12px;">--</td>
    <td style="padding: 12px;">--</td>
</tr>"""
        
        if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
            rows_html += f"""
<tr style="border-bottom: 1px solid #ecf0f1;">
    <td style="padding: 12px;"><b>Banco de Baterías Litio</b><br><span style="color:#7f8c8d; font-size:12px;">BAT-{sn_logger[-4:] if len(sn_logger) > 4 else '001'}</span></td>
    <td style="padding: 12px;">Batería</td>
    <td style="padding: 12px; color: #27ae60; font-weight: bold;">🟢 En línea</td>
    <td style="padding: 12px; color: #27ae60;">Normal</td>
    <td style="padding: 12px;">--</td>
    <td style="padding: 12px;">--</td>
</tr>"""
            
        if smart_meter_actual != "Ninguno":
            rows_html += f"""
<tr style="border-bottom: 1px solid #ecf0f1;">
    <td style="padding: 12px;"><b>{smart_meter_actual}</b><br><span style="color:#7f8c8d; font-size:12px;">MTR-{sn_logger[-4:] if len(sn_logger) > 4 else '001'}</span></td>
    <td style="padding: 12px;">Medidor</td>
    <td style="padding: 12px; color: #27ae60; font-weight: bold;">🟢 En línea</td>
    <td style="padding: 12px; color: #27ae60;">Normal</td>
    <td style="padding: 12px;">--</td>
    <td style="padding: 12px;">--</td>
</tr>"""
            
        html_table = f"""<div style="background-color: white; border-radius: 8px; border: 1px solid #eaeaea; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-top: 10px;">
    <table style="width: 100%; border-collapse: collapse; text-align: left; color: #2c3e50; font-size: 14px;">
        <tr style="border-bottom: 2px solid #ecf0f1; background-color: #f8f9fa;">
            <th style="padding: 12px; color: #7f8c8d;">Nombre/SN</th>
            <th style="padding: 12px; color: #7f8c8d;">Tipo</th>
            <th style="padding: 12px; color: #7f8c8d;">Estado</th>
            <th style="padding: 12px; color: #7f8c8d;">Actuación</th>
            <th style="padding: 12px; color: #7f8c8d;">Potencia solar(kW)</th>
            <th style="padding: 12px; color: #7f8c8d;">Producción diaria(kWh)</th>
        </tr>
        {rows_html}
    </table>
</div>"""
        st.markdown(html_table, unsafe_allow_html=True)
            
    if t_ctrl:
        with t_ctrl:
            st.info(f"⚙️ Configurando el inversor **{p.get('inversores', 'Deye')}** de la planta '{p['nombre']}'. Proceda con precaución.")
            
            st_bat, st_mo1, st_mo2, st_red, st_smart, st_bas, st_av1, st_av2, st_sis = st.tabs([
                "🔋 Baterías", "🔄 Modos-1", "🔄 Modos-2", "⚡ Red", "🧠 SmartLoad", "⚙️ Básica", "🛠️ Avanzadas-1", "🛠️ Avanzadas-2", "💻 Sistema"
            ])
            opts_sel = ["Seleccione", "Habilitado", "Deshabilitado"]
            
            with st_bat:
                st.markdown("<small style='color:#7f8c8d;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</small>", unsafe_allow_html=True)
                cb1, cb2, cb3, cb4, cb5 = st.columns(5)
                cb1.selectbox("* Tipo Batería", ["Modo Litio", "Plomo"])
                cb2.number_input("* Capacidad (Ah)", value=100)
                cb3.number_input("* Max Carga (A)", value=50)
                cb4.number_input("* Max Descarga (A)", value=50)
                cb5.number_input("* Desconexión %", value=10)
                cc1, cc2, cc3, cc4, cc5 = st.columns(5)
                cc1.number_input("* Reconexión %", value=35)
                cc2.number_input("* Batería Baja %", value=20)
                cc3.selectbox("* Paralelo bat1&bat2", opts_sel)
                cc4.selectbox("* Carga de Red", opts_sel)
                cc5.selectbox("* Carga Generador", opts_sel)

            with st_mo1:
                st.markdown("<small style='color:#7f8c8d;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</small>", unsafe_allow_html=True)
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.selectbox("* Modo", ["Autoconsumo", "Respaldo"])
                with m2:
                    st.markdown("<p style='font-size:12px; margin-bottom:5px;'>* Configuración</p>", unsafe_allow_html=True)
                    st.checkbox("Lunes", True); st.checkbox("Martes", True)
                m3.number_input("* Max Solar (W)", value=5000)
                m4.number_input("* Max Red (W)", value=5000)
                m5.selectbox("* Prioridad", ["Carga", "Batería"])

            with st_mo2:
                st.toggle("* FuncionamientoporPeriodos", value=False)

            with st_red:
                if not st.session_state["red_desbloqueada"]:
                    st.markdown("<div style='color:#f39c12; font-weight:bold; margin-bottom:10px;'>🔒 Introduzca la contraseña 'admin123' para desbloquear</div>", unsafe_allow_html=True)
                    c_pw1, c_pw2 = st.columns([2, 3])
                    pwd = c_pw1.text_input("Contraseña", type="password", label_visibility="collapsed")
                    if c_pw1.button("Desbloquear", type="secondary"):
                        if pwd == "admin123":
                            st.session_state["red_desbloqueada"] = True
                            st.rerun()
                        else: st.error("❌ Contraseña incorrecta.")
                else:
                    st.success("🔓 Panel de Red Desbloqueado")
                    r_c1, r_c2 = st.columns(2)
                    r_c1.selectbox("* Normativa Aplicada", ["Seleccione", "Colombia (RETIE / NTC 2050)", "IEEE 1547", "IEC 61727"])
                    r_c2.number_input("* Límite de Inyección a red (%)", min_value=0, max_value=100, value=100)
                    st.markdown("<div style='margin-top: 10px; font-weight: bold; color: #2c3e50;'>Protecciones de Tensión AC (V) y Tiempos de Despeje (s)</div>", unsafe_allow_html=True)
                    cv1, ct1, cv2, ct2 = st.columns([2, 1, 2, 1])
                    cv1.number_input("* Sobre Tensión Máx (V)", value=253.0)
                    ct1.number_input("* Tiempo (s)", value=0.1, key="t_ov")
                    cv2.number_input("* Sub Tensión Mín (V)", value=198.0)
                    ct2.number_input("* Tiempo (s)", value=0.2, key="t_uv")
                    cv3, cv4 = st.columns(2)
                    cv3.number_input("* Tensión Máxima de Inyección (V)", value=242.0)
                    cv4.number_input("* Tensión Mínima de Inyección (V)", value=210.0)
                    st.markdown("<div style='margin-top: 15px; font-weight: bold; color: #2c3e50;'>Protecciones de Frecuencia (Hz) y Tiempos de Despeje (s)</div>", unsafe_allow_html=True)
                    cf1, cft1, cf2, cft2 = st.columns([2, 1, 2, 1])
                    cf1.number_input("* Sobre Frecuencia Máx (Hz)", value=60.5)
                    cft1.number_input("* Tiempo (s)", value=0.2, key="t_of")
                    cf2.number_input("* Sub Frecuencia Mín (Hz)", value=59.5)
                    cft2.number_input("* Tiempo (s)", value=0.2, key="t_uf")
                    st.markdown("<div style='margin-top: 15px; font-weight: bold; color: #2c3e50;'>Reconexión</div>", unsafe_allow_html=True)
                    cr1, cr2 = st.columns(2)
                    cr1.number_input("* Tiempo de reconexión a la red (s)", value=60)
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔒 Bloquear Red"):
                        st.session_state["red_desbloqueada"] = False
                        st.rerun()

            with st_smart:
                cs1, cs2, cs3 = st.columns(3)
                cs1.selectbox("* SmartLoad", ["Seleccione", "Habilitado"])
                cs2.selectbox("* Par CA Red", opts_sel)
                cs3.selectbox("* Par CA Carga", opts_sel)

            with st_bas:
                st.toggle("Sonido zumbador", value=True)

            with st_av1:
                st.markdown("<small style='color:#7f8c8d;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</small>", unsafe_allow_html=True)
                a1, a2, a3, a4, a5 = st.columns(5)
                a1.selectbox("* Configuración ARC", options=opts_sel)
                a2.selectbox("* Gen Peak-afeitado", options=opts_sel)
                a3.number_input("* Potencia reducción de picos (W)", value=1000)
                a4.selectbox("* Reducción de picos de la red", options=opts_sel)
                a5.number_input("* Potencia reducción red (W)", value=1000)
                b1, b2, b3, b4, b5 = st.columns(5)
                b1.selectbox("* Paralelo", options=opts_sel)
                b2.selectbox("* Modo (Maestro Esclavo)", options=["Seleccione", "Maestro", "Esclavo"])
                b3.number_input("* Modbus SN", value=1)
                b4.selectbox("* DRM", options=opts_sel)
                b5.selectbox("* Modo Isla de Señal", options=opts_sel)
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.number_input("* Retraso de respaldo", value=0)
                c2.number_input("* relación CT", value=1000)
                c3.selectbox("* EX_MeterCT", options=opts_sel)
                c4.selectbox("* Medidor red2", options=opts_sel)
                c5.selectbox("* Escaneo MPPT", options=opts_sel)
                d1, d2, d3, d4, d5 = st.columns(5)
                d1.selectbox("* Seleccionar Medidor", options=opts_sel)
                d2.selectbox("* Alimentación asimétrica", options=opts_sel)
                d3.selectbox("* Relé principal en el lado...", options=opts_sel, key="d3_rele")
                d4.selectbox("* Relé de derivación en...", options=opts_sel, key="d4_rele")
                d5.empty()

            with st_av2:
                av_col1, _, _ = st.columns([1.5, 1, 2])
                av_col1.selectbox("* DC 1 para turbina eólica", options=opts_sel)
                
            with st_sis:
                st.markdown("<br><h4 style='color: #e74c3c; margin-top: 0;'>⚠️ Comandos Críticos del Sistema</h4>", unsafe_allow_html=True)
                st.info("💡 **Nota de Ingeniería:** El comando de reinicio remoto ejecuta un apagado digital suave (Soft Reset). A diferencia de un corte físico de breakers, este método protege los relés internos y las tarjetas. El equipo no sufre desgaste mecánico al reiniciarse por esta vía.")
                
                if not st.session_state["reinicio_desbloqueado"]:
                    st.markdown("<div style='color:#f39c12; font-weight:bold; margin-bottom:10px;'>🔒 Introduzca la contraseña 'admin123' para habilitar el panel de sistema</div>", unsafe_allow_html=True)
                    c_pw1, c_pw2 = st.columns([2, 3])
                    pwd_res = c_pw1.text_input("Contraseña Sistema", type="password", label_visibility="collapsed")
                    if c_pw1.button("Desbloquear Sistema", type="secondary"):
                        if pwd_res == "admin123":
                            st.session_state["reinicio_desbloqueado"] = True
                            st.rerun()
                        else: st.error("❌ Contraseña incorrecta.")
                else:
                    st.success("🔓 Panel de Sistema Desbloqueado")
                    col_r1, col_r2 = st.columns([1, 1])
                    if col_r1.button("🔄 Reiniciar Inversor", type="primary", use_container_width=True):
                        with st.spinner("Conectando con la planta y enviando comando de Soft Reset..."):
                            time.sleep(2.5)
                        st.success("✅ Comando de reinicio aceptado por el inversor. El equipo volverá a estar en línea en 3 a 5 minutos.")
                    
                    if col_r2.button("🏭 Restaurar de Fábrica", type="secondary", use_container_width=True):
                        st.error("❌ Función bloqueada de forma permanente para evitar pérdida de parámetros RETIE y códigos de red.")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔒 Bloquear Sistema"):
                        st.session_state["reinicio_desbloqueado"] = False
                        st.rerun()
        
            st.markdown("<br><hr style='margin:10px 0;'>", unsafe_allow_html=True)
            b_col1, b_col2, b_col3 = st.columns([6, 2, 2])
            with b_col2: st.button("Mirada lasciva", use_container_width=True, type="secondary")
            with b_col3:
                if st.button("Configurar", type="primary", use_container_width=True):
                    with st.spinner("Enviando..."): time.sleep(1.5)
                    st.success("¡Configuración aplicada!")

    with t_rep:
        st.markdown("### 📄 Descarga de Reporte Ejecutivo PDF")
        st.write("Genere un informe formal con membrete de CV INGENIERIA SAS para enviarlo a sus clientes.")
        pdf_bytes = generar_pdf(p, d)
        st.download_button(
            label="📄 Generar y Descargar PDF",
            data=pdf_bytes,
            file_name=f"Reporte_CV_Ing__{p['nombre']}.pdf",
            mime="application/pdf",
            type="primary"
        )

    if t_om:
        with t_om:
            st.markdown("### 📅 Agenda de Mantenimiento")
            with st.form("f_mant"):
                mc1, mc2, mc3 = st.columns([2, 1, 1])
                m_tipo = mc1.selectbox("Tipo de Tarea", ["💦 Limpieza Paneles", "🔋 Revisión Baterías", "🔌 Revisión Inversor"])
                m_fecha = mc2.date_input("Fecha")
                m_resp = mc3.text_input("Técnico")
                m_notas = st.text_input("Observaciones")
                if st.form_submit_button("➕ Agendar"):
                    guardar_mantenimiento(p['nombre'], {"fecha": str(m_fecha), "tipo": m_tipo, "resp": m_resp, "notas": m_notas, "estado": "⏳ Pendiente"})
                    st.rerun()
            st.markdown("<br><h4>📋 Historial</h4>", unsafe_allow_html=True)
            mantenimientos = cargar_mantenimientos().get(p['nombre'], [])
            if not mantenimientos: st.info("No hay mantenimientos programados.")
            else:
                for i, m in enumerate(reversed(mantenimientos)):
                    real_idx = len(mantenimientos) - 1 - i
                    st.markdown(f"<div style='background:white; padding:15px; border-radius:8px; border:1px solid #eaeaea; margin-bottom:10px;'><b>{m['tipo']}</b> - {m['estado']}<br><span style='font-size:12px; color:#7f8c8d;'>📅 {m['fecha']} | 👨‍🔧 {m['resp']} | 📝 {m['notas']}</span></div>", unsafe_allow_html=True)
                    c_btn1, c_btn2, _ = st.columns([1,1,8])
                    if m['estado'] == "⏳ Pendiente" and c_btn1.button("✅", key=f"ok_{real_idx}"):
                        actualizar_estado_mantenimiento(p['nombre'], real_idx, "✅ Completado")
                        st.rerun()
                    if c_btn2.button("🗑️", key=f"del_{real_idx}"):
                        eliminar_mantenimiento(p['nombre'], real_idx)
                        st.rerun()

elif menu == "🚨 Centro de Alertas":
    st.title("🚨 CENTRO DE ALERTAS")
    if not plantas_permitidas: st.info("No hay plantas registradas.")
    else: st.success("✅ Todos los sistemas operando dentro de los parámetros normales.")
