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
import hashlib

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y ESTILO (CSS)
# ==========================================
st.set_page_config(page_title="HMI INVERSOR FV - CV INGENIERÍA SAS", page_icon="☀️", layout="wide")

css_global = """
<style>
/* Estilo general y paleta de colores: Azul CV (profundo), Grises (fondo), Blanco */
:root {
    --primary-color: #003366; /* Azul profundo CV */
    --secondary-color: #f0f2f5; /* Gris claro de fondo */
    --text-color: #2c3e50;
    --accent-color: #f39c12; /* Naranja acento CV */
    --border-color: #e0e0e0;
}

[data-testid="stAppViewContainer"] {
    background-color: var(--secondary-color);
}

/* Panel central blanco y nítido */
.block-container { 
    background-color: rgba(255, 255, 255, 0.98) !important; 
    padding: 2rem !important; 
    border-radius: 12px; 
    margin-top: 1rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

/* SIDEBAR OSCURO PROFESIONAL */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #112027 0%, #1a323c 50%, #162a33 100%) !important;
    border-right: 1px solid #2c5364 !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; text-shadow: none !important; }

/* Títulos y textos nítidos en el panel blanco */
.stMarkdown { color: var(--text-color); }
h1, h2, h3, h4, h5 { color: var(--primary-color) !important; }
label { color: var(--text-color) !important; font-weight: 500;}

/* Estilo para las Tarjetas/Paneles (Cards) */
.hmi-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    border: 1px solid var(--border-color);
}

/* Estilo para los KPI Tiles */
.kpi-tile { text-align: center; border-right: 1px solid var(--border-color); }
.kpi-tile:last-child { border-right: none; }
.kpi-label { color: #7f8c8d; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; }
.hmi-metric-large { font-size: 2.2rem; font-weight: 700; color: var(--primary-color); }
.hmi-unit { font-size: 1rem; color: #7f8c8d; vertical-align: baseline; }

/* Estilo para las Tabs (Pestañas) estilo Solarman Business */
div[data-testid="stTabs"] > div[data-baseweb="tab-list"] {
    background-color: transparent; border-bottom: 2px solid var(--border-color); gap: 15px;
}
div[data-testid="stTabs"] button[data-baseweb="tab"] p {
    color: var(--text-color) !important; font-weight: 600 !important; font-size: 16px !important; 
}
div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color: var(--accent-color) !important; border-bottom: 2px solid var(--accent-color) !important; background-color: transparent !important;
}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent-color) !important; border-bottom: 2px solid var(--accent-color) !important; background-color: transparent !important;
}

/* Estilo para los Badges de Estado */
.hmi-status-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}
.status-connected { background-color: #27ae6020; color: #27ae60; border: 1px solid #27ae6050; }
.status-disconnected { background-color: #c0392b20; color: #c0392b; border: 1px solid #c0392b50; }

/* Inputs y Selectbox */
input, select { border-radius: 8px; border: 1px solid var(--border-color); }
</style>
"""
st.markdown(css_global, unsafe_allow_html=True)

# ==========================================
# 2. GESTIÓN DE SESIÓN Y DATOS ( JSON )
# ==========================================
if "autenticado" not in st.session_state: 
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
    st.session_state["rol"] = None
if "registro" not in st.session_state: st.session_state["registro"] = False
if "red_desbloqueada" not in st.session_state: st.session_state["red_desbloqueada"] = False

# --- BASE DE DATOS MOCK (JSON) ---
def cargar_usuarios():
    if not os.path.exists('usuarios.json'): 
        # Usuario admin por defecto para CV Ingeniería SAS
        with open('usuarios.json', 'w') as f: json.dump({"admin@cv.co": {"pwd": hashlib.sha256("solar123".encode()).hexdigest(), "rol": "admin"}}, f)
    with open('usuarios.json', 'r') as f: return json.load(f)

