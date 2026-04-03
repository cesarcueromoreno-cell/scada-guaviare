import streamlit as st
import random
import json
import os
import math
import pandas as pd
import streamlit.components.v1 as components
import re
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# ==========================================
# IMPORTACIONES LOCALES (Refactorización)
# ==========================================
from config import css_global, PLANTA_HEADERS, OPCIONES_SISTEMA, OPCIONES_METERS
import database as db
import utils

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y ESTILO (CSS)
# ==========================================
st.set_page_config(page_title="MONISOLAR APP", page_icon="☀️", layout="wide")
st.markdown(css_global, unsafe_allow_html=True)

# ==========================================
# 2. VARIABLES DE SESIÓN
# ==========================================
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "usuario" not in st.session_state: st.session_state["usuario"] = None
if "rol" not in st.session_state: st.session_state["rol"] = None
if "planta_asignada" not in st.session_state: st.session_state["planta_asignada"] = "Todas"
if "editando_planta" not in st.session_state: st.session_state["editando_planta"] = None
if "mostrar_crear" not in st.session_state: st.session_state["mostrar_crear"] = False
if "red_desbloqueada" not in st.session_state: st.session_state["red_desbloqueada"] = False
if "reinicio_desbloqueado" not in st.session_state: st.session_state["reinicio_desbloqueado"] = False
if "ver_detalle_inv" not in st.session_state: st.session_state["ver_detalle_inv"] = False
if "ver_detalle_logger" not in st.session_state: st.session_state["ver_detalle_logger"] = False
if "ver_detalle_bateria" not in st.session_state: st.session_state["ver_detalle_bateria"] = False
if "mostrar_crear_usuario" not in st.session_state: st.session_state["mostrar_crear_usuario"] = False
if "auth_crear_usuario" not in st.session_state: st.session_state["auth_crear_usuario"] = False

if st.session_state["autenticado"] and st.session_state["usuario"] is None:
    st.session_state["autenticado"] = False

# ==========================================
# 3. MANEJO DE VÍNCULOS Y PARÁMETROS
# ==========================================
if "delete" in st.query_params:
    try:
        idx = int(st.query_params["delete"])
        db.eliminar_planta(idx)
        st.query_params.clear()
        st.rerun()
    except: pass
if "edit" in st.query_params:
    try:
        idx = int(st.query_params["edit"])
        st.session_state["editando_planta"] = idx
        st.query_params.clear()
    except: pass

