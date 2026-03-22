import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="SCADA Guaviare", page_icon="⚡", layout="centered")

st.title("⚡ Centro de Control Web")
st.markdown("**Planta Solar - San José del Guaviare**")
st.markdown("---")

def leer_fronius():
    return 4500 + random.randint(-200, 200)

def leer_goodwe():
    return 3200 + random.randint(-150, 150), 98

pot_fronius = leer_fronius()
pot_goodwe, soc_goodwe = leer_goodwe()

col1, col2 = st.columns(2)

with col1:
    st.metric(label="🔵 Inversor Fronius", value=f"{pot_fronius} W")

with col2:
    st.metric(label="🟠 Híbrido GoodWe", value=f"{pot_goodwe} W", delta=f"Batería: {soc_goodwe}%")

st.markdown("### 📊 Generación en Tiempo Real")

datos_grafica = pd.DataFrame({
    "Equipos": ["Fronius", "GoodWe"],
    "Potencia (W)": [pot_fronius, pot_goodwe]
}).set_index("Equipos")

st.bar_chart(datos_grafica, color=["#1f77b4"])

st.markdown("---")
if st.button("🔄 Actualizar Datos"):
    st.rerun()
