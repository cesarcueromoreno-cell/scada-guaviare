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
import time

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y ESTILO (CSS)
# ==========================================
st.set_page_config(page_title="MOMISOLAR APP", page_icon="☀️", layout="wide")

css_global = """
<style>
/* =========================================
   REPARACIÓN DEFINITIVA DE COLORES 
   ========================================= */

/* FONDO DEL PAISAJE (Global) */
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=1920");
    background-size: cover; background-position: center; background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }

/* Textos blancos SOLO para las partes que están directo sobre el paisaje (Login y Títulos fuera del panel) */
.stApp > header + div > div > div > div > h1, 
.stApp > header + div > div > div > div > h3 { 
    color: #ffffff !important; 
    text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important; 
}

/* SIDEBAR OSCURO Y BOTÓN DE SALIR VISIBLE */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #112027 0%, #1a323c 50%, #162a33 100%) !important;
    border-right: 1px solid #2c5364 !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; text-shadow: none !important; }
/* Arreglo del botón "Cerrar Sesión" para que se vea el texto */
[data-testid="stSidebar"] button { background-color: rgba(255,255,255,0.1) !important; border: 1px solid rgba(255,255,255,0.3) !important; }
[data-testid="stSidebar"] button p { color: #ffffff !important; font-weight: bold !important; }
[data-testid="stSidebar"] button:hover { background-color: rgba(231, 76, 60, 0.8) !important; }

/* =========================================
   PANEL CENTRAL (TEXTOS OSCUROS LEGIBLES)
   ========================================= */
/* El gran contenedor blanco central */
.block-container { 
    background-color: rgba(244, 247, 249, 0.95) !important; 
    padding: 2rem !important; 
    border-radius: 12px; 
    margin-top: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

/* OBLIGAMOS a que TODO el texto dentro del panel blanco sea oscuro y sin sombra */
.block-container h1, .block-container h2, .block-container h3, .block-container h4, 
.block-container h5, .block-container p, .block-container span, .block-container label, 
.block-container div {
    color: #2c3e50 !important; 
    text-shadow: none !important;
}

/* TARJETAS KPI (Producción, Consumo, etc.) */
div.solarman-card { 
    background: #ffffff !important; border-radius: 8px !important; padding: 20px !important; 
    box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important; text-align: center !important; border: 1px solid #eaeaea !important; 
}
div.solarman-card div.solarman-val { font-size: 26px !important; font-weight: bold !important; margin-bottom: 5px !important; }
div.solarman-card div.solarman-lbl { font-size: 13px !important; text-transform: uppercase !important; color: #7f8c8d !important; }
div.solarman-card span.solarman-lbl-sm { color: #7f8c8d !important; font-size: 10px !important; text-transform: uppercase !important;}

/* LISTA DE PLANTAS EN PANORAMA */
.tarjeta-dash-pro { background-color: #ffffff !important; padding: 15px !important; border-radius: 8px !important; margin-bottom: 10px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important; display: flex !important; align-items: center !important; justify-content: space-between !important; border: 1px solid #eaeaea !important;}
.tarjeta-label-pro { font-size: 11px !important; color: #7f8c8d !important; text-transform: uppercase !important; margin-bottom: 2px !important; white-space: nowrap !important; }
.tarjeta-dato-pro { font-size: 16px !important; font-weight: bold !important; color: #2c3e50 !important; white-space: nowrap !important; }

/* TABS ESTILO SOLARMAN BUSINESS */
div[data-testid="stTabs"] > div[data-baseweb="tab-list"] { border-bottom: 1px solid #e0e0e0 !important; gap: 15px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"] p, div[data-testid="stTabs"] button[data-baseweb="tab"] span { color: #7f8c8d !important; font-weight: 600 !important; font-size: 16px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"] { background-color: transparent !important; border: none !important; border-bottom: 3px solid transparent !important; border-radius: 0 !important; box-shadow: none !important; padding-bottom: 10px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #e74c3c !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p, div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] span { color: #2c3e50 !important; }

/* BOTONES INFERIORES AZULES */
div[data-testid="stButton"] button[kind="primary"] { background-color: #2d8cf0 !important; border-color: #2d8cf0 !important; border-radius: 4px !important; }
div[data-testid="stButton"] button[kind="primary"] p { color: white !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { background-color: #57a3f3 !important; }
div[data-testid="stButton"] button[kind="secondary"] { border-color: #2d8cf0 !important; border-radius: 4px !important; background-color: white !important; }
div[data-testid="stButton"] button[kind="secondary"] p { color: #2d8cf0 !important; }

/* LOGIN ESTILO CRISTAL */
[data-testid="stForm"] { background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(10px) !important; border-radius: 12px !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important; }
[data-testid="stForm"] p { color: white !important; text-shadow: 1px 1px 3px black !important; }
[data-testid="stExpanderDetails"] { background: rgba(255, 255, 255, 0.95) !important; }
[data-testid="stExpanderDetails"] p { color: #2c3e50 !important; text-shadow: none !important; }
</style>
"""
st.markdown(css_global, unsafe_allow_html=True)

