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
# 1. CONFIGURACIÓN INICIAL Y FONDO
# ==========================================
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="wide") 

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=1920");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    [data-testid="stAppViewBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 15px; padding: 2rem; margin-top: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .tarjeta-planta {
        background-color: #ffffff; border-left: 5px solid #2ecc71;
        padding: 15px; border-radius: 8px; margin-bottom: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .tarjeta-titulo { color: #2c3e50; font-size: 18px; font-weight: bold; margin-bottom: 10px; }
    .tarjeta-dato { font-size: 22px; font-weight: bold; color: #34495e; }
    .tarjeta-label { font-size: 12px; color: #7f8c8d; text-transform: uppercase; }
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
        with open(ARCHIVO_USUARIOS, 'w') as f: json.dump({"admin": "solar123"}, f)
    with open(ARCHIVO_USUARIOS, 'r') as f: return json.load(f)

def guardar_usuario(usuario, contrasena):
    usuarios = cargar_usuarios()
    usuarios[usuario] = contrasena
    with open(ARCHIVO_USUARIOS, 'w') as f: json.dump(usuarios, f)

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [{"nombre": "Planta Principal", "ubicacion": "Guaviare", "capacidad": "13.92 kWp", "inversores": "Híbrido Multimarca", "datalogger": "SN: CV-001", "bat_marca": "Deye/Pylontech", "bat_tipo": "Litio (LiFePO4)"}]
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
    st.markdown("<h1 style='text-align: center;'>🔒 CENTRAL GESTIÓN DE PLANTAS</h1>", unsafe_allow_html=True)
    col1, col_centro, col2 = st.columns([1, 2, 1]) 
    with col_centro:
        with st.form("login_form"):
            usuario_input = st.text_input("👤 Usuario")
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

# --- MOTOR DE INTEGRACIÓN SOLARMAN ---
SOLARMAN_APP_ID = "TU_APP_ID_AQUI"
SOLARMAN_APP_SECRET = "TU_APP_SECRET_AQUI"
SOLARMAN_EMAIL = "tu_correo@cvingenieria.com"
SOLARMAN_PASSWORD = "tu_password"

def obtener_token_solarman():
    return None

def obtener_datos_reales(planta):
    cap_texto = str(planta.get("capacidad", "5"))
    solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
    try: cap_val = float(solo_numeros[0]) * 1000 if solo_numeros else 5000 
    except: cap_val = 5000 
    
    pot_simulada = int(cap_val * random.uniform(0.1, 0.8))
    energia_simulada = round((pot_simulada * random.uniform(3.5, 5.0)) / 1000, 1)
    estado = "Simulado (Falta configurar API)" if planta.get("inversores") == "Deye" else "Simulado"

    return {
        "solar": pot_simulada,
        "casa": 1750 + random.randint(-40, 40),
        "soc": random.randint(50, 99),
        "energia_diaria": energia_simulada,
        "status": estado
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
st.sidebar.title("Navegación CV")
st.sidebar.write(f"👤 Bienvenido, **{st.session_state.get('usuario_actual', 'admin')}**")

menu = st.sidebar.radio("Ir a:", ["🌐 Panorama General", "📊 Monitoreo Detallado", "🏢 Gestión de Portafolio"])

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()
st.sidebar.info("**CV INGENIERIA SAS**")

# ==========================================
# VENTANA 1: PANORAMA GENERAL
# ==========================================
if menu == "🌐 Panorama General":
    st.title("🌐 PANORAMA GENERAL DEL PORTAFOLIO")
    st.markdown("**Vista global rápida - CV INGENIERIA SAS**")
    
    if not plantas_guardadas:
        st.warning("No hay plantas registradas. Ve a Gestión para agregar una.")
    else:
        for i, pl in enumerate(plantas_guardadas):
            datos = obtener_datos_reales(pl)
            cap_texto = str(pl.get("capacidad", "0"))
            solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
            cap_limpia = f"{solo_numeros[0]} kWp" if solo_numeros else "N/A"

            tarjeta = f"""
            <div class="tarjeta-planta">
                <div class="tarjeta-titulo">{pl['nombre']} <span style="float:right; font-size:12px; color:#95a5a6;">{datos['status']}</span></div>
                <div style="display: flex; justify-content: space-between; text-align: center; margin-top: 15px;">
                    <div><div class="tarjeta-dato">{datos['solar']} W</div><div class="tarjeta-label">Energía (Potencia)</div></div>
                    <div><div class="tarjeta-dato">{datos['energia_diaria']} kWh</div><div class="tarjeta-label">Producción Diaria</div></div>
                    <div><div class="tarjeta-dato">{cap_limpia}</div><div class="tarjeta-label">Capacidad Total</div></div>
                </div>
            </div>
            """
            st.markdown(tarjeta, unsafe_allow_html=True)
            
            with st.expander(f"📉 Ver gráfica de comportamiento: {pl['nombre']}", expanded=False):
                df_historico = simular_historico_24h(pl)
                fig = px.area(df_historico, x="timestamp", y=["Generación FV", "Consumo Carga"], color_discrete_map={"Generación FV": "#e67e22", "Consumo Carga": "#e74c3c"})
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text=None, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis=dict(tickformat="%H:%M"), yaxis_title="Potencia (kW)", margin=dict(l=20, r=20, t=10, b=20), height=300)
                fig.update_traces(fill='tozeroy', mode='lines', line=dict(width=2))
                fig.update_traces(selector=dict(name="Consumo Carga"), fill='none')
                st.plotly_chart(fig, use_container_width=True, key=f"graf_pan_{i}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            
        if st.button("🔄 Actualizar Todo"): st.rerun()

# ==========================================
# VENTANA 2: MONITOREO DETALLADO Y REPORTE
# ==========================================
elif menu == "📊 Monitoreo Detallado":
    st.title("📊 MONITOREO DETALLADO POR PLANTA")
    st.markdown("**Analiza el comportamiento individual - CV INGENIERIA SAS**")
    
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

        diagrama_svg = f"""
        <div style="background: transparent; padding: 20px; width: 100%; max-width: 500px; margin: auto; font-family: sans-serif;">
            <svg viewBox="0 0 400 350" width="100%">
                <path d="M 100 85 V 150 H 170 M 300 85 V 150 H 230 M 170 150 H 100 V 230 M 230 150 H 300 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
                <circle r="6" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 85 V 150 H 170" /></circle>
                <circle r="6" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>
                <circle r="6" fill="#e67e22"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 230" /></circle>
                <rect x="165" y="115" width="70" height="70" rx="12" fill="#ffffff" stroke="#3498db" stroke-width="3"/>
                <rect x="175" y="125" width="50" height="25" rx="3" fill="#2c3e50"/> <text x="200" y="142" text-anchor="middle" font-size="8" fill="#55efc4" font-weight="bold">CV-ENG</text>
                <text x="200" y="200" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">Híbrido</text>
                <g transform="translate(30,20)"><rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/><rect x="10" y="10" width="45" height="65" fill="#1a237e" rx="2"/><text x="65" y="35" font-size="11" fill="#636e72" font-weight="bold">FV TOTAL</text><text x="65" y="65" font-size="18" font-weight="bold" fill="#2d3436">{pot_solar} W</text></g>
                <g transform="translate(230,20)"><rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/><text x="65" y="35" font-size="11" fill="#636e72" font-weight="bold">RED ELÉC.</text><text x="65" y="65" font-size="18" font-weight="bold" fill="#d63031">0 W</text></g>
                <g transform="translate(30,230)"><rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/><rect x="10" y="10" width="45" height="65" rx="4" fill="#636e72"/><text x="32" y="67" text-anchor="middle" font-size="10" font-weight="bold" fill="{color_bat}">{soc}%</text><text x="65" y="35" font-size="11" fill="#636e72" font-weight="bold">BATERÍA</text><text x="65" y="65" font-size="18" font-weight="bold" fill="#27ae60">{pot_bat} W</text></g>
                <g transform="translate(230,230)"><rect width="140" height="85" rx="12" fill="white" stroke="#f1f2f6" stroke-width="1"/><text x="75" y="35" font-size="11" fill="#636e72" font-weight="bold">CARGA</text><text x="75" y="65" font-size="18" font-weight="bold" fill="#e67e22">{pot_casa} W</text></g>
            </svg>
        </div>
        """
        components.html(diagrama_svg, height=520) 
        
        st.markdown("---")
        st.markdown("### 📉 Comportamiento de Generación Vs. Consumo (Hoy)")
        
        df_historico = simular_historico_24h(d)
        fig2 = px.area(df_historico, x="timestamp", y=["Generación FV", "Consumo Carga"], color_discrete_map={"Generación FV": "#e67e22", "Consumo Carga": "#e74c3c"})
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title_text=None, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis=dict(tickformat="%H:%M", dtick=2 * 3600000), yaxis_title="Potencia (kW)", margin=dict(l=20, r=20, t=20, b=20))
        fig2.update_traces(fill='tozeroy', mode='lines', line=dict(width=2))
        fig2.update_traces(selector=dict(name="Consumo Carga"), fill='none')
        st.plotly_chart(fig2, use_container_width=True, key="graf_monitoreo_principal")

        # --- NUEVA FUNCIÓN: DESCARGA DE INFORME ---
        st.markdown("---")
        st.markdown("### 📄 Exportar Datos")
        
        # Preparamos los datos estructurados para Excel
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datos_informe = {
            "Fecha/Hora Consulta": [fecha_hora_actual],
            "Nombre de Planta": [d['nombre']],
            "Ubicación": [d['ubicacion']],
            "Capacidad (kWp)": [d['capacidad']],
            "Marca Inversor": [d['inversores']],
            "Batería": [f"{d.get('bat_marca','N/A')} ({d.get('bat_tipo','N/A')})"],
            "Estado Conexión": [datos_act['status']],
            "Generación FV Actual (W)": [pot_solar],
            "Consumo Carga Actual (W)": [pot_casa],
            "Nivel Batería SOC (%)": [soc],
            "Producción Diaria (kWh)": [datos_act['energia_diaria']]
        }
        
        # Convertimos a formato CSV para descargar
        df_informe = pd.DataFrame(datos_informe)
        csv_data = df_informe.to_csv(index=False).encode('utf-8-sig') # utf-8-sig ayuda a Excel a leer las tildes
        
        nombre_archivo = f"Reporte_Planta_{d['nombre'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        
        st.download_button(
            label="📥 Descargar Informe Técnico (CSV / Excel)",
            data=csv_data,
            file_name=nombre_archivo,
            mime="text/csv",
            use_container_width