def cargar_plantas():
    if not os.path.exists('plantas.json'): return []
    try:
        with open('plantas.json', 'r') as f: return json.load(f)
    except: return []

# ==========================================
# 3. VISTA: LOGIN
# ==========================================
if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #f1c40f !important; text-shadow: 2px 2px 5px rgba(0,0,0,0.5);'>☀️ CV INGENIERÍA SAS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);'>HMI DE GESTIÓN INVERSORES HÍBRIDOS</h3><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        with st.form("login_form"):
            st.markdown("<h4 style='text-align: center; color: white !important;'>Iniciar Sesión</h4>", unsafe_allow_html=True)
            u_login = st.text_input("Usuario (Correo)")
            p_login = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar", use_container_width=True, type="primary"):
                db = cargar_usuarios()
                if u_login in db and db[u_login]["pwd"] == hashlib.sha256(p_login.encode()).hexdigest():
                    st.session_state.update({"autenticado": True, "usuario": u_login, "rol": db[u_login]["rol"]})
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# ==========================================
# 4. NAVEGACIÓN Y SIDEBAR
# ==========================================
st.sidebar.markdown(f"""
<div style="text-align: center; padding: 10px;">
<h3 style="color: white; margin-top:0;">📋 CV INGENIERÍA</h3>
<p style="color: #cbd5e0; font-size: 11px;">HMI DE GESTIÓN FV</p>
<div style="border-top:1px solid #324a5f; margin:10px 0;"></div>
<p style="color: white; font-weight: 600;">👤 {st.session_state['usuario']}</p>
<p style="color: #cbd5e0; font-size: 12px; text-transform:uppercase;">ROL: {st.session_state['rol']}</p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("IR A:", ["🌐 Panorama General", "📊 Panel de Planta", "🚨 Alarmas"])

# BOTÓN CERRAR SESIÓN ARREGLADO (Sin TypeError)
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
    st.session_state.update({"autenticado": False, "usuario": None, "rol": None, "red_desbloqueada": False})
    st.rerun()

# --- FUNCIONES DE SIMULACIÓN DATOS ---
def get_realtime_data(pl):
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(pl.get("capacidad", "10")))[0]) if re.findall(r"[-+]?\d*\.\d+|\d+", str(pl.get("capacidad", "10"))) else 10.0
    # Jitter dinámico para que se mueva
    base_sol = cap * random.uniform(0.1, 0.85)
    jitter = base_sol * 0.02 * random.uniform(-1, 1) # 2% de variación
    p_sol = max(0, int((base_sol + jitter) * 1000))
    
    e_dia = round((p_sol/1000 * random.uniform(3.5, 5.0)), 1)
    soc = random.randint(30, 99) 
    
    # Lógica de flujo
    p_casa = int(1500 + 200 * random.uniform(-1, 1))
    p_bat = 0; p_red = 0
    
    balance = p_sol - p_casa
    if balance > 0: # Exceso
        p_bat = balance # Cargar batería
        if soc > 95: # Bat llena, exportar
            p_red = -balance
            p_bat = 0
    else: # Déficit
        p_bat = balance # Descargar batería
        if soc < 20: # Bat vacía, importar
            p_red = abs(balance)
            p_bat = 0
            
    return {"solar": p_sol, "casa": p_casa, "bat": p_bat, "red": p_red, "soc": soc, "hoy": e_dia}

def simular_historico_24h(planta):
    cap_val = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(planta.get("capacidad", "10")))[0]) if re.findall(r"[-+]?\d*\.\d+|\d+", str(planta.get("capacidad", "10"))) else 10.0
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
# 5. VISTA: PANORAMA GENERAL
# ==========================================
if menu == "🌐 Panorama General":
    st.title("🌐 PANORAMA GENERAL DE PLANTAS")
    plantas = cargar_plantas()
    if not plantas: st.info("No hay plantas registradas. Use '📊 Panel de Planta' -> 'O&M' para agregar datos simulados."); st.stop()
    
    search_query = st.text_input("🔍 Buscar planta:", placeholder="Nombre de la planta...", label_visibility="collapsed")

    filtered = [p for p in plantas if search_query.lower() in p['nombre'].lower()]

    if not filtered: st.info("No se encontraron plantas.")
    
    for p in filtered:
        metrics = get_realtime_data(p)
        
        st.markdown(f"""
        <div class="hmi-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h3>{p['nombre'].upper()}</h3>
                    <p style="color: #7f8c8d; font-size: 0.9rem; margin:0;">📍 {p.get('ubicacion','N/A')} | SN: {p.get('sn','N/A')}</p>
                </div>
                <span class="hmi-status-badge status-connected">En Línea</span>
            </div>
            <div style="border-top:1px solid #e0e0e0; margin:10px 0;"></div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; text-align:center;">
                <div class="kpi-tile">
                    <p class="kpi-label">Potencia Actual</p>
                    <p><span class="hmi-metric-large">{(metrics['solar']/1000):.2f}</span><span class="hmi-unit"> kW</span></p>
                </div>
                <div class="kpi-tile">
                    <p class="kpi-label">Generación Hoy</p>
                    <p><span class="hmi-metric-large">{metrics['hoy']}</span><span class="hmi-unit"> kWh</span></p>
                </div>
                <div class="kpi-tile">
                    <p class="kpi-label">Batería</p>
                    <p><span class="hmi-metric-large">{metrics['soc']}%</span><span class="hmi-unit"> SOC</span></p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, _ = st.columns([1, 6])
        if c1.button("Ver Detalle", key=f"panel_{p['nombre']}", use_container_width=True): 
            st.session_state["planta_seleccionada"] = p['nombre']
            st.session_state["nav_main"] = "📊 Panel de Planta"
            st.rerun()

# ==========================================
# 6. VISTA: PANEL DE PLANTA (EL PLATO FUERTE)
# ==========================================
elif menu == "📊 Panel de Planta":
    plantas = cargar_plantas()
    if not plantas: st.info("No hay plantas registradas. Agregue una."); st.stop()
    
    col_sel, _ = st.columns([1.5, 2])
    planta_sel = col_sel.selectbox("📋 Seleccionar planta activa:", [p['nombre'] for p in plantas], index=0, label_visibility="collapsed")
    p = next(pl for pl in plantas if pl['nombre'] == planta_sel)
    
    # Obtener datos "reales" dinámicos
    d = get_realtime_data(p)
    
    st.markdown(f"## {p['nombre'].upper()} <span style='font-size:14px; color:#7f8c8d; font-weight:normal;'>| SN: {p.get('sn','N/A')} | Inversor: {p.get('inversor','Híbrido')} | ÚLTIMA ACTUALIZACIÓN: {datetime.now().strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)
    
    # KPIs SUPERIORES TIPO SOLARMAN BUSINESS
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#3498db;'>{round(d['solar']/1000, 2)} kW</div><div class='solarman-lbl'>Producción Solar Acutal</div></div>", unsafe_allow_html=True)
    kpi2.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#e67e22;'>{round(d['casa']/1000, 2)} kW</div><div class='solarman-lbl'>Consumo Casa Actual</div></div>", unsafe_allow_html=True)
    
    soc_color = "#27ae60" if d['soc'] > 20 else "#e74c3c"
    kpi3.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:{soc_color};'>🔋 {d['soc']}%</div><div class='solarman-lbl'>Estado de Batería (SOC)</div></div>", unsafe_allow_html=True)
    
    red_txt = f"{round(abs(d['red'])/1000, 2)} kW"
    if d['red'] < 0: red_lbl = "Exportando a Red ⚡"; red_color = "#3498db"
    elif d['red'] > 0: red_lbl = "Importando de Red 🛑"; red_color = "#e74c3c"
    else: red_lbl = "Red Estable"; red_color = "#7f8c8d"
    kpi4.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:{red_color};'>{red_txt}</div><div class='solarman-lbl'>{red_lbl}</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # TABS PRINCIPALES
    if st.session_state['rol'] == 'admin':
        t_graf, t_ctrl, t_red, t_om = st.tabs(["📈 Panel Gráfico", "⚙️ Control Remoto", "⚡ Control de Red", "🛠️ O&M"])
    else:
        t_graf, t_om = st.tabs(["📈 Panel Gráfico", "🛠️ O&M"])
        t_ctrl, t_red = None, None
    
    with t_graf:
        # ------------------------------------------------------------------------------------------------
        # EL DIAGRAMA DE FLUJO "BONITO Y QUE SE MUEVE" (SVG HD ANIMADO)
        # ------------------------------------------------------------------------------------------------
        st.markdown("<h4 style='text-align:center;'>Esquema de Flujo de Energía en Tiempo Real</h4>", unsafe_allow_html=True)
        
        # Lógica de dirección de flujos (puntos animados)
        bat_inverter = "descargando" if d['bat'] < 0 else "cargando" if d['bat'] > 0 else "idle"
        inverter_red = "exportando" if d['red'] < 0 else "importando" if d['red'] > 0 else "idle"
        
        # Velocidades fijas
        v_solar = 1.5; v_casa = 1.5; v_bat = 1.5; v_red = 1.5
        
        diagrama_hd_svg = f"""
        <div style="background: white; border-radius: 12px; padding: 25px; border: 1px solid #eaeaea; max-width: 900px; margin: auto;">
            <svg viewBox="0 0 450 350" width="100%">
                <defs>
                    <linearGradient id="grad_inverter" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#f8f9fa;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#dfe6e9;stop-opacity:1" />
                    </linearGradient>
                    <filter id="shadow" x("-10%", "-10%", "120%", "120%")>
                        <feDropShadow dx="1" dy="2" stdDeviation="2" flood-color="rgba(0,0,0,0.1)"/>
                    </filter>
                </defs>
            
                <path d="M 80 85 V 160 H 190" fill="none" stroke="#dfe6e9" stroke-width="6" stroke-linecap="round"/>
                <path d="M 260 160 H 370 V 230" fill="none" stroke="#dfe6e9" stroke-width="6" stroke-linecap="round"/>
                <path d="M 210 195 V 260 H 120 V 230" fill="none" stroke="#dfe6e9" stroke-width="6" stroke-linecap="round"/>
                <path d="M 240 160 H 370 V 85" fill="none" stroke="#dfe6e9" stroke-width="6" stroke-linecap="round"/>
                
                <circle r="6" fill="#3498db" filter="url(#shadow)">
                    <animateMotion dur="{v_solar}s" repeatCount="indefinite" path="M 80 85 V 160 H 190" keyTimes="0;1" keySplines="0.4 0 0.2 1" calcMode="spline" />
                </circle>
                
                {f'<circle r="6" fill="#2ecc71" filter="url(#shadow)"><animateMotion dur="{v_bat}s" repeatCount="indefinite" path="M 210 195 V 260 H 120 V 230" /></circle>' if bat_inverter == "cargando" else ''}
                {f'<circle r="6" fill="#2ecc71" filter="url(#shadow)"><animateMotion dur="{v_bat}s" repeatCount="indefinite" path="M 120 230 V 260 H 210 V 195" /></circle>' if bat_inverter == "descargando" else ''}

                <circle r="6" fill="#e74c3c" filter="url(#shadow)">
                    <animateMotion dur="{v_casa}s" repeatCount="indefinite" path="M 260 160 H 370 V 230" />
                </circle>
                
                {f'<circle r="6" fill="#3498db" filter="url(#shadow)"><animateMotion dur="{v_red}s" repeatCount="indefinite" path="M 240 160 H 370 V 85" /></circle>' if inverter_red == "exportando" else ''}
                {f'<circle r="6" fill="#7f8c8d" filter="url(#shadow)"><animateMotion dur="{v_red}s" repeatCount="indefinite" path="M 370 85 V 160 H 240" /></circle>' if inverter_red == "importando" else ''}
                
                <rect x="185" y="125" width="80" height="80" rx="15" fill="url(#grad_inverter)" stroke="#3498db" stroke-width="4" filter="url(#shadow)"/>
                <rect x="195" y="135" width="60" height="30" rx="5" fill="#2c3e50"/> 
                <text x="225" y="155" text-anchor="middle" font-family="Arial" font-size="10" fill="#55efc4" font-weight="bold">CV-ENG</text>
                <text x="225" y="192" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="#3498db">Híbrido</text>
                
                <g transform="translate(60,30)" filter="url(#shadow)">
                    <image href="https://img.icons8.com/color/48/solar-panel.png" width="45" height="45" x="-20" y="-20"/>
                    <text x="25" y="45" font-family="Arial" font-size="18" font-weight="bold" fill="#3498db" text-anchor="middle">{d['solar']} W</text>
                </g>
                
                <g transform="translate(370,30)" filter="url(#shadow)">
                    <image href="https://img.icons8.com/fluency/48/electrical.png" width="45" height="45" x="-20" y="-20"/>
                    <text x="25" y="45" font-family="Arial" font-size="18" font-weight="bold" fill="#7f8c8d" text-anchor="middle">{abs(d['red'])} W</text>
                </g>
                
                <g transform="translate(60,260)" filter="url(#shadow)">
                    <image href="https://img.icons8.com/color/48/car-battery.png" width="45" height="45" x="-20" y="-20"/>
                    <text x="25" y="45" font-family="Arial" font-size="18" font-weight="bold" fill="#27ae60" text-anchor="middle">{abs(d['bat'])} W</text>
                    <text x="25" y="60" font-family="Arial" font-size="12" font-weight="bold" fill="{soc_color}" text-anchor="middle">SOC: {d['soc']}%</text>
                </g>
                
                <g transform="translate(370,260)" filter="url(#shadow)">
                    <image href="https://img.icons8.com/color/48/home.png" width="45" height="45" x="-20" y="-20"/>
                    <text x="25" y="45" font-family="Arial" font-size="18" font-weight="bold" fill="#e74c3c" text-anchor="middle">{d['casa']} W</text>
                </g>
            </svg>
        </div>
        """
        components.html(diagrama_hd_svg, height=450)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_grafica_hist, _ = st.columns([7, 3])
        with col_grafica_hist:
            st.markdown("<div style='background:white; border-radius:12px; padding:15px; border:1px solid #eaeaea; box-shadow: 0 2px 6px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
            df_historico = simular_historico_24h(p)
            fig2 = px.area(df_historico, x="timestamp", y=["Generación FV", "Consumo Carga"], color_discrete_map={"Generación FV": "#3498db", "Consumo Carga": "#e74c3c"})
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text=None, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis=dict(tickformat="%H:%M", dtick=2 * 3600000, gridcolor="#f0f0f0"), yaxis=dict(gridcolor="#f0f0f0"), yaxis_title="kW", margin=dict(l=10, r=10, t=10, b=10), height=380)
            fig2.update_traces(fill='tozeroy', mode='lines', line=dict(width=2))
            fig2.update_traces(selector=dict(name="Consumo Carga"), fill='none')
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            
    # --- CONTROL REMOTO (INTACTO) ---
    if t_ctrl:
        with t_ctrl:
            st.info(f"⚙️ Configurando el inversor **{p.get('inversores', 'Deye')}** de la planta '{p['nombre']}'. Proceda con precaución.")
            st_bat, st_mo1, st_mo2, st_smart, st_bas, st_av1, st_av2 = st.tabs([
                "🔋 Baterías", "🔄 Modos-1", "🔄 Modos-2", "🧠 SmartLoad", "⚙️ Básica", "🛠️ Avanzadas-1", "🛠️ Avanzadas-2"
            ])
            opts_sel = ["Seleccione", "Habilitado", "Deshabilitado"]
            
            with st_bat:
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

            with st_smart:
                cs1, cs2, cs3 = st.columns(3)
                cs1.selectbox("* SmartLoad", ["Seleccione", "Habilitado"])
                cs2.selectbox("* Par CA Red", opts_sel)
                cs3.selectbox("* Par CA Carga", opts_sel)

            with st_bas:
                st.toggle("Sonido zumbador", value=True)

            with st_av1:
                a1, a2, a3, a4, a5 = st.columns(5)
                a1.selectbox("* Configuración ARC", options=opts_sel)
                a2.selectbox("* Gen Peak-afeitado", options=opts_sel)
                a3.number_input("* Potencia reducción pico red (W)", value=1000)
                a4.selectbox("* DRM", options=opts_sel)
                a5.selectbox("* Modo Isla de Señal", options=opts_sel)

            with st_av2:
                av_col1, av_col2 = st.columns(2)
                av_col1.number_input("* relación CT", value=1000)
                av_col2.empty()
        
            st.markdown("<br><hr style='margin:10px 0;'>", unsafe_allow_html=True)
            b_col1, b_col2, b_col3 = st.columns([6, 2, 2])
            with b_col2: st.button("Mirada lasciva", use_container_width=True, type="secondary")
            with b_col3:
                if st.button("Configurar", type="primary", use_container_width=True):
                    with st.spinner("Enviando..."): time.sleep(1.5)
                    st.success("¡Configuración aplicada!")

    # --- CONTROL DE RED (PRESERVADO INTACTO CON LÍMITE DE INYECCIÓN) ---
    if t_red:
        with t_red:
            st.markdown("<h4>Configuración de Límite de Red y Parámetros de Tensión/Frecuencia</h4>", unsafe_allow_html=True)
            if not st.session_state["red_desbloqueada"]:
                st.markdown("<div style='color:#f39c12; font-weight:bold; margin-bottom:10px;'>🔒 Introduzca la contraseña 'admin123' para desbloquear</div>", unsafe_allow_html=True)
                c_pw1, c_pw2 = st.columns([2, 3])
                pwd = c_pw1.text_input("Contraseña Red", type="password", label_visibility="collapsed")
                if c_pw1.button("Desbloquear Red", type="secondary"):
                    if pwd == "admin123":
                        st.session_state["red_desbloqueada"] = True
                        st.rerun()
                    else: st.error("❌ Contraseña incorrecta.")
            else:
                st.success("🔓 Panel de Red Desbloqueado")
                
                r_c1, r_c2 = st.columns(2)
                r_c1.selectbox("* Normativa Aplicada", ["Seleccione", "Colombia (RETIE / NTC 2050)", "IEEE 1547", "IEC 61727"])
                
                # INYECCIÓN A RED (%) PRESERVADO INTACTO
                r_c2.number_input("* Límite de Inyección a red (%)", min_value=0, max_value=100, value=100)
                
                st.markdown("<div style='margin-top: 10px; font-weight: bold; color: #2c3e50;'>Protecciones de Tensión AC (V) y Tiempos de Despeje (s)</div>", unsafe_allow_html=True)
                cv1, ct1, cv2, ct2 = st.columns([2, 1, 2, 1])
                cv1.number_input("* Sobre Tensión Máx (V)", value=253.0)
                ct1.number_input("* Tiempo s", value=0.1, key="t_ov", label_visibility="collapsed")
                cv2.number_input("* Sub Tensión Mín (V)", value=198.0)
                ct2.number_input("* Tiempo s", value=0.2, key="t_uv", label_visibility="collapsed")
                
                cv3, ct3, cv4, ct4 = st.columns([2, 1, 2, 1])
                cv3.number_input("* Tensión Máxima de Inyección (V)", value=242.0)
                ct3.empty()
                cv4.number_input("* Tensión Mínima de Inyección (V)", value=210.0)
                ct4.empty()

                st.markdown("<div style='margin-top: 15px; font-weight: bold; color: #2c3e50;'>Protecciones de Frecuencia (Hz) y Tiempos de Despeje (s)</div>", unsafe_allow_html=True)
                cf1, cft1, cf2, cft2 = st.columns([2, 1, 2, 1])
                cf1.number_input("* Sobre Frecuencia Máx (Hz)", value=60.5)
                cft1.number_input("* Tiempo s", value=0.2, key="t_of", label_visibility="collapsed")
                cf2.number_input("* Sub Frecuencia Mín (Hz)", value=59.5)
                cft2.number_input("* Tiempo s", value=0.2, key="t_uf", label_visibility="collapsed")
                
                st.markdown("<div style='margin-top: 15px; font-weight: bold; color: #2c3e50;'>Reconexión</div>", unsafe_allow_html=True)
                cr1, cr2 = st.columns(2)
                cr1.number_input("* Tiempo de reconexión a la red (s)", value=60)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔒 Bloquear Red"):
                    st.session_state["red_desbloqueada"] = False
                    st.rerun()
                if st.button("💾 Guardar Configuración de Red", type="primary"):
                    st.success("Guardado (Mock)")

    # --- O&M (INTACTO) ---
    if t_om:
        with t_om:
            st.markdown("### 📅 Agenda de Mantenimiento / Reportes")
            df_informe = pd.DataFrame({"Fecha Consulta": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")], "Planta": [p['nombre']], "Producción Diaria (kWh)": [d['hoy']]})
            csv_data = df_informe.to_csv(index=False).encode('utf-8-sig') 
            st.download_button(label="📥 Descargar Reporte Diario (Excel/CSV)", data=csv_data, file_name=f"Reporte_{p['nombre']}_{datetime.now().strftime('%Y%M%D')}.csv", mime="text/csv", use_container_width=True)
            
            st.markdown("<br><hr style='margin:10px 0;'>", unsafe_allow_html=True)
            with st.form("f_mant"):
                mc1, mc2, mc3 = st.columns([2, 1, 1])
                m_tipo = mc1.selectbox("Tipo de Tarea", ["💦 Limpieza Paneles", "🔋 Revisión Baterías", "🔌 Revisión Inversor"])
                m_fecha = mc2.date_input("Fecha Programada")
                m_resp = mc3.text_input("Técnico Responsable")
                m_notas = st.text_input("Observaciones")
                if st.form_submit_button("➕ Agendar Mantenimiento"):
                    # guardar_mantenimiento(p['nombre'], {"fecha": str(m_fecha), "tipo": m_tipo, "resp": m_resp, "notas": m_notas, "estado": "⏳ Pendiente"})
                    st.success("Agendado (Mock)")
            
            st.markdown("<br><h4>📋 Historial de Tareas</h4>", unsafe_allow_html=True)
            # mantenimientos = cargar_mantenimientos().get(p['nombre'], [])
            st.info("No hay mantenimientos programados (Mock).")

elif menu == "🚨 Centro de Alertas":
    st.title("🚨 ALERTAS")
    plantas = cargar_plantas()
    if not plantas: st.info("No hay plantas registradas.")
    else:
        for p in plantas:
            if random.random() < 0.33:
                st.error(f"❌ ALERTA ACTIVA en {p['nombre'].upper()}: Fallo de comunicación Datalogger (SN: {p.get('datalogger','N/A')}) - Error Modbus 0x01. Verifique conexión a internet.")
            else:
                st.success(f"✅ Todo funciona correctamente en {p['nombre'].upper()}. Sin alarmas activas.")
