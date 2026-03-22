import streamlit as st
import random
import streamlit.components.v1 as components

st.set_page_config(page_title="SCADA Guaviare", page_icon="⚡", layout="centered")

st.title("⚡ Centro de Control Web")
st.markdown("**Planta Solar - San José del Guaviare**")
st.markdown("---")

# 1. Simulamos datos matemáticamente lógicos
pot_solar = 4250 + random.randint(-50, 50)
pot_grid = 0  # Red en cero, como en tu captura
pot_load = 2100 + random.randint(-20, 20)
pot_bat = pot_solar - pot_load  # El excedente (aprox 2150W) carga la batería
soc_bat = 100

# 2. LA MAGIA: Código HTML y SVG para dibujar el diagrama animado
diagrama_svg = f"""
<div style="background-color: #ffffff; border-radius: 15px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); width: 100%; max-width: 500px; margin: auto; font-family: 'Segoe UI', Arial, sans-serif;">
    <h3 style="text-align: left; color: #333; margin-top: 0; margin-bottom: 20px;">Flujo de energía</h3>
    <svg viewBox="0 0 400 300" width="100%" height="100%">
        
        <path d="M 100 80 V 150 H 170" fill="none" stroke="#e0e0e0" stroke-width="3"/>
        <path d="M 300 80 V 150 H 230" fill="none" stroke="#e0e0e0" stroke-width="3"/>
        <path d="M 170 150 H 100 V 220" fill="none" stroke="#e0e0e0" stroke-width="3"/>
        <path d="M 230 150 H 300 V 220" fill="none" stroke="#e0e0e0" stroke-width="3"/>

        <circle cx="0" cy="0" r="5" fill="#3498db">
            <animateMotion dur="1.5s" repeatCount="indefinite" path="M 100 80 V 150 H 170" />
        </circle>
        
        <circle cx="0" cy="0" r="5" fill="#2ecc71">
            <animateMotion dur="1.5s" repeatCount="indefinite" path="M 170 150 H 100 V 220" />
        </circle>
        
        <circle cx="0" cy="0" r="5" fill="#e67e22">
            <animateMotion dur="1.5s" repeatCount="indefinite" path="M 230 150 H 300 V 220" />
        </circle>

        <rect x="165" y="115" width="70" height="70" rx="15" fill="#f4f6f8" stroke="#3498db" stroke-width="2"/>
        <text x="200" y="153" text-anchor="middle" font-size="28">🎛️</text>

        <rect x="35" y="10" width="130" height="70" rx="10" fill="white" stroke="#ecf0f1" stroke-width="2"/>
        <text x="100" y="35" text-anchor="middle" font-size="14" fill="#7f8c8d">☀️ Producción</text>
        <text x="100" y="60" text-anchor="middle" font-size="18" font-weight="bold" fill="#2c3e50">{pot_solar} W</text>

        <rect x="235" y="10" width="130" height="70" rx="10" fill="white" stroke="#ecf0f1" stroke-width="2"/>
        <text x="300" y="35" text-anchor="middle" font-size="14" fill="#7f8c8d">🗼 Red</text>
        <text x="300" y="60" text-anchor="middle" font-size="18" font-weight="bold" fill="#e74c3c">{pot_grid} W</text>

        <rect x="35" y="220" width="130" height="70" rx="10" fill="white" stroke="#ecf0f1" stroke-width="2"/>
        <text x="100" y="245" text-anchor="middle" font-size="14" fill="#7f8c8d">🔋 Batería <tspan fill="#3498db" font-weight="bold">{soc_bat}%</tspan></text>
        <text x="100" y="270" text-anchor="middle" font-size="18" font-weight="bold" fill="#2ecc71">{pot_bat} W</text>

        <rect x="235" y="220" width="130" height="70" rx="10" fill="white" stroke="#ecf0f1" stroke-width="2"/>
        <text x="300" y="245" text-anchor="middle" font-size="14" fill="#7f8c8d">🏠 Carga</text>
        <text x="300" y="270" text-anchor="middle" font-size="18" font-weight="bold" fill="#e67e22">{pot_load} W</text>
    </svg>
</div>
"""

# 3. Renderizamos el componente en la web
components.html(diagrama_svg, height=350)

st.markdown("---")
if st.button("🔄 Refrescar Lecturas"):
    st.rerun()
