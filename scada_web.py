import streamlit as st
import random
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components  # Nueva librería necesaria

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# ==========================================
st.set_page_config(page_title="SCADA Guaviare", page_icon="⚡", layout="centered")

st.title("⚡ Centro de Control Web - SCADA Guaviare")
st.markdown("**Planta Solar - San José del Guaviare, Colombia**")
st.markdown("---")


# ==========================================
# 2. LECTURA DE EQUIPOS (Mantenida de la lección anterior)
# ==========================================
# Simulamos una fluctuación realista +/- 100W
def leer_fronius():
    return 4500 + random.randint(-100, 100)

def leer_goodwe():
    # Retorna: Potencia Total (W) y SOC de Batería (%)
    return 3200 + random.randint(-100, 100), 98

pot_fronius = leer_fronius()
pot_goodwe, soc_goodwe = leer_goodwe()


# ==========================================
# 3. DISEÑO DE LA WEB (UI ORIGINAL MANTENIDA)
# ==========================================
st.markdown("### 📊 Indicadores Principales")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="🔵 Inversor Fronius (FV 1)", value=f"{pot_fronius} W")

with col2:
    st.metric(label="🟠 Híbrido GoodWe (FV 2)", value=f"{pot_goodwe} W", delta=f"Batería: {soc_goodwe}%")

st.markdown("---")


# ==========================================
# 4. DIAGRAMA DE FLUJO Deye-style (Integración Nueva)
# ==========================================
# Calculamos un escenario doméstico lógico basado en los datos simulados
pot_solar_total = pot_fronius + pot_goodwe  # Total paneles
pot_load = 1800 + random.randint(-20, 20)  # Consumo casa simulado
pot_red = 0  # Red en cero, como en tu captura

# El excedente solar carga la batería (Si es positivo, carga. Si es negativo, descarga)
pot_bat = pot_solar_total - pot_load  

# LA MAGIA: Código HTML y SVG para dibujar el diagrama animado (recreando tu imagen Deye)
diagrama_svg = f"""
<div style="background-color: #f9f9f9; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 500px; margin: auto; font-family: 'Segoe UI', sans-serif;">
    <h3 style="text-align: center; color: #333; margin-top: 0; margin-bottom: 20px;">Diagrama de Energía</h3>
    <svg viewBox="0 0 400 300" width="100%" height="100%">
        
        <path d="M 100 80 H 170" fill="none" stroke="#ddd" stroke-width="3"/>
        <path d="M 230 150 H 300 V 80" fill="none" stroke="#ddd" stroke-width="3"/>
        <path d="M 170 150 H 100 V 220" fill="none" stroke="#ddd" stroke-width="3"/>
        <path d="M 230 150 H 300 V 220" fill="none" stroke="#ddd" stroke-width="3"/>

        <circle cx="0" cy="0" r="5" fill="#3498db">
            <animateMotion dur="1s" repeatCount="indefinite" path="M 100 80 H 170" />
        </circle>
        
        <circle cx="0" cy="0" r="5" fill="#2ecc71">
            <animateMotion dur="1.2s" repeatCount="indefinite" path="M 170 150 H 100 V 220" />
        </circle>
        
        <circle cx="0" cy="0" r="5" fill="#e67e22">
            <animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 220" />
        </circle>

        <rect x="165" y="115" width="70" height="70" rx="15" fill="#e1f5fe" stroke="#3498db" stroke-width="2"/>
        <text x="200" y="153" text-anchor="middle" font-size="28">🎛️</text>
        <text x="200" y="175" text-anchor="middle" font-size="10" font-weight="bold" fill="#3498db">Deye Hybrid</text>

        <rect x="35" y="30" width="130" height="70" rx="10" fill="white" stroke="#eee" stroke-width="2"/>
        <text x="100" y="55" text-anchor="middle" font-size="14" fill="#7f8c8d">☀️ FV Total</text>
        <text x="100" y="80" text-anchor="middle" font-size="18" font-weight="bold" fill="#2c3e50">{pot_solar_total} W</text>

        <rect x="235" y="30" width="130" height="70" rx="10" fill="white" stroke="#eee" stroke-width="2"/>
        <text x="300" y="55" text-anchor="middle" font-size="14" fill="#7f8c8d">🗼 Red</text>
        <text x="300" y="80" text-anchor="middle" font-size="18" font-weight="bold" fill="#e74c3c">{pot_red} W</text>

        <rect x="35" y="220" width="130" height="70" rx="10" fill="white" stroke="#eee" stroke-width="2"/>
        <text x="100" y="245" text-anchor="middle" font-size="14" fill="#7f8c8d">🔋 Batería ({soc_goodwe}%)</text>
        <text x="100" y="270" text-anchor="middle" font-size="18" font-weight="bold" fill="#2ecc71">{pot_bat} W</text>

        <rect x="235" y="220" width="130" height="70" rx="10" fill="white" stroke="#eee" stroke-width="2"/>
        <text x="300" y="245" text-anchor="middle" font-size="14" fill="#7f8c8d">🏠 Carga (Casa)</text>
        <text x="300" y="270" text-anchor="middle" font-size="18" font-weight="bold" fill="#e67e22">{pot_load} W</text>
    </svg>
</div>
"""
# 5. RENDERIZADO DE LA WEB
st.markdown("### 🔄 Estado del Sistema (Deye Flow Chart)")
components.html(diagrama_svg, height=350)  # Incrustamos el diagrama SVG animado

st.markdown("---")
if st.button("🔄 Refrescar Lecturas"):
    st.rerun()  # Esto recarga la página web instantáneamente
