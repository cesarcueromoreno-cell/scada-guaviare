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

PLANTA_HEADERS = ["nombre", "ubicacion", "capacidad", "inversores", "datalogger", "tipo_sistema", "smart_meter", "imagen_url"]

def cargar_usuarios():
    if not supabase: return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}
    try:
        res = supabase.table("usuarios").select("*").execute()
        if not res.data:
            supabase.table("usuarios").insert({"usuario": "admin", "pwd": "solar123", "rol": "admin", "estado": "active", "planta_asignada": "Todas"}).execute()
            return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}
        return {r["usuario"]: {"pwd": r["pwd"], "status": r["estado"], "role": r["rol"], "planta_asignada": r["planta_asignada"]} for r in res.data}
    except: return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}

def solicitar_usuario(usuario, contrasena):
    db = cargar_usuarios()
    if usuario in db: return False, "⚠️ Este usuario ya existe o tiene una solicitud pendiente."
    if supabase:
        try:
            supabase.table("usuarios").insert({"usuario": str(usuario), "pwd": str(contrasena), "estado": "pending", "rol": "viewer", "planta_asignada": "Pendiente Asignar"}).execute()
            return True, "✅ Solicitud enviada. Espere a que el Administrador apruebe su cuenta."
        except: pass
    return False, f"❌ {db_estado}"

def actualizar_usuario_bd(usuario_id, nuevo_estado, nuevo_rol, nueva_planta, nueva_pwd=None):
    if supabase:
        datos = {"estado": str(nuevo_estado), "rol": str(nuevo_rol), "planta_asignada": str(nueva_planta)}
        if nueva_pwd: datos["pwd"] = str(nueva_pwd)
        try: supabase.table("usuarios").update(datos).eq("usuario", str(usuario_id)).execute()
        except: pass

def eliminar_usuario_bd(usuario_id):
    if supabase:
        try: supabase.table("usuarios").delete().eq("usuario", str(usuario_id)).execute()
        except: pass

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

def actualizar_planta(idx, p_edit):
    if not supabase: return False, db_estado
    try:
        plantas = cargar_plantas()
        if idx < len(plantas):
            datos = {k: str(v) for k, v in p_edit.items() if k not in ["id", "creado_en"]}
            supabase.table("plantas").update(datos).eq("id", plantas[idx]["id"]).execute()
            return True, ""
    except Exception as e:
        return False, str(e)
    return False, "Error desconocido"

def eliminar_planta(idx):
    if supabase:
        try:
            plantas = cargar_plantas()
            if idx < len(plantas):
                supabase.table("plantas").delete().eq("id", plantas[idx]["id"]).execute()
        except: pass

def cargar_mantenimientos():
    if supabase:
        try:
            res = supabase.table("mantenimientos").select("*").order("id").execute()
            mants = {}
            for r in res.data:
                planta = r["planta_nombre"]
                if planta not in mants: mants[planta] = []
                mants[planta].append({"fecha": str(r["fecha"]), "tipo": r["tipo_tarea"], "resp": r["tecnico"], "notas": r["notas"], "estado": r["estado"]})
            return mants
        except: return {}
    return {}

def guardar_mantenimiento(planta, datos_mant):
    if supabase:
        try:
            supabase.table("mantenimientos").insert({
                "planta_nombre": str(planta), "fecha": str(datos_mant["fecha"]), "tipo_tarea": str(datos_mant["tipo"]),
                "tecnico": str(datos_mant["resp"]), "notas": str(datos_mant["notas"]), "estado": str(datos_mant["estado"])
            }).execute()
        except: pass

def actualizar_estado_mantenimiento(planta, indice, nuevo_estado):
    if supabase:
        try:
            res = supabase.table("mantenimientos").select("*").eq("planta_nombre", str(planta)).order("id").execute()
            if indice < len(res.data):
                supabase.table("mantenimientos").update({"estado": str(nuevo_estado)}).eq("id", res.data[indice]["id"]).execute()
        except: pass

def eliminar_mantenimiento(planta, indice):
    if supabase:
        try:
            res = supabase.table("mantenimientos").select("*").eq("planta_nombre", str(planta)).order("id").execute()
            if indice < len(res.data):
                supabase.table("mantenimientos").delete().eq("id", res.data[indice]["id"]).execute()
        except: pass

# ==========================================
# 3. MANEJO DE VÍNCULOS Y PARÁMETROS
# ==========================================
if "delete" in st.query_params:
    try:
        idx = int(st.query_params["delete"])
        eliminar_planta(idx)
        st.query_params.clear()
        st.rerun()
    except: pass
if "edit" in st.query_params:
    try:
        idx = int(st.query_params["edit"])
        st.session_state["editando_planta"] = idx
        st.query_params.clear()
    except: pass

# ==========================================
# 5. LOGIN
# ==========================================
if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #f1c40f !important;'>☀️ MONISOLAR APP</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white !important;'>Plataforma de Gestión - CV INGENIERÍA SAS</h3><br>", unsafe_allow_html=True)
    
    if not supabase:
        st.error(f"🔴 ESTADO DE CONEXIÓN: {db_estado}. Por favor verifica el cuadro de Secrets en Streamlit.")
        
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
# 6. FILTRADO DE SEGURIDAD Y NAVEGACIÓN
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

if "menu_anterior" not in st.session_state or st.session_state["menu_anterior"] != menu:
    st.session_state["ver_detalle_inv"] = False
    st.session_state["ver_detalle_logger"] = False
    st.session_state["ver_detalle_bateria"] = False
    st.session_state["menu_anterior"] = menu

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.update({"autenticado": False, "usuario": None, "rol": None, "planta_asignada": "Todas", "red_desbloqueada": False, "reinicio_desbloqueado": False, "ver_detalle_inv": False, "ver_detalle_logger": False, "ver_detalle_bateria": False})
    st.rerun()

# ==========================================
# 7. FUNCIONES DE SIMULACIÓN Y GRÁFICOS
# ==========================================
def subir_imagen_simulado(uploaded_file):
    if uploaded_file is not None:
        with st.spinner("Procesando imagen local..."):
            time.sleep(1) 
            return "https://images.unsplash.com/photo-1508514177221-188b1c77eca0?auto=format&fit=crop&w=800&q=80" 
    return ""

def get_data(pl):
    cap_val = pl.get("capacidad", "5")
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val))[0]) * 1000 if re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val)) else 5000
    p_sol = int(cap * random.uniform(0.1, 0.8))
    e_dia = round((p_sol * random.uniform(3.5, 5.0)) / 1000, 1)
    soc = random.randint(15, 99) 
    return {"solar": p_sol, "casa": int(p_sol*0.4) + random.randint(500, 1500), "soc": soc, "hoy": e_dia, "alertas": []}