# ==========================================
# 2. BLINDAJE DE VARIABLES DE SESIÓN
# ==========================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "usuario" not in st.session_state: st.session_state["usuario"] = None
if "rol" not in st.session_state: st.session_state["rol"] = None
if "editando_planta" not in st.session_state: st.session_state["editando_planta"] = None
if "mostrar_crear" not in st.session_state: st.session_state["mostrar_crear"] = False
if "red_desbloqueada" not in st.session_state: st.session_state["red_desbloqueada"] = False

if st.session_state["autenticado"] and st.session_state["usuario"] is None:
    st.session_state["autenticado"] = False

# ==========================================
# 3. BASE DE DATOS Y LÓGICA DE USUARIOS
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'
ARCHIVO_USUARIOS = 'usuarios.json'
ARCHIVO_MANTENIMIENTOS = 'mantenimientos.json'

def cargar_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'w') as f: json.dump({"admin": {"pwd": "solar123", "status": "active", "role": "admin"}}, f)
    with open(ARCHIVO_USUARIOS, 'r') as f: db = json.load(f)
    if "admin" in db and isinstance(db["admin"], dict):
        db["admin"]["role"] = "admin"
        db["admin"]["status"] = "active"
        with open(ARCHIVO_USUARIOS, 'w') as f: json.dump(db, f)
    return db

def solicitar_usuario(usuario, contrasena):
    usuarios = cargar_usuarios()
    if usuario in usuarios: return False, "⚠️ Este usuario ya existe o tiene una solicitud pendiente."
    usuarios[usuario] = {"pwd": contrasena, "status": "pending", "role": "viewer"}
    with open(ARCHIVO_USUARIOS, 'w') as f: json.dump(usuarios, f)
    return True, "✅ Solicitud enviada. Espere a que el Administrador apruebe su cuenta."

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [{"nombre": "cancha las malvinas off grid", "ubicacion": "Barranquilla", "capacidad": "30 kWp", "inversores": "Deye", "datalogger": "2412120039"}]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(inicial, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

def guardar_planta(nueva):
    plantas = cargar_plantas()
    plantas.append(nueva)
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

# --- MANEJO DE ACCIONES POR QUERY PARAMS (LÁPIZ/PAPELERA) ---
if "delete" in st.query_params:
    try:
        idx = int(st.query_params["delete"])
        pl = cargar_plantas()
        if 0 <= idx < len(pl):
            pl.pop(idx)
            with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(pl, f)
        st.query_params.clear()
    except: pass

if "edit" in st.query_params:
    try:
        idx = int(st.query_params["edit"])
        st.session_state["editando_planta"] = idx
        st.query_params.clear()
    except: pass

# ==========================================
# 4. LOGIN (PERFECTAMENTE VISIBLE)
# ==========================================
if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #f1c40f !important;'>☀️ MOMISOLAR APP</h1>", unsafe_allow_html=True)
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
                if u in db and db[u]["pwd"] == p:
                    if db[u].get("status") == "pending": st.warning("⚠️ Cuenta pendiente de aprobación.")
                    else:
                        st.session_state.update({"autenticado": True, "usuario": u, "rol": db[u]["role"]})
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
# 5. NAVEGACIÓN Y DATOS
# ==========================================
plantas = cargar_plantas()
st.sidebar.markdown("<h2 style='text-align: center; color: #f1c40f !important; text-shadow: none !important;'>☀️ MOMISOLAR APP</h2>", unsafe_allow_html=True)
st.sidebar.write(f"👤 **{st.session_state.get('usuario', '')}** | Rol: {'Instalador/Admin' if st.session_state.get('rol') == 'admin' else 'Cliente'}")
menu = st.sidebar.radio("Ir a:", ["🌐 Panorama General", "📊 Panel de Planta", "🚨 Centro de Alertas"])
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.update({"autenticado": False, "usuario": None, "rol": None, "red_desbloqueada": False})
    st.rerun()

# --- FUNCIONES DE SIMULACIÓN ---
def get_data(pl):
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(pl.get("capacidad", "5")))[0]) * 1000 if re.findall(r"[-+]?\d*\.\d+|\d+", str(pl.get("capacidad", "5"))) else 5000
    p_sol = int(cap * random.uniform(0.1, 0.8))
    e_dia = round((p_sol * random.uniform(3.5, 5.0)) / 1000, 1)
    soc = random.randint(15, 99) 
    return {"solar": p_sol, "casa": 1750 + random.randint(-40, 40), "soc": soc, "hoy": e_dia, "alertas": []}

