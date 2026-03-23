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

# CSS GLOBAL (Fondo transparente y letras blancas para la app en general)
css_global = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=1920");
    background-size: cover; 
    background-position: center; 
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }

.block-container, [data-testid="stMainBlockContainer"], div[data-testid="block-container"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
}

h1, h2, h3, h4, h5, p, .stMarkdown span {
    color: #ffffff !important;
    text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important;
}

label, label p, label div, button[data-baseweb="tab"] p, button[data-baseweb="tab"] span {
    color: #ffffff !important;
    text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important;
}

[data-testid="stAlert"] {
    background-color: rgba(255, 255, 255, 0.95) !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
}
[data-testid="stAlert"] * {
    color: #2c3e50 !important;
    text-shadow: none !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
    border-right: 1px solid #4ca1af !important;
    box-shadow: 4px 0 15px rgba(0,0,0,0.5) !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
    text-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background-color: rgba(241, 196, 15, 0.15) !important;
    border-left: 5px solid #f1c40f !important;
    box-shadow: 0 0 10px rgba(241, 196, 15, 0.2) !important;
}
[data-testid="stSidebar"] [data-testid="stAlert"] * {
    color: #f1c40f !important; 
    font-weight: bold !important;
    letter-spacing: 1px !important;
}

.tarjeta-planta *, input, select, textarea, button span {
    color: #2c3e50 !important;
    text-shadow: none !important;
}

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
</style>
"""
st.markdown(css_global, unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS (PLANTAS Y USUARIOS)
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'
ARCHIVO_USUARIOS = 'usuarios.json'

def cargar_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'w') as f: json.dump({"admin": "solar123"}, f)
    with open(ARCHIVO_USUARIOS, 'r') as f: return json.load(f)

def guardar_usuario(usuario, contrasena):
    usuarios = cargar_usuarios()
    usuarios[usuario] = contrasena
    with open(ARCHIVO_USUARIOS, 'w') as f: json.dump(usuarios, f)

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

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center; font-size: 3.5rem; color: #f1c40f !important;'>☀️ MOMISOLAR APP</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Plataforma de Gestión - CV INGENIERÍA SAS</h3><br>", unsafe_allow_html=True)
    
    col1, col_centro, col2 = st.columns([1, 2, 1]) 
    with col_centro:
        with st.form("login_form"):
            usuario_input = st.text_input("👤 Correo / Usuario")
            contrasena_input = st.text_input("🔑 Contraseña", type="password") 
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                usuarios_bd = cargar_usuarios()
                if usuario_input in usuarios_bd and usuarios_bd[usuario_input] == contrasena_input:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_actual"] = usuario_input
                    st.rerun() 
                else:
                    st.error("❌ Credenciales incorrectas.")
    st.stop() 

# --- MOTOR DE INTEGRACIÓN SOLARMAN CON ALERTAS ---
def obtener_datos_reales(planta):
    cap_texto = str(planta.get("capacidad", "5"))
    solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
    try: cap_val = float(solo_numeros[0]) * 1000 if solo_numeros else 5000 
    except: cap_val = 5000 
    
    pot_simulada = int(cap_val * random.uniform(0.1, 0.8))
    energia_simulada = round((pot_simulada * random.uniform(3.5, 5.0)) / 1000, 1)
    estado = "Simulado (Falta API)" if planta.get("inversores") in ["Deye", "Sylvania"] else "Simulado"
    
    soc_actual = random.randint(15, 99) 
    alertas_activas = []
    
    if soc_actual <= 25:
        alertas_activas.append("⚠️ Batería Baja: Nivel de SOC crítico (<=25%). Riesgo de desconexión de cargas.")
    if random.random() < 0.15: 
        alertas_activas.append("🔌 Falla de Red AC: Sin voltaje detectado en la acometida. Operando en modo Off-Grid.")

    return {
        "solar": pot_simulada, "casa": 1750 + random.randint(-40, 40),
        "soc": soc_actual, "energia_diaria": energia_simulada, "status": estado,
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
        
        generacion = 0
        if 6 <= hora <= 18:
            x = (hora - 6) / 12 * math.pi
            generacion = max(0, (cap_val * 0.9) * math.sin(x) * random.uniform(0.95, 1.05))
            
        base_consumo = cap_val * 0.2
        pico_consumo = cap_val * 0.3 * math.sin((hora-7)/2 * math.pi) if 7 <= hora <= 9 else (cap_val * 0.4 * math.sin((hora-18)/3 * math.pi) if 18 <= hora <= 21 else 0)
        consumo = max(cap_val * 0.1, base_consumo + pico_consumo + (cap_val * 0.05 * random.uniform(-1, 1)))
        
        datos.append({"timestamp": timestamp, "Generación FV": round(generacion, 2), "Consumo Carga": round(consumo, 2)})
        
    return pd.DataFrame(datos)

plantas_guardadas = cargar_plantas()

# ==========================================
# 3. NAVEGACIÓN PRINCIPAL
# ==========================================
st.sidebar.title("☀️ MOMISOLAR APP")
rol_actual = "Instalador/Admin" if st.session_state.get('usuario_actual') == 'admin' else "Cliente"
st.sidebar.write(f"👤 Usuario: **{st.session_state.get('usuario_actual', 'admin')}**\n\n🛡️ Rol: {rol_actual}")

# Se consolidaron los menús porque "Control de Inversores" ahora vive DENTRO del Panel de Planta
menu = st.sidebar.radio("Ir a:", ["🌐 Panorama General", "📊 Panel de Planta", "🏢 Gestión de Portafolio", "🚨 Centro de Alertas"])

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()
    
st.sidebar.info("**POWERED BY:**\n\n**CV INGENIERIA SAS**")

# ==========================================
# INYECCIÓN DE CSS DINÁMICO (MODO DASHBOARD BLANCO PARA EL PANEL DE PLANTA)
# ==========================================
if menu == "📊 Panel de Planta":
    st.markdown("""
    <style>
    /* Transformar el fondo en un espacio de trabajo limpio tipo Solarman */
    .block-container, [data-testid="stMainBlockContainer"] {
        background-color: #f4f7f9 !important;
        backdrop-filter: none !important;
        border-radius: 0px !important;
    }
    /* Forzar todos los textos principales a oscuros */
    h1, h2, h3, h4, h5, p, span, label, div {
        color: #2c3e50 !important;
        text-shadow: none !important;
    }
    /* Tarjetas de métricas superiores */
    .solarman-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #eaeaea;
    }
    .solarman-val { font-size: 26px; font-weight: bold; color: #2c3e50; margin-bottom: 5px; }
    .solarman-lbl { font-size: 13px; color: #7f8c8d; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# VENTANA 1: PANORAMA GENERAL
# ==========================================
if menu == "🌐 Panorama General":
    st.title("🌐 PANORAMA GENERAL DEL PORTAFOLIO")
    st.markdown("**MOMISOLAR APP - Vista global rápida**")
    
    if not plantas_guardadas:
        st.warning("No hay plantas registradas. Ve a Gestión para agregar una.")
    else:
        st.markdown("<h3 style='margin-bottom:10px; color:#ffffff;'>Directorio Técnico de Plantas</h3>", unsafe_allow_html=True)
        
        col_espacio, col_buscador = st.columns([2, 1])
        with col_buscador:
            busqueda = st.text_input("🔍 Buscar planta", label_visibility="collapsed", placeholder="Ingrese nombre o ciudad...")
        
        plantas_filtradas = [pl for pl in plantas_guardadas if busqueda.lower() in pl['nombre'].lower() or busqueda.lower() in pl['ubicacion'].lower()]

        st.markdown('<div style="overflow-x: auto; padding-bottom: 15px;"><div style="min-width: 1050px;">', unsafe_allow_html=True)
        
        header_tabla = f"""
<div style="background:#ffffff; border-radius: 8px; padding: 10px 15px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
<div style="display:flex; align-items:center;">
<div style="color: #3498db; font-size:16px; margin-right:10px;">☀️</div>
<div style="font-weight:bold; color: #2c3e50;">Listado Activo (Total {len(plantas_filtradas)})</div>
</div>
</div>
"""
        st.markdown(header_tabla, unsafe_allow_html=True)
        
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

                fila_pro = f"""
<div class="tarjeta-dash-pro" style="position:relative;">
{alerta_html}
<div style="display:flex; align-items:center; width: 320px; flex-shrink: 0;">
<img src="https://img.icons8.com/color/48/solar-panel.png" style="width: 32px; height:32px; margin-right:15px; border-radius:4px;"/>
<div>
<div style="font-size: 15px; font-weight: bold; color: #2c3e50;">{pl['nombre']}</div>
<div style="font-size: 12px; color: #7f8c8d;"><img src="https://img.icons8.com/material-rounded/24/marker.png" style="width:12px; height:12px; margin-right:3px;"/>{pl['ubicacion']}</div>
</div>
</div>
<div class="tarjeta-dash-item" style="text-align: center; width: 50px; flex-shrink: 0;">
<div class="tarjeta-label-pro">Com</div>
<div style="font-size:16px;">📶</div>
</div>
<div class="tarjeta-dash-item" style="text-align: center; width: 60px; flex-shrink: 0;">
<div class="tarjeta-label-pro">Alertas</div>
<div style="font-size:16px;">{status_icon}</div>
</div>
<div class="tarjeta-dash-item" style="width: 140px; flex-shrink: 0;">
<div class="tarjeta-label-pro">Capacidad</div>
<div class="tarjeta-dato-pro">{cap_limpia}</div>
</div>
<div class="tarjeta-dash-item" style="width: 160px; flex-shrink: 0;">
<div class="tarjeta-label-pro">Potencia Solar Actual</div>
<div class="tarjeta-dato-pro">{datos['solar']} W</div>
</div>
<div class="tarjeta-dash-item" style="width: 150px; flex-shrink: 0;">
<div class="tarjeta-label-pro">Producción Diaria</div>
<div class="tarjeta-dato-pro" style="color: #27ae60 !important;">{datos['energia_diaria']} kWh</div>
</div>
<div style="display: flex; gap: 5px; width: 60px; flex-shrink: 0;">
<img src="https://img.icons8.com/material-rounded/24/edit.png" style="width:18px; height:18px; cursor:pointer; opacity:0.6;"/>
<img src="https://img.icons8.com/material-rounded/24/filled-trash.png" style="width:18px; height:18px; cursor:pointer; opacity:0.6;"/>
</div>
</div>
"""
                st.markdown(fila_pro, unsafe_allow_html=True)
            
        st.markdown("</div></div>", unsafe_allow_html=True) 
            
        if st.button("🔄 Actualizar Todo"): st.rerun()

# ==========================================
# VENTANA 2: PANEL DE PLANTA (EL NUEVO WORKSPACE BLANCO + CONFIGURACIÓN)
# ==========================================
elif menu == "📊 Panel de Planta":
    
    if not plantas_guardadas:
        st.warning("No hay plantas registradas en el sistema.")
    else:
        # Selector principal superior
        col_tit, col_sel = st.columns([2, 1])
        with col_sel:
            planta_sel = st.selectbox("Cambiar de Planta:", [p["nombre"] for p in plantas_guardadas], label_visibility="collapsed")
        d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
        datos_act = obtener_datos_reales(d)
        
        estado_ico = "🟢 En línea" if not datos_act["alertas"] else "🔴 Con Alertas"
        st.markdown(f"<h2>{d['nombre']} <span style='font-size:14px; color:#7f8c8d; font-weight:normal;'>ID: {hashlib.md5(d['nombre'].encode()).hexdigest()[:8].upper()} | {estado_ico}</span></h2>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top:0px; margin-bottom:20px; border-color:#e0e0e0;'>", unsafe_allow_html=True)

        # MÉTRICAS SUPERIORES ESTILO SOLARMAN
        prod_solar = datos_act["energia_diaria"]
        consumo_sim = round(prod_solar * 0.45, 1)
        carga_bat = round(prod_solar * 0.2, 1)
        descarga_bat = round(prod_solar * 0.1, 1)
        
        c1, c2, c3, c4 = st.columns([1.5, 1.5, 1, 1])
        with c1:
            st.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#3498db;'>{prod_solar} kWh</div><div class='solarman-lbl'>Producción Solar</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='solarman-card'><div class='solarman-val' style='color:#e67e22;'>{consumo_sim} kWh</div><div class='solarman-lbl'>Consumo</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='solarman-card'><div style='font-size:14px; font-weight:bold;'>🔋 {carga_bat} kWh <span style='color:#7f8c8d; font-size:10px;'>Cargar</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px;'>🔋 {descarga_bat} kWh <span style='color:#7f8c8d; font-size:10px;'>Descargar</span></div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='solarman-card'><div style='font-size:14px; font-weight:bold;'>⚡ 0 kWh <span style='color:#7f8c8d; font-size:10px;'>Alimentado</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px;'>⚡ 0 kWh <span style='color:#7f8c8d; font-size:10px;'>Desde Red</span></div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ÁREA PRINCIPAL DIVIDIDA EN PESTAÑAS (Aquí se integra el Control de Inversores)
        tab_monitor, tab_control, tab_reportes = st.tabs(["📈 Panel Gráfico y Flujo", "⚙️ Control Remoto del Inversor", "📄 Reportes y Datos"])
        
        with tab_monitor:
            col_grafica, col_flujo = st.columns([7, 3])
            
            with col_grafica:
                st.markdown("<div style='background:white; border-radius:8px; padding:15px; border:1px solid #eaeaea;'>", unsafe_allow_html=True)
                df_historico = simular_historico_24h(d)
                fig2 = px.area(
                    df_historico, x="timestamp", y=["Generación FV", "Consumo Carga"], 
                    color_discrete_map={"Generación FV": "#3498db", "Consumo Carga": "#e74c3c"}
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                    legend_title_text=None, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), 
                    xaxis=dict(tickformat="%H:%M", dtick=2 * 3600000, gridcolor="#f0f0f0"), 
                    yaxis=dict(gridcolor="#f0f0f0"), yaxis_title="kW", margin=dict(l=10, r=10, t=10, b=10), height=380
                )
                fig2.update_traces(fill='tozeroy', mode='lines', line=dict(width=2))
                fig2.update_traces(selector=dict(name="Consumo Carga"), fill='none')
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col_flujo:
                # Diagrama de flujo ajustado para fondo blanco
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
                        
                        <g transform="translate(60,30)">
                            <image href="https://img.icons8.com/color/48/solar-panel.png" width="40" height="40" x="-15" y="-15"/>
                            <text x="5" y="40" font-size="16" font-weight="bold" fill="#3498db" text-anchor="middle">{pot_solar} W</text>
                        </g>
                        
                        <g transform="translate(260,30)">
                            <image href="https://img.icons8.com/fluency/48/electrical.png" width="40" height="40" x="-15" y="-15"/>
                            <text x="5" y="40" font-size="16" font-weight="bold" fill="#7f8c8d" text-anchor="middle">0 W</text>
                        </g>
                        
                        <g transform="translate(60,260)">
                            <image href="https://img.icons8.com/color/48/car-battery.png" width="40" height="40" x="-15" y="-15"/>
                            <text x="5" y="40" font-size="16" font-weight="bold" fill="#27ae60" text-anchor="middle">{pot_bat} W</text>
                            <text x="5" y="55" font-size="11" font-weight="bold" fill="{color_bat}" text-anchor="middle">SOC: {soc}%</text>
                        </g>
                        
                        <g transform="translate(260,260)">
                            <image href="https://img.icons8.com/color/48/home.png" width="40" height="40" x="-15" y="-15"/>
                            <text x="5" y="40" font-size="16" font-weight="bold" fill="#e74c3c" text-anchor="middle">{pot_casa} W</text>
                        </g>
                    </svg>
                </div>
                """
                components.html(diagrama_svg, height=415)

        with tab_control:
            # AQUÍ VIVE AHORA EL CONTROL MAESTRO DE INVERSORES
            if st.session_state.get('usuario_actual') != 'admin':
                st.error("⛔ ACCESO DENEGADO")
                st.warning("El control de parámetros es exclusivo para el Administrador de CV INGENIERIA SAS.")
            else:
                st.info(f"⚙️ Configurando el inversor **{d['inversores']}** de la planta '{d['nombre']}'. Proceda con precaución.")
                
                sub_t1, sub_t2, sub_t3 = st.tabs(["🔋 Parámetros BMS", "⚡ Red y Normativa", "🕒 Time of Use (TOU)"])
                
                with sub_t1:
                    col_b1, col_b2 = st.columns(2)
                    col_b1.number_input("Max Corriente Carga (A)", min_value=10, max_value=150, value=60)
                    col_b2.number_input("Max Corriente Descarga (A)", min_value=10, max_value=150, value=80)
                    col_s1, col_s2, col_s3 = st.columns(3)
                    col_s1.number_input("SOC Parada (Shutdown %)", min_value=5, max_value=40, value=20)
                    col_s2.number_input("SOC Alarma (Low Warn %)", min_value=10, max_value=50, value=35)
                    col_s3.number_input("SOC Reinicio (Restart %)", min_value=20, max_value=100, value=50)

                with sub_t2:
                    col_g1, col_g2 = st.columns(2)
                    col_g1.selectbox("Normativa Aplicada", ["Colombia (RETIE / NTC 2050)", "IEEE 1547", "IEC 61727"])
                    col_g2.slider("Límite de Inyección a red (%) - Zero Export", min_value=0, max_value=100, value=0)
                    col_v1, col_v2 = st.columns(2)
                    col_v1.number_input("Voltaje Máx. AC (V)", min_value=220, max_value=270, value=253)
                    col_v2.number_input("Voltaje Mín. AC (V)", min_value=180, max_value=210, value=198)

                with sub_t3:
                    st.checkbox("Habilitar Carga desde la Red Eléctrica (Grid Charge)")
                    col_t1, col_t2 = st.columns(2)
                    col_t1.time_input("Inicio de carga forzada", value=datetime.strptime("00:00", "%H:%M"))
                    col_t2.time_input("Fin de carga forzada", value=datetime.strptime("05:00", "%H:%M"))
                    st.slider("SOC Objetivo para carga desde la red (%)", min_value=10, max_value=100, value=100)

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 Escribir Parámetros al Datalogger", use_container_width=True):
                    with st.spinner("Estableciendo conexión P2P con el inversor..."):
                        time.sleep(2)
                    st.success("¡Parámetros actualizados exitosamente!")

        with tab_reportes:
            st.markdown("### 📄 Descarga de Datos en Bruto")
            st.write("Exporte las métricas del día actual para auditoría o informes al cliente.")
            
            fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            datos_informe = {
                "Fecha Consulta": [fecha_hora_actual], "Planta": [d['nombre']],
                "Capacidad": [d['capacidad']], "Batería SOC (%)": [soc_actual],
                "Producción Diaria (kWh)": [prod_solar]
            }
            df_informe = pd.DataFrame(datos_informe)
            csv_data = df_informe.to_csv(index=False).encode('utf-8-sig') 
            
            st.download_button(
                label="📥 Descargar Informe CSV", data=csv_data, 
                file_name=f"Reporte_{d['nombre'].replace(' ', '_')}.csv", mime="text/csv"
            )

# ==========================================
# VENTANA 3: GESTIÓN DE PORTAFOLIO Y USUARIOS
# ==========================================
elif menu == "🏢 Gestión de Portafolio":
    st.title("🏢 CONFIGURACIÓN DE PROYECTOS")
    st.markdown("**Asistente de Puesta en Marcha - MOMISOLAR APP**")
    
    st.markdown("### 🛠️ Flujo de Creación y Autorización")

    with st.expander("1️⃣ Crear Proyecto (Añadir Planta)", expanded=False):
        st.write("Complete los datos técnicos del nuevo sistema solar.")
        with st.form("f_planta"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nombre de la Planta")
            n_tipo = c2.selectbox("Tipo de Planta", ["Residencial", "Comercial e Industrial", "Off-Grid"])
            
            c3, c4 = st.columns(2)
            n_ubi = c3.text_input("Ubicación (Ciudad/Región)")
            n_tz = c4.selectbox("Zona Horaria y Moneda", ["GMT-5 (Bogotá) - Moneda: COP", "GMT-5 (Lima) - Moneda: USD"])

            n_inv = c3.selectbox("Marca de Inversor", ["Deye", "GoodWe", "Fronius", "Huawei", "Growatt", "Must", "Sylvania"])
            n_cap = c4.text_input("Capacidad (kWp)")
            
            st.markdown("---")
            c5, c6 = st.columns(2)
            n_b_m = c5.selectbox("Marca de Batería", ["Ninguna", "Pylontech", "Deye", "BYD", "Trojan", "Sylvania"])
            n_b_t = c6.selectbox("Tecnología de Batería", ["Litio (LiFePO4)", "Plomo-Ácido", "AGM", "Gel"])
            
            if st.form_submit_button("💾 Crear Planta (createPlant)"):
                if n_nom:
                    guardar_planta({
                        "nombre": n_nom, "ubicacion": n_ubi, "capacidad": n_cap, 
                        "inversores": n_inv, "datalogger": "Pendiente", "bat_marca": n_b_m, "bat_tipo": n_b_t
                    })
                    st.success("Planta creada exitosamente en el Data Center local.")
                    st.rerun()

    with st.expander("2️⃣ Vincular Datalogger y Configurar Red", expanded=False):
        st.write("Asocie el hardware de comunicación a la planta creada.")
        if plantas_guardadas:
            p_sel = st.selectbox("Seleccione la Planta:", [p["nombre"] for p in plantas_guardadas])
            sn_logger = st.text_input("Número de Serie (SN) del Datalogger o QR:")
            
            st.markdown("#### Configuración Wi-Fi (Hotspot del Inversor)")
            cw1, cw2 = st.columns(2)
            cw1.text_input("SSID de la Red Local")
            cw2.text_input("Contraseña de la Red Local", type="password")
            
            if st.button("📡 Vincular y Conectar (bindDevice & connect)", use_container_width=True):
                with st.spinner("Conectando al hotspot... asignando DHCP y enlazando SN..."):
                    time.sleep(3)
                st.success(f"Datalogger {sn_logger} vinculado a la planta '{p_sel}'. Sincronización en curso.")
                st.info("Por favor espere de 5 a 10 minutos para la validación (fetchData).")
        else:
            st.warning("Cree una planta en el Paso 1 primero.")

    with st.expander("3️⃣ Compartir / Autorizar Planta (App Cliente)", expanded=False):
        st.write("Cree los accesos para que el usuario final visualice su sistema.")
        with st.form("f_usuario"):
            n_usr = st.text_input("Correo electrónico del Cliente")
            n_pwd = st.text_input("Contraseña de acceso temporal", type="password")
            
            if plantas_guardadas:
                p_auth = st.selectbox("Autorizar visualización de la Planta:", ["Todas (Rol Instalador/Admin)"] + [p["nombre"] for p in plantas_guardadas])
            else:
                p_auth = st.selectbox("Autorizar visualización de la Planta:", ["Ninguna disponible"])
                
            permiso = st.selectbox("Nivel de Permiso", ["Solo Lectura (Invitado)", "Edición y Control (Propietario)"])
            
            if st.form_submit_button("✉️ Autorizar y Enviar Acceso"):
                if n_usr and n_pwd:
                    guardar_usuario(n_usr, n_pwd)
                    st.success(f"Permisos asignados. El cliente '{n_usr}' ya puede iniciar sesión en MOMISOLAR APP.")
                    time.sleep(2) 
                    st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Directorio de Plantas Activas")
    
    for i, pl in enumerate(plantas_guardadas):
        col_info, col_btn = st.columns([5, 1]) 
        with col_info:
            st.markdown(f"<div style='background: white; color: black; padding: 10px; border-radius: 5px;'><b>{pl['nombre']}</b> | {pl['ubicacion']} | Inversor: {pl['inversores']}</div>", unsafe_allow_html=True)
        with col_btn:
            if st.button("🗑️", key=f"del_btn_{i}", help="Borrar planta"):
                eliminar_planta(i)
                st.rerun()

# ==========================================
# VENTANA 4: CENTRO DE ALERTAS
# ==========================================
elif menu == "🚨 Centro de Alertas":
    st.title("🚨 CENTRO DE ALERTAS Y DIAGNÓSTICO")
    st.markdown("**Monitor de fallos y notificaciones - MOMISOLAR APP**")
    
    if not plantas_guardadas:
        st.info("No hay plantas registradas para monitorear.")
    else:
        alertas_totales = 0
        
        for pl in plantas_guardadas:
            datos = obtener_datos_reales(pl)
            
            if datos.get("alertas"):
                st.markdown(f"### 📍 Proyecto: {pl['nombre']} ({pl['ubicacion']})")
                for alerta in datos["alertas"]:
                    alertas_totales += 1
                    if "Batería" in alerta:
                        st.warning(alerta)
                    elif "Red" in alerta:
                        st.error(alerta)
        
        st.markdown("---")
        if alertas_totales == 0:
            st.success("✅ Excelente. Todos los sistemas están operando con normalidad. No hay alarmas activas en la red MQTT.")
        else:
            st.info(f"Se detectaron {alertas_totales} alerta(s) activa(s). Se recomienda revisar el histórico del inversor o contactar al fabricante.")
            if st.button("🔄 Refrescar Estado de Red"):
                st.rerun()
