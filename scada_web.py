import streamlit as st
import random
import json
import os
import math
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import streamlit.components.v1 as components
import re
import hashlib

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y CSS CLON SOLARMAN
# ==========================================
st.set_page_config(page_title="MOMISOLAR APP", page_icon="☀️", layout="wide", initial_sidebar_state="expanded") 

# CSS PARA CLONAR LA INTERFAZ DE SOLARMAN
css_solarman = """
<style>
/* Resetear fondos y márgenes de Streamlit */
.stApp { background-color: #f0f2f5; }
.block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; max-width: 100% !important; }

/* Ocultar header nativo de Streamlit */
[data-testid="stHeader"] { display: none; }

/* MENÚ LATERAL (BLANCO) */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e0e0e0 !important;
}
[data-testid="stSidebar"] * { color: #515a6e !important; }
[data-testid="stSidebarUserContent"] { padding-top: 1rem; }

/* TEXTOS GENERALES EN NEGRO/GRIS OSCURO */
h1, h2, h3, h4, h5, p, span, div, label { color: #1c2434; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }

/* BARRA SUPERIOR CUSTOM (HEADER AZUL OSCURO) */
.solarman-topbar {
    background-color: #1a2238;
    color: white;
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-left: -1rem;
    margin-right: -1rem;
    margin-top: -1rem;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.solarman-topbar .logo { display: flex; align-items: center; font-size: 20px; font-weight: bold; color: white !important;}
.solarman-topbar .logo img { margin-right: 10px; width: 24px; }
.solarman-topbar .user-area { font-size: 14px; color: #a0aabf !important; display: flex; align-items: center; gap: 15px;}

/* TARJETAS DE MÉTRICAS (KPIs) */
.kpi-card {
    background: white; border-radius: 4px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    text-align: center; border: 1px solid #e8eaec; height: 100%;
}
.kpi-val { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
.kpi-lbl { font-size: 12px; color: #808695; text-transform: uppercase; }

/* TABLAS ESTILO SOLARMAN */
.table-header {
    background-color: #f8f8f9; padding: 10px 15px; font-weight: bold; font-size: 12px; color: #515a6e;
    border-bottom: 1px solid #e8eaec; display: flex; border-top: 1px solid #e8eaec;
}
.table-row {
    background-color: white; padding: 12px 15px; font-size: 13px; color: #515a6e;
    border-bottom: 1px solid #e8eaec; display: flex; align-items: center; transition: background-color 0.2s;
}
.table-row:hover { background-color: #f3f3f3; }
.col-nombre { flex: 2; display: flex; align-items: center; font-weight: 500; color: #2d8cf0; cursor: pointer; }
.col-estado { flex: 1; display: flex; gap: 10px; }
.col-capacidad { flex: 1; }
.col-potencia { flex: 1; }
.col-energia { flex: 1; }
.col-accion { flex: 0.5; text-align: right; }

/* ESTILOS DE TABS TIPO MENÚ SUPERIOR */
.solarman-tabs { display: flex; border-bottom: 1px solid #dcdee2; margin-bottom: 15px; gap: 20px; padding-left: 10px;}
.solarman-tab { padding: 10px 0; font-size: 14px; color: #515a6e; cursor: pointer; border-bottom: 2px solid transparent; }
.solarman-tab.active { color: #2d8cf0; border-bottom: 2px solid #2d8cf0; font-weight: 500; }

/* BADGES DE ESTADO */
.badge-green { color: #19be6b; font-size: 12px; display: flex; align-items: center; gap: 4px; }
.badge-red { color: #ed4014; font-size: 12px; display: flex; align-items: center; gap: 4px; }

/* BOTÓN VOLVER */
.btn-volver { color: #808695; font-size: 14px; cursor: pointer; display: inline-flex; align-items: center; gap: 5px; margin-bottom: 15px;}
.btn-volver:hover { color: #2d8cf0; }
</style>
"""
st.markdown(css_global, unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DATOS Y ESTADO DE SESIÓN
# ==========================================
ARCHIVO_PLANTAS = 'plantas.json'

def cargar_plantas():
    if not os.path.exists(ARCHIVO_PLANTAS):
        inicial = [
            {"nombre": "Cancha las malvinas off grid", "ubicacion": "BARRANQUILLA", "capacidad": "30 kWp", "inversores": "Deye", "id": "1D172475"},
            {"nombre": "Planta Principal CV", "ubicacion": "GUAVIARE", "capacidad": "13.92 kWp", "inversores": "Sylvania", "id": "9B3A4F12"}
        ]
        with open(ARCHIVO_PLANTAS, 'w') as f: json.dump(inicial, f)
    with open(ARCHIVO_PLANTAS, 'r') as f: return json.load(f)

plantas_guardadas = cargar_plantas()

# SIMULADOR DE DATOS
def obtener_datos_reales(planta):
    cap_texto = str(planta.get("capacidad", "5"))
    solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
    try: cap_val = float(solo_numeros[0]) * 1000 if solo_numeros else 5000 
    except: cap_val = 5000 
    
    pot_simulada = int(cap_val * random.uniform(0.1, 0.8))
    energia_simulada = round((pot_simulada * random.uniform(3.5, 5.0)) / 1000, 1)
    
    soc = random.randint(15, 100) 
    alertas = []
    if soc <= 25: alertas.append("Batería Baja")
    if random.random() < 0.1: alertas.append("Falla de Red")

    return {"solar": pot_simulada, "casa": 1750 + random.randint(-40, 40), "soc": soc, "energia_diaria": energia_simulada, "alertas": alertas}

def simular_historico_24h(cap_val):
    hora_actual = datetime.now()
    inicio_dia = hora_actual.replace(hour=0, minute=0, second=0, microsecond=0)
    datos = []
    for minutos in range(0, 24 * 60, 15):
        timestamp = inicio_dia + timedelta(minutes=minutos)
        hora = timestamp.hour
        generacion = max(0, (cap_val * 0.9) * math.sin((hora - 6) / 12 * math.pi) * random.uniform(0.95, 1.05)) if 6 <= hora <= 18 else 0
        consumo = max(cap_val * 0.1, cap_val * 0.2 + (cap_val * 0.3 * math.sin((hora-7)/2 * math.pi) if 7<=hora<=9 else (cap_val * 0.4 * math.sin((hora-18)/3 * math.pi) if 18<=hora<=21 else 0)))
        datos.append({"timestamp": timestamp, "Producción Solar": round(generacion, 2), "Consumo": round(consumo, 2)})
    return pd.DataFrame(datos)

# MANEJO DE NAVEGACIÓN (VISTA LISTA VS VISTA PLANTA)
if "vista_actual" not in st.session_state:
    st.session_state.vista_actual = "lista"
if "planta_seleccionada" not in st.session_state:
    st.session_state.planta_seleccionada = None

# ==========================================
# 3. HEADER GLOBAL (IMITANDO SOLARMAN)
# ==========================================
st.markdown("""
<div class="solarman-topbar">
    <div class="logo">
        <img src="https://img.icons8.com/fluency/48/solar-energy.png"/> MOMISOLAR APP
    </div>
    <div class="user-area">
        <span>🌐 Internacional</span>
        <span>🌐 Español</span>
        <span>👤 admin_cv</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. MENÚ LATERAL (SIDEBAR BLANCO)
# ==========================================
# Forzamos el menú lateral a imitar la estructura de Solarman
menu_opciones = ["Panel", "Monitor", "Análisis", "O&M", "Aplicaciones", "Gestión"]
menu_seleccionado = st.sidebar.radio("Navegación", menu_opciones, index=1)
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align:center; color:#c5c8ce; font-size:12px;'>POWERED BY<br><b>CV INGENIERÍA SAS</b></div>", unsafe_allow_html=True)


if menu_seleccionado != "Monitor":
    st.info("Módulo en desarrollo para MOMISOLAR APP.")
    st.stop()

# ==========================================
# 5. VISTA 1: LISTA DE PLANTAS (EL DIRECTORIO)
# ==========================================
if st.session_state.vista_actual == "lista":
    
    st.markdown("<h2 style='color:#1c2434; font-weight:normal; margin-bottom:20px;'>Plantas</h2>", unsafe_allow_html=True)
    
    # Pestañas superiores de estado (Total, En línea, etc.)
    st.markdown(f"""
    <div class="solarman-tabs">
        <div class="solarman-tab active" style="color:#2d8cf0; border-bottom:2px solid #2d8cf0;">Total({len(plantas_guardadas)})</div>
        <div class="solarman-tab"><span style="color:#19be6b;">(i)</span> En línea({len(plantas_guardadas)})</div>
        <div class="solarman-tab"><span style="color:#ed4014;">(x)</span> Desconectado(0)</div>
        <div class="solarman-tab"><span style="color:#ff9900;">(!)</span> Alertas(0)</div>
    </div>
    """, unsafe_allow_html=True)

    # Contenedor principal blanco
    st.markdown("<div style='background:white; padding:20px; border-radius:4px; border:1px solid #e8eaec;'>", unsafe_allow_html=True)
    
    # Buscador y botón crear
    c_busc, c_btn = st.columns([4, 1])
    with c_busc:
        st.text_input("Buscar", label_visibility="collapsed", placeholder="Por favor, ingrese el nombre de la planta")
    with c_btn:
        st.button("Crear una planta", type="primary", use_container_width=True)

    # CABECERA DE LA TABLA
    st.markdown("""
    <div class="table-header" style="margin-top:20px;">
        <div class="col-nombre">Nombre ↕</div>
        <div class="col-estado">Com ❓</div>
        <div class="col-estado">Alertas</div>
        <div class="col-capacidad">Capacidad ↕</div>
        <div class="col-potencia">Potencia solar ↕</div>
        <div class="col-energia">Producción de hoy ↕</div>
        <div class="col-accion">Operación</div>
    </div>
    """, unsafe_allow_html=True)

    # FILAS DE LA TABLA
    for pl in plantas_guardadas:
        datos = obtener_datos_reales(pl)
        
        # Para hacer el nombre clickable en Streamlit sin recargar toda la página feo, usamos un botón oculto o form.
        # Aquí usamos columnas para simular la fila
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 0.7, 0.7, 1, 1, 1, 0.5])
        
        with col1:
            st.markdown(f"<div style='padding: 10px 0;'>", unsafe_allow_html=True)
            if st.button(f"🏢 {pl['nombre']}\n📍 {pl['ubicacion']}", key=f"btn_pl_{pl['id']}", help="Clic para ver detalles"):
                st.session_state.planta_seleccionada = pl
                st.session_state.vista_actual = "planta"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col2: st.markdown("<div style='padding: 15px 0; color:#19be6b;'>📶</div>", unsafe_allow_html=True)
        with col3: st.markdown(f"<div style='padding: 15px 0; color:{'#19be6b' if not datos['alertas'] else '#ed4014'};'>{'🟢' if not datos['alertas'] else '🔴'}</div>", unsafe_allow_html=True)
        with col4: st.markdown(f"<div style='padding: 15px 0;'>{pl['capacidad']}</div>", unsafe_allow_html=True)
        with col5: st.markdown(f"<div style='padding: 15px 0;'>{datos['solar']/1000} kW</div>", unsafe_allow_html=True)
        with col6: st.markdown(f"<div style='padding: 15px 0;'>{datos['energia_diaria']} kWh</div>", unsafe_allow_html=True)
        with col7: st.markdown("<div style='padding: 15px 0; font-size:16px; color:#c5c8ce;'>⚙️ 🗑️</div>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:0; padding:0; border-color:#e8eaec;'>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# 6. VISTA 2: DASHBOARD DE UNA PLANTA (EL DETALLE)
# ==========================================
elif st.session_state.vista_actual == "planta":
    planta = st.session_state.planta_seleccionada
    datos = obtener_datos_reales(planta)
    
    # Extraer capacidad numérica para las gráficas
    cap_texto = str(planta.get("capacidad", "5"))
    solo_numeros = re.findall(r"[-+]?\d*\.\d+|\d+", cap_texto)
    cap_val = float(solo_numeros[0]) if solo_numeros else 5.0
    
    # 6.1 BREADCRUMB / BOTÓN VOLVER
    if st.button("← Volver a la lista Planta"):
        st.session_state.vista_actual = "lista"
        st.session_state.planta_seleccionada = None
        st.rerun()
        
    # 6.2 CABECERA DE LA PLANTA (Título e ID)
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap: 15px; margin-bottom: 10px;">
        <h2 style="margin:0;">{planta['nombre']}</h2>
        <span style="color:#808695; font-size:13px;">ID:{planta['id']}</span>
        <span class="badge-green">🟢 En línea</span>
        <span class="badge-green">🟢 Sin alertas</span>
    </div>
    <div style="color:#808695; font-size:12px; margin-bottom:20px;">Última actualización {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}</div>
    """, unsafe_allow_html=True)

    # 6.3 PESTAÑAS INTERNAS DE LA PLANTA (Día, Mes, Año...)
    st.markdown("""
    <div style="display:flex; gap:10px; margin-bottom:15px; align-items:center;">
        <div style="border:1px solid #2d8cf0; border-radius:4px; overflow:hidden; display:flex;">
            <div style="background:#2d8cf0; color:white; padding:5px 15px; font-size:13px;">Día</div>
            <div style="background:white; color:#515a6e; padding:5px 15px; font-size:13px; border-left:1px solid #e8eaec;">Mes</div>
            <div style="background:white; color:#515a6e; padding:5px 15px; font-size:13px; border-left:1px solid #e8eaec;">Año</div>
            <div style="background:white; color:#515a6e; padding:5px 15px; font-size:13px; border-left:1px solid #e8eaec;">Total</div>
        </div>
        <div style="color:#808695; margin-left:10px;"> < 2026/03/23 📅 > </div>
    </div>
    """, unsafe_allow_html=True)

    # 6.4 LAYOUT PRINCIPAL DEL DASHBOARD (Gráfica Izquierda / Flujo Derecha)
    col_izq, col_der = st.columns([7, 3])
    
    with col_izq:
        # TARJETAS DE KPIs (Producción, Consumo, Batería)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"""
            <div class="kpi-card" style="display:flex; justify-content:space-around; align-items:center;">
                <div>
                    <div class="kpi-val" style="color:#1c2434;">{datos['energia_diaria']} kWh</div>
                    <div class="kpi-lbl">Producción Solar</div>
                </div>
                <div style="width:1px; height:40px; background:#e8eaec;"></div>
                <div>
                    <div class="kpi-val" style="color:#1c2434;">{round(datos['energia_diaria']*0.4, 1)} kWh</div>
                    <div class="kpi-lbl">Consumo</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="kpi-card" style="display:flex; justify-content:space-around; align-items:center; padding:10px;">
                <div style="text-align:left;">
                    <div style="font-size:13px; font-weight:bold; color:#1c2434;">🔋 {round(datos['energia_diaria']*0.2,1)} kWh</div>
                    <div style="font-size:11px; color:#c5c8ce;">Cargar</div>
                    <div style="font-size:13px; font-weight:bold; color:#1c2434; margin-top:5px;">🔋 {round(datos['energia_diaria']*0.1,1)} kWh</div>
                    <div style="font-size:11px; color:#c5c8ce;">Descargar</div>
                </div>
                <div style="width:1px; height:40px; background:#e8eaec;"></div>
                <div style="text-align:left;">
                    <div style="font-size:13px; font-weight:bold; color:#1c2434;">⚡ 0 kWh</div>
                    <div style="font-size:11px; color:#c5c8ce;">Alimentado a red</div>
                    <div style="font-size:13px; font-weight:bold; color:#1c2434; margin-top:5px;">⚡ 0 kWh</div>
                    <div style="font-size:11px; color:#c5c8ce;">Desde la red</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # GRÁFICA PRINCIPAL
        st.markdown("<div style='background:white; padding:15px; border:1px solid #e8eaec; border-radius:4px;'>", unsafe_allow_html=True)
        df_historico = simular_historico_24h(cap_val)
        
        # Invertir el consumo para que se vea hacia abajo (como en Solarman)
        df_historico["Consumo Negativo"] = df_historico["Consumo"] * -1
        
        fig = px.area(
            df_historico, x="timestamp", y=["Producción Solar", "Consumo Negativo"], 
            color_discrete_map={"Producción Solar": "#2d8cf0", "Consumo Negativo": "#19be6b"}
        )
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="white", height=350,
            margin=dict(l=0, r=0, t=20, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=""),
            xaxis=dict(tickformat="%H:%M", dtick=3 * 3600000, gridcolor="#f3f3f3", title=""), 
            yaxis=dict(gridcolor="#f3f3f3", title="kW", zeroline=True, zerolinecolor="#e8eaec")
        )
        fig.update_traces(fill='tozeroy', mode='lines', line=dict(width=2))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_der:
        # PESTAÑAS LATERALES (Gráfico de flujo / Inversor / Alertas)
        st.markdown("""
        <div style="display:flex; border-bottom:1px solid #e8eaec; margin-bottom:15px; background:white; padding-top:10px; border-radius:4px 4px 0 0; border:1px solid #e8eaec; border-bottom:none;">
            <div style="padding:10px 15px; color:#2d8cf0; border-bottom:2px solid #2d8cf0; font-weight:500; font-size:13px;">Gráfico de flujo</div>
            <div style="padding:10px 15px; color:#515a6e; font-size:13px;">Inversor</div>
            <div style="padding:10px 15px; color:#515a6e; font-size:13px;">Alertas</div>
        </div>
        """, unsafe_allow_html=True)
        
        # DIAGRAMA DE FLUJO
        pot_solar = datos["solar"]
        pot_casa = datos["casa"]
        pot_bat = pot_solar - pot_casa
        soc = datos["soc"]
        color_bat = "#19be6b" if soc > 20 else "#ed4014"
        
        diagrama_svg = f"""
        <div style="background: white; border: 1px solid #e8eaec; border-top:none; border-radius: 0 0 4px 4px; padding: 20px; height: 320px; display: flex; justify-content:center; align-items: center; margin-top:-15px;">
            <svg viewBox="0 0 300 300" width="100%">
                <path d="M 150 70 V 130 M 150 170 V 230 M 90 150 H 130 M 170 150 H 210" fill="none" stroke="#e8eaec" stroke-width="3"/>
                <circle r="4" fill="#2d8cf0"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 150 70 V 130" /></circle>
                <circle r="4" fill="#ed4014"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 150 170 V 230" /></circle>
                <circle r="4" fill="#19be6b"><animateMotion dur="1.5s" repeatCount="indefinite" path="M 130 150 H 90" /></circle>
                
                <rect x="130" y="130" width="40" height="40" rx="4" fill="#515a6e"/>
                
                <g transform="translate(130, 20)">
                    <image href="https://img.icons8.com/color/48/solar-panel.png" width="40" height="40" opacity="0.8"/>
                    <text x="20" y="55" font-size="12" font-weight="bold" fill="#515a6e" text-anchor="middle">{pot_solar} W</text>
                </g>
                <g transform="translate(30, 130)">
                    <image href="https://img.icons8.com/color/48/car-battery.png" width="40" height="40"/>
                    <text x="20" y="55" font-size="12" font-weight="bold" fill="#515a6e" text-anchor="middle">{pot_bat} W</text>
                    <text x="20" y="-5" font-size="11" font-weight="bold" fill="#1c2434" text-anchor="middle">SOC: {soc}%</text>
                </g>
                <g transform="translate(230, 130)">
                    <image href="https://img.icons8.com/fluency/48/electrical.png" width="40" height="40" opacity="0.6"/>
                    <text x="20" y="55" font-size="12" font-weight="bold" fill="#808695" text-anchor="middle">0 W</text>
                </g>
                <g transform="translate(130, 240)">
                    <image href="https://img.icons8.com/color/48/home.png" width="40" height="40"/>
                    <text x="20" y="55" font-size="12" font-weight="bold" fill="#ed4014" text-anchor="middle">{pot_casa} W</text>
                </g>
            </svg>
        </div>
        """
        components.html(diagrama_svg, height=350)
        
        # TARJETA DE BENEFICIOS AMBIENTALES (Abajo a la derecha)
        st.markdown(f"""
        <div style="background:white; border:1px solid #e8eaec; border-radius:4px; padding:15px; margin-top:10px;">
            <div style="font-size:14px; font-weight:bold; color:#1c2434; margin-bottom:15px;">Beneficios ambientales y económicos</div>
            
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; align-items:center;">
                <div style="color:#515a6e; font-size:13px;">🏭 Ahorro de carbón estándar</div>
                <div style="font-weight:bold; font-size:14px; color:#1c2434;">0.54 t</div>
            </div>
            
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; align-items:center;">
                <div style="color:#515a6e; font-size:13px;">☁️ Reducción de emisiones de CO₂</div>
                <div style="font-weight:bold; font-size:14px; color:#1c2434;">1.2 t</div>
            </div>
            
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; align-items:center;">
                <div style="color:#515a6e; font-size:13px;">🌲 Árboles plantados</div>
                <div style="font-weight:bold; font-size:14px; color:#1c2434;">97.6 Árboles</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