def simular_historico_24h(planta):
    cap_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(planta.get("capacidad", "5")))[0]) if re.findall(r"[-+]?\d*\.\d+|\d+", str(planta.get("capacidad", "5"))) else 5.0
    inicio_dia = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    datos = []
    for m in range(0, 24 * 60, 15):
        t = inicio_dia + timedelta(minutes=m)
        h = t.hour
        gen = max(0, (cap_val * 0.9) * math.sin((h - 6) / 12 * math.pi) * random.uniform(0.95, 1.05)) if 6 <= h <= 18 else 0
        con = max(cap_val * 0.1, cap_val * 0.2 + (cap_val * 0.3 * math.sin((h-7)/2 * math.pi) if 7<=h<=9 else (cap_val * 0.4 * math.sin((h-18)/3 * math.pi) if 18<=h<=21 else 0)))
        datos.append({"timestamp": t, "Generación FV": round(gen, 2), "Consumo Carga": round(con, 2)})
    return pd.DataFrame(datos)

# ==========================================
# 6. VISTA: PANORAMA GENERAL
# ==========================================
if menu == "🌐 Panorama General":
    st.title("🌐 PANORAMA GENERAL")
    
    if st.session_state["editando_planta"] is not None:
        idx = st.session_state["editando_planta"]
        p_edit = plantas[idx]
        st.markdown(f"<h3>✏️ Editar Parámetros: {p_edit['nombre']}</h3>", unsafe_allow_html=True)
        with st.form("edit"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nombre", p_edit['nombre'])
            u = c2.text_input("Ubicación", p_edit['ubicacion'])
            c = c1.text_input("Capacidad", p_edit.get('capacidad', ''))
            sn = c2.text_input("SN Datalogger", p_edit.get('datalogger', ''))
            if st.form_submit_button("💾 Guardar Cambios"):
                plantas[idx].update({"nombre": n, "ubicacion": u, "capacidad": c, "datalogger": sn})
                with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)
                st.session_state["editando_planta"] = None
                st.rerun()

    if st.session_state.get("mostrar_crear") and st.session_state['rol'] == 'admin':
        st.markdown("<h3>➕ Crear Nueva Planta</h3>", unsafe_allow_html=True)
        with st.form("crear_planta_form"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nombre de la Planta")
            n_ubi = c2.text_input("Ubicación")
            n_cap = c1.text_input("Capacidad (Ej: 30 kWp)")
            
            # ---> AQUÍ ESTÁ EL CAMBIO: Lista actualizada con Fronius <---
            n_inv = c2.selectbox("Marca de Inversor", ["Deye", "Fronius", "GoodWe", "Huawei", "Sylvania"])
            
            n_sn = st.text_input("SN del Datalogger")
            s1, s2 = st.columns(2)
            if s1.form_submit_button("💾 Guardar Nueva Planta"):
                if n_nom:
                    guardar_planta({"nombre": n_nom, "ubicacion": n_ubi, "capacidad": n_cap, "inversores": n_inv, "datalogger": n_sn})
                    st.session_state["mostrar_crear"] = False
                    st.rerun()
            if s2.form_submit_button("❌ Cancelar"):
                st.session_state["mostrar_crear"] = False
                st.rerun()

    col_bus, col_btn = st.columns([8, 2])
    with col_bus: c_bus = st.text_input("🔍 Buscar planta", placeholder="Buscar por nombre o ciudad", label_visibility="collapsed")
    with col_btn:
        if st.session_state['rol'] == 'admin':
            if st.button("Crear una planta", type="primary", use_container_width=True):
                st.session_state["mostrar_crear"] = not st.session_state.get("mostrar_crear", False)
                st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

    if not plantas: st.warning("No hay plantas registradas.")
    else:
        filtradas = [pl for pl in plantas if c_bus.lower() in pl['nombre'].lower() or c_bus.lower() in pl['ubicacion'].lower()]
        st.markdown('<div style="overflow-x: auto;"><div style="min-width: 1050px;">', unsafe_allow_html=True)
        for i, pl in enumerate(filtradas):
            dat = get_data(pl)
            col_card, col_btns = st.columns([11, 1])
            with col_card:
                st.markdown(f"""
                <div class="tarjeta-dash-pro" style="margin-bottom:0px;">
                <div style="display:flex; align-items:center; width: 320px; flex-shrink: 0;"><img src="https://img.icons8.com/color/48/solar-panel.png" style="width: 32px; margin-right:15px;"/><div style="font-size: 15px; font-weight: bold;">{pl['nombre']}</div></div>
                <div class="tarjeta-dash-item"><div class="tarjeta-label-pro">Potencia Solar</div><div class="tarjeta-dato-pro">{dat['solar']} W</div></div>
                <div class="tarjeta-dash-item"><div class="tarjeta-label-pro">Energía Hoy</div><div class="tarjeta-dato-pro" style="color:#27ae60 !important;">{dat['hoy']} kWh</div></div>
                </div>""", unsafe_allow_html=True)
            with col_btns:
                if st.session_state['rol'] == 'admin':
                    st.markdown("<div style='height:15px;'></div><div style='display:flex; gap:10px;'>", unsafe_allow_html=True)
                    st.markdown(f'<a href="?edit={i}" title="Editar"><img src="https://img.icons8.com/material-rounded/24/7f8c8d/edit.png" width="24"/></a> <a href="?delete={i}" title="Eliminar"><img src="https://img.icons8.com/material-rounded/24/7f8c8d/filled-trash.png" width="24"/></a>', unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

# ==========================================
# 7. VISTA: PANEL DE PLANTA Y CONTROL REMOTO
# ==========================================
elif menu == "📊 Panel de Planta":
    if not plantas:
        st.warning("No hay plantas registradas.")
        st.stop()
        
    pl_sel = st.selectbox("Seleccionar Planta:", [p["nombre"] for p in plantas], label_visibility="collapsed")
    p = next(x for x in plantas if x["nombre"] == pl_sel)
    d = get_data(p)
    
    st.markdown(f"<h2>{p['nombre']} <span style='font-size:14px; color:#7f8c8d; font-weight:normal;'>| 🟢 En línea | SN: {p.get('datalogger', '2412120039')}</span></h2><hr style='margin-top:0px; margin-bottom:20px; border-color:#e0e0e0;'>", unsafe_allow_html=True)
    
    # KPIs DE BATERÍA PERFECTOS
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#3498db !important;'>{d['hoy']} kWh</div><div class='solarman-lbl'>Producción Solar</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#e67e22 !important;'>{round(d['hoy']*0.45,1)} kWh</div><div class='solarman-lbl'>Consumo</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='solarman-card'><div style='font-size:16px; font-weight:bold; color:#2c3e50;'>🔋 {round(d['hoy']*0.2,1)} kWh <span class='solarman-lbl-sm'>Cargar</span></div><div style='font-size:16px; font-weight:bold; margin-top:5px; color:#2c3e50;'>🔋 {round(d['hoy']*0.1,1)} kWh <span class='solarman-lbl-sm'>Descargar</span></div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='solarman-card'><div style='font-size:16px; font-weight:bold; color:#2c3e50;'>⚡ 0 kWh <span class='solarman-lbl-sm'>A Red</span></div><div style='font-size:16px; font-weight:bold; margin-top:5px; color:#2c3e50;'>⚡ 0 kWh <span class='solarman-lbl-sm'>De Red</span></div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # TABS PRINCIPALES
    if st.session_state['rol'] == 'admin':
        t_graf, t_ctrl, t_rep, t_om = st.tabs(["📈 Panel Gráfico", "⚙️ Control Remoto del Inversor", "📄 Reportes", "🛠️ O&M"])
    else:
        t_graf, t_rep = st.tabs(["📈 Panel Gráfico", "📄 Reportes"])
        t_ctrl, t_om = None, None
    
    # --- GRÁFICA Y FLUJO ---
    with t_graf:
        col_grafica, col_flujo = st.columns([7, 3])
        with col_grafica:
            st.markdown("<div style='background:white; border-radius:8px; padding:15px; border:1px solid #eaeaea;'>", unsafe_allow_html=True)
            df_historico = simular_historico_24h(p)
            fig2 = px.area(df_historico, x="timestamp", y=["Generación FV", "Consumo Carga"], color_discrete_map={"Generación FV": "#3498db", "Consumo Carga": "#e74c3c"})
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text=None, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis=dict(tickformat="%H:%M", dtick=2 * 3600000, gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0"), yaxis_title="kW", margin=dict(l=10, r=10, t=10, b=10), height=380)
            fig2.update_traces(fill='tozeroy', mode='lines', line=dict(width=2))
            fig2.update_traces(selector=dict(name="Consumo Carga"), fill='none')
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_flujo:
            pot_bat = d["solar"] - d["casa"]
            color_bat = "#2ecc71" if d["soc"] > 20 else "#e74c3c"
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
                    <g transform="translate(60,30)"><image href="https://img.icons8.com/color/48/solar-panel.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#3498db" text-anchor="middle">{d['solar']} W</text></g>
                    <g transform="translate(260,30)"><image href="https://img.icons8.com/fluency/48/electrical.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#7f8c8d" text-anchor="middle">0 W</text></g>
                    <g transform="translate(60,260)"><image href="https://img.icons8.com/color/48/car-battery.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#27ae60" text-anchor="middle">{pot_bat} W</text><text x="5" y="55" font-size="11" font-weight="bold" fill="{color_bat}" text-anchor="middle">SOC: {d['soc']}%</text></g>
                    <g transform="translate(260,260)"><image href="https://img.icons8.com/color/48/home.png" width="40" height="40" x="-15" y="-15"/><text x="5" y="40" font-size="16" font-weight="bold" fill="#e74c3c" text-anchor="middle">{d['casa']} W</text></g>
                </svg>
            </div>
            """
            components.html(diagrama_svg, height=415)
            
    # --- CONTROL REMOTO ---
    if t_ctrl:
        with t_ctrl:
            st.info(f"⚙️ Configurando el inversor **{p.get('inversores', 'Deye')}** de la planta '{p['nombre']}'. Proceda con precaución.")
            st_bat, st_mo1, st_mo2, st_red, st_smart, st_bas, st_av1, st_av2 = st.tabs([
                "🔋 Baterías", "🔄 Modos-1", "🔄 Modos-2", "⚡ Red", "🧠 SmartLoad", "⚙️ Básica", "🛠️ Avanzadas-1", "🛠️ Avanzadas-2"
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

            # --- RED: CON LÍMITE DE INYECCIÓN Y TIEMPOS DE DESPEJE ---
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
        
            st.markdown("<br><hr style='margin:10px 0;'>", unsafe_allow_html=True)
            b_col1, b_col2, b_col3 = st.columns([6, 2, 2])
            with b_col2: st.button("Mirada lasciva", use_container_width=True, type="secondary")
            with b_col3:
                if st.button("Configurar", type="primary", use_container_width=True):
                    with st.spinner("Enviando..."): time.sleep(1.5)
                    st.success("¡Configuración aplicada!")

    # --- REPORTES Y DESCARGA CSV ---
    with t_rep:
        st.markdown("### 📄 Descarga de Datos Históricos")
        st.write("Exporte las métricas del día actual a Excel.")
        df_informe = pd.DataFrame({"Fecha Consulta": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")], "Planta": [p['nombre']], "Producción Diaria (kWh)": [d['hoy']]})
        csv_data = df_informe.to_csv(index=False).encode('utf-8-sig') 
        st.download_button(label="📥 Descargar Informe CSV", data=csv_data, file_name=f"Reporte_{p['nombre']}.csv", mime="text/csv")

    # --- O&M (AGENDA DE MANTENIMIENTO) ---
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
    st.title("🚨 ALERTAS")
    st.success("✅ Todo funciona correctamente.")