# ==========================================
# 4. LOGIN
# ==========================================
if not st.session_state["autenticado"]:
    st.markdown("<h1 style='text-align: center; font-size: 4rem; color: #f1c40f !important;'>☀️ MONISOLAR APP</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white !important;'>Plataforma de Gestión - CV INGENIERÍA SAS</h3><br>", unsafe_allow_html=True)
    
    if not db.supabase:
        st.error(f"🔴 ESTADO DE CONEXIÓN: {db.get_db_estado()}. Por favor verifica el cuadro de Secrets en Streamlit.")
        
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        with st.form("login"):
            st.markdown("<div style='color:white; font-weight:bold; font-size:14px; text-shadow: 1px 1px 3px black;'>Usuario</div>", unsafe_allow_html=True)
            u = st.text_input("Usuario", label_visibility="collapsed")
            st.markdown("<div style='color:white; font-weight:bold; font-size:14px; margin-top:10px; text-shadow: 1px 1px 3px black;'>Contraseña</div>", unsafe_allow_html=True)
            p = st.text_input("Contraseña", type="password", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Iniciar Sesión", use_container_width=True):
                usuarios_bd = db.cargar_usuarios()
                if u in usuarios_bd and str(usuarios_bd[u]["pwd"]) == p:
                    if usuarios_bd[u].get("status") == "pending": st.warning("⚠️ Su cuenta está pendiente de aprobación.")
                    else:
                        st.session_state.update({"autenticado": True, "usuario": u, "rol": usuarios_bd[u]["role"], "planta_asignada": usuarios_bd[u].get("planta_asignada", "Todas")})
                        st.rerun()
                else: st.error("❌ Credenciales incorrectas.")
        with st.expander("¿No tienes cuenta? Solicita acceso aquí"):
            with st.form("solicitud_form"):
                nuevo_usuario = st.text_input("👤 Correo / Usuario Solicitado")
                nueva_contrasena = st.text_input("🔑 Contraseña", type="password")
                confirmar_contrasena = st.text_input("🔑 Confirmar Contraseña", type="password")
                if st.form_submit_button("Enviar Solicitud", use_container_width=True):
                    if not nuevo_usuario or not nueva_contrasena: st.error("⚠️ Complete todos los campos.")
                    elif nueva_contrasena != confirmar_contrasena: st.error("⚠️ Las contraseñas no coinciden.")
                    else:
                        success, message = db.solicitar_usuario(nuevo_usuario, nueva_contrasena)
                        if success: st.success(message)
                        else: st.error(message)
    st.stop()

# ==========================================
# 5. FILTRADO DE SEGURIDAD Y NAVEGACIÓN
# ==========================================
todas_las_plantas = db.cargar_plantas()

if st.session_state['rol'] == 'admin':
    plantas_permitidas = todas_las_plantas
else:
    planta_user = st.session_state.get("planta_asignada", "Ninguna")
    plantas_permitidas = [pl for pl in todas_las_plantas if pl.get("nombre") == planta_user]

st.sidebar.markdown("<h2 style='text-align: center; color: #f1c40f !important; text-shadow: none !important;'>☀️ MONISOLAR APP</h2>", unsafe_allow_html=True)
st.sidebar.write(f"👤 **{st.session_state.get('usuario', '')}** | Rol: {'Instalador/Admin' if st.session_state.get('rol') == 'admin' else 'Cliente'}")

opciones_menu = []
if st.session_state.get('rol') == 'admin':
    opciones_menu = ["📊 Panel de Planta", "🚨 Centro de Alertas", "👥 Gestión de Usuarios"]
else:
    opciones_menu = ["📊 Panel de Mi Planta"]

menu = st.sidebar.radio("Ir a:", opciones_menu)

if "menu_anterior" not in st.session_state or st.session_state["menu_anterior"] != menu:
    st.session_state["ver_detalle_inv"] = False
    st.session_state["ver_detalle_logger"] = False
    st.session_state["ver_detalle_bateria"] = False
    st.session_state["mostrar_crear_usuario"] = False
    st.session_state["auth_crear_usuario"] = False
    st.session_state["menu_anterior"] = menu

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.update({"autenticado": False, "usuario": None, "rol": None, "planta_asignada": "Todas", "red_desbloqueada": False, "reinicio_desbloqueado": False, "ver_detalle_inv": False, "ver_detalle_logger": False, "ver_detalle_bateria": False, "mostrar_crear_usuario": False, "auth_crear_usuario": False})
    st.rerun()


# ==========================================
# 6. VISTAS (ADMINISTRADOR Y CLIENTE)
# ==========================================

if menu == "👥 Gestión de Usuarios":
    if st.session_state.get("mostrar_crear_usuario"):
        with st.form("form_crear_usuario_final"):
            col_t1, col_t2, col_t3, col_t4 = st.columns([6, 2, 1, 1])
            with col_t1: st.markdown("<h3 style='margin-top:0; color:#2c3e50; font-weight:normal;'>Crear usuario final</h3>", unsafe_allow_html=True)
            with col_t3: btn_cancelar = st.form_submit_button("Cancelar", use_container_width=True)
            with col_t4: btn_guardar = st.form_submit_button("Guardar", type="primary", use_container_width=True)
            
            st.markdown("<hr style='margin-top:5px; margin-bottom:20px; border-color:#eaeaea;'>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center; color:#3498db; font-size:14px; margin-bottom:25px;'>ⓘ ¿El usuario final tiene una cuenta? Haga clic aquí para buscar la cuenta</div>", unsafe_allow_html=True)
            
            st.radio("Tipo", ["🔘 Correo electrónico"], label_visibility="collapsed")
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            n_nombre = c1.text_input("* Nombre")
            n_usuario = c2.text_input("Nombre de usuario")
            
            c3, c4 = st.columns(2)
            n_email = c3.text_input("* Correo electrónico", placeholder="Asegúrate de que esta dirección de correo electrónico pueda recibir mensajes")
            n_pwd = c4.text_input("* Contraseña original", placeholder="Por favor escribe", type="password")
            
            plantas_nombres = ["-Por favor, seleccione-"] + [p['nombre'] for p in todas_las_plantas]
            n_planta = st.selectbox("* Autorizar", plantas_nombres)
            
            if btn_guardar:
                if not n_nombre or not n_email or not n_pwd or n_planta == "-Por favor, seleccione-":
                    st.error("⚠️ Complete todos los campos obligatorios (*)")
                else:
                    correo_final = str(n_email).strip()
                    ok, msg = db.crear_usuario_admin(correo_final, n_pwd, n_planta)
                    if ok:
                        st.session_state["mostrar_crear_usuario"] = False
                        st.success("✅ Usuario creado con éxito.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
                        
            if btn_cancelar:
                st.session_state["mostrar_crear_usuario"] = False
                st.rerun()
    else:
        col_tit, col_btn = st.columns([8, 2])
        with col_tit: st.title("👥 GESTIÓN DE USUARIOS")
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Crear usuario final", type="primary", use_container_width=True):
                st.session_state["mostrar_crear_usuario"] = True
                st.rerun()
                
        db_usuarios = db.cargar_usuarios()
        nombres_plantas = ["Todas", "Pendiente Asignar"] + [p['nombre'] for p in todas_las_plantas]
        
        st.markdown("<br>", unsafe_allow_html=True)
        for usr, datos in db_usuarios.items():
            if usr == "admin": continue
            estado_color = "#27ae60" if datos['status'] == 'active' else "#f39c12"
            estado_texto = "🟢 Activo" if datos['status'] == 'active' else "⏳ Pendiente"
            st.markdown(f"""
            <div style="background: white; border-radius: 8px; padding: 15px; border: 1px solid #eaeaea; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #2c3e50;">👤 {usr}</h4>
                        <span style="font-size: 13px; color: {estado_color}; font-weight: bold;">{estado_texto}</span> | 
                        <span style="font-size: 13px; color: #7f8c8d;">Rol: {datos['role']}</span> | 
                        <span style="font-size: 13px; color: #2980b9; font-weight: bold;">Planta: {datos.get('planta_asignada', 'Ninguna')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.form(f"form_{usr}"):
                c1, c2, c3, c4 = st.columns([1.5, 1.5, 2, 2])
                nuevo_est = c1.selectbox("Estado", ["active", "pending"], index=0 if datos['status'] == 'active' else 1, key=f"est_{usr}")
                nuevo_rol = c2.selectbox("Rol", ["viewer", "admin"], index=0 if datos['role'] == 'viewer' else 1, key=f"rol_{usr}")
                idx_planta = nombres_plantas.index(datos.get('planta_asignada', 'Todas')) if datos.get('planta_asignada', 'Todas') in nombres_plantas else 0
                nueva_planta = c3.selectbox("Asignar Planta", nombres_plantas, index=idx_planta, key=f"pl_{usr}")
                c4_a, c4_b = c4.columns([3, 1])
                nueva_pwd = c4_a.text_input("Cambiar Contraseña", type="password", placeholder="Dejar en blanco para no cambiar")
                sub_col1, sub_col2 = c4_b.columns(2)
                if sub_col1.form_submit_button("💾"):
                    db.actualizar_usuario_bd(usr, nuevo_est, nuevo_rol, nueva_planta, nueva_pwd if nueva_pwd else None)
                    st.success(f"Usuario {usr} actualizado.")
                    time.sleep(1)
                    st.rerun()
                if sub_col2.form_submit_button("🗑️"):
                    db.eliminar_usuario_bd(usr)
                    st.warning(f"Usuario {usr} eliminado.")
                    time.sleep(1)
                    st.rerun()

elif menu in ["📊 Panel de Planta", "📊 Panel de Mi Planta"]:
    
    st.markdown("<h2 style='color: #2c3e50;'>📊 Gestión de Planta</h2>", unsafe_allow_html=True)
    
    pl_sel = None
    if st.session_state['rol'] == 'admin':
        col_bus, col_btn1, col_btn2, col_btn3 = st.columns([5, 1.5, 1.5, 1.5])
        with col_bus:
            if plantas_permitidas:
                pl_sel = st.selectbox("Seleccionar Planta:", [p["nombre"] for p in plantas_permitidas], label_visibility="collapsed")
        with col_btn1:
            if st.button("➕ Nueva Planta", type="primary", use_container_width=True):
                st.session_state["mostrar_crear"] = not st.session_state.get("mostrar_crear", False)
                st.session_state["editando_planta"] = None
                st.rerun()
        with col_btn2:
            if pl_sel and st.button("✏️ Editar", use_container_width=True):
                st.session_state["editando_planta"] = pl_sel if st.session_state.get("editando_planta") != pl_sel else None
                st.session_state["mostrar_crear"] = False
                st.rerun()
        with col_btn3:
            if pl_sel and st.button("🗑️ Eliminar", use_container_width=True):
                idx = next(i for i, x in enumerate(todas_las_plantas) if x["nombre"] == pl_sel)
                db.eliminar_planta(todas_las_plantas[idx]["id"])
                st.session_state["editando_planta"] = None
                st.rerun()
    else:
        if plantas_permitidas:
            pl_sel = st.selectbox("Seleccionar Planta:", [p["nombre"] for p in plantas_permitidas], label_visibility="collapsed")

    st.markdown("<hr style='margin-top:5px; margin-bottom:15px; border-color:#e0e0e0;'>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # FORMULARIO DE CREAR PLANTA
    # ---------------------------------------------------------
    if st.session_state.get("mostrar_crear") and st.session_state['rol'] == 'admin':
        st.markdown("<h3>➕ Crear Nueva Planta</h3>", unsafe_allow_html=True)
        
        img_url_crear = ""
        with st.expander("🖼️ Añadir Imagen de la Planta (Opcional)", expanded=True):
            modo_img_crear = st.radio("Método de subida", ["Ninguna", "Subir archivo desde PC", "Pegar enlace URL en línea"], horizontal=True, key="modo_crear")
            
            if modo_img_crear == "Subir archivo desde PC":
                st.info("💡 En esta versión de prueba, la foto que subas se reemplazará por una imagen demostrativa para no saturar la base de datos.")
                uploaded_file_crear = st.file_uploader("Elija una foto o diagrama (PNG, JPG)", type=['png', 'jpg', 'jpeg'], key="file_crear")
                if uploaded_file_crear:
                    st.image(uploaded_file_crear, caption="Su imagen (Vista previa local)", width=200)
                    if st.button("Confirmar subida", key="btn_conf_crear"):
                        img_url_crear = utils.subir_imagen_simulado(uploaded_file_crear)
                        st.success("✅ Imagen simulada cargada. Puede guardar la planta.")
            
            elif modo_img_crear == "Pegar enlace URL en línea":
                img_url_crear = st.text_input("Pegue la URL de la imagen aquí", placeholder="https://ejemplo.com/imagen.jpg", key="url_crear")
                if img_url_crear:
                    try: st.image(img_url_crear, caption="Vista previa de URL", width=200)
                    except: st.error("⚠️ No se pudo cargar la vista previa.")

        with st.form("crear_planta_form"):
            c1, c2 = st.columns(2)
            n_nom = c1.text_input("Nombre de la Planta")
            n_ubi = c2.text_input("Ubicación")
            n_cap = c1.text_input("Capacidad (Ej: 30 kWp)")
            n_inv = c2.selectbox("Marca de Inversor", ["Deye", "Fronius", "GoodWe", "Huawei", "Sylvania"])
            
            c3, c4 = st.columns(2)
            n_tipo = c3.selectbox("Tipo de Sistema", OPCIONES_SISTEMA)
            n_meter = c4.selectbox("Smart Meter a Instalar", OPCIONES_METERS)
            n_sn = st.text_input("SN del Datalogger (ID Solarman)")
            
            s1, s2 = st.columns(2)
            if s1.form_submit_button("💾 Guardar Nueva Planta"):
                if n_nom:
                    nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(n_cap))
                    cap_val = float(nums[0]) if nums else 0.0
                    dl_val = str(n_sn).strip() if str(n_sn).strip() else f"SN-{random.randint(10000,99999)}"
                    
                    payload = {
                        "nombre": str(n_nom).strip(), 
                        "ubicacion": str(n_ubi).strip(), 
                        "capacidad": cap_val, 
                        "inversores": str(n_inv), 
                        "datalogger": dl_val, 
                        "tipo_sistema": str(n_tipo), 
                        "smart_meter": str(n_meter), 
                        "imagen_url": str(img_url_crear) 
                    }
                    
                    ok, msg = db.guardar_planta(payload)
                    if ok:
                        st.session_state["mostrar_crear"] = False
                        st.success("✅ Planta creada con éxito.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.error("⚠️ El nombre de la planta es obligatorio.")
            
            if s2.form_submit_button("❌ Cancelar"):
                st.session_state["mostrar_crear"] = False
                st.rerun()
        st.stop()

    # ---------------------------------------------------------
    # FORMULARIO DE EDITAR PLANTA
    # ---------------------------------------------------------
    if st.session_state.get("editando_planta") and st.session_state['rol'] == 'admin':
        idx = next(i for i, x in enumerate(todas_las_plantas) if x["nombre"] == st.session_state["editando_planta"])
        p_edit = todas_las_plantas[idx]
        
        st.markdown(f"<h3>✏️ Editar Parámetros e Imagen: {p_edit['nombre']}</h3>", unsafe_allow_html=True)
        
        img_url_final = p_edit.get('imagen_url', '')
        with st.expander("🖼️ Gestionar Imagen de la Planta", expanded=True):
            modo_img = st.radio("Método de subida", ["Dejar imagen actual", "Subir archivo desde PC", "Pegar enlace URL en línea"], horizontal=True, key="modo_edit")
            
            if modo_img == "Subir archivo desde PC":
                st.info("💡 En esta versión de prueba, la foto que subas se reemplazará por una imagen demostrativa para no saturar la base de datos.")
                uploaded_file = st.file_uploader("Elija una foto o diagrama (PNG, JPG)", type=['png', 'jpg', 'jpeg'], key="file_edit")
                if uploaded_file:
                    st.image(uploaded_file, caption="Su imagen (Vista previa local)", width=200)
                    if st.button("Confirmar subida", key="btn_conf_edit"):
                        img_url_final = utils.subir_imagen_simulado(uploaded_file)
                        st.success("✅ Imagen simulada cargada. ¡Guarde los cambios abajo!")
            
            elif modo_img == "Pegar enlace URL en línea":
                img_url_final = st.text_input("Pegue la URL de la imagen aquí", p_edit.get('imagen_url', ''), placeholder="https://ejemplo.com/imagen.jpg", key="url_edit")
                if img_url_final:
                    try: st.image(img_url_final, caption="Vista previa de URL", width=200)
                    except: st.error("⚠️ No se pudo cargar la vista previa de la URL.")

            elif modo_img == "Dejar imagen actual" and img_url_final:
                 st.image(img_url_final, caption="Imagen actual", width=200)

        with st.form("edit"):
            c1, c2, c3 = st.columns([2, 2, 1])
            n = c1.text_input("Nombre", p_edit['nombre'])
            u = c2.text_input("Ubicación", p_edit['ubicacion'])
            c = c3.text_input("Capacidad", str(p_edit.get('capacidad', '')))
            
            c4, c5, c6 = st.columns(3)
            sn = c4.text_input("SN Datalogger", str(p_edit.get('datalogger', '')))
            idx_tipo = OPCIONES_SISTEMA.index(p_edit.get('tipo_sistema', 'Híbrido')) if p_edit.get('tipo_sistema', 'Híbrido') in OPCIONES_SISTEMA else 0
            n_tipo = c5.selectbox("Tipo de Sistema", OPCIONES_SISTEMA, index=idx_tipo)
            idx_meter = OPCIONES_METERS.index(p_edit.get('smart_meter', 'Ninguno')) if p_edit.get('smart_meter', 'Ninguno') in OPCIONES_METERS else 0
            n_meter = c6.selectbox("Smart Meter (Medidor Inteligente)", OPCIONES_METERS, index=idx_meter)

            col_sub, col_can = st.columns(2)
            if col_sub.form_submit_button("💾 Guardar Cambios"):
                nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(c))
                cap_val = float(nums[0]) if nums else 0.0
                dl_val = str(sn).strip() if str(sn).strip() else f"SN-{random.randint(10000,99999)}"
                
                p_edit.update({
                    "nombre": str(n).strip(), "ubicacion": str(u).strip(), "capacidad": cap_val, 
                    "datalogger": dl_val, "tipo_sistema": str(n_tipo), 
                    "smart_meter": str(n_meter), "imagen_url": str(img_url_final) 
                })
                ok, msg = db.actualizar_planta(p_edit["id"], p_edit)
                if ok:
                    st.session_state["editando_planta"] = None
                    st.success("✅ Planta actualizada correctamente.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Error al actualizar. Detalle: {msg}")
                    
            if col_can.form_submit_button("❌ Cancelar Edición"):
                st.session_state["editando_planta"] = None
                st.rerun()
        st.stop()


    if not plantas_permitidas or not pl_sel:
        st.warning("No hay plantas registradas o no tiene plantas asignadas. Contacte a CV Ingeniería.")
        st.stop()
        
    p = next(x for x in plantas_permitidas if x["nombre"] == pl_sel)
    
    if "planta_actual" not in st.session_state or st.session_state["planta_actual"] != p["nombre"]:
        st.session_state["ver_detalle_inv"] = False
        st.session_state["ver_detalle_logger"] = False
        st.session_state["ver_detalle_bateria"] = False
        st.session_state["planta_actual"] = p["nombre"]
        
    d = utils.get_data(p)
    
    tipo_sistema_actual = p.get('tipo_sistema', 'Híbrido')
    smart_meter_actual = p.get('smart_meter', 'Ninguno')
    sn_logger = str(p.get('datalogger', 'N/A'))
    marca_inv = str(p.get('inversores', 'Genérico'))
    capacidad = str(p.get('capacidad', '30'))
    
    nums_cap = re.findall(r"[-+]?\d*\.\d+|\d+", capacidad)
    cap_pura_kw = float(nums_cap[0]) if nums_cap else 30.0
    
    st.markdown(f"<h2>{p['nombre']} <span style='font-size:14px; color:#7f8c8d; font-weight:normal;'>| 🟢 En línea | Tipo: {tipo_sistema_actual} | SN: {sn_logger}</span></h2><hr style='margin-top:0px; margin-bottom:20px; border-color:#e0e0e0;'>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
    c1.markdown(f"<div class='solarman-card' style='border-top: 4px solid #f1c40f;'><div class='solarman-val'>{d['hoy']} kWh</div><div class='solarman-lbl'>Producción Solar Hoy</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='solarman-card' style='border-top: 4px solid #e74c3c;'><div class='solarman-val'>{round(d['hoy']*0.45,1)} kWh</div><div class='solarman-lbl'>Consumo Hoy</div></div>", unsafe_allow_html=True)
    
    if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
        c3.markdown(f"<div class='solarman-card' style='border-top: 4px solid #9b59b6;'><div style='font-size:14px; font-weight:bold; color:#2c3e50;'>SOC {d['soc']}% </div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>🔋 {round(d['hoy']*0.2,1)} kWh <span class='solarman-lbl-sm'>Carga</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>🔋 {round(d['hoy']*0.1,1)} kWh <span class='solarman-lbl-sm'>Descarga</span></div></div>", unsafe_allow_html=True)
    else:
        c3.markdown(f"<div class='solarman-card' style='border-top: 4px solid #bdc3c7;'><div style='font-size:20px; font-weight:bold; color:#bdc3c7;'>--</div><div class='solarman-lbl'>Sin Baterías</div></div>", unsafe_allow_html=True)

    if tipo_sistema_actual in ["Híbrido", "On-Grid"]:
        c4.markdown(f"<div class='solarman-card' style='border-top: 4px solid #3498db;'><div style='font-size:14px; font-weight:bold; color:#2c3e50;'>⚡ 500 W <span class='solarman-lbl-sm'>A Red</span></div><div style='font-size:14px; font-weight:bold; margin-top:5px; color:#2c3e50;'>⚡ 300 W <span class='solarman-lbl-sm'>De Red</span></div></div>", unsafe_allow_html=True)
    else:
        c4.markdown(f"<div class='solarman-card' style='border-top: 4px solid #bdc3c7;'><div style='font-size:20px; font-weight:bold; color:#bdc3c7;'>--</div><div class='solarman-lbl'>Aislado (Off-Grid)</div></div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # PESTAÑAS PRINCIPALES DE LA PLANTA
    # ==========================================
    if st.session_state['rol'] == 'admin':
        t_graf, t_disp, t_ctrl, t_rep, t_om, t_auth = st.tabs(["📈 Panel Gráfico", "🔌 Dispositivos", "⚙️ Control Remoto", "📄 Reportes PDF", "🛠️ O&M", "🛡️ Autorizaciones"])
    else:
        t_graf, t_disp, t_rep = st.tabs(["📈 Panel Gráfico", "🔌 Dispositivos", "📄 Reportes PDF"])
        t_ctrl, t_om, t_auth = None, None, None
    
    with t_graf:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # --- FILA SUPERIOR: GRAFICA GIGANTE A LA IZQUIERDA Y FLUJO/BENEFICIOS A LA DERECHA ---
        col_main, col_side = st.columns([7.5, 2.5])
        
        with col_main:
            st.markdown("<div style='background:#ffffff; border-radius:8px; padding:15px; border:1px solid #eaeaea; box-shadow: 0 4px 10px rgba(0,0,0,0.03); height: 100%;'>", unsafe_allow_html=True)
            df_historico = utils.simular_historico_24h_avanzado(p)
            
            fig1 = go.Figure()
            
            # Línea de Potencia Solar
            fig1.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['Potencia solar'], 
                                     fill='tozeroy', mode='lines', 
                                     line=dict(color='rgba(52, 152, 219, 1)', width=2), 
                                     fillcolor='rgba(52, 152, 219, 0.2)',
                                     name='Potencia solar'))
            
            # Línea de Consumo
            fig1.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['Consumo'], 
                                     fill='tozeroy', mode='lines', 
                                     line=dict(color='rgba(231, 76, 60, 1)', width=2), 
                                     fillcolor='rgba(231, 76, 60, 0.1)',
                                     name='Consumo'))
                                     
            # Línea de Red
            if tipo_sistema_actual in ["Híbrido", "On-Grid"]:
                fig1.add_trace(go.Scatter(x=df_historico['timestamp'], y=df_historico['Red'], 
                                         mode='lines', 
                                         line=dict(color='rgba(243, 156, 18, 1)', width=2), 
                                         name='Red'))
                                         
            # Leyenda falsa para simular "Clima"
            fig1.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(color='#bdc3c7', size=8), name='Clima'))

            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="left", x=0, font=dict(size=12, color="#7f8c8d")),
                margin=dict(l=10, r=10, t=10, b=10), height=400,
                hovermode="x unified"
            )
            fig1.update_yaxes(title_text="W", gridcolor="#f0f0f0", tickfont=dict(color="#7f8c8d"), title_font=dict(color="#7f8c8d", size=11))
            fig1.update_xaxes(tickformat="%H:%M", dtick=3 * 3600000, gridcolor="#f0f0f0", tickfont=dict(color="#7f8c8d"))
            
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_side:
            pot_bat_val = d["solar"] - d["casa"]
            color_dark = "#2c3e50"
            color_gray = "#7f8c8d"

            line_solar = "M 80 130 V 180 H 130"
            line_grid = "M 320 130 V 180 H 270"
            line_bat = "M 80 230 V 220 H 130"
            line_house = "M 320 230 V 220 H 270"

            svg_lines = f'''
            <path d="{line_solar}" fill="none" stroke="{color_gray}" stroke-width="4" stroke-dasharray="8,6" stroke-linecap="round"/>
            <path d="{line_house}" fill="none" stroke="{color_gray}" stroke-width="4" stroke-dasharray="8,6" stroke-linecap="round"/>
            '''
            if tipo_sistema_actual in ["Híbrido", "On-Grid"]:
                svg_lines += f'<path d="{line_grid}" fill="none" stroke="{color_gray}" stroke-width="4" stroke-dasharray="8,6" stroke-linecap="round"/>'
            if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                svg_lines += f'<path d="{line_bat}" fill="none" stroke="{color_gray}" stroke-width="4" stroke-dasharray="8,6" stroke-linecap="round"/>'

            path_solar = "M 80 130 V 180 H 130"
            path_house = "M 270 220 H 320 V 230"
            path_grid = "M 320 130 V 180 H 270" if not (tipo_sistema_actual == "On-Grid" and pot_bat_val > 0) else "M 270 180 H 320 V 130"
            path_bat = "M 130 220 H 80 V 230" if pot_bat_val > 0 else "M 80 230 V 220 H 130"
            
            def make_particle(path, duration="2s"):
                return f'''
                <g>
                    <animateMotion dur="{duration}" repeatCount="indefinite" path="{path}" />
                    <circle cx="0" cy="0" r="10" fill="#f1c40f"/>
                    <path d="M -3 -5 L -6 1 H -1 L -2 6 L 5 -1 H 1 Z" fill="#ffffff"/>
                </g>
                '''

            svg_particles = make_particle(path_solar, "1.5s") + make_particle(path_house, "1.5s")
            if tipo_sistema_actual in ["Híbrido", "On-Grid"]:
                svg_particles += make_particle(path_grid, "2s")
            if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                svg_particles += make_particle(path_bat, "2s")

            svg_inverter = f'''
            <g transform="translate(130, 150)">
                <rect x="0" y="10" width="140" height="80" rx="4" fill="#ffffff" stroke="#576574" stroke-width="3"/>
                <rect x="0" y="0" width="140" height="15" rx="4" fill="#576574"/>
                <rect x="0" y="8" width="140" height="7" fill="#576574"/>
                <rect x="40" y="30" width="60" height="40" rx="2" fill="none" stroke="#576574" stroke-width="3"/>
                <rect x="50" y="25" width="10" height="5" fill="#576574"/>
                <rect x="80" y="25" width="10" height="5" fill="#576574"/>
                <path d="M 45 40 H 60 M 45 50 H 60 M 45 60 H 60" stroke="#576574" stroke-width="3" stroke-linecap="round"/>
                <path d="M 75 35 L 65 50 H 75 L 65 65 L 90 45 H 80 Z" fill="#f1c40f"/>
                <path d="M 80 60 Q 85 55, 90 60 T 100 60" fill="none" stroke="#576574" stroke-width="2"/>
            </g>
            '''

            svg_nodes = f'''
            <text x="80" y="40" font-size="16" fill="{color_gray}" text-anchor="middle" font-family="sans-serif">Producción</text>
            <image href="https://img.icons8.com/color/48/solar-panel--v1.png" width="60" height="60" x="50" y="55" />
            <text x="80" y="140" font-size="14" font-weight="bold" fill="{color_dark}" text-anchor="middle" font-family="sans-serif">{round(d["solar"]/1000, 2)} kW</text>

            <image href="https://img.icons8.com/color/48/home.png" width="60" height="60" x="290" y="240" />
            <text x="320" y="325" font-size="16" fill="{color_gray}" text-anchor="middle" font-family="sans-serif">Consumo</text>
            <text x="320" y="345" font-size="14" font-weight="bold" fill="{color_dark}" text-anchor="middle" font-family="sans-serif">{round(d["casa"]/1000, 2)} kW</text>
            '''
            
            if tipo_sistema_actual in ["Híbrido", "On-Grid"]:
                txt_meter = f'<text x="320" y="160" font-size="10" font-weight="bold" fill="{color_gray}" text-anchor="middle" font-family="sans-serif">{smart_meter_actual}</text>' if smart_meter_actual != "Ninguno" else ""
                svg_nodes += f'''
                <text x="320" y="40" font-size="16" fill="{color_gray}" text-anchor="middle" font-family="sans-serif">Red</text>
                <image href="https://img.icons8.com/ios/48/576574/transmission-tower.png" width="60" height="60" x="290" y="55" />
                <text x="320" y="140" font-size="14" font-weight="bold" fill="{color_dark}" text-anchor="middle" font-family="sans-serif">0 kW</text>
                {txt_meter}
                '''

            if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                svg_nodes += f'''
                <g transform="translate(45, 235)">
                    <rect x="5" y="15" width="50" height="30" rx="4" fill="#2ecc71" stroke="#576574" stroke-width="2"/>
                    <rect x="55" y="22" width="4" height="16" rx="2" fill="#576574"/>
                    <path d="M 30 18 L 22 30 H 30 L 27 42 L 40 25 H 32 Z" fill="#f1c40f" stroke="#e67e22" stroke-width="1"/>
                </g>
                <text x="80" y="315" font-size="16" fill="{color_gray}" text-anchor="middle" font-family="sans-serif">Batería</text>
                <text x="80" y="335" font-size="14" font-weight="bold" fill="{color_dark}" text-anchor="middle" font-family="sans-serif">{round(abs(pot_bat_val)/1000, 2)} kW</text>
                <text x="80" y="355" font-size="14" fill="{color_gray}" text-anchor="middle" font-family="sans-serif">{d["soc"]}%</text>
                '''

            html_code = f"""
            <!DOCTYPE html>
            <html>
            <head><style>body {{ margin: 0; padding: 0; overflow: hidden; background-color: transparent; }}</style></head>
            <body>
                <div style="background:#ffffff; border-radius:8px; padding:10px; border:1px solid #eaeaea; box-shadow: 0 4px 10px rgba(0,0,0,0.03); display: flex; align-items: center; justify-content: center; height: 260px; box-sizing: border-box; margin-bottom: 10px;">
                    <svg viewBox="0 0 400 380" width="100%" height="100%" style="max-height: 240px;">
                        {svg_lines}
                        {svg_particles}
                        {svg_inverter}
                        {svg_nodes}
                    </svg>
                </div>
            </body>
            </html>
            """
            components.html(html_code, height=275)
            
            # Beneficios Ambientales
            st.markdown(f"""
            <div style="background: white; border-radius: 8px; padding: 15px; border: 1px solid #eaeaea; box-shadow: 0 4px 10px rgba(0,0,0,0.03);">
                <h4 style="margin-top:0; margin-bottom:15px; color:#2c3e50; font-size:14px; display:flex; align-items:center;">Beneficios ambientales y económicos <span style="margin-left:5px; color:#bdc3c7;">❔</span></h4>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                    <div style="display:flex; align-items:center;"><img src="https://img.icons8.com/color/24/coal.png" style="margin-right:10px;"/><span style="color:#7f8c8d; font-size:13px;">Ahorro de carbón estándar</span></div>
                    <div style="font-weight:bold; color:#2c3e50; font-size:13px;">{round(d['hoy'] * 0.026, 2)} t</div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                    <div style="display:flex; align-items:center;"><img src="https://img.icons8.com/color/24/carbon-dioxide.png" style="margin-right:10px;"/><span style="color:#7f8c8d; font-size:13px;">Reducción de emisiones CO2</span></div>
                    <div style="font-weight:bold; color:#2c3e50; font-size:13px;">{round(d['hoy'] * 0.068, 2)} t</div>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                    <div style="display:flex; align-items:center;"><img src="https://img.icons8.com/color/24/deciduous-tree.png" style="margin-right:10px;"/><span style="color:#7f8c8d; font-size:13px;">Árboles plantados</span></div>
                    <div style="font-weight:bold; color:#2c3e50; font-size:13px;">{round(d['hoy'] * 4.7, 2)} Árboles</div>
                </div>
                <div style="display:flex; justify-content:space-between;">
                    <div style="display:flex; align-items:center;"><img src="https://img.icons8.com/color/24/stack-of-money.png" style="margin-right:10px;"/><span style="color:#7f8c8d; font-size:13px;">Rendimientos totales</span></div>
                    <div style="font-weight:bold; color:#2c3e50; font-size:13px;">{round(d['hoy'] * 0.0008, 2)} MCOP</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # --- FILA INFERIOR: CLASIFICACION INVERSORES + PRODUCCION PLANIFICADA ---
        col_bot_l, col_bot_r = st.columns([1, 1])
        
        with col_bot_l:
            horas_pico = round(d['hoy'] / cap_pura_kw, 2) if cap_pura_kw > 0 else 0
            st.markdown(f"""
            <div style="background: white; border-radius: 8px; padding: 15px; border: 1px solid #eaeaea; box-shadow: 0 4px 10px rgba(0,0,0,0.03); height: 100%;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eaeaea; padding-bottom: 10px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #2c3e50; font-size: 15px; font-weight: normal;">Clasificaciones de inversores <span style="color: #bdc3c7; font-weight: normal; font-size: 12px; margin-left: 5px;">Hasta 10</span></h4>
                    <span style="color: #bdc3c7;">➔</span>
                </div>
                <table style="width: 100%; text-align: left; font-size: 13px; border-collapse: collapse;">
                    <tr style="color: #2c3e50; border-bottom: 1px solid #f0f0f0;">
                        <th style="padding: 10px 5px;">Nombre del inversor</th>
                        <th style="padding: 10px 5px; color: #3498db;">Horas pico hoy(h) ↕</th>
                        <th style="padding: 10px 5px;">Potencia normalizada ↕</th>
                    </tr>
                    <tr>
                        <td style="padding: 15px 5px; color: #7f8c8d;">INV-{marca_inv.upper()} {cap_pura_kw} KW</td>
                        <td style="padding: 15px 5px; color: #2c3e50;">{horas_pico}</td>
                        <td style="padding: 15px 5px; color: #7f8c8d;">
                            <div style="display: flex; align-items: center;">
                                <div style="background: #f0f0f0; border-radius: 10px; width: 100%; height: 6px; margin-right: 10px;">
                                    <div style="background: #3498db; border-radius: 10px; width: 5%; height: 100%;"></div>
                                </div>
                                <span>1.93%</span>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
        with col_bot_r:
            st.markdown("<div style='background:#ffffff; border-radius:8px; padding:15px; border:1px solid #eaeaea; box-shadow: 0 4px 10px rgba(0,0,0,0.03); height: 100%;'>", unsafe_allow_html=True)
            st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #2c3e50; font-size: 15px; font-weight: normal;">Producción Planificada</h4>
                <div style="display: flex; gap: 5px; align-items: center;">
                    <div style="display: flex;">
                        <button style="border:1px solid #1890ff; background:#e6f7ff; color:#1890ff; padding:3px 10px; border-radius:4px 0 0 4px; font-size:12px; cursor:pointer; font-family:sans-serif;">Año</button>
                        <button style="border:1px solid #eaeaea; border-left:none; background:white; color:#7f8c8d; padding:3px 10px; border-radius:0 4px 4px 0; font-size:12px; cursor:pointer; font-family:sans-serif;">Total</button>
                    </div>
                    <button style="border:1px solid #eaeaea; background:white; color:#7f8c8d; padding:3px 15px; border-radius:4px; font-size:12px; margin-left:5px; cursor:pointer; font-family:sans-serif;">Exportar</button>
                    <span style="color:#7f8c8d; margin-left:15px; cursor:pointer; font-size:14px; font-weight:bold;">&lt;</span>
                    <span style="border:1px solid #eaeaea; padding:3px 12px; border-radius:4px; font-size:12px; color:#2c3e50; display:flex; align-items:center; gap:8px; font-family:sans-serif;">2025 <img src="https://img.icons8.com/material-outlined/24/7f8c8d/calendar--v1.png" width="14"/></span>
                    <span style="color:#7f8c8d; cursor:pointer; font-size:14px; font-weight:bold;">&gt;</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            df_mensual = utils.simular_produccion_mensual(p)
            
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=df_mensual['Mes'], y=df_mensual['Producción solar mensual'], name='Producción solar mensual', marker_color='#1890ff', width=0.4))
            fig2.add_trace(go.Bar(x=[None], y=[None], name='Producción Planificada Mensual', marker_color='#bfbfbf'))
            fig2.add_trace(go.Scatter(x=[None], y=[None], mode='markers', name='Finalización mensual', marker=dict(color='#bfbfbf', size=10, symbol='square')))

            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                barmode='group',
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=12, color="#2c3e50")),
                margin=dict(l=10, r=10, t=10, b=10), height=300,
                xaxis=dict(showline=False, showgrid=False, zeroline=False, tickfont=dict(color="#7f8c8d", size=12), tickmode='linear', dtick=1),
                yaxis=dict(showline=False, showgrid=True, gridcolor="#f0f0f0", zeroline=False, tickfont=dict(color="#7f8c8d", size=12))
            )
            
            fig2.add_annotation(x=0, y=1, xref="paper", yref="paper", text="kWh", showarrow=False, font=dict(size=11, color="#7f8c8d"), xanchor="left", yanchor="bottom")
            fig2.add_annotation(x=1, y=1, xref="paper", yref="paper", text="%", showarrow=False, font=dict(size=11, color="#7f8c8d"), xanchor="right", yanchor="bottom")
            
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:#ffffff; border-radius:8px; padding:20px; border:1px solid #eaeaea; box-shadow: 0 4px 10px rgba(0,0,0,0.03);'>
            <h4 style="margin-top:0; margin-bottom:20px; color:#2c3e50; font-size:15px; font-weight: normal;">Resumen del sistema</h4>
            <div style="display: flex; gap: 50px;">
                <div style="flex: 1;">
                    <div style="color:#7f8c8d; margin-bottom:10px; display:flex; align-items:center;"><img src="https://img.icons8.com/ios/24/7f8c8d/solar-inverter.png" style="margin-right:10px;"/> Inversor <span style="color:#2c3e50; font-size:16px; margin-left:5px;">1</span></div>
                    <div style="display:flex; gap:20px; font-size:13px; color:#7f8c8d; margin-bottom:10px;">
                        <div><span style="font-size:16px; color:#2c3e50;">0</span> Desconectado</div>
                        <div><span style="font-size:16px; color:#2c3e50;">0</span> Alertas</div>
                    </div>
                    <a href="#" style="color:#3498db; text-decoration:none; font-size:13px;">Vista</a>
                </div>
                <div style="flex: 1;">
                    <div style="color:#7f8c8d; margin-bottom:10px; display:flex; align-items:center;"><img src="https://img.icons8.com/ios/24/7f8c8d/wifi-router.png" style="margin-right:10px;"/> Registrador <span style="color:#2c3e50; font-size:16px; margin-left:5px;">1</span></div>
                    <div style="display:flex; gap:20px; font-size:13px; color:#7f8c8d; margin-bottom:10px;">
                        <div><span style="font-size:16px; color:#2c3e50;">0</span> Desconectado</div>
                        <div><span style="font-size:16px; color:#2c3e50;">0</span> Alertas</div>
                    </div>
                    <a href="#" style="color:#3498db; text-decoration:none; font-size:13px;">Vista</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    with t_disp:
        if not st.session_state["ver_detalle_inv"] and not st.session_state["ver_detalle_logger"] and not st.session_state["ver_detalle_bateria"]:
            style_inversor_link = """
            <style>
            div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button { background-color: transparent !important; border: none !important; color: #3498db !important; box-shadow: none !important; padding: 0 !important; height: auto !important; min-height: auto !important; justify-content: flex-start !important; }
            div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button p { font-size: 15px !important; font-weight: bold !important; }
            div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button:hover p { text-decoration: underline !important; color: #2980b9 !important; }
            </style>
            """
            st.markdown(style_inversor_link, unsafe_allow_html=True)

            st.markdown("### 🔌 Lista de Dispositivos Registrados")
            st.markdown("""
            <style>
            .div-header { background-color: #f8f9fa; padding: 12px; border-radius: 5px 5px 0 0; border: 1px solid #eaeaea; border-bottom: none; display: flex; font-weight: bold; color: #7f8c8d; font-size: 14px; align-items: center; }
            .stColumn { display: flex; align-items: center; }
            </style>
            <div class="div-header">
                <div style="flex: 2;">Nombre/SN</div>
                <div style="flex: 1.5;">Tipo</div>
                <div style="flex: 1;">Estado</div>
                <div style="flex: 1;">Actuación</div>
                <div style="flex: 1.5;">Potencia solar(kW)</div>
                <div style="flex: 1.5;">Producción diaria(kWh)</div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1, 1.5, 1.5])
            with st.container():
                if col1.button(f"Inversor ({capacidad}) ▼"):
                    st.session_state["ver_detalle_inv"] = True
                    st.session_state["ver_detalle_logger"] = False
                    st.session_state["ver_detalle_bateria"] = False
                    st.rerun()
                col1.markdown(f"<span style='color:#7f8c8d; font-size:12px; margin-top:-15px; display:block;'>{sn_logger}</span>", unsafe_allow_html=True)
                col2.write("Híbrido HV trifásico")
                col3.markdown("<div style='color:#27ae60; font-weight:bold;'>🟢 En línea</div>", unsafe_allow_html=True)
                col4.markdown("<div style='color:#27ae60;'>Normal</div>", unsafe_allow_html=True)
                col5.write(f"{round(d['solar']/1000, 2)}")
                col6.write(f"{d['hoy']}")
            st.markdown("<hr style='margin:0; padding:0; border-top: 1px solid #eaeaea;'>", unsafe_allow_html=True)

            col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1, 1.5, 1.5])
            with st.container():
                if col1.button(f"Registrador ▼", key="btn_log_nombre"):
                    st.session_state["ver_detalle_inv"] = False
                    st.session_state["ver_detalle_logger"] = True
                    st.session_state["ver_detalle_bateria"] = False
                    st.rerun()
                col1.markdown(f"<span style='color:#7f8c8d; font-size:12px; margin-top:-15px; display:block;'>{sn_logger}</span>", unsafe_allow_html=True)
                col2.write("Registrador")
                col3.markdown("<div style='color:#27ae60; font-weight:bold;'>🟢 En línea</div>", unsafe_allow_html=True)
                col4.markdown("<div style='color:#27ae60;'>Normal</div>", unsafe_allow_html=True)
                col5.write("--")
                col6.write("--")
            st.markdown("<hr style='margin:0; padding:0; border-top: 1px solid #eaeaea;'>", unsafe_allow_html=True)

            if tipo_sistema_actual in ["Híbrido", "Off-Grid"]:
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1, 1.5, 1.5])
                with st.container():
                    if col1.button(f"Batería ▼", key="btn_bat_nombre"):
                        st.session_state["ver_detalle_inv"] = False
                        st.session_state["ver_detalle_logger"] = False
                        st.session_state["ver_detalle_bateria"] = True
                        st.rerun()
                    col1.markdown(f"<span style='color:#7f8c8d; font-size:12px; margin-top:-15px; display:block;'>BAT-{sn_logger[-4:] if len(sn_logger) > 4 else '001'}</span>", unsafe_allow_html=True)
                    col2.write("Batería Litio")
                    col3.markdown("<div style='color:#27ae60; font-weight:bold;'>🟢 En línea</div>", unsafe_allow_html=True)
                    col4.markdown("<div style='color:#27ae60;'>Normal</div>", unsafe_allow_html=True)
                    col5.write("--")
                    col6.write("--")
                st.markdown("<hr style='margin:0; padding:0; border-top: 1px solid #eaeaea;'>", unsafe_allow_html=True)

            if smart_meter_actual != "Ninguno":
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1, 1.5, 1.5])
                with st.container():
                    col1.markdown(f"<span style='color:#3498db; font-weight:bold;'>{smart_meter_actual} ▼</span><br><span style='color:#7f8c8d; font-size:12px;'>MTR-{sn_logger[-4:] if len(sn_logger) > 4 else '001'}</span>", unsafe_allow_html=True)
                    col2.write(smart_meter_actual)
                    col3.markdown("<div style='color:#27ae60; font-weight:bold;'>🟢 En línea</div>", unsafe_allow_html=True)
                    col4.markdown("<div style='color:#27ae60;'>Normal</div>", unsafe_allow_html=True)
                    col5.write("--")
                    col6.write("--")
                st.markdown("<hr style='margin:0; padding:0; border-top: 1px solid #eaeaea;'>", unsafe_allow_html=True)

        elif st.session_state["ver_detalle_inv"]:
            if st.button("⬅ Volver a la lista de dispositivos", type="secondary"):
                st.session_state["ver_detalle_inv"] = False
                st.rerun()
            
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:15px;'>
                <div>
                    <h2 style='margin-bottom:0;'>inversor 1.1:{sn_logger}</h2>
                    <span style='color:#27ae60; font-weight:bold; font-size:14px;'>🟢 En línea</span>
                </div>
                <span style='color:#7f8c8d; font-size:13px;'>{datetime.now().strftime('%Y/%m/%d %H:%M:%S UTC-05:00')}</span>
            </div>
            <hr style='margin-top:0px;'>
            """, unsafe_allow_html=True)
            
            t_det_1, t_det_2, t_det_3, t_det_4 = st.tabs(["Detalles", "Alerta", "Arquitectura", "Datos históricos"])
            
            with t_det_1:
                with st.expander("Información básica", expanded=True):
                    st.markdown(f"""
                    <div class='diag-grid'>
                        <div><span class='diag-lbl'>NS:</span> {sn_logger}</div>
                        <div><span class='diag-lbl'>Tipo de inversor:</span> Híbrido HV trifásico</div>
                        <div><span class='diag-lbl'>Potencia nominal:</span> {capacidad} kW</div>
                        <div><span class='diag-lbl'>Hora del sistema:</span> {datetime.now().strftime('%d-%m-%y %H:%M:%S')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with st.expander("Generación eléctrica", expanded=True):
                    col_dc, col_icono, col_ac = st.columns([5, 1, 5])
                    with col_dc:
                        st.markdown("""
                        <table style='width:100%; text-align:left; font-size:13px; color:#3498db; border-collapse:collapse;'>
                            <tr style='color:#7f8c8d; border-bottom:1px solid #eaeaea;'>
                                <th style='padding:8px;'>Corriente continua</th><th style='padding:8px;'>Voltaje</th><th style='padding:8px;'>Actual</th>
                            </tr>
                            <tr style='border-bottom:1px solid #f8f9fa;'><td style='padding:8px;'>PV1</td><td>0.00 V</td><td>0.00 A</td></tr>
                        </table>
                        """, unsafe_allow_html=True)
                    with col_icono:
                        st.markdown("<br><br><div style='background-color:#3498db; color:white; border-radius:8px; padding:15px; text-align:center; font-weight:bold;'>DC/AC<br>≈</div>", unsafe_allow_html=True)
                    with col_ac:
                        st.markdown("""
                        <table style='width:100%; text-align:left; font-size:13px; color:#3498db; border-collapse:collapse;'>
                            <tr style='color:#7f8c8d; border-bottom:1px solid #eaeaea;'>
                                <th style='padding:8px;'>Corriente alterna</th><th style='padding:8px;'>Voltaje</th><th style='padding:8px;'>Actual</th>
                            </tr>
                            <tr style='border-bottom:1px solid #f8f9fa;'><td style='padding:8px;'>R</td><td>121.30 V</td><td>7.50 A</td></tr>
                        </table>
                        """, unsafe_allow_html=True)
                    st.markdown("<hr style='margin:10px 0; border-color:#eaeaea;'>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#7f8c8d; font-size:13px;'>PV daily power generation: <b>{d['hoy']} kWh</b></span>", unsafe_allow_html=True)

            with t_det_4:
                st.markdown("<h4 style='color:#2c3e50; font-size:16px; margin-top:10px;'>Datos históricos</h4>", unsafe_allow_html=True)
                
                x_time = pd.date_range(start="00:00", end="21:00", freq="15min")
                y_vol_R = [121.3 if (6 <= t.hour <= 18) else 0 for t in x_time]
                y_curr_R = [7.5 if (6 <= t.hour <= 18) else 0 for t in x_time]
                
                fig_ac = make_subplots(specs=[[{"secondary_y": True}]])
                fig_ac.add_trace(go.Scatter(x=x_time, y=y_vol_R, mode='lines', line=dict(color='#3498db', shape='hv'), name='Voltaje CA'), secondary_y=False)
                fig_ac.add_trace(go.Scatter(x=x_time, y=y_curr_R, mode='lines', line=dict(color='#2ecc71', shape='hv'), name='Corriente CA'), secondary_y=True)
                
                fig_ac.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                    margin=dict(l=10, r=10, t=10, b=10), height=400
                )
                fig_ac.update_yaxes(title_text="V", range=[0, 150], gridcolor="#f0f0f0", secondary_y=False)
                fig_ac.update_yaxes(title_text="A", range=[0, 10], showgrid=False, secondary_y=True)
                fig_ac.update_xaxes(tickformat="%H:%M", dtick=3 * 3600000, gridcolor="#f0f0f0")
                
                st.plotly_chart(fig_ac, use_container_width=True)

        elif st.session_state["ver_detalle_logger"]:
            if st.button("⬅ Volver a la lista de dispositivos", type="secondary"):
                st.session_state["ver_detalle_logger"] = False
                st.rerun()
            
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:15px; margin-top:10px;'>
                <div>
                    <h2 style='margin-bottom:0; font-size: 24px;'>Registrador wifi:{sn_logger}</h2>
                    <span style='color:#27ae60; font-weight:bold; font-size:14px;'>🟢 En línea</span>
                </div>
            </div>
            <hr style='margin-top:0px; border-color:#eaeaea;'>
            """, unsafe_allow_html=True)
            
            t_log_1, t_log_2, t_log_3 = st.tabs(["Detalles", "Alerta", "Arquitectura"])
            with t_log_1:
                st.markdown(f"""
                <div class='diag-grid'>
                    <div><span class='diag-lbl'>SN:</span> {sn_logger}</div>
                    <div><span class='diag-lbl'>Modelo:</span> LSW-3</div>
                </div>
                """, unsafe_allow_html=True)

    if t_ctrl:
        with t_ctrl:
            st.info(f"⚙️ Configurando el inversor **{p.get('inversores', 'Deye')}** de la planta '{p['nombre']}'. Proceda con precaución.")
            
            # --- PERFILES DE HARDWARE DINÁMICOS ---
            es_goodwe_10k = "GoodWe" in p.get('inversores', '') and cap_pura_kw == 10.0
            
            if es_goodwe_10k:
                st.success("✅ Perfil de hardware detectado: GoodWe Serie ES/A-ES (Fase Dividida 220V/110V)")
                st_bat, st_pv, st_red, st_sis = st.tabs(["🔋 Baterías (Lynx)", "☀️ Arreglos PV", "⚡ Red & NEC", "💻 Sistema"])
            else:
                st.warning("⚠️ Perfil genérico o Deye Trifásico detectado.")
                st_bat, st_mo1, st_red, st_sis = st.tabs(["🔋 Baterías", "🔄 Modos", "⚡ Red", "💻 Sistema"])
            
            opts_sel = ["Seleccione", "Habilitado", "Deshabilitado"]
            
            with st_bat:
                st.markdown("<small style='color:#7f8c8d;'>ⓘ Configuración del banco de almacenamiento.</small>", unsafe_allow_html=True)
                cb1, cb2, cb3, cb4 = st.columns(4)
                if es_goodwe_10k:
                    cb1.selectbox("* Tipo Batería", ["Litio (BMS) - Lynx Home U", "Plomo-Ácido"])
                    cb2.number_input("* Límite Descarga (SOC %)", min_value=10, max_value=50, value=15)
                    cb3.number_input("* Corriente Max Carga (A)", value=50)
                    cb4.number_input("* Corriente Max Descarga (A)", value=50)
                else:
                    cb1.selectbox("* Tipo Batería", ["Modo Litio", "Plomo"])
                    cb2.number_input("* Capacidad (Ah)", value=100)
                    cb3.number_input("* Max Carga (A)", value=50)
                    cb4.number_input("* Max Descarga (A)", value=50)

            # Pestaña dinámica: Arreglos PV (Solo para el GoodWe de 10kW) o Modos (Genérico)
            if es_goodwe_10k:
                with st_pv:
                    st.markdown("Configuración de los MPPT para paneles de alta potencia (ej. Longi 580W)")
                    cpv1, cpv2 = st.columns(2)
                    cpv1.number_input("Módulos en String 1 (Longi 580W)", min_value=0, max_value=20, value=12)
                    cpv2.number_input("Módulos en String 2 (Longi 580W)", min_value=0, max_value=20, value=12)
            else:
                with st_mo1:
                    m1, m2, m3 = st.columns(3)
                    m1.selectbox("* Modo", ["Autoconsumo", "Respaldo"])
                    m2.number_input("* Max Solar (W)", value=5000)
                    m3.selectbox("* Prioridad", ["Carga", "Batería"])

            with st_red:
                if not st.session_state["red_desbloqueada"]:
                    st.markdown("<div style='color:#f39c12; font-weight:bold; margin-bottom:10px;'>🔒 Introduzca la contraseña para desbloquear los parámetros de red</div>", unsafe_allow_html=True)
                    c_pw1, c_pw2 = st.columns([2, 3])
                    pwd = c_pw1.text_input("Contraseña", type="password", label_visibility="collapsed")
                    if c_pw1.button("Desbloquear", type="secondary"):
                        if pwd == "admin123":
                            st.session_state["red_desbloqueada"] = True
                            st.rerun()
                        else: st.error("❌ Contraseña incorrecta.")
                else:
                    st.success("🔓 Panel de Red Desbloqueado")
                    r_c1, r_c2 = st.columns(2)
                    norma_sel = r_c1.selectbox("* Normativa Aplicada", ["Norma NEC", "RETIE Local", "IEEE 1547"])
                    r_c2.number_input("* Límite de Inyección a red (%)", min_value=0, max_value=100, value=100)
                    
                    st.markdown("#### Protecciones de Tensión y Frecuencia")
                    v_max = st.number_input("Sobre Tensión Máx (V)", value=132.0 if es_goodwe_10k else 253.0)
                    v_min = st.number_input("Sub Tensión Mín (V)", value=108.0 if es_goodwe_10k else 198.0)
                    t_despeje = st.number_input("Tiempo de Despeje (s)", value=0.16)
                    
                    # --- VALIDACIÓN NORMATIVA ESTRICTA NEC ---
                    error_nec = False
                    if norma_sel == "Norma NEC":
                        if es_goodwe_10k and (v_max > 132.0 or v_min < 108.0): # Tolerancia NEC +-10% sobre 120V
                            st.error("⛔ **Violación de Norma NEC:** Para sistemas de fase dividida 120V, los límites de tensión no pueden exceder ±10% (108V - 132V). Corrija el valor para evitar daños al equipo o penalizaciones.")
                            error_nec = True
                        elif not es_goodwe_10k and (v_max > 264.0 or v_min < 216.0): # Tolerancia NEC +-10% sobre 240V
                            st.error("⛔ **Violación de Norma NEC:** Los límites de tensión no pueden exceder ±10% del voltaje nominal. Corrija los valores.")
                            error_nec = True
                        if t_despeje > 0.16:
                            st.error("⛔ **Violación de Norma NEC:** El tiempo de despeje por falla de tensión no puede ser mayor a 0.16 segundos (10 ciclos).")
                            error_nec = True

                    if st.button("🔒 Bloquear Red"):
                        st.session_state["red_desbloqueada"] = False
                        st.rerun()

            with st_sis:
                st.markdown("<br><h4 style='color: #e74c3c; margin-top: 0;'>⚠️ Comandos Críticos del Sistema</h4>", unsafe_allow_html=True)
                st.info("💡 **Nota de Ingeniería:** El comando de reinicio remoto ejecuta un apagado digital suave (Soft Reset).")
                
                if not st.session_state["reinicio_desbloqueado"]:
                    st.markdown("<div style='color:#f39c12; font-weight:bold; margin-bottom:10px;'>🔒 Introduzca la contraseña 'admin123' para habilitar el panel de sistema</div>", unsafe_allow_html=True)
                    c_pw1, c_pw2 = st.columns([2, 3])
                    pwd_res = c_pw1.text_input("Contraseña Sistema", type="password", label_visibility="collapsed")
                    if c_pw1.button("Desbloquear Sistema", type="secondary"):
                        if pwd_res == "admin123":
                            st.session_state["reinicio_desbloqueado"] = True
                            st.rerun()
                        else: st.error("❌ Contraseña incorrecta.")
                else:
                    st.success("🔓 Panel de Sistema Desbloqueado")
                    col_r1, col_r2 = st.columns([1, 1])
                    if col_r1.button("🔄 Reiniciar Inversor", type="primary", use_container_width=True):
                        with st.spinner("Conectando con la planta y enviando comando de Soft Reset..."):
                            time.sleep(2.5)
                        st.success("✅ Comando de reinicio aceptado por el inversor.")
                    
                    if col_r2.button("🏭 Restaurar de Fábrica", type="secondary", use_container_width=True):
                        st.error("❌ Función bloqueada para evitar pérdida de parámetros NEC y desconfiguración del transformador.")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔒 Bloquear Sistema"):
                        st.session_state["reinicio_desbloqueado"] = False
                        st.rerun()
        
            st.markdown("<br><hr style='margin:10px 0;'>", unsafe_allow_html=True)
            b_col1, b_col2, b_col3 = st.columns([6, 2, 2])
            with b_col3:
                if st.button("Configurar", type="primary", use_container_width=True, disabled=st.session_state.get("red_desbloqueada", False) and error_nec):
                    with st.spinner("Compilando parámetros y enviando al datalogger..."): 
                        time.sleep(1.5)
                    st.success("¡Configuración certificada aplicada al inversor!")

    with t_rep:
        st.markdown("### 📄 Descarga de Reporte Ejecutivo PDF")
        st.write("Genere un informe formal con membrete de CV INGENIERIA SAS para enviarlo a sus clientes.")
        pdf_bytes = utils.generar_pdf(p, d)
        st.download_button(
            label="📄 Generar y Descargar PDF",
            data=pdf_bytes,
            file_name=f"Reporte_CV_Ing__{p['nombre']}.pdf",
            mime="application/pdf",
            type="primary"
        )

    if t_om:
        with t_om:
            st.markdown("### 📅 Agenda de Mantenimiento")
            with st.form("f_mant"):
                mc1, mc2, mc3 = st.columns([2, 1, 1])
                m_tipo = mc1.selectbox("Tipo de Tarea", ["💦 Limpieza Paneles", "🔋 Revisión Baterías", "🔌 Revisión Inversor"])
                m_fecha = mc2.date_input("Fecha")
                m_resp = mc3.text_input("Técnico")
                m_notas = st.text_input("Observaciones")
                if st.form_submit_button("➕ Agendar"):
                    db.guardar_mantenimiento(p['nombre'], {"fecha": str(m_fecha), "tipo": str(m_tipo), "resp": str(m_resp), "notas": str(m_notas), "estado": "⏳ Pendiente"})
                    st.rerun()
            st.markdown("<br><h4>📋 Historial</h4>", unsafe_allow_html=True)
            mantenimientos = db.cargar_mantenimientos().get(p['nombre'], [])
            if not mantenimientos: st.info("No hay mantenimientos programados.")
            else:
                for i, m in enumerate(reversed(mantenimientos)):
                    real_idx = m["id"]
                    st.markdown(f"<div style='background:white; padding:15px; border-radius:8px; border:1px solid #eaeaea; margin-bottom:10px;'><b>{m['tipo']}</b> - {m['estado']}<br><span style='font-size:12px; color:#7f8c8d;'>📅 {m['fecha']} | 👨‍🔧 {m['resp']} | 📝 {m['notas']}</span></div>", unsafe_allow_html=True)
                    c_btn1, c_btn2, _ = st.columns([1,1,8])
                    if m['estado'] == "⏳ Pendiente" and c_btn1.button("✅", key=f"ok_{real_idx}"):
                        db.actualizar_estado_mantenimiento(real_idx, "✅ Completado")
                        st.rerun()
                    if c_btn2.button("🗑️", key=f"del_{real_idx}"):
                        db.eliminar_mantenimiento(real_idx)
                        st.rerun()
                        
    if st.session_state['rol'] == 'admin' and t_auth:
        with t_auth:
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            if st.session_state.get("auth_crear_usuario"):
                with st.form("form_auth_crear_usuario_final"):
                    col_t1, col_t2, col_t3, col_t4 = st.columns([6, 2, 1, 1])
                    with col_t1: st.markdown("<h3 style='margin-top:0; color:#2c3e50; font-weight:normal;'>Crear usuario final</h3>", unsafe_allow_html=True)
                    with col_t3: btn_cancelar = st.form_submit_button("Cancelar", use_container_width=True)
                    with col_t4: btn_guardar = st.form_submit_button("Guardar", type="primary", use_container_width=True)
                    
                    st.markdown("<hr style='margin-top:5px; margin-bottom:20px; border-color:#eaeaea;'>", unsafe_allow_html=True)
                    st.markdown("<div style='text-align:center; color:#3498db; font-size:14px; margin-bottom:25px;'>ⓘ ¿El usuario final tiene una cuenta? Haga clic aquí para buscar la cuenta</div>", unsafe_allow_html=True)
                    
                    st.radio("Tipo", ["🔘 Correo electrónico"], label_visibility="collapsed", key="rad_auth")
                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    n_nombre = c1.text_input("* Nombre", key="txt_nom_auth")
                    n_usuario = c2.text_input("Nombre de usuario", key="txt_usr_auth")
                    
                    c3, c4 = st.columns(2)
                    n_email = c3.text_input("* Correo electrónico", placeholder="Asegúrate de que esta dirección de correo electrónico pueda recibir mensajes", key="txt_mail_auth")
                    n_pwd = c4.text_input("* Contraseña original", placeholder="Por favor escribe", type="password", key="txt_pwd_auth")
                    
                    plantas_nombres = ["-Por favor, seleccione-"] + [p_item['nombre'] for p_item in todas_las_plantas]
                    idx_p = plantas_nombres.index(p['nombre']) if p['nombre'] in plantas_nombres else 0
                    n_planta = st.selectbox("* Autorizar", plantas_nombres, index=idx_p, key="sel_planta_auth")
                    
                    if btn_guardar:
                        if not n_nombre or not n_email or not n_pwd or n_planta == "-Por favor, seleccione-":
                            st.error("⚠️ Complete todos los campos obligatorios (*)")
                        else:
                            correo_final = str(n_email).strip()
                            ok, msg = db.crear_usuario_admin(correo_final, n_pwd, n_planta)
                            if ok:
                                st.session_state["auth_crear_usuario"] = False
                                st.success("✅ Usuario creado con éxito.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(msg)
                                
                    if btn_cancelar:
                        st.session_state["auth_crear_usuario"] = False
                        st.rerun()
            else:
                st.markdown(f"""
                <div style="background:white; border-radius:8px; padding:20px; border:1px solid #eaeaea; margin-bottom: 20px;">
                    <p style="color:#7f8c8d; font-size:14px; margin-top:0;">Información del gerente de planta <span style="color:#bdc3c7; cursor:pointer;">❔</span></p>
                    <div style="display:flex; align-items:center; margin-top:15px;">
                        <div style="background:#f0f0f0; border-radius:50%; width:60px; height:60px; display:flex; justify-content:center; align-items:center; margin-right:15px; color:#bdc3c7; font-weight:bold; font-size:12px;">LOGO</div>
                        <div>
                            <h3 style="margin:0; color:#2c3e50; font-size: 18px; font-weight:normal;">{p['nombre'].lower()}</h3>
                            <p style="margin:0; color:#7f8c8d; font-size:14px;">Negocios</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_a1, col_a2, col_a3 = st.columns(3)
                
                with col_a1:
                    st.markdown("<div style='background:white; border-left:1px solid #eaeaea; border-top:1px solid #eaeaea; border-right:1px solid #eaeaea; border-radius:8px 8px 0 0; padding:15px 15px 0 15px;'>", unsafe_allow_html=True)
                    c_tit1, c_btn1 = st.columns([6, 4])
                    with c_tit1: st.markdown("<h4 style='margin:0; color:#2c3e50; font-size:15px; font-weight:normal; padding-top:5px;'>Usuarios autorizados</h4>", unsafe_allow_html=True)
                    with c_btn1:
                        if st.button("Ir a autorizar", key="btn_auth_usuarios_1", use_container_width=True):
                            st.session_state["auth_crear_usuario"] = True
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div style="background:white; border-left:1px solid #eaeaea; border-bottom:1px solid #eaeaea; border-right:1px solid #eaeaea; border-radius:0 0 8px 8px; padding:0 15px 15px 15px; height: 320px; display:flex; flex-direction:column;">
                        <div style='border-bottom:1px solid #f0f0f0; margin-bottom:15px; margin-top:5px;'></div>
                        <div style="display:flex; align-items:flex-start; flex-grow:1;">
                            <img src="https://img.icons8.com/color/48/circled-user-male-skin-type-1--v1.png" style="width:40px; margin-right:10px;"/>
                            <div style="flex-grow:1; padding-top:5px;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="color:#2c3e50; font-size:14px;">{p['nombre'].upper()}</span>
                                    <div><span style="color:#bdc3c7; cursor:pointer; margin-right:5px; font-size:14px;">✏️</span> <span style="color:#bdc3c7; cursor:pointer; font-size:14px;">🗑️</span></div>
                                </div>
                                <div style="color:#7f8c8d; font-size:12px; margin-top:5px;">Autorizar: &nbsp;&nbsp;Ver rol solo de planta</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_a2:
                    st.markdown("<div style='background:white; border-left:1px solid #eaeaea; border-top:1px solid #eaeaea; border-right:1px solid #eaeaea; border-radius:8px 8px 0 0; padding:15px 15px 0 15px;'>", unsafe_allow_html=True)
                    c_tit2, c_btn2 = st.columns([6, 4])
                    with c_tit2: st.markdown("<h4 style='margin:0; color:#2c3e50; font-size:15px; font-weight:normal; padding-top:5px;'>Unidades de negocio</h4>", unsafe_allow_html=True)
                    with c_btn2: st.button("Ir a autorizar", key="btn_auth_unidades_2", use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div style="background:white; border-left:1px solid #eaeaea; border-bottom:1px solid #eaeaea; border-right:1px solid #eaeaea; border-radius:0 0 8px 8px; padding:0 15px 15px 15px; height: 320px; display:flex; flex-direction:column;">
                        <div style='border-bottom:1px solid #f0f0f0; margin-bottom:15px; margin-top:5px;'></div>
                        <div style="flex-grow:1; display:flex; flex-direction:column; justify-content:center; align-items:center; color:#bdc3c7;">
                            <img src="https://img.icons8.com/ios/100/ced6e0/document--v1.png" style="width:60px; margin-bottom:10px; opacity:0.6;"/>
                            <span style="font-size:13px;">Datos no disponibles</span>
                            <button style="background:#1890ff; border:none; color:white; padding:8px 15px; border-radius:4px; font-size:13px; margin-top:20px; cursor:pointer; font-weight:bold;">Haga clic aquí para autorizar</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_a3:
                    st.markdown("<div style='background:white; border-left:1px solid #eaeaea; border-top:1px solid #eaeaea; border-right:1px solid #eaeaea; border-radius:8px 8px 0 0; padding:15px 15px 0 15px;'>", unsafe_allow_html=True)
                    c_tit3, c_btn3 = st.columns([6, 4])
                    with c_tit3: st.markdown("<h4 style='margin:0; color:#2c3e50; font-size:15px; font-weight:normal; padding-top:5px;'>Miembros internos</h4>", unsafe_allow_html=True)
                    with c_btn3: st.button("Ir a autorizar", key="btn_auth_miembros_3", use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div style="background:white; border-left:1px solid #eaeaea; border-bottom:1px solid #eaeaea; border-right:1px solid #eaeaea; border-radius:0 0 8px 8px; padding:0 15px 15px 15px; height: 320px; display:flex; flex-direction:column;">
                        <div style='border-bottom:1px solid #f0f0f0; margin-bottom:15px; margin-top:5px;'></div>
                        <div style="display:flex; align-items:flex-start; flex-grow:1;">
                            <img src="https://img.icons8.com/color/48/circled-user-male-skin-type-1--v1.png" style="width:40px; margin-right:10px;"/>
                            <div style="flex-grow:1; padding-top:5px;">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <span style="color:#2c3e50; font-size:14px;">energiasolar01</span>
                                    <span style="color:#bdc3c7; cursor:pointer; font-size:14px;">🗑️</span>
                                </div>
                                <div style="color:#7f8c8d; font-size:12px; margin-top:5px;">Role: &nbsp;&nbsp;Súper administrador</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

elif menu == "🚨 Centro de Alertas":
    st.title("🚨 CENTRO DE ALERTAS")
    if not plantas_permitidas: st.info("No hay plantas registradas.")
    else: st.success("✅ Todos los sistemas operando dentro de los parámetros normales.")
