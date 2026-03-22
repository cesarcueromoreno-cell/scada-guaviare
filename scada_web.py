import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURACIÓN Y BASE DE DATOS
# ==========================================
st.set_page_config(page_title="SCADA Multi-Planta", page_icon="⚡", layout="centered")

ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        plantas_iniciales = [
            {
                "nombre": "Planta Principal", 
                "ubicacion": "San José del Guaviare", 
                "capacidad": "13.92 kWp", 
                "inversores": "Fronius + GoodWe",
                "datalogger": "SN: 240.123456 / IP: 192.168.1.15" # Dato nuevo
            }
        ]
        with open(ARCHIVO_PLANTAS, 'w') as f:
            json.dump(plantas_iniciales, f)
    with open(ARCHIVO_PLANTAS, 'r') as f:
        return json.load(f)

def guardar_planta(nueva_planta):
    plantas = cargar_plantas()
    plantas.append(nueva_planta)
    with open(ARCHIVO_PLANTAS, 'w') as f:
        json.dump(plantas, f)

plantas_guardadas = cargar_plantas()

# ==========================================
# 2. MOTOR MATEMÁTICO SOLAR
# ==========================================
def generar_curva_solar(nombre_planta):
    random.seed(nombre_planta) 
    pico_maximo = random.randint(4000, 15000) 
    
    horas = [f"{h:02d}:00" for h in range(6, 19)] 
    energia = []
    
    for h in range(6, 19):
        porcentaje_sol = math.sin(math.pi * (h - 6) / 12)
        valor = pico_maximo * porcentaje_sol + random.randint(-400, 400) 
        energia.append(max(0, int(valor))) 
        
    random.seed() 
    df = pd.DataFrame({"Hora": horas, "Generación (W)": energia})
    return df.set_index("Hora")

# ==========================================
# 3. MENÚ LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["📊 Monitoreo en Vivo", "🏢 Gestión de Plantas"])
st.sidebar.markdown("---")
st.sidebar.info("Panel de Control Multimarca")

# ==========================================
# VENTANA 1: MONITOREO EN VIVO DINÁMICO
# ==========================================
if menu == "📊 Monitoreo en Vivo":
    st.title("⚡ Centro de Control Web")
    
    nombres_plantas = [p["nombre"] for p in plantas_guardadas]
    planta_seleccionada = st.selectbox("Seleccione la planta a monitorear:", nombres_plantas)
    
    detalles = next(p for p in plantas_guardadas if p["nombre"] == planta_seleccionada)
    # Mostramos el datalogger también en la vista principal
    dl_info = detalles.get("datalogger", "No registrado")
    
    st.markdown(f"**Ubicación:** {detalles['ubicacion']} | **Capacidad:** {detalles['capacidad']}")
    st.markdown(f"**Equipos:** {detalles['inversores']} | 📡 **Datalogger:** `{dl_info}`")
    st.markdown("---")

    st.markdown("### 📈 Curva de Generación Diaria")
    datos_historial = generar_curva_solar(planta_seleccionada)
    st.area_chart(datos_historial, color="#f1c40f")

    pot_solar_total = datos_historial.iloc[-1]["Generación (W)"] + random.randint(-150, 150)
    pot_solar_total = max(0, pot_solar_total)
    
    pot_load = 1800 + random.randint(-50, 50)
    pot_red = 0
    pot_bat = pot_solar_total - pot_load  
    soc_bateria = random.randint(40, 100) 

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
    components.html(diagrama_svg, height=350)
    
    if st.button("🔄 Refrescar Lecturas"):
        st.rerun()

# ==========================================
# VENTANA 2: GESTIÓN DE PLANTAS
# ==========================================
elif menu == "🏢 Gestión de Plantas":
    st.title("🏢 Directorio de Instalaciones")
    st.markdown("Administra todo tu portafolio de proyectos solares.")
    
    with st.expander("➕ Registrar Nueva Planta", expanded=False):
        with st.form("formulario_planta"):
            col_a, col_b = st.columns(2)
            with col_a:
                nuevo_nombre = st.text_input("Nombre del Proyecto")
                nueva_capacidad = st.text_input("Capacidad (ej: 30 kW)")
            with col_b:
                nueva_ubicacion = st.text_input("Ubicación")
                nuevos_inversores = st.selectbox("Marcas de Inversores", ["Fronius", "GoodWe", "Huawei", "Deye", "Híbrido Multimarca"])
            
            # EL NUEVO CAMPO DEL DATALOGGER (Ocupa todo el ancho abajo)
            nuevo_datalogger = st.text_input("📡 Datalogger / Módulo Wi-Fi (Número de Serie, IP o MAC)")
            
            if st.form_submit_button("💾 Guardar Planta"):
                if nuevo_nombre != "":
                    # Ahora guardamos también el datalogger en la base de datos
                    guardar_planta({
                        "nombre": nuevo_nombre, 
                        "ubicacion": nueva_ubicacion, 
                        "capacidad": nueva_capacidad, 
                        "inversores": nuevos_inversores,
                        "datalogger": nuevo_datalogger if nuevo_datalogger else "No especificado"
                    })
                    st.success("¡Planta registrada con éxito!")
                    st.rerun()
                else:
                    st.error("Por favor, ponle un nombre al proyecto.")

    st.markdown("---")
    st.markdown("### 📋 Plantas Activas")
    for planta in plantas_guardadas:
        # Usamos .get() por si acaso hay plantas viejas que no tenían este dato
        dl = planta.get("datalogger", "No registrado")
        st.info(f"**{planta['nombre']}** \n📍 {planta['ubicacion']} | ⚡ {planta['capacidad']} | 🎛️ {planta['inversores']} | 📡 **DL:** `{dl}`")
