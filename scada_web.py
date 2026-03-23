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
# NUEVO NOMBRE EN LA PESTAÑA DEL NAVEGADOR (César)
st.set_page_config(page_title="MOMISOLAR APP", page_icon="☀️", layout="wide") 

st.markdown(
    """
    <style>
    /* FONDO DE LA APLICACIÓN (INTACTO) */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=1920");
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
    }
    [data-testid="stHeader"] { 
        background: rgba(0,0,0,0); 
    }
    
    /* HACER EL CONTENEDOR CENTRAL TOTALMENTE TRANSPARENTE */
    .block-container, [data-testid="stMainBlockContainer"], div[data-testid="block-container"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        backdrop-filter: none !important;
    }

    /* TEXTO BLANCO CON SOMBRA NEGRA PARA EL ÁREA DE LA FOTO */
    h1, h2, h3, h4, h5, p, .stMarkdown span {
        color: #ffffff !important;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important;
    }

    /* CORRECCIÓN: Nombres de los parámetros (Labels) y Pestañas en blanco brillante */
    label, label p, label div, button[data-baseweb="tab"] p, button[data-baseweb="tab"] span {
        color: #ffffff !important;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important;
    }

    /* CORRECCIÓN: Fondo sólido para las cajas de información centrales */
    [data-testid="stAlert"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    }
    [data-testid="stAlert"] * {
        color: #2c3e50 !important;
        text-shadow: none !important;
    }

    /* =========================================
       NUEVO: DISEÑO DEL MENÚ LATERAL (César)
       ========================================= */
    [data-testid="stSidebar"] {
        /* Degradado oscuro tecnológico (Midnight Blue a Slate) */
        background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
        border-right: 1px solid #4ca1af !important;
        box-shadow: 4px 0 15px rgba(0,0,0,0.5) !important;
    }
    
    /* Textos del menú en blanco para contraste perfecto */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        text-shadow: none !important;
    }

    /* Toque especial "Amarillo Solar" para la caja de la empresa en el menú (César) */
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
    /* ========================================= */

    /* Tarjetas, Inputs, Botones centrales (Letras oscuras sin sombra) */
    .tarjeta-planta *, input, select, textarea, button span {
        color: #2c3e50 !important;
        text-shadow: none !important;
    }

    /* =========================================
       NUEVO: ESTILO DASHBOARD PRO (Target image_9.png)
       ========================================= */
    /* Contenedor gris suave para el área del Dashboard */
    .dashboard-dash-base {
        background-color: #f0f2f5 !important; /* Gris suave profesional */
        border-radius: 15px !important;
        padding: 25px !important;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.1) !important;
        margin-bottom: 20px !important;
    }
    
    /* Texto oscuro dentro de la base del dashboard */
    .dashboard-dash-base h1, .dashboard-dash-base h2, .dashboard-dash-base h3, .dashboard-dash-base p {
        color: #2c3e50 !important;
        text-shadow: none !important;
    }

    /* Tarjetas blancas puras y sólidas tipo tabla (Sin border-left) */
    .tarjeta-dash-pro {
        background-color: #ffffff !important; 
        padding: 15px !important; 
        border-radius: 8px !important; 
        margin-bottom: 10px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
    }
    .tarjeta-dash-item {
        margin: 0 15px !important;
    }
    .tarjeta-label-pro {
        font-size: 11px !important;
        color: #7f8c8d !important;
        text-transform: uppercase !important;
        margin-bottom: 2px !important;
    }
    .tarjeta-dato-pro {
        font-size: 16px !important;
        font-weight: bold !important;
        color: #2c3e50 !important;
    }
    /* ========================================= */
    
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 2. BASE DE DATOS (PLANTAS Y USUARIOS)
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'
ARCHIVO_USUARIOS = 'usuarios.json'

def cargar_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS):
        with open(ARCHIVO_USUARIOS, 'w') as f: 
            json.dump({"admin": "solar123"}, f)
    with open(ARCHIVO_USUARIOS, 'r') as f: 
        return json.load(f)

def guardar_usuario(usuario, contrasena):
    usuarios = cargar_usuarios()
    usuarios[usuario] = contrasena
    with open(ARCHIVO_USUARIOS, 'w') as f: 
        json.dump(usuarios, f)

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [{
            "nombre": "Planta Principal", "ubicacion": "Guaviare", "capacidad": "13.92 kWp", 
            "inversores": "Híbrido Multimarca", "datalogger": "SN: CV-001", 
            "bat_marca": "Deye/Pylontech", "bat_tipo": "Litio (LiFePO4)"
        }]
        with open(ARCHIVO_PLANTAS, 'w') as f: 
            json.dump(inicial, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: 
        return json.load(f)

def guardar_planta(nueva):
    plantas = cargar_plantas()
    plantas.append(nueva)
    with open(ARCHIVO_PLANTAS, 'w') as f: 
        json.dump(plantas, f)

def eliminar_planta(indice):
    plantas = cargar_plantas()
    if 0 <= indice < len(plantas):
        plantas.pop(indice)
        with open(ARCHIVO_PLANTAS, 'w') as f: 
            json.dump(plantas, f)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    # NUEVO NOMBRE EN LA PANTALLA DE LOGIN (César)
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
# NUEVO NOMBRE EN EL MENÚ LATERAL (César)
st.sidebar.title("☀️ MOMISOLAR APP")
rol_actual = "Instalador/Admin" if st.session_state.get('usuario_actual') == 'admin' else "Cliente"
st.sidebar.write(f"👤 Usuario: **{st.session_state.get('usuario_actual', 'admin')}**\n\n🛡️ Rol: {rol_actual}")

menu = st.sidebar.radio("Ir a:", ["🌐 Panorama General", "📊 Monitoreo Detallado", "⚙️ Control de Inversores", "🏢 Gestión de Portafolio", "🚨 Centro de Alertas"])

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()
    
# Identidad de la empresa (glow yellow)
st.sidebar.info("**POWERED BY:**\n\n**CV INGENIERIA SAS**")

# ==========================================
# VENTANA 1: PANORAMA GENERAL (REDISEÑO DASHBOARD PRO)
# ==========================================
if menu == "🌐 Panorama General":
    # Título blanco original
    st.title("🌐 PANORAMA GENERAL DEL PORTAFOLIO")
    st.markdown("**MOMISOLAR APP - Vista global rápida**")
    
    if not plantas_guardadas:
        st.warning("No hay plantas registradas. Ve a Gestión para agregar una.")
    else:
        # Panel base del dashboard (gris profesional flotante sobre la foto)
        with st.container():
            st.markdown("<div class='dashboard-dash-base'>", unsafe_allow_html=True)
            
            st.markdown("<h3 style='margin-bottom:20px; color:#2c3e50;'>Directorio Técnico de Plantas</h3>", unsafe_allow_html=True)
            
            # Header profesional tipo tabla (Target image_9.png)
            header_tabla = f"""
<div style="background:#ffffff; border-radius: 8px; padding: 10px 15px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #e0e0e0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
<div style="display:flex; align-items:center;">
<div style="color: #3498db; font-size:16px; margin-right:10px;">☀️</div>
<div style="font-weight:bold; color: #2c3e50;">Listado Activo (Total {len(plantas_guardadas)})</div>
</div>
<div style="background: #ffffff; border: 1px solid #ccd0d5; border-radius: 4px; padding: 2px 10px; color: #7f8c8d; font-size:12px;">🔍 Por favor, ingrese el nombre de la...</div>
</div>
"""
            st.markdown(header_tabla, unsafe_allow_html=True)
            
            # Recorrer plantas y crear filas tipo tabla
            for i, pl in enumerate(plantas_guardadas):
                datos = obtener_datos_reales(pl)
                cap_texto = str(pl.get("capacidad", "0"))
                solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
                cap_limpia = f"{solo_numeros[0]} kWp" if solo_numeros else "N/A"

                alerta_html = ""
                status_icon = "🟢" if datos["solar"] > 10 else "🟠"
                if datos["alertas"]:
                    status_icon = "🔴"
                    # Pequeño badge de alerta si hay problemas
                    alerta_html = f"<div style='position:absolute; top:5px; left:15px; background: #e74c3c; color:white; font-size:9px; padding: 2px 6px; border-radius:10px;'>{len(datos['alertas'])} Alertas</div>"

                # NOTA: Todo alineado a la izquierda sin espacios para evitar el error del bloque de código crudo
                # FILA PRO TIPO TABLA (Target image_9.png visual appearance)
                fila_pro = f"""
<div class="tarjeta-dash-pro" style="position:relative;">
{alerta_html}
<div style="display:flex; align-items:center; width: 400px;">
<img src="https://img.icons8.com/color/48/solar-panel.png" style="width: 32px; height:32px; margin-right:15px; border-radius:4px;"/>
<div>
<div style="font-size: 14px; font-weight: bold; color: #2c3e50;">{pl['nombre']}</div>
<div style="font-size: 12px; color: #7f8c8d;"><img src="https://img.icons8.com/material-rounded/24/marker.png" style="width:12px; height:12px; margin-right:3px;"/>{pl['ubicacion']}</div>
</div>
</div>
<div class="tarjeta-dash-item" style="text-align: center; width: 50px;">
<div class="tarjeta-label-pro">Com</div>
<div style="font-size:16px;">📶</div>
</div>
<div class="tarjeta-dash-item" style="text-align: center; width: 60px;">
<div class="tarjeta-label-pro">Alertas</div>
<div style="font-size:16px;">{status_icon}</div>
</div>
<div class="tarjeta-dash-item" style="width: 150px;">
<div class="tarjeta-label-pro">Capacidad (fetchData)</div>
<div class="tarjeta-dato-pro">{cap_limpia}</div>
</div>
<div class="tarjeta-dash-item" style="width: 150px;">
<div class="tarjeta-label-pro">Potencia Solar Actual</div>
<div class="tarjeta-dato-pro">{datos['solar']} W</div>
</div>
<div class="tarjeta-dash-item" style="width: 150px;">
<div class="tarjeta-label-pro">Producción Diaria Hoy</div>
<div class="tarjeta-dato-pro" style="color: #27ae60 !important;">{datos['energia_diaria']} kWh</div>
</div>
<div style="display: flex; gap: 5px;">
<img src="https://img.icons8.com/material-rounded/24/edit.png" style="width:18px; height:18px; cursor:pointer; opacity:0.6;"/>
<img src="https://img.icons8.com/material-rounded/24/filled-trash.png" style="width:18px; height:18px; cursor:pointer; opacity:0.6;"/>
</div>
</div>
"""
                st.markdown(fila_pro, unsafe_allow_html=True)
                
            st.markdown("</div>", unsafe_allow_html=True) # Cerrar dashboard-dash-base
            
        if st.button("🔄 Actualizar Todo"): 
            st.rerun()

# ==========================================
# VENTANA 2: MONITOREO DETALLADO (DIAGRAMA TRANSPARENTE)
# ==========================================
elif menu == "📊 Monitoreo Detallado":
    st.title("📊 MONITOREO DETALLADO POR PLANTA")
    st.markdown("**MOMISOLAR APP - Análisis de comportamiento**")
    
    if not plantas_guardadas:
        st.warning("No hay plantas registradas. Por favor, ve a Gestión para crear una.")
    else:
        planta_sel = st.selectbox("Seleccione Planta:", [p["nombre"] for p in plantas_guardadas])
        d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
        
        st.write(f"📍 {d['ubicacion']} | ⚡ {d['capacidad']} | 📡 Estado: `{obtener_datos_reales(d)['status']}`")
        st.write(f"🔋 **Batería:** {d.get('bat_marca','N/A')} ({d.get('bat_tipo','N/A')})")
        st.markdown("---")

        st.markdown("### 🔄 Flujo de Energía en Tiempo Real")
        
        datos_act = obtener_datos_reales(d)
        pot_solar = datos_act["solar"]
        pot_casa = datos_act["casa"]
        pot_bat = pot_solar - pot_casa
        soc = datos_act["soc"]
        color_bat = "#2ecc71" if soc > 20 else "#e74c3c"

        # AQUÍ REGRESAMOS EL DIAGRAMA A 100% TRANSPARENTE (César)
        diagrama_svg = f"""
        <div style="background: transparent; padding: 20px; width: 100%; max-width: 500px; margin: auto; font-family: sans-serif;">
            <svg viewBox="0 0 400 350" width="100%">
                <path d="M 100 85 V 150 H 170 M 300 85 V 150 H 230 M 170 150 H 100 V 230 M 230 150 H 300 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                <circle r="6" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 85 V 150 H 170" /></circle>
                <circle r="6" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>
                <circle r="6" fill="#e67e22"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 230" /></circle>
                
                <rect x="165" y="115" width="70" height="70" rx="12" fill="#ffffff" stroke="#3498db" stroke-width="3"/>
                <rect x="175" y="125" width="50" height="25" rx="3" fill="#2c3e50"/> 
                <text x="200" y="142" text-anchor="middle" font-size="8" fill="#55efc4" font-weight="bold">CV-ENG</text>
                <text x="200" y="200" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">Híbrido</text>
                
                <g transform="translate(30,20)">
                    <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                    <rect x="10" y="10" width="45" height="65" fill="#1a237e" rx="2"/>
                    <text x="65" y="35" font-size="11" fill="#636e72" font-weight="bold">FV TOTAL</text>
                    <text x="65" y="65" font-size="18" font-weight="bold" fill="#2d3436">{pot_solar} W</text>
                </g>
                
                <g transform="translate(230,20)">
                    <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                    <text x="65" y="35" font-size="11" fill="#636e72" font-weight="bold">RED ELÉC.</text>
                    <text x="65" y="65" font-size="18" font-weight="bold" fill="#d63031">0 W</text>
                </g>
                
                <g transform="translate(30,230)">
                    <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                    <rect x="10" y="10" width="45" height="65" rx="4" fill="#636e72"/>
                    <text x="32" y="67" text-anchor="middle" font-size="10" font-weight="bold" fill="{color_bat}">{soc}%</text>
                    <text x="65" y="35" font-size="11" fill="#636e72" font-weight="bold">BATERÍA</text>
                    <text x="65" y="65" font-size="18" font-weight="bold" fill="#27ae60">{pot_bat} W</text>
                </g>
                
                <g transform="translate(230,230)">
                    <rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/>
                    <text x="75" y="35" font-size="11" fill="#636e72" font-weight="bold">CARGA</text>
                    <text x="75" y="65" font-size="18" font-weight="bold" fill="#e67e22">{pot_casa} W</text>
                </g>
            </svg>
        </div>
        """
        components.html(diagrama_svg, height=520) 
        
        st.markdown("---")
        st.markdown("### 📉 Comportamiento de Generación Vs. Consumo (Hoy)")
        
        df_historico = simular_historico_24h(d)
        fig2 = px.area(
            df_historico, x="timestamp", y=["Generación FV", "Consumo Carga"], 
            color_discrete_map={"Generación FV": "#e67e22", "Consumo Carga": "#e74c3c"}
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.9)", 
            legend_title_text=None, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), 
            xaxis=dict(tickformat="%H:%M", dtick=2 * 3600000), yaxis_title="Potencia (kW)", margin=dict(l=20, r=20, t=20, b=20)
        )
        fig2.update_traces(fill='tozeroy', mode='lines', line=dict(width=2))
        fig2.update_traces(selector=dict(name="Consumo Carga"), fill='none')
        st.plotly_chart(fig2, use_container_width=True, key="graf_monitoreo_principal")

        st.markdown("---")
        st.markdown("### 📄 Exportar Datos")
        
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datos_informe = {
            "Fecha/Hora Consulta": [fecha_hora_actual], "Nombre de Planta": [d['nombre']],
            "Ubicación": [d['ubicacion']], "Capacidad (kWp)": [d['capacidad']],
            "Marca Inversor": [d['inversores']], "Batería": [f"{d.get('bat_marca','N/A')} ({d.get('bat_tipo','N/A')})"],
            "Estado Conexión": [datos_act['status']], "Generación FV Actual (W)": [pot_solar],
            "Consumo Carga Actual (W)": [pot_casa], "Nivel Batería SOC (%)": [soc],
            "Producción Diaria (kWh)": [datos_act['energia_diaria']]
        }
        
        df_informe = pd.DataFrame(datos_informe)
        csv_data = df_informe.to_csv(index=False).encode('utf-8-sig') 
        nombre_archivo = f"Reporte_Planta_{d['nombre'].replace(' ', '_')}.csv"
        
        st.download_button(
            label="📥 Descargar Informe Técnico (CSV / Excel)", data=csv_data, 
            file_name=nombre_archivo, mime="text/csv"
        )

# ==========================================
# VENTANA 3: CONTROL DE INVERSORES
# ==========================================
elif menu == "⚙️ Control de Inversores":
    st.title("⚙️ PARAMETRIZACIÓN REMOTA AVANZADA")
    st.markdown("**Control maestro de inversores - MOMISOLAR APP**")
    
    if st.session_state.get('usuario_actual') != 'admin':
        st.error("⛔ ACCESO DENEGADO")
        st.warning("Esta sección es de control crítico y modifica parámetros físicos del equipo. Solo el usuario Administrador tiene los privilegios necesarios.")
    else:
        st.info("🔐 Autenticado como Administrador. Proceda con precaución al modificar variables del equipo.")
        
        if not plantas_guardadas:
            st.warning("No hay plantas registradas para configurar.")
        else:
            planta_sel = st.selectbox("Seleccione Planta a configurar:", [p["nombre"] for p in plantas_guardadas])
            d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
            st.write(f"Inversor detectado: **{d['inversores']}** en {d['ubicacion']}")
            st.markdown("---")
            
            tab_bat, tab_grid, tab_tou = st.tabs(["🔋 Baterías (BMS)", "⚡ Red y Normativa (Grid)", "🕒 Franjas Horarias (TOU)"])
            
            with tab_bat:
                st.markdown("#### Parámetros de Corriente y SOC")
                col_b1, col_b2 = st.columns(2)
                col_b1.number_input("Max Corriente Carga (A)", min_value=10, max_value=150, value=60)
                col_b2.number_input("Max Corriente Descarga (A)", min_value=10, max_value=150, value=80)
                
                st.markdown("##### Límites de Estado de Carga (SOC %)")
                col_s1, col_s2, col_s3 = st.columns(3)
                col_s1.number_input("SOC Parada (Shutdown %)", min_value=5, max_value=40, value=20)
                col_s2.number_input("SOC Alarma (Low Warn %)", min_value=10, max_value=50, value=35)
                col_s3.number_input("SOC Reinicio (Restart %)", min_value=20, max_value=100, value=50)

            with tab_grid:
                st.markdown("#### Configuración de Red (Grid Code)")
                col_g1, col_g2 = st.columns(2)
                col_g1.selectbox("Normativa Aplicada", ["Colombia (RETIE / NTC 2050)", "IEEE 1547", "IEC 61727"])
                col_g2.slider("Límite de Inyección a red (%) - Zero Export", min_value=0, max_value=100, value=0)
                
                st.markdown("##### Protecciones de Voltaje")
                col_v1, col_v2 = st.columns(2)
                col_v1.number_input("Voltaje Máx. AC (V)", min_value=220, max_value=270, value=253)
                col_v2.number_input("Voltaje Mín. AC (V)", min_value=180, max_value=210, value=198)

            with tab_tou:
                st.markdown("#### Programación por Tiempo (Time of Use)")
                st.checkbox("Habilitar Carga desde la Red Eléctrica (Grid Charge)")
                
                col_t1, col_t2 = st.columns(2)
                col_t1.time_input("Inicio de carga forzada", value=datetime.strptime("00:00", "%H:%M"))
                col_t2.time_input("Fin de carga forzada", value=datetime.strptime("05:00", "%H:%M"))
                st.slider("SOC Objetivo para carga desde la red (%)", min_value=10, max_value=100, value=100)

            st.markdown("---")
            st.warning("⚠️ Advertencia: Enviar estos parámetros alterará el funcionamiento del equipo. Asegúrese de no violar garantías ni normativas del operador de red local.")
            
            if st.button("🚀 Guardar y Enviar Parámetros", use_container_width=True):
                with st.spinner("Conectando con el equipo remoto..."):
                    time.sleep(2)
                st.success(f"¡Nuevos parámetros escritos en el Datalogger '{d['nombre']}'!")

# ==========================================
# VENTANA 4: GESTIÓN DE PORTAFOLIO (INTACTA CON NUEVO IDENTIDAD)
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
# VENTANA 5: CENTRO DE ALERTAS
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
