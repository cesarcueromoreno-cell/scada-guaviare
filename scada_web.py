import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y SEGURIDAD (LOGIN)
# ==========================================
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="centered")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔒 CENTRAL GESTION DE PLANTAS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>CV INGENIERIA SAS</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Ingrese sus credenciales para acceder al panel de control.</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    col_vacia1, col_centro, col_vacia2 = st.columns([1, 2, 1]) 
    
    with col_centro:
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario")
            contrasena = st.text_input("🔑 Contraseña", type="password") 
            submit_login = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit_login:
                if usuario == "admin" and contrasena == "solar123":
                    st.session_state["autenticado"] = True
                    st.rerun() 
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
    st.stop() 

# ==========================================
# 2. BASE DE DATOS Y MOTOR SOLAR
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        plantas_iniciales = [{
            "nombre": "Planta Principal", "ubicacion": "San José del Guaviare", 
            "capacidad": "13.92 kWp", "inversores": "Fronius + GoodWe", 
            "datalogger": "SN: 240.123456", "bat_marca": "GoodWe Lynx", "bat_tipo": "Litio (LiFePO4)"
        }]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas_iniciales, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

def guardar_planta(nueva_planta):
    plantas = cargar_plantas()
    plantas.append(nueva_planta)
    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)

plantas_guardadas = cargar_plantas()

def generar_curva_solar(nombre_planta):
    random.seed(nombre_planta) 
    pico_max = random.randint(4000, 15000) 
    horas = [f"{h:02d}:00" for h in range(6, 19)] 
    energia = [max(0, int(pico_max * math.sin(math.pi * (h - 6) / 12) + random.randint(-400, 400))) for h in range(6, 19)]
    random.seed() 
    return pd.DataFrame({"Hora": horas, "Generación (W)": energia}).set_index("Hora")

# ==========================================
# 3. MENÚ LATERAL
# ==========================================
st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["📊 Monitoreo en Vivo", "🏢 Gestión de Plantas"])
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()
st.sidebar.info("Plataforma Oficial \n**CV INGENIERIA SAS**")

# ==========================================
# VENTANA 1: MONITOREO (INTERFAZ REALISTA)
# ==========================================
if menu == "📊 Monitoreo en Vivo":
    st.title("⚡ CENTRAL GESTION DE PLANTAS")
    st.markdown("**CV INGENIERIA SAS**")
    
    planta_sel = st.selectbox("Seleccione planta:", [p["nombre"] for p in plantas_guardadas])
    det = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
    dl_info = det.get("datalogger", "No registrado")
    
    st.markdown(f"📍 {det['ubicacion']} | ⚡ {det['capacidad']} | 📡 DL: `{dl_info}`")
    st.markdown(f"🔋 **Batería:** {det.get('bat_marca','N/A')} ({det.get('bat_tipo','N/A')})")
    st.markdown("---")

    st.markdown("### 📈 Curva de Generación Diaria")
    datos_h = generar_curva_solar(planta_sel)
    st.area_chart(datos_h, color="#f1c40f")

    # Cálculos para diagrama en tiempo real
    pot_solar = max(0, datos_h.iloc[-1]["Generación (W)"] + random.randint(-100, 100))
    pot_load = 1800 + random.randint(-50, 50)
    pot_bat = pot_solar - pot_load
    soc = random.randint(40, 100)

    st.markdown("### 🔄 Flujo de Energía en Tiempo Real (Realista)")
    
    # LA MAGIA VISUAL: Código SVG actualizado con imágenes realistas
    diagrama_svg = f"""
    <div style="background-color: #f9f9f9; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 500px; margin: auto; font-family: sans-serif;">
        <svg viewBox="0 0 400 350" width="100%" height="100%">
            <defs>
                <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
                    <feDropShadow dx="1" dy="1" stdDeviation="1" flood-color="#ccc"/>
                </filter>
            </defs>

            <path d="M 100 80 V 150 H 170" fill="none" stroke="#e0e0e0" stroke-width="4" stroke-linecap="round"/>
            <path d="M 300 80 V 150 H 230" fill="none" stroke="#e0e0e0" stroke-width="4" stroke-linecap="round"/>
            <path d="M 170 150 H 100 V 230" fill="none" stroke="#e0e0e0" stroke-width="4" stroke-linecap="round"/>
            <path d="M 230 150 H 300 V 230" fill="none" stroke="#e0e0e0" stroke-width="4" stroke-linecap="round"/>
            
            <circle r="6" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 80 V 150 H 170" /></circle>
            <circle r="6" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>
            <circle r="6" fill="#e67e22"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 230" /></circle>
            
            <rect x="165" y="115" width="70" height="70" rx="10" fill="white" stroke="#1f77b4" stroke-width="2" filter="url(#shadow)"/>
            <image href="https://img.icons8.com/fluency/96/inverter.png" x="175" y="125" height="50" width="50"/>

            <rect x="30" y="20" width="140" height="80" rx="10" fill="white" stroke="#eee" stroke-width="2" filter="url(#shadow)"/>
            <image href="https://img.icons8.com/color/144/solar-panel.png" x="40" y="30" height="60" width="60"/>
            <text x="110" y="55" font-size="12" fill="#7f8c8d" font-weight="bold">FV Total</text>
            <text x="110" y="75" font-size="16" font-weight="bold">{pot_solar} W</text>
            
            <rect x="230" y="20" width="140" height="80" rx="10" fill="white" stroke="#eee" stroke-width="2" filter="url(#shadow)"/>
            <image href="https://img.icons8.com/external-flaticons-flat-flat-icons/128/external-power-plant-energy-plant-external-flaticons-flat-flat-icons.png" x="240" y="30" height="60" width="60"/>
            <text x="310" y="55" font-size="12" fill="#7f8c8d" font-weight="bold">Red</text>
            <text x="310" y="75" font-size="16" font-weight="bold">0 W</text>

            <rect x="30" y="230" width="140" height="80" rx="10" fill="white" stroke="#eee" stroke-width="2" filter="url(#shadow)"/>
            <image href="https://img.icons8.com/external-kiranshastry-solid-kiranshastry/128/external-battery-battery-and-charging-kiranshastry-solid-kiranshastry-3.png" x="40" y="240" height="60" width="60"/>
            <text x="110" y="260" font-size="12" fill="#7f8c8d" font-weight="bold">Batería ({soc}%)</text>
            <text x="110" y="280" font-size="16" font-weight="bold" fill="#2ecc71">{pot_bat} W</text>
            
            <rect x="230" y="230" width="140" height="80" rx="10" fill="white" stroke="#eee" stroke-width="2" filter="url(#shadow)"/>
            <image href="https://img.icons8.com/fluency/144/cottage.png" x="240" y="240" height="60" width="60"/>
            <text x="310" y="260" font-size="12" fill="#7f8c8d" font-weight="bold">Carga (Casa)</text>
            <text x="310" y="280" font-size="16" font-weight="bold" fill="#e67e22">{pot_load} W</text>
            
        </svg>
    </div>
    """
    
    # RENDERIZADO DE LA WEB CON ALTURA AJUSTADA
    components.html(diagrama_svg, height=520) 
    
    if st.button("🔄 Refrescar Lecturas"):
        st.rerun()

