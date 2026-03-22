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
# 2. BASE DE DATOS Y MOTOR MATEMÁTICO SOLAR
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        # Actualizamos la planta por defecto con los nuevos datos de batería
        plantas_iniciales = [{
            "nombre": "Planta Principal", 
            "ubicacion": "San José del Guaviare", 
            "capacidad": "13.92 kWp", 
            "inversores": "Fronius + GoodWe", 
            "datalogger": "SN: 240.123456 / IP: 192.168.1.15",
            "bat_marca": "GoodWe Lynx Home U",
            "bat_tipo": "Litio (LiFePO4)"
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
    pico_maximo = random.randint(4000, 15000) 
    horas = [f"{h:02d}:00" for h in range(6, 19)] 
    energia = []
    for h in range(6, 19):
        porcentaje_sol = math.sin(math.pi * (h - 6) / 12)
        energia.append(max(0, int(pico_maximo * porcentaje_sol + random.randint(-400, 400)))) 
    random.seed() 
    return pd.DataFrame({"Hora": horas, "Generación (W)": energia}).set_index("Hora")

# ==========================================
# 3. MENÚ LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["📊 Monitoreo en Vivo", "🏢 Gestión de Plantas"])
st.sidebar.markdown("---")

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()

st.sidebar.info("Plataforma Oficial \n**CV INGENIERIA SAS**")

# ==========================================
# VENTANA 1: MONITOREO EN VIVO DINÁMICO
# ==========================================
if menu == "📊 Monitoreo en Vivo":
    st.title("⚡ CENTRAL GESTION DE PLANTAS")
    st.markdown("**CV INGENIERIA SAS**")
    st.markdown("---")
    
    planta_seleccionada = st.selectbox("Seleccione la planta a monitorear:", [p["nombre"] for p in plantas_guardadas])
    detalles = next(p for p in plantas_guardadas if p["nombre"] == planta_seleccionada)
    
    # Extraemos todos los datos (con .get por si hay plantas viejas registradas sin estos datos)
    dl_info = detalles.get("datalogger", "No registrado")
    bat_marca = detalles.get("bat_marca", "Ninguna")
    bat_tipo = detalles.get("bat_tipo", "N/A")
    
    # Mostramos el encabezado súper profesional
    st.markdown(f"**Ubicación:** {detalles['ubicacion']} | **Capacidad:** {detalles['capacidad']}")
    st.markdown(f"**Equipos:** {detalles['inversores']} | 📡 **Datalogger:** `{dl_info}`")
    st.markdown(f"🔋 **Almacenamiento:** {bat_marca} | **Tecnología:** {bat_tipo}")
    st.markdown("---")

    st.markdown("### 📈 Curva de Generación Diaria")
    datos_historial = generar_curva_solar(planta_seleccionada)
    st.area_chart(datos_historial, color="#f1c40f")

    pot_solar_total = max(0, datos_historial.iloc[-1]["Generación (W)"] + random.randint(-150, 150))
    pot_load = 1800 + random.randint(-50, 50)
    pot_red = 0
    pot_bat = pot_solar_total - pot_load  
    soc_bateria = random.randint(40, 100) if bat_marca != "Ninguna" else 0 # Si no hay batería, SOC 0%

    st.markdown("### 🔄 Flujo de Energía en Tiempo Real")
    diagrama_svg = f"""
    <div style="background-color: #f9f9f9; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 500px; margin: auto; font-family: 'Segoe UI', sans-serif;">
        <svg viewBox="0 0 400 330" width="100%" height="100%">
            <path d="M 100 80 H 170" fill="none" stroke="#ddd" stroke-width="3"/>
            <path d="M 230 150 H 300 V 80" fill="none" stroke="#ddd" stroke-width="3"/>
            <path d="M 170 150 H 100 V 220" fill="none" stroke="#ddd" stroke-width="3"/>
            <path d="M 230 150 H 300 V 220" fill="none" stroke="#ddd" stroke-width="3"/>
            <circle cx="0" cy="0" r="5" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 80 H 170" /></circle>
            <circle cx="0" cy="0" r="5" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 220" /></circle>
            <circle cx="0" cy="0" r="5" fill="#e67e22"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 220" /></circle>
            <rect x="165" y="115" width="70" height="70" rx="15" fill="#e1f5fe" stroke="#3498db" stroke-width="2"/>
            <text x="200" y="153" text-anchor="middle" font-size="28">🎛️</text>
            <text x="200" y="175" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">Inversor</text>
            <rect x="35" y="30" width="130" height="70" rx="10" fill="white" stroke="#eee" stroke-width="2"/>
            <text x="100" y="55" text-anchor="middle" font-size="14" fill="#7f8c8d">☀️ FV Total</text>
            <text x="100" y="80" text-anchor="middle" font-size="18" font-weight="bold" fill="#2c3e50">{pot_solar_total} W</text>
            <rect x="235" y="30" width="130" height="70" rx="10" fill="white" stroke="#eee" stroke-width="2"/>
            <text x="300" y="55" text-anchor="middle" font-size="14" fill="#7f8c8d">🗼 Red</text>
            <text x="300" y="80" text-anchor="middle" font-size="18" font-weight="bold" fill="#e74c3c">{pot_red} W</text>
            <rect x="35" y="220" width="130" height="70" rx="10" fill="white" stroke="#eee" stroke-width="2"/>
            <text x="100" y="245" text-anchor="middle" font-size="14" fill="#7f8c8d">🔋 Batería ({soc_bateria}%)</text>
            <text x="100" y="270" text-anchor="middle" font-size="18" font-weight="bold" fill="#2ecc71">{pot_bat} W</text>
            <rect x="235" y="220" width="130" height="70" rx="10" fill="white" stroke="#eee" stroke-width="2"/>
            <text x="300" y="245" text-anchor="middle" font-size="14" fill="#7f8c8d">🏠 Carga (Casa)</text>
            <text x="300" y="270" text-anchor="middle" font-size="18" font-weight="bold" fill="#e67e22">{pot_load} W</text>
        </svg>
    </div>
    """
    components.html(diagrama_svg, height=500)
    
    if st.button("🔄 Refrescar Lecturas"):
        st.rerun()

# ==========================================
# VENTANA 2: GESTIÓN DE PLANTAS
# ==========================================
elif menu == "🏢 Gestión de Plantas":
    st.title("🏢 Directorio de Instalaciones")
    st.markdown("**CV INGENIERIA SAS - Gestión de Portafolio**")
    
    with st.expander("➕ Registrar Nueva Planta", expanded=False):
        with st.form("formulario_planta"):
            # Fila 1: Datos básicos
            col_a, col_b = st.columns(2)
            with col_a:
                nuevo_nombre = st.text_input("Nombre del Proyecto")
                nueva_capacidad = st.text_input("Capacidad (ej: 30 kW)")
            with col_b:
                nueva_ubicacion = st.text_input("Ubicación")
                nuevos_inversores = st.selectbox("Marcas de Inversores", ["Fronius", "GoodWe", "Huawei", "Deye", "Growatt", "Híbrido Multimarca"])
            
            # Fila 2: NUEVO - Gestión de Baterías
            st.markdown("##### 🔋 Configuración de Almacenamiento")
            col_c, col_d = st.columns(2)
            with col_c:
                nueva_bat_marca = st.selectbox("Marca de Baterías", ["Ninguna (On-Grid)", "Pylontech", "Deye", "GoodWe", "BYD", "Huawei", "Growatt", "Trojan", "Genérica", "Otra"])
            with col_d:
                nueva_bat_tipo = st.selectbox("Tecnología (Química)", ["No aplica", "Litio (LiFePO4)", "Plomo-Ácido", "AGM", "Gel", "Ion-Litio"])
            
            # Fila 3: Comunicaciones
            nuevo_datalogger = st.text_input("📡 Datalogger / Módulo Wi-Fi (Número de Serie, IP o MAC)")
            
            if st.form_submit_button("💾 Guardar Planta"):
                if nuevo_nombre != "":
                    guardar_planta({
                        "nombre": nuevo_nombre, 
                        "ubicacion": nueva_ubicacion, 
                        "capacidad": nueva_capacidad, 
                        "inversores": nuevos_inversores, 
                        "datalogger": nuevo_datalogger if nuevo_datalogger else "No especificado",
                        "bat_marca": nueva_bat_marca,    # Guardamos marca
                        "bat_tipo": nueva_bat_tipo       # Guardamos tecnología
                    })
                    st.success("¡Planta registrada con éxito!")
                    st.rerun()
                else:
                    st.error("Por favor, ponle un nombre al proyecto.")

    st.markdown("---")
    st.markdown("### 📋 Plantas Activas")
    for planta in plantas_guardadas:
        dl = planta.get("datalogger", "No registrado")
        b_marca = planta.get("bat_marca", "Ninguna")
        b_tipo = planta.get("bat_tipo", "N/A")
        
        # Mostramos la información completa en las tarjetas del directorio
        texto_tarjeta = f"""**{planta['nombre']}** 📍 Ubicación: {planta['ubicacion']} | ⚡ Capacidad: {planta['capacidad']}  
        🎛️ Inversor: {planta['inversores']} | 📡 DL: `{dl}`  
        🔋 Baterías: {b_marca} ({b_tipo})"""
        
        st.info(texto_tarjeta)
