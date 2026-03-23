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
/* FONDO DE LA APLICACIÓN */
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=1920");
    background-size: cover; background-position: center; background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }

/* CONTENEDOR CENTRAL TRANSPARENTE */
.block-container { background-color: transparent !important; }

/* TEXTOS Y LABELS */
h1, h2, h3, h4, h5, p, span, label { color: #ffffff !important; text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important; }

/* SIDEBAR OSCURO */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #112027 0%, #1a323c 50%, #162a33 100%) !important;
    border-right: 1px solid #2c5364 !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; text-shadow: none !important; }

/* ESTILO PANELES BLANCOS (VISTA PLANTA) */
.white-panel {
    background-color: #f4f7f9 !important; padding: 20px; border-radius: 0px;
}
.white-panel h2, .white-panel h3, .white-panel p, .white-panel span, .white-panel label, .white-panel div {
    color: #2c3e50 !important; text-shadow: none !important;
}

/* TABS ESTILO SOLARMAN BUSINESS */
div[data-testid="stTabs"] > div[data-baseweb="tab-list"] { background-color: transparent !important; border-bottom: 1px solid #e0e0e0 !important; gap: 15px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"] p, div[data-testid="stTabs"] button[data-baseweb="tab"] span { color: #7f8c8d !important; text-shadow: none !important; font-weight: 600 !important; font-size: 16px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"] { background-color: transparent !important; border: none !important; border-bottom: 3px solid transparent !important; border-radius: 0 !important; box-shadow: none !important; padding-bottom: 10px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #e74c3c !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p, div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] span { color: #2c3e50 !important; }

/* CORRECCIÓN DEL BOTÓN AZUL Y LOS ICONOS */
div[data-testid="stButton"] button[kind="primary"] {
    background-color: #2d8cf0 !important; border-color: #2d8cf0 !important; color: white !important; border-radius: 4px !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover { background-color: #57a3f3 !important; }
div[data-testid="stButton"] button[kind="secondary"] {
    color: #2d8cf0 !important; border-color: #2d8cf0 !important; border-radius: 4px !important; background-color: white !important;
}
.iconos-accion .stButton button { border: none !important; background: transparent !important; box-shadow: none !important; padding: 0 !important; color: #7f8c8d !important; font-size: 20px !important; }
.iconos-accion .stButton button:hover { color: #2c3e50 !important; transform: scale(1.1) !important; }

.solarman-card { background: #ffffff !important; border-radius: 8px !important; padding: 20px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important; text-align: center !important; border: 1px solid #eaeaea !important; }
.solarman-val { font-size: 26px !important; font-weight: bold !important; margin-bottom: 5px !important; }
.solarman-lbl { font-size: 13px !important; text-transform: uppercase !important; }
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

if st.session_state["autenticado"] and st.session_state["usuario"] is None:
    st.session_state["autenticado"] = False

# ==========================================
# 3. BASE DE DATOS Y LÓGICA DE USUARIOS
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'
ARCHIVO_USUARIOS = 'usuarios.json'

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
    if usuario in usuarios:
        return False, "⚠️ Este usuario ya existe o tiene una solicitud pendiente."
    
    usuarios[usuario] = {"pwd": contrasena, "status": "pending", "role": "viewer"}
    with open(ARCHIVO_USUARIOS, 'w') as f: 
        json.dump(usuarios, f)
    return True, "✅ Solicitud enviada. Espere a que el Administrador apruebe su cuenta."

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [{"nombre": "cancha las malvinas off grid", "ubicacion": "Barranquilla", "capacidad": "30 kWp", "inversores": "Deye", "datalogger": "2412120039"}]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(inicial, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

# --- LOGIN (AHORA CON "CREAR USUARIO" RESTAURADO) ---
if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #f1c40f !important;'>☀️ MOMISOLAR APP</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white !important;'>Plataforma de Gestión - CV INGENIERÍA SAS</h3><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        # Formulario de Inicio de Sesión
        with st.form("login"):
            st.markdown("<div style='color:white; font-weight:bold; font-size:14px; text-shadow: 1px 1px 3px black;'>Usuario</div>", unsafe_allow_html=True)
            u = st.text_input("Usuario", label_visibility="collapsed")
            st.markdown("<div style='color:white; font-weight:bold; font-size:14px; margin-top:10px; text-shadow: 1px 1px 3px black;'>Contraseña</div>", unsafe_allow_html=True)
            p = st.text_input("Contraseña", type="password", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                db = cargar_usuarios()
                if u in db and db[u]["pwd"] == p:
                    if db[u].get("status") == "pending":
                        st.warning("⚠️ Su cuenta aún está pendiente de aprobación por el Administrador.")
                    else:
                        st.session_state.update({"autenticado": True, "usuario": u, "rol": db[u]["role"]})
                        st.rerun()
                else: 
                    st.error("❌ Credenciales incorrectas o usuario no registrado.")
        
        # Formulario de Solicitud (Crear Usuario)
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
                        if success: 
                            st.success(message)
                        else: 
                            st.error(message)
    st.stop()

# ==========================================
# 4. NAVEGACIÓN Y DATOS
# ==========================================
plantas = cargar_plantas()
st.sidebar.markdown("<h2 style='text-align: center; color: #f1c40f !important; text-shadow: none !important;'>☀️ MOMISOLAR APP</h2>", unsafe_allow_html=True)
st.sidebar.write(f"👤 **{st.session_state.get('usuario', '')}** | Rol: {'Instalador/Admin' if st.session_state.get('rol') == 'admin' else 'Cliente'}")
menu = st.sidebar.radio("Ir a:", ["🌐 Panorama General", "📊 Panel de Planta", "🚨 Centro de Alertas"])
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.update({"autenticado": False, "usuario": None, "rol": None})
    st.rerun()

# --- FUNCIONES DE SIMULACIÓN ---
def get_data(pl):
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(pl.get("capacidad", "5")))[0]) * 1000 if re.findall(r"[-+]?\d*\.\d+|\d+", str(pl.get("capacidad", "5"))) else 5000
    p_sol = int(cap * random.uniform(0.1, 0.8))
    e_dia = round((p_sol * random.uniform(3.5, 5.0)) / 1000, 1)
    soc = random.randint(15, 99) 
    return {"solar": p_sol, "casa": 1750 + random.randint(-40, 40), "soc": soc, "hoy": e_dia, "alertas": []}

def sim_graph():
    df = pd.DataFrame({"timestamp": [datetime.now().replace(hour=h, minute=0) for h in range(24)], 
                       "Generación FV": [10 * math.sin(h*math.pi/12) if 6<h<18 else 0 for h in range(24)],
                       "Consumo Carga": [random.randint(2, 5) for _ in range(24)]})
    return df

# ==========================================
# 5. VISTA: PANORAMA GENERAL
# ==========================================
if menu == "🌐 Panorama General":
    st.title("🌐 PANORAMA GENERAL")
    
    if st.session_state["editando_planta"] is not None:
        idx = st.session_state["editando_planta"]
        p_edit = plantas[idx]
        st.markdown("<div style='background:rgba(255,255,255,0.95); padding:20px; border-radius:10px; margin-bottom:20px;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#2c3e50 !important; text-shadow:none !important;'>✏️ Editar Parámetros: {p_edit['nombre']}</h3>", unsafe_allow_html=True)
        with st.form("edit"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Nombre", p_edit['nombre'])
            u = c2.text_input("Ubicación", p_edit['ubicacion'])
            c = c1.text_input("Capacidad", p_edit.get('capacidad', ''))
            sn = c2.text_input("SN Datalogger", p_edit.get('datalogger', ''))
            if st.form_submit_button("💾 Guardar"):
                plantas[idx].update({"nombre": n, "ubicacion": u, "capacidad": c, "datalogger": sn})
                with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)
                st.session_state["editando_planta"] = None
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    for i, pl in enumerate(plantas):
        d = get_data(pl)
        col_t1, col_t2 = st.columns([11, 1])
        with col_t1:
            st.markdown(f"""
            <div style="background:white; padding:15px; border-radius:8px; display:flex; justify-content:space-between; align-items:center; border:1px solid #ddd; margin-bottom:10px;">
                <div style="color:#2c3e50; font-size:16px;"><b>{pl['nombre']}</b><br><small style="color:#7f8c8d;">📍 {pl['ubicacion']} | SN: {pl.get('datalogger', 'N/A')}</small></div>
                <div style="color:#2c3e50">Potencia Solar:<br><b>{d['solar']} W</b></div>
                <div style="color:#27ae60">Energía Hoy:<br><b>{d['hoy']} kWh</b></div>
            </div>
            """, unsafe_allow_html=True)
        with col_t2:
            if st.session_state['rol'] == 'admin':
                st.markdown("<div style='height:15px;'></div><div class='iconos-accion'>", unsafe_allow_html=True)
                if st.button("✎", key=f"ed_{i}"):
                    st.session_state["editando_planta"] = i
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 6. VISTA: PANEL DE PLANTA (CLON SOLARMAN)
# ==========================================
elif menu == "📊 Panel de Planta":
    if not plantas:
        st.warning("No hay plantas registradas.")
        st.stop()
        
    st.markdown('<div class="white-panel">', unsafe_allow_html=True)
    pl_sel = st.selectbox("Seleccionar Planta:", [p["nombre"] for p in plantas], label_visibility="collapsed")
    p = next(x for x in plantas if x["nombre"] == pl_sel)
    d = get_data(p)
    
    st.markdown(f"<h2>{p['nombre']} <span style='font-size:14px; color:gray;'>| 🟢 En línea | SN: {p.get('datalogger', '2412120039')}</span></h2><hr style='margin-top:0px; margin-bottom:20px; border-color:#e0e0e0;'>", unsafe_allow_html=True)
    
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#3498db;'>{d['hoy']} kWh</div><div class='solarman-lbl' style='color:#7f8c8d;'>Producción Solar</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#e67e22;'>{round(d['hoy']*0.45,1)} kWh</div><div class='solarman-lbl' style='color:#7f8c8d;'>Consumo</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='solarman-card'><div style='font-size:14px; font-weight:bold; color:#2c3e50;'>🔋 {round(d['hoy']*0.2,1)} kWh <span style='color:#7f8c8d; font-size:10px;'>Cargar</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>🔋 {round(d['hoy']*0.1,1)} kWh <span style='color:#7f8c8d; font-size:10px;'>Descargar</span></div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='solarman-card'><div style='font-size:14px; font-weight:bold; color:#2c3e50;'>⚡ 0 kWh <span style='color:#7f8c8d; font-size:10px;'>A Red</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>⚡ 0 kWh <span style='color:#7f8c8d; font-size:10px;'>De Red</span></div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # TABS PRINCIPALES
    if st.session_state['rol'] == 'admin':
        t_graf, t_ctrl, t_rep, t_om = st.tabs(["📈 Panel Gráfico", "⚙️ Control Remoto del Inversor", "📄 Reportes", "🛠️ O&M"])
    else:
        t_graf, t_rep = st.tabs(["📈 Panel Gráfico", "📄 Reportes"])
        t_ctrl, t_om = None, None
    
    with t_graf:
        st.info("Gráfica de flujo y energía activa en la versión completa.")
        
    if t_ctrl:
        with t_ctrl:
            st.info(f"⚙️ Configurando el inversor **{p.get('inversores', 'Deye')}** de la planta '{p['nombre']}'. Proceda con precaución.")
            
            # SUB-TABS EXACTOS
            st_bat, st_mo1, st_mo2, st_red, st_smart, st_bas, st_av1, st_av2 = st.tabs([
                "🔋 Baterías", "🔄 Modos-1", "🔄 Modos-2", "⚡ Red", "🧠 SmartLoad", "⚙️ Básica", "🛠️ Avanzadas-1", "🛠️ Avanzadas-2"
            ])
            opts_sel = ["Seleccione", "Habilitado", "Deshabilitado"]
            
            with st_bat:
                st.markdown("<small style='color:#7f8c8d;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</small>", unsafe_allow_html=True)
                cb1, cb2, cb3, cb4, cb5 = st.columns(5)
                cb1.selectbox("* Tipo Batería", ["Modo Litio", "Plomo"])
                cb2.number_input("* Capacidad (Ah)", 100)
                cb3.number_input("* Max Carga (A)", 50)
                cb4.number_input("* Max Descarga (A)", 50)
                cb5.number_input("* Desconexión %", 10)

            with st_mo1:
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.selectbox("* Modo", ["Autoconsumo", "Respaldo"])
                with m2:
                    st.markdown("<p style='color:#2c3e50 !important; font-size:12px; margin-bottom:5px;'>* Configuración</p>", unsafe_allow_html=True)
                    st.checkbox("Lunes", True); st.checkbox("Martes", True)
                m3.number_input("* Max Solar (W)", 5000)
                m4.number_input("* Max Red (W)", 5000)
                m5.selectbox("* Prioridad", ["Carga", "Batería"])

            with st_mo2:
                st.toggle("* FuncionamientoporPeriodos", False)

            with st_red:
                st.markdown("🔒 **Introduzca la contraseña para desbloquear**")
                st.text_input("Password", type="password", label_visibility="collapsed")
                st.button("Desbloquear", type="secondary") 

            with st_smart:
                st.markdown("<small style='color:#7f8c8d;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</small>", unsafe_allow_html=True)
                cs1, cs2, cs3 = st.columns(3)
                cs1.selectbox("* SmartLoad", ["Seleccione", "Habilitado"])
                cs2.selectbox("* Par CA Red", ["Seleccione", "Habilitado"])
                cs3.selectbox("* Par CA Carga", ["Seleccione", "Habilitado"])

            with st_bas:
                st.markdown("<h4>Configuración Básica</h4>", unsafe_allow_html=True)
                st.markdown("<small style='color:#7f8c8d;'>ⓘ Configuración general del dispositivo.</small>", unsafe_allow_html=True)
                st.toggle("Sonido zumbador", True)

            with st_av1:
                st.markdown("<small style='color:#7f8c8d;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</small>", unsafe_allow_html=True)
                a1, a2, a3 = st.columns(3)
                a1.selectbox("* Configuración ARC", opts_sel)
                a2.number_input("* Potencia de reducción de picos (W)", 1000)

            with st_av2:
                st.markdown("<h4>Funciones Avanzadas-2</h4>", unsafe_allow_html=True)
                st.markdown("<small style='color:#7f8c8d;'>ⓘ El grupo de comandos actual debe configurarse como un todo.</small>", unsafe_allow_html=True)
                st.markdown("<div style='color: #2c3e50; font-weight: bold; margin-bottom: 10px; margin-top: 15px;'>Configuración Baterías</div>", unsafe_allow_html=True)
                av_col1, av_col2, av_col3 = st.columns([1.5, 1, 2])
                with av_col1:
                    st.selectbox("* DC 1 para turbina eólica", ["Seleccione", "Habilitado", "Deshabilitado"])
        
            st.markdown("<br><hr style='margin:10px 0;'>", unsafe_allow_html=True)
            b_col1, b_col2, b_col3 = st.columns([6, 2, 2])
            with b_col2:
                st.button("Mirada lasciva", use_container_width=True, type="secondary")
            with b_col3:
                if st.button("Configurar", type="primary", use_container_width=True):
                    with st.spinner("Enviando comandos..."):
                        time.sleep(1.5)
                    st.success("¡Configuración aplicada!")

    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🚨 Centro de Alertas":
    st.title("🚨 ALERTAS")
    st.success("✅ Todo funciona correctamente.")