def simular_historico_24h_avanzado(planta):
    cap_val = planta.get("capacidad", "30")
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val))[0]) if re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val)) else 30.0
    inicio_dia = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    datos = []
    
    for m in range(0, 24 * 60, 30):
        t = inicio_dia + timedelta(minutes=m)
        h = t.hour + t.minute/60.0
        
        # Simulación de campana de Gauss para el sol
        gen = max(0, cap * math.exp(-0.5 * ((h - 13) / 2.5)**2) * random.uniform(0.9, 1.1)) if 6 <= h <= 18 else 0
        con = max(cap * 0.15, cap * 0.3 * math.exp(-0.5 * ((h - 8) / 2)**2) + cap * 0.4 * math.exp(-0.5 * ((h - 19) / 2.5)**2)) * random.uniform(0.9, 1.1)
        
        diff = gen - con
        grid_feed = max(0, diff) if pl.get('tipo_sistema', 'Híbrido') != 'Off-Grid' else 0
        grid_purchase = max(0, -diff) if pl.get('tipo_sistema', 'Híbrido') != 'Off-Grid' else 0
        
        datos.append({
            "timestamp": t,
            "Generation PV": round(gen, 2),
            "Total Consumption": round(con, 2),
            "Grid Purchase": round(grid_purchase, 2),
            "Grid Feed-in": round(grid_feed, 2)
        })
    return pd.DataFrame(datos)

