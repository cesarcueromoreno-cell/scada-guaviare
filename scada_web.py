import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. ESTILO Y FONDO REAL (IMAGEN)
# ==========================================
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="centered")

# Inyectamos el fondo de pantalla real
fondo_solar_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1509391366360-fe5ace4a1012?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

.main .block-container {
    background-color: rgba(255, 255, 255, 0.85); /* Caja blanca semi-transparente para leer bien */
    padding: 3rem;
    border-radius: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    margin-top: 2rem;
}

h1, h2, h3, p {
    color: #1a237e !important; /* Azul oscuro corporativo */
}
</style>
"""
st.markdown(fondo_solar_css, unsafe_allow_html=True)

# ==========================================
# 2. SEGURIDAD (LOGIN)
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔒 CENTRAL GESTIÓN DE PLANTAS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>CV INGENIERIA SAS</h3>", unsafe_allow_html=True)
    
    col1, col_centro, col2 = st.columns([1, 2, 1])
    with col_centro:
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario")
            contrasena = st.text_input("🔑 Contraseña", type="password")
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                if usuario == "admin" and contrasena == "solar123":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
    st.stop()

# ==========================================
# 3. BASE DE DATOS Y MOTOR SOLAR (INTACTO)
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [{"nombre": "Planta Principal", "ubicacion": "Guaviare", "capacidad": "13.92 kWp", "inversores": "Híbrido", "datalogger": "SN: CV-001", "bat_marca": "Deye", "bat_tipo": "Litio"}]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(inicial, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

def guardar_planta(nueva):
    plantas = cargar_plantas()
    plantas.append(nueva)
    with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(plantas, f)

plantas_guardadas = cargar_plantas()

# ==========================================
# 4. NAVEGACIÓN Y MONITOREO
# ==========================================
st.sidebar.title("Navegación CV")
menu = st.sidebar.radio("Ir a:", ["📊 Monitoreo", "🏢 Gestión"])
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()

if menu == "📊 Monitoreo":
    st.title("⚡ MONITOREO EN VIVO")
    st.markdown("### CV INGENIERIA SAS")
    
    planta_sel = st.selectbox("Seleccione Planta:", [p["nombre"] for p in plantas_guardadas])
    d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
    
    st.write(f"📍 {d['ubicacion']} | ⚡ {d['capacidad']} | 📡 DL: `{d.get('datalogger','N/A')}`")
    
    # Datos simulados para el diagrama
    pot_solar = random.randint(4000, 5000)
    pot_casa = 1800
    pot_bat = pot_solar - pot_casa

    # DIAGRAMA NATIVO (EL QUE TE GUSTÓ)
    diagrama_svg = f"""
    <div style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #eee;">
        <svg viewBox="0 0 400 350" width="100%">
            <path d="M 100 85 V 150 H 170" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            <path d="M 300 85 V 150 H 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            <path d="M 170 150 H 100 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            <path d="M 230 150 H 300 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            <circle r="6" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 85 V 150 H 170" /></circle>
            <circle r="6" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>
            <circle r="6" fill="#e67e22"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 230" /></circle>
            <rect x="165" y="115" width="70" height="70" rx="12" fill="#ffffff" stroke="#3498db" stroke-width="3"/>
            <text x="200" y="155" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">Deye</text>
            <g transform="translate(30,20)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eee" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72">FV TOTAL</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold">{pot_solar} W</text>
            </g>
            <g transform="translate(230,20)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eee" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72">RED</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold">0 W</text>
            </g>
            <g transform="translate(30,230)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eee" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72">BATERÍA</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold">{pot_bat} W</text>
            </g>
            <g transform="translate(230,230)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eee" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#636e72">CARGA</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold">{pot_casa} W</text>
            </g>
        </svg>
    </div>
    """
    components.html(diagrama_svg, height=500)
    if st.button("🔄 Actualizar"): st.rerun()

else:
    st.title("🏢 GESTIÓN DE PORTAFOLIO")
    with st.form("f_planta"):
        nombre = st.text_input("Nombre Planta")
        ubi = st.text_input("Ubicación")
        if st.form_submit_button("💾 Guardar"):
            if nombre:
                guardar_planta({"nombre": nombre, "ubicacion": ubi})
                st.rerun()
    for pl in plantas_guardadas:
        st.info(f"**{pl['nombre']}** - {pl['ubicacion']}")
