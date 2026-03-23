import streamlit as st
import random
import json
import os
import math
import pandas as pd
import requests
from pymodbus.client import ModbusTcpClient
import re
import hashlib
from datetime import datetime, timedelta
import plotly.express as px
import time

# --- MOCKS ---
MODBUS_IP = "192.168.1.10"
MODBUS_PORT = 502

class MockModbusClient:
    def __init__(self, host, port): self.host = host; self.port = port
    def connect(self): return random.choice([True, False])
    def read_holding_registers(self, address, count, slave):
        return type('obj', (object,), {'registers': [random.randint(0, 100) for _ in range(count)]})()
    def write_register(self, address, value, slave): return True
    def close(self): pass

try: client = ModbusTcpClient(MODBUS_IP, port=MODBUS_PORT); connection_status = "🟢 Conectado" if client.connect() else "🔴 Desconectado (Fallo de Red)"
except Exception as e: client = MockModbusClient(MODBUS_IP, MODBUS_PORT); connection_status = "🟠 Modo Simulación (Fallo de Red)"

def cargar_plantas():
    if not os.path.exists('plantas.json'): return []
    try:
        with open('plantas.json', 'r') as f: return json.load(f)
    except json.JSONDecodeError: return []

def guardar_planta(nueva_planta):
    plantas = cargar_plantas()
    plantas.append(nueva_planta)
    with open('plantas.json', 'w') as f: json.dump(plantas, f)

def cargar_usuarios():
    if not os.path.exists('usuarios.json'): return {}
    with open('usuarios.json', 'r') as f: return json.load(f)

def simular_historico_24h():
    inicio_dia = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    datos = []
    for m in range(0, 24 * 60, 15): 
        t = inicio_dia + timedelta(minutes=m)
        h = t.hour
        generacion_fv = random.uniform(0.1, 12.0) if 6 <= h <= 18 else 0
        consumo_carga = random.uniform(1.0, 5.0)
        datos.append({"timestamp": t, "Generación FV (kW)": round(generacion_fv, 2), "Consumo Carga (kW)": round(consumo_carga, 2)})
    return pd.DataFrame(datos)

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y ESTILO (CSS)
# ==========================================
st.set_page_config(page_title="HMI INVERSOR FV - CV INGENIERÍA SAS", page_icon="☀️", layout="wide")

css_global = """
<style>
/* Estilo general y paleta de colores: Azul CV (profundo), Grises (fondo), Blanco, Naranja CV (acentos) */
:root {
    --primary-color: #003366;
    --secondary-color: #f0f2f5;
    --text-color: #2c3e50;
    --accent-color: #f39c12;
    --border-color: #e0e0e0;
}

[data-testid="stAppViewContainer"] {
    background-color: var(--secondary-color);
}

.stMarkdown { color: var(--text-color); }
h1, h2, h3, h4, h5 { color: var(--primary-color); }
label { color: var(--text-color); font-weight: 500;}

/* Estilo para las Tarjetas/Paneles (Cards) */
.hmi-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hmi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(0,0,0,0.12); }
.hmi-card h3 { margin-bottom: 5px; font-size: 1.1rem; }
.hmi-card h4 { color: #7f8c8d; font-size: 0.9rem; margin-top: 0; }
.hmi-metric-large { font-size: 2.2rem; font-weight: 700; color: var(--primary-color); }
.hmi-unit { font-size: 1rem; color: #7f8c8d; vertical-align: baseline; }

/* Estilo para los KPI Tiles */
.kpi-tile { text-align: center; border-right: 1px solid var(--border-color); }
.kpi-tile:last-child { border-right: none; }
.kpi-label { color: #7f8c8d; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; }

/* Estilo para las Tabs (Pestañas) */
div[data-testid="stTabs"] > div[data-baseweb="tab-list"] {
    background-color: transparent; border-bottom: 2px solid var(--border-color); gap: 15px;
}
div[data-testid="stTabs"] button[data-baseweb="tab"] p {
    color: var(--text-color); font-weight: 600; font-size: 16px; 
}
div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
    color: var(--accent-color); border-bottom: 2px solid var(--accent-color); background-color: transparent;
}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent-color); border-bottom: 2px solid var(--accent-color); background-color: transparent;
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
.status-sim { background-color: #f39c1220; color: #f39c12; border: 1px solid #f39c1250; }

/* Botones Primary/Secondary */
div[data-testid="stButton"] button { border-radius: 8px; }
div[data-testid="stButton"] button[kind="primary"] { background-color: var(--accent-color); border-color: var(--accent-color); }
div[data-testid="stButton"] button[kind="secondary"] { color: var(--primary-color); border-color: var(--border-color); }

/* Inputs y Selectbox */
input, select { border-radius: 8px; border: 1px solid var(--border-color); padding: 10px; }
</style>
"""
st.markdown(css_global, unsafe_allow_html=True)

