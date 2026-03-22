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
# CAMBIO 1: Título de la pestaña del navegador
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="centered")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    # CAMBIO 2: Pantalla de Login con tu marca
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
        plantas_iniciales = [{"nombre": "Planta Principal", "ubicacion": "San José del Guaviare", "capacidad": "13.92 kWp", "inversores": "Fronius + GoodWe", "datalogger": "SN: 240.123456 / IP: 192.168.1.15"}]
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

# CAMBIO 3: Marca en la barra lateral
st.sidebar.info("Plataforma Oficial \n**CV INGENIERIA SAS**")

# ==========================================
# VENTANA 1: MONITOREO EN VIVO DINÁMICO
# ==========================================
if menu == "📊 Monitoreo en Vivo":
    # CAMBIO 4: Título principal de la plataforma
    st.title("⚡ CENTRAL GESTION DE PLANTAS")
    st.markdown("**CV INGENIERIA SAS**")
    st.markdown("---")
    
    planta_seleccionada = st.selectbox("Seleccione la planta a monitorear:", [p["nombre"] for p in plantas_guardadas])
    detalles = next(p for p in plantas_guardadas if p["nombre"] == planta_seleccionada)
    dl_info = detalles.get("datalogger", "No registrado")
    
    st.markdown(f"**Ubicación:** {detalles['ubicacion']} | **Capacidad:** {detalles['capacidad']}")
    st.markdown(f"**Equipos:** {detalles['inversores']} | 📡 **Datalogger:** `{dl_info}`")
    st.markdown("---")

    st.markdown("### 📈 Curva de Generación Diaria")
    datos_historial = generar_curva_solar(planta_seleccionada)
    st.area_chart(datos_historial, color="#f1c40f")

    pot_solar_total = max(0, datos_historial.iloc[-1]["Generación (W)"] + random.randint(-150, 150))
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
            <path d="M 170 150 H 100 V 22
