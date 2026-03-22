import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components

# ==========================================
# 1. ESTILO Y FONDO REAL (NUEVO - NO CAMBIA FUNCIONALIDAD)
# ==========================================
st.set_page_config(page_title="Central CV Ingeniería", page_icon="⚡", layout="centered")

# CSS para inyectar una foto real del parque solar de Icono8 de fondo
fondo_corporativo_css = """
<style>
/* 1. Fondo de la aplicación principal (sin tocar la barra lateral) */
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1509391366360-fe5ace4a1012?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* 2. Hacemos que la cabecera sea transparente */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* 3. Estilo de los textos principales para que sean legibles sobre el fondo */
h1, h2, h3, p, label, [data-testid="stMarkdownContainer"] {
    color: #0d47a1 !important; /* Azul oscuro corporativo */
}

/* 4. Estilo de las cajas de Streamlit (widgets) para que se integren */
.stTextInput>div>div>input, .stSelectbox>div>div>select {
    background-color: rgba(255, 255, 255, 0.8) !important;
}

/* 5. Aseguramos que los contenedores de los diagramas tengan su fondo blanco */
.stMarkdownContainer svg, .stMarkdownContainer iframe {
    background-color: white !important;
    border-radius: 15px;
}
</style>
"""
# RENDERIZADO DEL ESTILO VISUAL
st.markdown(fondo_corporativo_css, unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS Y MOTOR SOLAR - NO TOCAR
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        plantas_iniciales = [{
            "nombre": "Planta Principal", "ubicacion": "San José del Guaviare", 
            "capacidad": "13.92 kWp", "inversores": "Híbrido Multimarca", 
            "datalogger": "SN: CV-001", "bat_marca": "Deye/Pylontech", "bat_tipo": "Litio (LiFePO4)"
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
# 3. SEGURIDAD (LOGIN) - NO TOCAR
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center;'>🔒 CENTRAL GESTIÓN DE PLANTAS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #1f77b4;'>CV INGENIERIA SAS</h3>", unsafe_allow_html=True)
    
    col1, col_centro, col2 = st.columns([1, 2, 1]) 
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
                    st.error("❌ Credenciales incorrectas.")
    st.stop() 

# ==========================================
# 4. MENÚ LATERAL - NO TOCAR
# ==========================================
st.sidebar.title("Navegación CV")
menu = st.sidebar.radio("Ir a:", ["📊 Monitoreo", "🏢 Gestión"])
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.rerun()
st.sidebar.info("**CV INGENIERIA SAS**")

# ==========================================
# VENTANA 1: MONITOREO (INTERFAZ ORIGINAL BLINDADA)
# ==========================================
if menu == "📊 Monitoreo":
    st.title("⚡ MONITOREO EN VIVO")
    st.markdown("### CV INGENIERIA SAS")
    st.markdown("---")
    
    planta_sel = st.selectbox("Seleccione Planta:", [p["nombre"] for p in plantas_guardadas])
    d = next(p for p in plantas_guardadas if p["nombre"] == planta_sel)
    
    st.write(f"📍 {d['ubicacion']} | ⚡ {d['capacidad']} | 📡 DL: `{d.get('datalogger','N/A')}`")
    st.markdown("---")

    st.markdown("### 📈 Curva de Generación Diaria")
    datos_h = generar_curva_solar(planta_sel)
    st.area_chart(datos_h, color="#f1c40f")

    # Datos simulados para diagrama
    pot_solar = max(0, datos_h.iloc[-1]["Generación (W)"] + random.randint(-100, 100))
    pot_load = 1800 + random.randint(-50, 50)
    pot_bat = pot_solar - pot_load
    soc = random.randint(40, 100)

    st.markdown("### 🔄 Flujo de Energía en Tiempo Real")
    
    # EL DIBUJO ORIGINAL (SVG NATIVO DIBUJADO) - NO TOCAR ""
    diagrama_svg = f"""
    <div style="background-color: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 500px; margin: auto; font-family: sans-serif;">
        <svg viewBox="0 0 400 350" width="100%" height="100%">
            <path d="M 100 85 V 150 H 170" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            <path d="M 300 85 V 150 H 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            <path d="M 170 150 H 100 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            <path d="M 230 150 H 300 V 230" fill="none" stroke="#dfe6e9" stroke-width="5" stroke-linecap="round"/>
            
            <circle r="6" fill="#f1c40f"><animateMotion dur="1s" repeatCount="indefinite" path="M 100 85 V 150 H 170" /></circle>
            <circle r="6" fill="#2ecc71"><animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 230" /></circle>
            <circle r="6" fill="#e67e22"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 230" /></circle>
            
            <rect x="165" y="115" width="70" height="70" rx="12" fill="#ffffff" stroke="#3498db" stroke-width="3"/>
            <rect x="175" y="125" width="50" height="25" rx="3" fill="#2c3e50"/> <text x="200" y="142" text-anchor="middle" font-size="8" fill="#55efc4" font-weight="bold">Deye</text>
            <text x="200" y="200" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">Híbrido</text>

            <g transform="translate(30,20)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eceff1" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#607d8b" font-weight="bold">FV TOTAL</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold">{pot_solar} W</text>
            </g>
            
            <g transform="translate(230,20)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eceff1" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#607d8b" font-weight="bold">RED ELÉC.</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold">0 W</text>
            </g>

            <g transform="translate(30,230)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eceff1" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#607d8b" font-weight="bold">BATERÍA ({soc}%)</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold">{pot_bat} W</text>
            </g>
            
            <g transform="translate(230,230)">
                <rect width="140" height="85" rx="12" fill="white" stroke="#eceff1" stroke-width="1"/>
                <text x="70" y="35" text-anchor="middle" font-size="11" fill="#607d8b" font-weight="bold">CARGA</text>
                <text x="70" y="65" text-anchor="middle" font-size="18" font-weight="bold">{pot_casa} W</text>
            </g>
        </svg>
    </div>
    """
    
    components.html(diagrama_svg, height=520) 
    if st.button("🔄 Refrescar Datos"): st.rerun()

# ==========================================
# VENTANA 2: GESTIÓN DE PROYECTOS - NO TOCAR
# ==========================================
else:
    st.title("🏢 GESTIÓN DE PORTAFOLIO")
    with st.expander("➕ Registrar Nueva Planta", expanded=False):
        with st.form("f_planta"):
            nombre = st.text_input("Nombre Planta")
            ubi = st.text_input("Ubicación")
            cap = st.text_input("Capacidad (kWp)")
            inv = st.text_input("Inversor")
            dl = st.text_input("Datalogger")
            if st.form_submit_button("💾 Guardar"):
                if nombre:
                    guardar_planta({"nombre": nombre, "ubicacion": ubi, "capacidad": cap, "inversores": inv, "datalogger": dl})
                    st.success("Planta registrada")
                    st.rerun()
    for pl in plantas_guardadas:
        st.info(f"**{pl['nombre']}** | {pl['ubicacion']} | 🔋 {pl.get('inversores','Híbrido')}")