# ==========================================
# 2. AUTENTICACIÓN Y REGISTRO (JSON)
# ==========================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False; st.session_state["usuario"] = None; st.session_state["rol"] = None
if "registro" not in st.session_state: st.session_state["registro"] = False

def login(usuario, contrasena):
    db = cargar_usuarios()
    if usuario in db and db[usuario]["contrasena"] == hashlib.sha256(contrasena.encode()).hexdigest():
        st.session_state["autenticado"] = True; st.session_state["usuario"] = usuario; st.session_state["rol"] = db[usuario]["rol"]
        return True
    return False

def registrar(usuario, contrasena):
    db = cargar_usuarios()
    if usuario in db: return False, "El usuario ya existe."
    db[usuario] = {"contrasena": hashlib.sha256(contrasena.encode()).hexdigest(), "rol": "instalador"}
    with open('usuarios.json', 'w') as f: json.dump(db, f)
    return True, "Registro exitoso."

def logout(): st.session_state["autenticado"] = False; st.session_state["usuario"] = None; st.session_state["rol"] = None; st.rerun()

# --- VISTA: LOGIN ---
if not st.session_state["autenticado"]:
    st.markdown('<div class="hmi-card" style="max-width:400px; margin: 100px auto;">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top:0;'>☀️ CV INGENIERÍA - HMI</h2>", unsafe_allow_html=True)
    
    if st.session_state["registro"]:
        with st.form("registro_form"):
            r_user = st.text_input("Usuario (Correo)")
            r_pass = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Crear Cuenta")
            if submitted: 
                res, msg = registrar(r_user, r_pass)
                if res: st.success(msg); time.sleep(1); st.session_state["registro"] = False; st.rerun()
                else: st.error(msg)
        if st.button("Volver al Login"): st.session_state["registro"] = False; st.rerun()
    else:
        with st.form("login_form"):
            st.markdown("<h4 style='text-align: center;'>Iniciar Sesión</h4>", unsafe_allow_html=True)
            u_login = st.text_input("Usuario (Correo)", key="u_login")
            p_login = st.text_input("Contraseña", type="password", key="p_login")
            if st.form_submit_button("Entrar", use_container_width=True, kind="primary"):
                if login(u_login, p_login): st.rerun()
                else: st.error("❌ Credenciales incorrectas.")
        st.markdown("<p style='text-align: center;'>ó</p>", unsafe_allow_html=True)
        if st.button("Regístrate como Instalador", use_container_width=True): st.session_state["registro"] = True; st.rerun()
    
    st.markdown("<p style='text-align: center; font-size: 10px; color: #7f8c8d; margin-top: 20px;'>Versión HMI 1.0 | CV Ingeniería SAS</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 3. NAVEGACIÓN Y SIDEBAR (OSCURO)
# ==========================================
st.sidebar.markdown(f"""
<div class="hmi-card" style="background:transparent; box-shadow:none; padding:10px; border-radius:0;">
<h3 style="color: white; margin-top:0;">📋 CV INGENIERÍA SAS</h3>
<p style="color: #cbd5e0; font-size: 11px;">HMI DE GESTIÓN FV</p>
<div style="border-top:1px solid #324a5f; margin:10px 0;"></div>
<p style="color: white; font-weight: 600;">👤 {st.session_state['usuario']}</p>
<p style="color: #cbd5e0; font-size: 12px; text-transform:uppercase;">ROL: {st.session_state['rol']}</p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("IR A:", ["🌐 Panorama General", "📊 Panel de Planta", "🚨 Alarmas", "📄 Reportes"], key="nav")
if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True, kind="secondary"): logout()

# ==========================================
# 4. VISTA: PANORAMA GENERAL
# ==========================================
if menu == "🌐 Panorama General":
    st.markdown("## 🌐 PANORAMA GENERAL DE PLANTAS")
    plantas = cargar_plantas()
    
    # Crear planta EXPANDER
    with st.expander("➕ Crear una nueva planta", expanded=not plantas):
        with st.form("crear_planta"):
            n_nombre = st.text_input("Nombre de la planta")
            n_ubicacion = st.text_input("Ubicación")
            n_inversor = st.selectbox("Marca/Modelo del Inversor", ["Deye", "Huawei", "GoodWe", "Otros"])
            n_modbus_ip = st.text_input("IP Modbus (Ej: 192.168.1.10)")
            n_modbus_port = st.number_input("Puerto Modbus", value=502)
            if st.form_submit_button("Guardar Planta"):
                if n_nombre and n_modbus_ip: guardar_planta({"nombre": n_nombre, "ubicacion": n_ubicacion, "inversor": n_inversor, "modbus_ip": n_modbus_ip, "modbus_port": n_modbus_port}); st.rerun()
                else: st.error("⚠️ Nombre e IP son obligatorios.")

    # Filtro de búsqueda
    search_query = st.text_input("🔍 Buscar planta por nombre o ciudad:", placeholder="Escribe el nombre de la planta", label_visibility="collapsed")

    if not plantas: st.info("No hay plantas registradas. Usa el botón de arriba para agregar una."); st.stop()

    # Grid de PLANTAS
    filtered_plantas = [p for p in plantas if search_query.lower() in p['nombre'].lower() or search_query.lower() in p['ubicacion'].lower()]

    if not filtered_plantas: st.info("No se encontraron plantas que coincidan con la búsqueda.")
    
    # Simulación de KPI para cards
    def get_simulated_metrics(planta): return {"power": random.uniform(2.1, 10.5), "energy_today": random.uniform(8.1, 45.3), "alerts": random.randint(0, 3)}

    for p in filtered_plantas:
        metrics = get_simulated_metrics(p)
        alert_text = f"{metrics['alerts']} Alertas" if metrics['alerts'] > 0 else "0 Alertas"
        alert_color = "#e74c3c" if metrics['alerts'] > 0 else "#2ecc71"
        
        st.markdown(f"""
        <div class="hmi-card plant-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h3>{p['nombre']} <span style='font-size: 10px; color: #7f8c8d;'>| Inversor: {p['inversor']} | {p['modbus_ip']}</span></h3>
                    <h4>📍 {p['ubicacion']}</h4>
                </div>
                <span class="hmi-status-badge status-connected">CONEXIÓN OK</span>
            </div>
            <div style="border-top:1px solid #e0e0e0; margin:10px 0;"></div>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; text-align:center;">
                <div class="kpi-tile">
                    <p class="kpi-label">⚡ Potencia Actual</p>
                    <p><span class="hmi-metric-large">{metrics['power']:.2f}</span><span class="hmi-unit"> kW</span></p>
                </div>
                <div class="kpi-tile">
                    <p class="kpi-label">🔋 Energía Hoy</p>
                    <p><span class="hmi-metric-large">{metrics['energy_today']:.1f}</span><span class="hmi-unit"> kWh</span></p>
                </div>
                <div class="kpi-tile" style="color: {alert_color}; font-weight:700;">
                    <p class="kpi-label">🚨 Alertas</p>
                    <p style="font-size: 1.5rem; margin-top:10px;">{alert_text}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, _ = st.columns([1,1,6])
        if col1.button("🗑️ Eliminar", key=f"del_{p['nombre']}", kind="secondary", use_container_width=True): 
            plantas.remove(p); 
            with open('plantas.json', 'w') as f: json.dump(plantas, f); 
            st.rerun()
        if col2.button("📊 Ver Panel", key=f"panel_{p['nombre']}", kind="secondary", use_container_width=True): st.session_state["nav"] = "Panel de Planta"; st.rerun()

# ==========================================
# 5. VISTA: PANEL DE PLANTA
# ==========================================
elif menu == "📊 Panel de Planta":
    plantas = cargar_plantas()
    if not plantas: st.info("No hay plantas registradas. Ve a Panorama General."); st.stop()
    
    col1, _ = st.columns([1, 1])
    planta_sel = col1.selectbox("📋 Seleccionar planta:", [p['nombre'] for p in plantas], index=0)
    p = next(pl for pl in plantas if pl['nombre'] == planta_sel)
    
    st.markdown(f"## 📊 PANEL DE CONTROL - {p['nombre'].upper()} <span style='font-size:14px; color:gray;'>| 📍 {p['ubicacion']} | Inversor: {p['inversor']}</span>", unsafe_allow_html=True)
    
    # -------------------------------------------------------------
    # KPI TILES ARRIBA (Mas dinámico, mas real)
    # -------------------------------------------------------------
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    # Simulado potencia actual con "jitter"
    power_now = random.uniform(8.5, 9.8) + random.uniform(-0.1, 0.1)
    progress_val = int((power_now / 12.0) * 100) # Mock de capacidad maxima 12kW

    kpi1.markdown(f"""
    <div class="hmi-card kpi-tile" style="border:none;">
        <p class="kpi-label">⚡ Potencia Solar Actual</p>
        <p><span class="hmi-metric-large">{power_now:.2f}</span><span class="hmi-unit"> kW</span></p>
        <div style="background-color:#e0e0e0; border-radius:10px; height:10px; width:100%; margin-top:10px;">
            <div style="background-color:var(--accent-color); border-radius:10px; height:10px; width:{progress_val}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    energy_today = random.uniform(35.2, 42.1)
    kpi2.markdown(f"""
    <div class="hmi-card kpi-tile" style="border:none;">
        <p class="kpi-label">🔋 Energía Generada Hoy</p>
        <p><span class="hmi-metric-large">{energy_today:.1f}</span><span class="hmi-unit"> kWh</span></p>
    </div>
    """, unsafe_allow_html=True)

    ahorro_tot = random.uniform(1210.5, 1225.1)
    kpi3.markdown(f"""
    <div class="hmi-card kpi-tile" style="border:none;">
        <p class="kpi-label">💰 Ahorro Estimado Hoy (COP)</p>
        <p><span class="hmi-metric-large">${ahorro_tot:,.0f}</span><span class="hmi-unit"> COP</span></p>
    </div>
    """, unsafe_allow_html=True)

    status_class = "status-connected" if "🟢" in connection_status else "status-sim" if "🟠" in connection_status else "status-disconnected"
    kpi4.markdown(f"""
    <div class="hmi-card kpi-tile" style="border:none;">
        <p class="kpi-label">🔗 ESTADO CONEXIÓN MODBUS</p>
        <p style='margin-top:10px;'><span class="hmi-status-badge {status_class}">{connection_status}</span></p>
        <p style='font-size:11px; color: #7f8c8d; margin-top:5px;'>{p['modbus_ip']}:{p['modbus_port']}</p>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # DIAGRAMA DE FLUJO ( Plotly Sankey o similar - Mock)
    # -------------------------------------------------------------
    import plotly.graph_objects as go

    st.markdown("<div class='hmi-card'>", unsafe_allow_html=True)
    st.markdown("### 🔄 Diagrama de Flujo de Energía (Mock)")
    
    p_sol = power_now
    p_casa = p_sol * 0.4
    p_bat_in = p_sol * 0.3
    p_red_out = p_sol * 0.3

    fig = go.Figure(go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "#324a5f", width = 1.0),
          label = ["PANEL SOLAR", "INVERSOR CV", "CONSUMO CASA", "BATERÍA (In)", "RED (Exportación)"],
          color = ["#f1c40f", "#324a5f", "#e74c3c", "#2ecc71", "#7f8c8d"]
        ),
        link = dict(
          source = [0, 1, 1, 1], # indices, solar->inversor->casa, inversor->bateria, inversor->red
          target = [1, 2, 3, 4],
          value = [p_sol, p_casa, p_bat_in, p_red_out],
          color = ["#f1c40f50", "#324a5f50", "#2ecc7150", "#7f8c8d50"]
      )))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_size=11, margin=dict(l=10, r=10, t=10, b=10), height=300)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


    # -------------------------------------------------------------
    # HISTÓRICO 24H ( Plotly Express)
    # -------------------------------------------------------------
    st.markdown("<div class='hmi-card'>", unsafe_allow_html=True)
    st.markdown("### 📈 Desempeño Histórico (24h)")
    df_historico = simular_historico_24h()
    fig2 = px.line(df_historico, x="timestamp", y=["Generación FV (kW)", "Consumo Carga (kW)"], color_discrete_sequence=["var(--accent-color)", "#e74c3c"])
    fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text=None, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis_title=None, yaxis_title="kW", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


    # -------------------------------------------------------------
    # PESTAÑAS (Tabs) - Se estilizan para verse mejor
    # -------------------------------------------------------------
    if st.session_state['rol'] == 'admin':
        t_control, t_red, t_tou, t_reports = st.tabs(["⚙️ Control Avanzado (Advanced-1)", "⚡ Parámetros de Red (Red)", "📅 TOU Settings", "📄 Reportes/O&M"])
    else:
        t_tou, t_reports = st.tabs(["📅 TOU Settings", "📄 Reportes/O&M"])
        t_control = None; t_red = None

    # --- PESTAÑA: CONTROL AVANZADO (Advanced-1) ---
    if t_control:
        with t_control:
            st.markdown("<h4>Configuración de Control del Inversor</h4>", unsafe_allow_html=True)
            st.info("ⓘ Modifique estos parámetros bajo supervisión de CV Ingeniería.")
            
            c1, c2, c3, c4 = st.columns(4)
            # Sección Generador
            with c1:
                st.markdown('##### 🏭 Generador Externo')
                p1_mode = st.selectbox("Modo Gen", ["Manual", "Automático"])
                p1_max = st.number_input("Max Potencia Gen (W)", value=5000)
                st.checkbox("Lunes")
                st.checkbox("Martes")
            # Sección Paralelo/CT
            with c2:
                st.markdown('##### 🔄 Paralelo / CT')
                st.selectbox("Modo (M/S)", ["Maestro", "Esclavo"])
                st.number_input("Medidor red2 (Modbus SN)", value=1)
                st.number_input("relación CT", value=1000)
                st.selectbox("relé de derivación lado grid", ["Habilitado", "Deshabilitado"])
            # Sección ARC / Peak
            with c3:
                st.markdown('##### 🛠️ Protecciones ARC / Peak-Shaving')
                st.selectbox("Modo DRM", ["Habilitado", "Deshabilitado"])
                st.selectbox("configuración ARC", ["Habilitado", "Deshabilitado"])
                st.number_input("Potencia de reducción pico de red (W)", value=1000)
                st.selectbox("Peakeando la red", ["Habilitado", "Deshabilitado"])
            # Otros
            with c4:
                st.markdown('##### 🧠 Inteligencia')
                st.selectbox("Modo Isla Señal", ["Habilitado", "Deshabilitado"])
                st.number_input("Retraso de respaldo", value=0)
                st.selectbox("Alimentación Asimétrica", ["Habilitado", "Deshabilitado"])
                st.selectbox("MPPT Scan", ["Habilitado", "Deshabilitado"])

            _, _c_action, _ = st.columns([6,1,1])
            _c_action.button("💾 Guardar Config Advanced-1", use_container_width=True, kind="primary")

    # --- PESTAÑA: PARÁMETROS DE RED (Red) ---
    if t_red:
        with t_red:
            st.markdown("<h4>Configuración de Límite de Red y Protección</h4>", unsafe_allow_html=True)
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.markdown("##### ⚡ Parámetros de Tensión")
                norma = st.selectbox("Normativa", ["RETIE / NTC 2050 (Colombia)", "IEEE 1547", "IEC 61727"])
                v_max = st.number_input("Sobre Tensión Max (Over V) (V)", value=253.0)
                v_min = st.number_input("Sub Tensión Min (Under V) (V)", value=198.0)
            with col_r2:
                st.markdown("##### ⚡ Frecuencia y Reconexión")
                f_max = st.number_input("Sobre Frecuencia Max (Over f) (Hz)", value=60.5)
                f_min = st.number_input("Sub Frecuencia Min (Under f) (Hz)", value=59.5)
                t_reco = st.number_input("Tiempo de Reconexión (s)", value=60)
            with col_r3:
                st.markdown("##### 🔌 Límite Inyección")
                st.toggle("Habilitar Export Limit")
                limit_val = st.number_input("Límite de Inyección a red (W)", value=0)

            _, _c_action_red, _ = st.columns([6,1,1])
            _c_action_red.button("💾 Guardar Config Red", use_container_width=True, kind="primary")

    # --- PESTAÑA: TOU SETTINGS ---
    with t_tou:
        st.markdown("<h4>🕒 Gestión de Energía por Periodos de Tiempo (TOU)</h4>", unsafe_allow_html=True)
        # Mock de 6 periodos con structured formatting ( tiles)
        tou_opts = cargar_usuarios() # Usamos esto como mock db para tou settings si queremos guardar
        
        for i in range(1, 7):
            st.markdown(f'<div class="hmi-card tou-period-tile">', unsafe_allow_html=True)
            col1, col2, col3, col4, col5 = st.columns([1,2,2,2,1])
            col1.markdown(f'##### Periodo {i}')
            col2.time_input("Inicio", key=f"tou_start_{i}", value=datetime.strptime(f"{i*4}:00", "%H:%M").time())
            col3.number_input("SOC Batería (%)", value=100 - i*10, key=f"tou_soc_{i}")
            col4.selectbox("Fuente Grid/Gen", ["SOLO SOLAR", "GRID MIX", "GEN MIX"], key=f"tou_src_{i}")
            col5.toggle("TOU En", value=True, key=f"tou_en_{i}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        _, _c_action_tou, _ = st.columns([6,1,1])
        _c_action_tou.button("💾 Guardar Config TOU", use_container_width=True, kind="primary")


    # --- PESTAÑA: REPORTES Y O&M ---
    with t_reports:
        r_c1, r_c2 = st.columns(2)
        with r_c1:
            st.markdown("<h4>📄 Reportes de Generación</h4>", unsafe_allow_html=True)
            r_type = st.selectbox("Tipo", ["Diario", "Mensual"])
            r_date = st.date_input("Fecha", value=datetime.now())
            csv = df_historico.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Reporte (Mock)", data=csv, file_name=f"{p['nombre']}_reporte_{r_type}_{r_date}.csv", mime='text/csv', use_container_width=True)

        with r_c2:
            st.markdown("<h4>🛠️ Mantenimiento y Logs</h4>", unsafe_allow_html=True)
            st.markdown('<div class="hmi-card" style="font-family: monospace; font-size:11px;">', unsafe_allow_html=True)
            st.write(">> [2024-07-28 09:30] Config Advanced-1 guardada por rlopez")
            st.write(">> [2024-07-28 10:15] Conexión Modbus OK")
            st.write(">> [2024-07-28 11:00] Generación FV Pico Alcanzado: 11.5 kW")
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 6. ALARMAS Y CENTRO DE ALERTAS
# ==========================================
elif menu == "🚨 Alarmas":
    st.markdown("## 🚨 CENTRO DE ALERTAS Y ALARMAS ACTIVAS")
    plantas = cargar_plantas()
    if not plantas: st.info("No hay plantas registradas. No hay alarmas."); st.stop()
    
    # Mock de alarmas
    for p in plantas:
        alert_count = random.randint(0, 3)
        if alert_count > 0:
            st.markdown(f"#### Alertas en: {p['nombre']}")
            for _ in range(alert_count):
                error_code = random.randint(100, 200)
                st.error(f"❌ Alerta Activa: Error {error_code} - Fallo de Comunicación Modbus / Alta Temperatura Inversor (Mock)")
        else: st.success(f"✅ Sin alertas activas en: {p['nombre']}")

# ==========================================
# 7. REPORTES DE GESTIÓN (CSV)
# ==========================================
elif menu == "📄 Reportes":
    st.markdown("## 📄 REPORTE DE GESTIÓN MENSUAL (MOCK)")
    st.download_button("📥 Descargar Resumen General (Excel)", b"MOCK EXCEL DATA", file_name="resumen_general_plantas.xlsx")