def simular_datos_7_dias(planta):
    cap_val = planta.get("capacidad", "30")
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val))[0]) if re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val)) else 30.0
    
    fechas = [(datetime.now() - timedelta(days=i)).strftime("%a\n(%b %d)") for i in range(6, -1, -1)]
    datos = []
    for f in fechas:
        gen_pv = round(cap * random.uniform(3.5, 5.0), 1)
        cons = round(gen_pv * random.uniform(0.6, 1.2), 1)
        grid_p = round(cons * random.uniform(0.1, 0.4), 1)
        grid_f = round(gen_pv * random.uniform(0.05, 0.3), 1)
        datos.append({"Día": f, "Gen PV": gen_pv, "Cons Total": cons, "Grid Purchase": grid_p, "Grid Feed-in": grid_f})
    
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
# 8. VISTAS (ADMINISTRADOR Y CLIENTE)
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
    st.session_state["ver_detalle_inv"] = False
    st.session_state["ver_detalle_logger"] = False
    st.session_state["ver_detalle_bateria"] = False
    
    if st.session_state["editando_planta"] is not None:
        idx = st.session_state["editando_planta"]
        p_edit = plantas_permitidas[idx]
        st.markdown(f"<h3>✏️ Editar Parámetros e Imagen: {p_edit['nombre']}</h3>", unsafe_allow_html=True)
        
        img_url_final = p_edit.get('imagen_url', '')
        with st.expander("🖼️ Gestionar Imagen de la Planta", expanded=True):
            modo_img = st.radio("Método de subida", ["Dejar imagen actual", "Subir archivo desde PC", "Pegar enlace URL en línea"], horizontal=True, key="modo_edit")
            
            if modo_img == "Subir archivo desde PC":
                st.info("💡 En esta versión de prueba, la foto que subas se reemplazará por una imagen demostrativa para no saturar la base de datos.")
                uploaded_file = st.file_uploader("Elija una foto o diagrama (PNG, JPG)", type=['png', 'jpg', 'jpeg'], key="file_edit")
                if uploaded_file:
                    st.image(uploaded_file, caption="Su imagen (Vista previa local)", width=200)
                    if st.button("Confirmar subida", key="btn_conf_edit"):
                        img_url_final = subir_imagen_simulado(uploaded_file)
                        st.success("✅ Imagen simulada cargada. ¡Guarde los cambios abajo!")
            
            elif modo_img == "Pegar enlace URL en línea":
                img_url_final = st.text_input("Pegue la URL de la imagen aquí", p_edit.get('imagen_url', ''), placeholder="https://ejemplo.com/imagen.jpg", key="url_edit")
                if img_url_final:
                    try: st.image(img_url_final, caption="Vista previa de URL", width=200)
                    except: st.error("⚠️ No se pudo cargar la vista previa de la URL.")

            elif modo_img == "Dejar imagen actual" and img_url_final:
                 st.image(img_url_final, caption="Imagen actual", width=200)

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
                nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(c))
                cap_val = float(nums[0]) if nums else 0.0
                dl_val = str(sn).strip() if str(sn).strip() else f"SN-{random.randint(10000,99999)}"
                
                p_edit.update({
                    "nombre": str(n).strip(), "ubicacion": str(u).strip(), "capacidad": cap_val, 
                    "datalogger": dl_val, "tipo_sistema": str(n_tipo), 
                    "smart_meter": str(n_meter), "imagen_url": str(img_url_final) 
                })
                ok, msg = actualizar_planta(idx, p_edit)
                if ok:
                    st.session_state["editando_planta"] = None
                    st.success("✅ Planta actualizada correctamente.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Error al actualizar. Detalle: {msg}")

    if st.session_state.get("mostrar_crear"):
        st.markdown("<h3>➕ Crear Nueva Planta</h3>", unsafe_allow_html=True)
        
        img_url_crear = ""
        with st.expander("🖼️ Añadir Imagen de la Planta (Opcional)", expanded=True):
            modo_img_crear = st.radio("Método de subida", ["Ninguna", "Subir archivo desde PC", "Pegar enlace URL en línea"], horizontal=True, key="modo_crear")
            
            if modo_img_crear == "Subir archivo desde PC":
                st.info("💡 En esta versión de prueba, la foto que subas se reemplazará por una imagen demostrativa para no saturar la base de datos.")
                uploaded_file_crear = st.file_uploader("Elija una foto o diagrama (PNG, JPG)", type=['png', 'jpg', 'jpeg'], key="file_crear")
                if uploaded_file_crear:
                    st.image(uploaded_file_crear, caption="Su imagen (Vista previa local)", width=200)
                    if st.button("Confirmar subida", key="btn_conf_crear"):
                        img_url_crear = subir_imagen_simulado(uploaded_file_crear)
                        st.success("✅ Imagen simulada cargada. Puede guardar la planta.")
            
            elif modo_img_crear == "Pegar enlace URL en línea":
                img_url_crear = st.text_input("Pegue la URL de la imagen aquí", placeholder="https://ejemplo.com/imagen.jpg", key="url_crear")
                if img_url_crear:
                    try: st.image(img_url_crear, caption="Vista previa de URL", width=200)
                    except: st.error("⚠️ No se pudo cargar la vista previa.")

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
                    nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(n_cap))
                    cap_val = float(nums[0]) if nums else 0.0
                    dl_val = str(n_sn).strip() if str(n_sn).strip() else f"SN-{random.randint(10000,99999)}"
                    
                    payload = {
                        "nombre": str(n_nom).strip(), 
                        "ubicacion": str(n_ubi).strip(), 
                        "capacidad": cap_val, 
                        "inversores": str(n_inv), 
                        "datalogger": dl_val, 
                        "tipo_sistema": str(n_tipo), 
                        "smart_meter": str(n_meter), 
                        "imagen_url": str(img_url_crear) 
                    }
                    
                    ok, msg = guardar_planta(payload)
                    if ok:
                        st.session_state["mostrar_crear"] = False
                        st.success("✅ Planta creada con éxito.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.error("⚠️ El nombre de la planta es obligatorio.")
            
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
            
            img_portada = pl.get('imagen_url', '')
            img_html = f'<div style="width: 80px; height: 60px; border-radius: 6px; margin-right: 15px; background-image: url(\'{img_portada}\'); background-size: cover; background-position: center; border: 1px solid #ddd;"></div>' if img_portada else '<img src="https://img.icons8.com/color/48/solar-panel.png" style="width: 48px; margin-right:15px;"/>'

            col_card, col_btns = st.columns([11, 1])
            with col_card:
                st.markdown(f"""
                <div class="tarjeta-dash-pro" style="margin-bottom:0px;">
                <div style="display:flex; align-items:center; width: 320px; flex-shrink: 0;">
                    {img_html}
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
    
    if "planta_actual" not in st.session_state or st.session_state["planta_actual"] != p["nombre"]:
        st.session_state["ver_detalle_inv"] = False
        st.session_state["ver_detalle_logger"] = False
        st.session_state["ver_detalle_bateria"] = False
        st.session_state["planta_actual"] = p["nombre"]
        
    d = get_data(p)
    
    tipo_sistema_actual = p.get('tipo_sistema', 'Híbrido')
    smart_meter_actual = p.get('smart_meter', 'Ninguno')
    sn_logger = str(p.get('datalogger', 'N/A'))
    marca_inv = str(p.get('inversores', 'Genérico'))
    capacidad = str(p.get('capacidad', '30'))
    
    st.markdown(f"<h2>{p['nombre']} <span style='font-size:14px; color:#7f8c8d; font-weight:normal;'>| 🟢 En línea | Tipo: {tipo_sistema_actual} | SN: {sn_logger}</span></h2><hr style='margin-top:0px; margin-bottom:20px; border-color:#e0e0e0;'>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
    c1.markdown(f"<div class='solarman-card' style='border-top: 4px solid #f1c40f;'><div class='solarman-val'>{d['hoy']} kWh</div><div class='solarman-lbl'>Producción Solar Hoy</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='solarman-card' style='border-top: 4px solid #e74c3c;'><div class='solarman-val'>{round(d['hoy']*0.45,1)} kWh</div><div class='solarman-lbl'>Consumo Hoy</div></div>", unsafe_allow_html=True)
    
    if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
        c3.markdown(f"<div class='solarman-card' style='border-top: 4px solid #9b59b6;'><div style='font-size:14px; font-weight:bold; color:#2c3e50;'>SOC {d['soc']}% </div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>🔋 {round(d['hoy']*0.2,1)} kWh <span class='solarman-lbl-sm'>Carga</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>🔋 {round(d['hoy']*0.1,1)} kWh <span class='solarman-lbl-sm'>Descarga</span></div></div>", unsafe_allow_html=True)
    else:
        c3.markdown(f"<div class='solarman-card' style='border-top: 4px solid #bdc3c7;'><div style='font-size:20px; font-weight:bold; color:#bdc3c7;'>--</div><div class='solarman-lbl'>Sin Baterías</div></div>", unsafe_allow_html=True)

    if tipo_sistema_actual in ["Híbrido", "On-Grid"]:
        c4.markdown(f"<div class='solarman-card' style='border-top: 4px solid #3498db;'><div style='font-size:14px; font-weight:bold; color:#2c3e50;'>⚡ 500 W <span class='solarman-lbl-sm'>A Red</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>⚡ 300 W <span class='solarman-lbl-sm'>De Red</span></div></div>", unsafe_allow_html=True)
    else:
        c4.markdown(f"<div class='solarman-card' style='border-top: 4px solid #bdc3c7;'><div style='font-size:20px; font-weight:bold; color:#bdc3c7;'>--</div><div class='solarman-lbl'>Aislado (Off-Grid)</div></div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state['rol'] == 'admin':
        t_graf, t_disp, t_ctrl, t_rep, t_om = st.tabs(["📈 Panel Gráfico", "🔌 Dispositivos", "⚙️ Control Remoto", "📄 Reportes PDF", "🛠️ O&M"])
    else:
        t_graf, t_disp, t_rep = st.tabs(["📈 Panel Gráfico", "🔌 Dispositivos", "📄 Reportes PDF"])
        t_ctrl, t_om = None, None
    
    with t_graf:
        col_g1, col_g2 = st.columns([1, 1])
        
        with col_g1:
            st.markdown("<div style='background:#1f2937; border-radius:8px; padding:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>", unsafe_allow_html=True)
            df_historico = simular_historico_24h_avanzado(p)
            
            fig1 = make_subplots(specs=[[{"secondary_y": False}]])
            
            fig1.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['Generation PV'], 
                                     fill='tozeroy', mode='lines', 
                                     line=dict(color='#f1c40f', width=2), 
                                     name='Generation PV',
                                     hovertemplate='%{y:.2f} kW<extra></extra>'))
            
            fig1.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['Total Consumption'], 
                                     mode='lines', 
                                     line=dict(color='#e74c3c', width=2.5), 
                                     name='Total Consumption',
                                     hovertemplate='%{y:.2f} kW<extra></extra>'))
                                     
            if tipo_sistema_actual in ["Híbrido", "On-Grid"]:
                fig1.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['Grid Purchase'], 
                                         mode='lines', 
                                         line=dict(color='#9b59b6', width=2), 
                                         name='Grid Purchase',
                                         hovertemplate='%{y:.2f} kW<extra></extra>'))
                
                fig1.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['Grid Feed-in'], 
                                         mode='lines', 
                                         line=dict(color='#3498db', width=2), 
                                         name='Grid Feed-in',
                                         hovertemplate='%{y:.2f} kW<extra></extra>'))

            fig1.update_layout(
                title=dict(text="Daily Power Flow Detail (Past 24 Hours Real-time)", font=dict(size=16, color='white', family="Arial")),
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=11, color="white")),
                margin=dict(l=10, r=10, t=40, b=10), 
                height=450,
                hovermode="x unified",
                hoverlabel=dict(bgcolor="#2c3e50", font=dict(size=12, color="white", family="Arial"))
            )
            
            fig1.update_yaxes(title_text="kW", gridcolor="#374151", tickfont=dict(color="white"))
            fig1.update_xaxes(tickformat="%I %p", dtick=3 * 3600000, gridcolor="#374151", tickfont=dict(color="white"))
            
            idx_max_gen = df_historico['Generation PV'].idxmax()
            max_gen = float(df_historico.loc[idx_max_gen, 'Generation PV'])
            max_gen_time = df_historico.loc[idx_max_gen, 'timestamp'] 
            
            fig1.add_annotation(x=max_gen_time, y=max_gen, text=f"Peak Solar: {max_gen:.0f} kW at 1 PM", 
                               showarrow=True, arrowhead=1, arrowcolor="#f1c40f", 
                               bgcolor="white", bordercolor="#f1c40f", font=dict(color="black", size=10))

            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_g2:
            st.markdown("<div style='background:#1f2937; border-radius:8px; padding:15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);'>", unsafe_allow_html=True)
            
            df_7dias = simular_datos_7_dias(p)
            
            fig2 = go.Figure()
            
            fig2.add_trace(go.Bar(x=df_7dias['Día'], y=df_7dias['Gen PV'], name='Gen PV', marker_color='#f1c40f', text=df_7dias['Gen PV'], textposition='outside'))
            fig2.add_trace(go.Bar(x=df_7dias['Día'], y=df_7dias['Cons Total'], name='Cons Total', marker_color='#e74c3c', text=df_7dias['Cons Total'], textposition='outside'))
            
            if tipo_sistema_actual in ["Híbrido", "On-Grid"]:
                fig2.add_trace(go.Bar(x=df_7dias['Día'], y=df_7dias['Grid Purchase'], name='Grid Purchase', marker_color='#9b59b6', text=df_7dias['Grid Purchase'], textposition='outside'))
                fig2.add_trace(go.Bar(x=df_7dias['Día'], y=df_7dias['Grid Feed-in'], name='Grid Feed-in', marker_color='#3498db', text=df_7dias['Grid Feed-in'], textposition='outside'))

            fig2.update_layout(
                title=dict(text="Daily Energy Category Comparison (kWh) - Past 7 Days", font=dict(size=16, color='white', family="Arial")),
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                barmode='group',
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=11, color="white")),
                margin=dict(l=10, r=10, t=40, b=10), 
                height=450,
                hoverlabel=dict(bgcolor="#2c3e50", font=dict(size=12, color="white", family="Arial"))
            )
            
            fig2.update_yaxes(gridcolor="#374151", tickfont=dict(color="white"))
            fig2.update_xaxes(tickfont=dict(color="white"))
            
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
    with t_disp:
        if not st.session_state["ver_detalle_inv"] and not st.session_state["ver_detalle_logger"] and not st.session_state["ver_detalle_bateria"]:
            style_inversor_link = """
            <style>
            div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button {
                background-color: transparent !important;
                border: none !important;
                color: #3498db !important;
                box-shadow: none !important;
                padding: 0 !important;
                height: auto !important;
                min-height: auto !important;
                justify-content: flex-start !important;
            }
            div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button p {
                font-size: 15px !important;
                font-weight: bold !important;
            }
            div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button:hover p {
                text-decoration: underline !important;
                color: #2980b9 !important;
            }
            </style>
            """
            st.markdown(style_inversor_link, unsafe_allow_html=True)

            st.markdown("### 🔌 Lista de Dispositivos Registrados")
            st.markdown("""
            <style>
            .div-header { background-color: #f8f9fa; padding: 12px; border-radius: 5px 5px 0 0; border: 1px solid #eaeaea; border-bottom: none; display: flex; font-weight: bold; color: #7f8c8d; font-size: 14px; align-items: center; }
            .stColumn { display: flex; align-items: center; }
            </style>
            <div class="div-header">
                <div style="flex: 2;">Nombre/SN</div>
                <div style="flex: 1.5;">Tipo</div>
                <div style="flex: 1;">Estado</div>
                <div style="flex: 1;">Actuación</div>
                <div style="flex: 1.5;">Potencia solar(kW)</div>
                <div style="flex: 1.5;">Producción diaria(kWh)</div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1, 1.5, 1.5])
            with st.container():
                if col1.button(f"Inversor ({capacidad}) ▼"):
                    st.session_state["ver_detalle_inv"] = True
                    st.session_state["ver_detalle_logger"] = False
                    st.session_state["ver_detalle_bateria"] = False
                    st.rerun()
                col1.markdown(f"<span style='color:#7f8c8d; font-size:12px; margin-top:-15px; display:block;'>{sn_logger}</span>", unsafe_allow_html=True)
                col2.write("Híbrido HV trifásico")
                col3.markdown("<div style='color:#27ae60; font-weight:bold;'>🟢 En línea</div>", unsafe_allow_html=True)
                col4.markdown("<div style='color:#27ae60;'>Normal</div>", unsafe_allow_html=True)
                col5.write(f"{round(d['solar']/1000, 2)}")
                col6.write(f"{d['hoy']}")
            st.markdown("<hr style='margin:0; padding:0; border-top: 1px solid #eaeaea;'>", unsafe_allow_html=True)

            col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1, 1.5, 1.5])
            with st.container():
                if col1.button(f"Registrador ▼", key="btn_log_nombre"):
                    st.session_state["ver_detalle_inv"] = False
                    st.session_state["ver_detalle_logger"] = True
                    st.session_state["ver_detalle_bateria"] = False
                    st.rerun()
                col1.markdown(f"<span style='color:#7f8c8d; font-size:12px; margin-top:-15px; display:block;'>{sn_logger}</span>", unsafe_allow_html=True)
                col2.write("Registrador")
                col3.markdown("<div style='color:#27ae60; font-weight:bold;'>🟢 En línea</div>", unsafe_allow_html=True)
                col4.markdown("<div style='color:#27ae60;'>Normal</div>", unsafe_allow_html=True)
                col5.write("--")
                col6.write("--")
            st.markdown("<hr style='margin:0; padding:0; border-top: 1px solid #eaeaea;'>", unsafe_allow_html=True)

            if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1, 1.5, 1.5])
                with st.container():
                    if col1.button(f"Batería ▼", key="btn_bat_nombre"):
                        st.session_state["ver_detalle_inv"] = False
                        st.session_state["ver_detalle_logger"] = False
                        st.session_state["ver_detalle_bateria"] = True
                        st.rerun()
                    col1.markdown(f"<span style='color:#7f8c8d; font-size:12px; margin-top:-15px; display:block;'>BAT-{sn_logger[-4:] if len(sn_logger) > 4 else '001'}</span>", unsafe_allow_html=True)
                    col2.write("Batería Litio")
                    col3.markdown("<div style='color:#27ae60; font-weight:bold;'>🟢 En línea</div>", unsafe_allow_html=True)
                    col4.markdown("<div style='color:#27ae60;'>Normal</div>", unsafe_allow_html=True)
                    col5.write("--")
                    col6.write("--")
                st.markdown("<hr style='margin:0; padding:0; border-top: 1px solid #eaeaea;'>", unsafe_allow_html=True)

            if smart_meter_actual != "Ninguno":
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1, 1.5, 1.5])
                with st.container():
                    col1.markdown(f"<span style='color:#3498db; font-weight:bold;'>{smart_meter_actual} ▼</span><br><span style='color:#7f8c8d; font-size:12px;'>MTR-{sn_logger[-4:] if len(sn_logger) > 4 else '001'}</span>", unsafe_allow_html=True)
                    col2.write(smart_meter_actual)
                    col3.markdown("<div style='color:#27ae60; font-weight:bold;'>🟢 En línea</div>", unsafe_allow_html=True)
                    col4.markdown("<div style='color:#27ae60;'>Normal</div>", unsafe_allow_html=True)
                    col5.write("--")
                    col6.write("--")
                st.markdown("<hr style='margin:0; padding:0; border-top: 1px solid #eaeaea;'>", unsafe_allow_html=True)

        elif st.session_state["ver_detalle_inv"]:
            if st.button("⬅ Volver a la lista de dispositivos", type="secondary"):
                st.session_state["ver_detalle_inv"] = False
                st.rerun()
            
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:15px;'>
                <div>
                    <h2 style='margin-bottom:0;'>inversor 1.1:{sn_logger}</h2>
                    <span style='color:#27ae60; font-weight:bold; font-size:14px;'>🟢 En línea</span>
                </div>
                <span style='color:#7f8c8d; font-size:13px;'>{datetime.now().strftime('%Y/%m/%d %H:%M:%S UTC-05:00')}</span>
            </div>
            <hr style='margin-top:0px;'>
            """, unsafe_allow_html=True)
            
            t_det_1, t_det_2, t_det_3, t_det_4 = st.tabs(["Detalles", "Alerta", "Arquitectura", "Datos históricos"])
            
            with t_det_1:
                with st.expander("Información básica", expanded=True):
                    st.markdown(f"""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>NS:</span> {sn_logger}</div>
                        <div><span class='diag-lbl'>Tipo de inversor:</span> Híbrido HV trifásico</div>
                        <div><span class='diag-lbl'>Potencia nominal:</span> {capacidad} kW</div>
                        <div><span class='diag-lbl'>Hora del sistema:</span> {datetime.now().strftime('%d-%m-%y %H:%M:%S')}</div>
                        <div><span class='diag-lbl'>HV Voltage:</span> 373 V</div>
                        <div><span class='diag-lbl'>Bus-N Voltage:</span> 186 V</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with st.expander("Información de versión", expanded=False):
                    st.markdown("""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>Versión protocolo:</span> 0104</div>
                        <div><span class='diag-lbl'>PRINCIPAL:</span> 3103-1086-1E10</div>
                        <div><span class='diag-lbl'>HMI:</span> 2001-C036</div>
                        <div><span class='diag-lbl'>Número versión batería 1:</span> 4101</div>
                        <div><span class='diag-lbl'>Número versión batería 2:</span> 0000</div>
                        <div><span class='diag-lbl'>Arc Board Firmware:</span> F204</div>
                        <div><span class='diag-lbl'>English Version:</span> 1004</div>
                        <div><span class='diag-lbl'>Versión en español:</span> 1004</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with st.expander("Generación eléctrica", expanded=True):
                    col_dc, col_icono, col_ac = st.columns([5, 1, 5])
                    with col_dc:
                        st.markdown("""
                        <table style='width:100%; text-align:left; font-size:13px; color:#3498db; border-collapse:collapse;'>
                            <tr style='color:#7f8c8d; border-bottom:1px solid #eaeaea;'>
                                <th style='padding:8px;'>Corriente continua</th><th style='padding:8px;'>Voltaje</th><th style='padding:8px;'>Actual</th><th style='padding:8px;'>Fuerza</th><th style='padding:8px;'>Estado</th>
                            </tr>
                            <tr style='border-bottom:1px solid #f8f9fa;'><td style='padding:8px;'>PV1</td><td>0.00 V</td><td>0.00 A</td><td>0.00 W</td><td>✔</td></tr>
                            <tr style='border-bottom:1px solid #f8f9fa;'><td style='padding:8px;'>PV2</td><td>0.00 V</td><td>0.00 A</td><td>0.00 W</td><td>✔</td></tr>
                            <tr style='border-bottom:1px solid #f8f9fa;'><td style='padding:8px;'>PV3</td><td>0.00 V</td><td>0.00 A</td><td>0.00 W</td><td>✔</td></tr>
                            <tr><td style='padding:8px;'>PV4</td><td>30.10 V</td><td>0.00 A</td><td>0.00 W</td><td>✔</td></tr>
                        </table>
                        """, unsafe_allow_html=True)
                    with col_icono:
                        st.markdown("<br><br><br><div style='background-color:#3498db; color:white; border-radius:8px; padding:15px; text-align:center; font-weight:bold;'>DC/AC<br>≈</div>", unsafe_allow_html=True)
                    with col_ac:
                        st.markdown("""
                        <table style='width:100%; text-align:left; font-size:13px; color:#3498db; border-collapse:collapse;'>
                            <tr style='color:#7f8c8d; border-bottom:1px solid #eaeaea;'>
                                <th style='padding:8px;'>Corriente alterna</th><th style='padding:8px;'>Voltaje</th><th style='padding:8px;'>Actual</th><th style='padding:8px;'>Frecuencia</th>
                            </tr>
                            <tr style='border-bottom:1px solid #f8f9fa;'><td style='padding:8px;'>R</td><td>121.30 V</td><td>7.50 A</td><td>60.00 Hz</td></tr>
                            <tr style='border-bottom:1px solid #f8f9fa;'><td style='padding:8px;'>S</td><td>121.20 V</td><td>7.90 A</td><td>--</td></tr>
                            <tr><td style='padding:8px;'>T</td><td>121.30 V</td><td>0.20 A</td><td>--</td></tr>
                        </table>
                        """, unsafe_allow_html=True)
                    st.markdown("<hr style='margin:10px 0; border-color:#eaeaea;'>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#7f8c8d; font-size:13px; margin-right:20px;'>PV daily power generation: <b>{d['hoy']} kWh</b></span> <span style='color:#7f8c8d; font-size:13px; margin-right:20px;'>Power factor: <b>0.00</b></span> <span style='color:#7f8c8d; font-size:13px;'>AC Voltage Max: <b>150.00 V</b></span>", unsafe_allow_html=True)

                with st.expander("Red eléctrica", expanded=False):
                    st.markdown("""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>Voltaje de red L1:</span> 0.00 V</div>
                        <div><span class='diag-lbl'>Corriente de red L1:</span> 0.00 A</div>
                        <div><span class='diag-lbl'>Potencia de red L1:</span> 0 W</div>
                        <div><span class='diag-lbl'>Voltaje de red L2:</span> 0.00 V</div>
                        <div><span class='diag-lbl'>Corriente de red L2:</span> 0.00 A</div>
                        <div><span class='diag-lbl'>Potencia de red L2:</span> 0 W</div>
                        <div><span class='diag-lbl'>Voltaje de red L3:</span> 0.00 V</div>
                        <div><span class='diag-lbl'>Corriente de red L3:</span> 0.00 A</div>
                        <div><span class='diag-lbl'>Potencia de red L3:</span> 0 W</div>
                        <div><span class='diag-lbl'>Estado de red:</span> Estática</div>
                        <div><span class='diag-lbl'>Frecuencia de red:</span> 0.00 Hz</div>
                        <div><span class='diag-lbl'>Potencia total de red:</span> 0 W</div>
                    </div>
                    """, unsafe_allow_html=True)

                with st.expander("Consumo eléctrico", expanded=False):
                    st.markdown("""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>Voltaje de carga L1:</span> 121.20 V</div>
                        <div><span class='diag-lbl'>Voltaje de carga L2:</span> 121.40 V</div>
                        <div><span class='diag-lbl'>Voltaje de carga L3:</span> 120.40 V</div>
                        <div><span class='diag-lbl'>Potencia de carga L1:</span> 940 W</div>
                        <div><span class='diag-lbl'>Potencia de carga L2:</span> 880 W</div>
                        <div><span class='diag-lbl'>Potencia de carga L3:</span> 21 W</div>
                        <div><span class='diag-lbl'>Consumo diario:</span> 9.10 kWh</div>
                        <div><span class='diag-lbl'>Frecuencia de carga:</span> 60.00 Hz</div>
                        <div><span class='diag-lbl'>Potencia consumo total:</span> 1.84 kW</div>
                    </div>
                    """, unsafe_allow_html=True)

                if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                    with st.expander("Batería", expanded=False):
                        st.markdown(f"""
                        <div class='diag-grid'>
                            <div><span class='diag-lbl'>Estado de batería:</span> Descargando</div>
                            <div><span class='diag-lbl'>Voltaje de batería:</span> 317.90 V</div>
                            <div><span class='diag-lbl'>Corriente de batería:</span> 5.82 A</div>
                            <div><span class='diag-lbl'>Potencia de batería:</span> 1.85 kW</div>
                            <div><span class='diag-lbl'>SoC:</span> {d['soc']} %</div>
                            <div><span class='diag-lbl'>Energía descarga diaria:</span> 9.00 kWh</div>
                            <div><span class='diag-lbl'>Tipo de batería:</span> Litio</div>
                            <div><span class='diag-lbl'>Fábrica de baterías:</span> Deye_HV</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with st.expander("BMS", expanded=False):
                        st.markdown("""
                        <div class='diag-grid'>
                            <div><span class='diag-lbl'>Voltaje BMS:</span> 318.00 V</div>
                            <div><span class='diag-lbl'>Corriente BMS:</span> 6.20 A</div>
                            <div><span class='diag-lbl'>Temperatura BMS:</span> 35.00 °C</div>
                            <div><span class='diag-lbl'>Límite corriente descarga:</span> 100 A</div>
                            <div><span class='diag-lbl'>Límite corriente carga:</span> 88 A</div>
                            <div><span class='diag-lbl'>SOH batería litio:</span> 99 %</div>
                        </div>
                        """, unsafe_allow_html=True)

                with st.expander("Temperatura y Estado", expanded=False):
                    st.markdown("""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>Temperatura batería:</span> 35.00 °C</div>
                        <div><span class='diag-lbl'>Temperatura CC:</span> 40.70 °C</div>
                        <div><span class='diag-lbl'>Temperatura CA:</span> 44.70 °C</div>
                        <div><span class='diag-lbl'>Estado relé lado CA:</span> 3</div>
                        <div><span class='diag-lbl'>Potencia carga UPS:</span> 1.84 kW</div>
                    </div>
                    """, unsafe_allow_html=True)

            with t_det_2: 
                st.markdown("<h4 style='color:#2c3e50; font-size:16px; margin-top:10px;'>Registro de banderas de hardware</h4>", unsafe_allow_html=True)
                st.markdown("""
                <div class='diag-grid' style='background:white; border:1px solid #eaeaea; border-radius:8px;'>
                    <div><span class='diag-lbl'>Bandera alarma batería litio:</span> 0000</div>
                    <div><span class='diag-lbl'>Bandera fallo batería litio:</span> 0000</div>
                    <div><span class='diag-lbl'>Bandera alarma batería litio 2:</span> 0000</div>
                    <div><span class='diag-lbl'>Bandera fallo batería litio 2:</span> 0000</div>
                </div>
                <div style='margin-top:20px; color:#27ae60; font-weight:bold;'>✔ No se detectan anomalías activas.</div>
                """, unsafe_allow_html=True)
                
            with t_det_3: 
                st.markdown("""
                <div style='display:flex; justify-content:space-between; align-items:center; margin-top:10px; border-bottom: 2px solid #eaeaea; padding-bottom: 10px;'>
                    <div style='color:#3498db; font-weight:bold; font-size:16px; border-bottom: 3px solid #3498db; padding-bottom: 8px; margin-bottom: -12px;'>Relación de comunicación</div>
                    <button style='background-color:#3498db; color:white; border:none; border-radius:4px; padding:6px 15px; font-weight:bold; cursor:pointer;'>Exportar</button>
                </div>
                <p style='color:#7f8c8d; font-size:13px; margin-top:15px;'>La topología de red real reflejada cuando el dispositivo está cargando datos.</p>
                """, unsafe_allow_html=True)

                time_str = datetime.now().strftime('%Y/%m/%d %H:%M:%S UTC-05:00')
                fake_logger_sn = sn_logger
                
                battery_html = ""
                if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                    battery_html = f"""<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left: 80px;'><span style='color:#7f8c8d;'>▼</span> Batería<br><span style='color:#7f8c8d; font-size:12px; margin-left: 15px;'>{sn_logger}M01</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>
<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left: 110px;'>Batería<br><span style='color:#7f8c8d; font-size:12px;'>03601000D2080004</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>"""

                table_html = f"""<div style='background:white; border:1px solid #eaeaea; border-radius:8px; overflow:hidden;'>
<table style='width:100%; text-align:left; font-size:14px; border-collapse:collapse;'>
<tr style='background-color:#f8f9fa; border-bottom:1px solid #eaeaea; color:#2c3e50;'>
<th style='padding:12px 20px;'>Tipo/SN</th><th style='padding:12px;'>Estado</th><th style='padding:12px;'>Actualizado</th>
</tr>
<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left:20px;'><span style='color:#7f8c8d;'>▼</span> Registrador<br><span style='color:#7f8c8d; font-size:12px; margin-left: 15px;'>{fake_logger_sn}</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>
<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left: 50px;'><span style='color:#3498db; font-weight:bold;'>▼ Inversor</span><br><span style='color:#3498db; font-size:12px; margin-left: 15px;'>INV-{sn_logger}</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>
{battery_html}
</table>
</div>"""
                st.markdown(table_html, unsafe_allow_html=True)
                
            with t_det_4:
                st.markdown("<h4 style='color:#2c3e50; font-size:16px; margin-top:10px;'>Datos históricos</h4>", unsafe_allow_html=True)
                
                col_r1, col_r2, col_r3, col_r4 = st.columns([4, 2, 2, 2])
                with col_r1:
                    st.radio("Periodo", ["Día", "Semana", "Mes", "Año", "Total"], horizontal=True, label_visibility="collapsed")
                with col_r2:
                    st.button("Seleccionar parámetros", use_container_width=True)
                with col_r3:
                    st.button("Exportar", use_container_width=True)
                with col_r4:
                    st.date_input("Fecha", value=datetime.now(), label_visibility="collapsed")
                    
                st.markdown("<hr style='margin:10px 0; border-color:#eaeaea;'>", unsafe_allow_html=True)
                
                col_p1, col_p2 = st.columns([2, 8])
                with col_p1:
                    st.markdown("<p style='color:#7f8c8d; font-size:14px; margin-top:10px;'>Plantilla del<br>sistema:</p>", unsafe_allow_html=True)
                with col_p2:
                    st.radio("Plantilla", ["Datos de CA", "Corriente DC", "Voltaje DC", "Corriente CC y voltaje CC"], horizontal=True, label_visibility="collapsed")
                    
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<a href='https://www.yuque.com/vwyy8s/za5o30/toaw7t?#%20%E3%80%8AHow%20to%20create%20my%20module%E3%80%8B' target='_blank' style='color:#3498db; font-size:14px; text-decoration:none;'>¿Cómo crear mi plantilla?</a>", unsafe_allow_html=True)

                x_time = pd.date_range(start="00:00", end="21:00", freq="15min")
                y_vol_R = [121.3 if (6 <= t.hour <= 18) else 0 for t in x_time]
                y_vol_S = [121.2 if (6 <= t.hour <= 18) else 0 for t in x_time]
                y_vol_T = [121.3 if (6 <= t.hour <= 18) else 0 for t in x_time]
                y_freq = [60.0 if (6 <= t.hour <= 18) else 0 for t in x_time]
                
                y_curr_R = [7.5 if (6 <= t.hour <= 18) else 0 for t in x_time]
                y_curr_S = [7.9 if (6 <= t.hour <= 18) else 0 for t in x_time]
                y_curr_T = [0.2 if (6 <= t.hour <= 18) else 0 for t in x_time]
                
                fig_ac = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig_ac.add_trace(go.Scatter(x=x_time, y=y_vol_R, mode='lines', line=dict(color='#3498db', shape='hv'), name='Voltaje CA R/U/A'), secondary_y=False)
                fig_ac.add_trace(go.Scatter(x=x_time, y=y_vol_S, mode='lines', line=dict(color='#e74c3c', shape='hv'), name='Voltaje CA S/V/B'), secondary_y=False)
                fig_ac.add_trace(go.Scatter(x=x_time, y=y_vol_T, fill='tozeroy', mode='lines', line=dict(color='#9b59b6', shape='hv'), name='Voltaje CA T/W/C'), secondary_y=False)
                fig_ac.add_trace(go.Scatter(x=x_time, y=y_freq, mode='lines', line=dict(color='#8e44ad', width=3, shape='hv'), name='Frecuencia R salida CA'), secondary_y=False)
                
                fig_ac.add_trace(go.Scatter(x=x_time, y=y_curr_R, mode='lines', line=dict(color='#2ecc71', shape='hv'), name='Corriente CA R/U/A'), secondary_y=True)
                fig_ac.add_trace(go.Scatter(x=x_time, y=y_curr_S, mode='lines', line=dict(color='#f1c40f', shape='hv'), name='Corriente CA S/V/B'), secondary_y=True)
                fig_ac.add_trace(go.Scatter(x=x_time, y=y_curr_T, mode='lines', line=dict(color='#1abc9c', shape='hv'), name='Corriente CA T/W/C'), secondary_y=True)
                
                fig_ac.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                    margin=dict(l=10, r=10, t=10, b=10), height=400
                )
                fig_ac.update_yaxes(title_text="Hz&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;V", range=[0, 150], gridcolor="#f0f0f0", secondary_y=False)
                fig_ac.update_yaxes(title_text="A", range=[0, 10], showgrid=False, secondary_y=True)
                fig_ac.update_xaxes(tickformat="%H:%M", dtick=3 * 3600000, gridcolor="#f0f0f0")
                
                st.plotly_chart(fig_ac, use_container_width=True)

        elif st.session_state["ver_detalle_logger"]:
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            if st.button("⬅ Volver a la lista de dispositivos", type="secondary"):
                st.session_state["ver_detalle_logger"] = False
                st.rerun()
            
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:15px; margin-top:10px;'>
                <div>
                    <h2 style='margin-bottom:0; font-size: 24px;'>Registrador wifi:{sn_logger}</h2>
                    <span style='color:#27ae60; font-weight:bold; font-size:14px;'>🟢 En línea</span>
                </div>
                <span style='color:#7f8c8d; font-size:13px;'>{datetime.now().strftime('%Y/%m/%d %H:%M:%S UTC-05:00')}</span>
            </div>
            <hr style='margin-top:0px; border-color:#eaeaea;'>
            """, unsafe_allow_html=True)
            
            t_log_1, t_log_2, t_log_3 = st.tabs(["Detalles", "Alerta", "Arquitectura"])
            
            with t_log_1:
                st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
                with st.expander("Información básica", expanded=True):
                    st.markdown(f"""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>SN:</span> {sn_logger}</div>
                        <div><span class='diag-lbl'>Modelo:</span> LSW-3</div>
                        <div><span class='diag-lbl'>Versión hardware:</span> LSW3_01_7A_0102</div>
                        <div><span class='diag-lbl'>Versión de firmware:</span> V1.0.6.28</div>
                        <div><span class='diag-lbl'>Versión protocolo:</span> 0104</div>
                        <div><span class='diag-lbl'>Hora del sistema:</span> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with st.expander("Información de Wi-Fi", expanded=False):
                    st.markdown("""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>SSID Conectado:</span> CV_SOLAR_GUEST</div>
                        <div><span class='diag-lbl'>Dirección IP Logger:</span> 192.168.1.105</div>
                        <div><span class='diag-lbl'>Intensidad de señal:</span> -65 dBm (Buena)</div>
                        <div><span class='diag-lbl'>Dirección MAC:</span> AA:BB:CC:DD:EE:FF</div>
                    </div>
                    """, unsafe_allow_html=True)

                with st.expander("Estado", expanded=False):
                    st.markdown("""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>Última actualización:</span> 15 segundos</div>
                        <div><span class='diag-lbl'>IP Servidor Remoto:</span> 47.102.152.71</div>
                        <div><span class='diag-lbl'>Tiempo Ping Servidor:</span> 180ms</div>
                    </div>
                    """, unsafe_allow_html=True)

            with t_log_2:
                st.markdown("""
                <div style='display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid #eaeaea; padding-bottom:10px; margin-bottom:15px; margin-top:10px;'>
                    <div style='display:flex; gap:20px; font-weight:bold; color:#7f8c8d; font-size:14px; align-items:center;'>
                        <span style='cursor:pointer;'>Todo</span>
                        <span style='color:#3498db; border-bottom:3px solid #3498db; padding-bottom:8px; margin-bottom:-11px; cursor:pointer;'>Abierto</span>
                        <span style='cursor:pointer;'>Cerrado</span>
                        <span style='cursor:pointer; border-left:1px solid #eaeaea; padding-left:15px;'>Filtrar ▼</span>
                    </div>
                    <div style='display:flex; gap:10px;'>
                        <button style='background:white; border:1px solid #eaeaea; border-radius:4px; padding:4px 8px; cursor:pointer;'>📥</button>
                        <button style='background:white; border:1px solid #eaeaea; border-radius:4px; padding:4px 8px; cursor:pointer; color:#7f8c8d; font-size:13px;'>🔄 Cerca ▼</button>
                    </div>
                </div>
                <p style='font-size:12px; color:#7f8c8d; line-height:1.5;'>La alerta "abierta" se refiere a la alerta que se está produciendo actualmente. Además, el ciclo de actualización del estado de alerta del dispositivo es de 5 minutos, por lo que el estado de alerta del dispositivo puede retrasarse. Es normal que a veces el dispositivo esté en estado de alerta, pero no hay una alerta "abierta".</p>
                
                <div style='text-align:center; padding: 60px 0;'>
                    <img src="https://img.icons8.com/ios/100/ced6e0/document--v1.png" width="60"/>
                    <p style='color:#7f8c8d; margin-top:10px; font-size:14px;'>Datos no disponibles</p>
                </div>
                
                <div style='display:flex; justify-content:flex-end; color:#bdc3c7; font-size:12px; align-items:center; gap:10px; margin-top:20px;'>
                    <span>< 1 ></span>
                    <select style='border:1px solid #eaeaea; border-radius:4px; padding:2px 5px; color:#bdc3c7;'><option>50/página</option></select>
                    <span>Ir a <input type="text" value="1" style="width:30px; text-align:center; border:1px solid #eaeaea; border-radius:4px; color:#bdc3c7;"> Página <b style='color:#bdc3c7;'>Total 0</b></span>
                </div>
                """, unsafe_allow_html=True)

            with t_log_3:
                st.markdown("""
                <div style='display:flex; justify-content:space-between; align-items:center; margin-top:10px; border-bottom: 2px solid #eaeaea; padding-bottom: 10px;'>
                    <div style='color:#3498db; font-weight:bold; font-size:16px; border-bottom: 3px solid #3498db; padding-bottom: 8px; margin-bottom: -12px;'>Relación de comunicación</div>
                    <button style='background-color:#3498db; color:white; border:none; border-radius:4px; padding:6px 15px; font-weight:bold; cursor:pointer;'>Exportar</button>
                </div>
                <p style='color:#7f8c8d; font-size:13px; margin-top:15px;'>La topología de red real reflejada cuando el dispositivo está cargando datos.</p>
                """, unsafe_allow_html=True)

                time_str = datetime.now().strftime('%Y/%m/%d %H:%M:%S UTC-05:00')
                fake_logger_sn = sn_logger
                
                battery_html = ""
                if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                    battery_html = f"""<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left: 80px;'><span style='color:#7f8c8d;'>▼</span> Batería<br><span style='color:#7f8c8d; font-size:12px; margin-left: 15px;'>{sn_logger}M01</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>
<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left: 110px;'>Batería<br><span style='color:#7f8c8d; font-size:12px;'>03601000D2080004</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>"""

                table_html = f"""<div style='background:white; border:1px solid #eaeaea; border-radius:8px; overflow:hidden;'>
<table style='width:100%; text-align:left; font-size:14px; border-collapse:collapse;'>
<tr style='background-color:#f8f9fa; border-bottom:1px solid #eaeaea; color:#2c3e50;'>
<th style='padding:12px 20px;'>Tipo/SN</th><th style='padding:12px;'>Estado</th><th style='padding:12px;'>Actualizado</th>
</tr>
<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left:20px;'><span style='color:#7f8c8d;'>▼</span> Registrador<br><span style='color:#7f8c8d; font-size:12px; margin-left: 15px;'>{fake_logger_sn}</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>
<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left: 50px;'><span style='color:#3498db; font-weight:bold;'>▼ Inversor</span><br><span style='color:#3498db; font-size:12px; margin-left: 15px;'>INV-{sn_logger}</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>
{battery_html}
</table>
</div>"""
                st.markdown(table_html, unsafe_allow_html=True)

        elif st.session_state["ver_detalle_bateria"]:
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            if st.button("⬅ Volver a la lista de dispositivos", type="secondary"):
                st.session_state["ver_detalle_bateria"] = False
                st.rerun()
            
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:15px; margin-top:10px;'>
                <div>
                    <h2 style='margin-bottom:0; font-size: 24px;'>Batería:{sn_logger}M01</h2>
                    <span style='color:#27ae60; font-weight:bold; font-size:14px;'>🟢 En línea</span>
                </div>
                <span style='color:#7f8c8d; font-size:13px;'>{datetime.now().strftime('%Y/%m/%d %H:%M:%S UTC-05:00')}</span>
            </div>
            <hr style='margin-top:0px; border-color:#eaeaea;'>
            """, unsafe_allow_html=True)
            
            t_bat_1, t_bat_2, t_bat_3, t_bat_4 = st.tabs(["Detalles", "Alerta", "Arquitectura", "Datos históricos"])
            
            with t_bat_1:
                st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
                with st.expander("Información básica", expanded=True):
                    st.markdown(f"""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>NS dispositivo conectado:</span> {sn_logger}M01</div>
                        <div><span class='diag-lbl'>Número paquete:</span> 6</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with st.expander("Información clave", expanded=True):
                    st.markdown(f"""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>Voltaje batería:</span> 323 V</div>
                        <div><span class='diag-lbl'>Corriente batería:</span> 0.00 A</div>
                        <div><span class='diag-lbl'>SOC batería:</span> 100 %</div>
                        <div><span class='diag-lbl'>SOH batería:</span> 100 %</div>
                        <div><span class='diag-lbl'>Temp batería:</span> 36.00 °C</div>
                    </div>
                    """, unsafe_allow_html=True)

                with st.expander("Límite de carga y descarga", expanded=True):
                    st.markdown("""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>Voltaje final carga:</span> 345 V</div>
                        <div><span class='diag-lbl'>Voltaje final descarga:</span> 0.00 V</div>
                        <div><span class='diag-lbl'>Corriente límite carga:</span> 0 A</div>
                        <div><span class='diag-lbl'>Corriente límite descarga:</span> 100 A</div>
                    </div>
                    """, unsafe_allow_html=True)

                with st.expander("Otro", expanded=True):
                    st.markdown("""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>Bandera carga forzada:</span> 0000</div>
                        <div><span class='diag-lbl'>Comprobar bandera SOC:</span> 0000</div>
                    </div>
                    """, unsafe_allow_html=True)

            with t_bat_2:
                st.markdown("""
                <div style='text-align:center; padding: 60px 0;'>
                    <img src="https://img.icons8.com/ios/100/ced6e0/document--v1.png" width="60"/>
                    <p style='color:#7f8c8d; margin-top:10px; font-size:14px;'>Datos no disponibles</p>
                </div>
                """, unsafe_allow_html=True)

            with t_bat_3:
                st.markdown("""
                <div style='display:flex; justify-content:space-between; align-items:center; margin-top:10px; border-bottom: 2px solid #eaeaea; padding-bottom: 10px;'>
                    <div style='color:#3498db; font-weight:bold; font-size:16px; border-bottom: 3px solid #3498db; padding-bottom: 8px; margin-bottom: -12px;'>Relación de comunicación</div>
                    <button style='background-color:#3498db; color:white; border:none; border-radius:4px; padding:6px 15px; font-weight:bold; cursor:pointer;'>Exportar</button>
                </div>
                <p style='color:#7f8c8d; font-size:13px; margin-top:15px;'>La topología de red real reflejada cuando el dispositivo está cargando datos.</p>
                """, unsafe_allow_html=True)

                time_str = datetime.now().strftime('%Y/%m/%d %H:%M:%S UTC-05:00')
                fake_logger_sn = sn_logger
                
                battery_html = f"""<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left: 80px;'><span style='color:#7f8c8d;'>▼</span> <span style='color:#3498db;'>Batería</span><br><span style='color:#3498db; font-size:12px; margin-left: 15px;'>{sn_logger}M01</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>
<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left: 110px;'>Batería<br><span style='color:#7f8c8d; font-size:12px;'>03601000D2080004</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>"""

                table_html = f"""<div style='background:white; border:1px solid #eaeaea; border-radius:8px; overflow:hidden;'>
<table style='width:100%; text-align:left; font-size:14px; border-collapse:collapse;'>
<tr style='background-color:#f8f9fa; border-bottom:1px solid #eaeaea; color:#2c3e50;'>
<th style='padding:12px 20px;'>Tipo/SN</th><th style='padding:12px;'>Estado</th><th style='padding:12px;'>Actualizado</th>
</tr>
<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left:20px;'><span style='color:#7f8c8d;'>▼</span> Registrador<br><span style='color:#7f8c8d; font-size:12px; margin-left: 15px;'>{fake_logger_sn}</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>
<tr style='border-bottom:1px solid #f8f9fa;'>
<td style='padding:12px; padding-left: 50px;'><span style='color:#3498db; font-weight:bold;'>▼ Inversor</span><br><span style='color:#3498db; font-size:12px; margin-left: 15px;'>INV-{sn_logger}</span></td>
<td style='padding:12px;'><img src="https://img.icons8.com/ios/24/576574/transmission-tower.png" width="16" /></td>
<td style='padding:12px; color:#2c3e50; font-size:13px;'>{time_str}</td>
</tr>
{battery_html}
</table>
</div>"""
                st.markdown(table_html, unsafe_allow_html=True)
                
            with t_bat_4:
                st.markdown("""
                <div style='text-align:center; padding: 40px 0;'>
                    <img src="https://img.icons8.com/ios/100/ced6e0/document--v1.png" width="60"/>
                    <p style='color:#7f8c8d; margin-top:10px; font-size:14px;'>Datos no disponibles</p>
                </div>
                """, unsafe_allow_html=True)


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
                    guardar_mantenimiento(p['nombre'], {"fecha": str(m_fecha), "tipo": str(m_tipo), "resp": str(m_resp), "notas": str(m_notas), "estado": "⏳ Pendiente"})
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