# ==========================================
# VENTANA 2: GESTIÓN DE PROYECTOS
# ==========================================
else:
    st.title("🏢 Gestión de Proyectos")
    st.markdown("**CV INGENIERIA SAS - Directorio**")
    
    with st.expander("➕ Registrar Nueva Planta", expanded=False):
        with st.form("f_planta"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nombre Proyecto")
            n_cap = c1.text_input("Capacidad (kWp)")
            n_ubi = c2.text_input("Ubicación")
            
            # LISTA SEGURA HACIA ABAJO
            n_inv = c2.selectbox(
                "Inversor", 
                [
                    "Fronius", 
                    "GoodWe", 
                    "Huawei", 
                    "Deye", 
                    "Growatt", 
                    "Híbrido Multimarca",
                    "Otro"
                ]
            )
            
            st.markdown("##### 🔋 Configuración de Batería")
            c3, c4 = st.columns(2)
            # LISTA SEGURA HACIA ABAJO
            n_b_m = c3.selectbox(
                "Marca Batería", 
                [
                    "Ninguna (On-Grid)", 
                    "Pylontech", 
                    "Deye", 
                    "GoodWe", 
                    "BYD", 
                    "Trojan", 
                    "Genérica",
                    "Otra"
                ]
            )
            # LISTA SEGURA HACIA ABAJO
            n_b_t = c4.selectbox(
                "Tecnología", 
                [
                    "No aplica", 
                    "Litio (LiFePO4)", 
                    "Plomo-Ácido", 
                    "AGM", 
                    "Gel", 
                    "Ion-Litio"
                ]
            )
            
            n_dl = st.text_input("📡 Datalogger (SN / IP / MAC)")
            
            if st.form_submit_button("💾 Guardar Planta"):
                if n_nom:
                    guardar_planta({
                        "nombre": n_nom, "ubicacion": n_ubi, "capacidad": n_cap, 
                        "inversores": n_inv, "datalogger": n_dl, 
                        "bat_marca": n_b_m, "bat_tipo": n_b_t
                    })
                    st.success("¡Planta registrada con éxito!")
                    st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Listado de Plantas Activas")
    for pl in plantas_guardadas:
        dl = pl.get("datalogger", "No registrado")
        b_marca = pl.get("bat_marca", "Ninguna")
        b_tipo = pl.get("bat_tipo", "N/A")
        
        texto_tarjeta = f"""**{pl['nombre']}** | 📍 {pl['ubicacion']} | ⚡ Capacidad: {pl['capacidad']}
        🎛️ Inversor: {pl['inversores']} | 📡 DL: `{dl}`
        🔋 Baterías: {b_marca} ({b_tipo})"""
        
        st.info(texto_tarjeta)
