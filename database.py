# database.py
import streamlit as st
from supabase import create_client

def init_db():
    if "SUPABASE_URL" not in st.secrets or "SUPABASE_KEY" not in st.secrets:
        return None, "❌ Las llaves de Supabase no se encuentran en los Secrets."
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key), "OK"
    except Exception as e:
        return None, f"❌ Error de conexión al servidor: {e}"

# Instancia global para ser usada por las funciones
supabase, db_estado = init_db()

def get_db_estado():
    return db_estado

def cargar_usuarios():
    if not supabase: return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}
    try:
        res = supabase.table("usuarios").select("*").execute()
        if not res.data:
            supabase.table("usuarios").insert({"usuario": "admin", "pwd": "solar123", "rol": "admin", "estado": "active", "planta_asignada": "Todas"}).execute()
            return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}
        return {r["usuario"]: {"pwd": r["pwd"], "status": r["estado"], "role": r["rol"], "planta_asignada": r["planta_asignada"]} for r in res.data}
    except: return {"admin": {"pwd": "solar123", "status": "active", "role": "admin", "planta_asignada": "Todas"}}

def solicitar_usuario(usuario, contrasena):
    db = cargar_usuarios()
    if usuario in db: return False, "⚠️ Este usuario ya existe o tiene una solicitud pendiente."
    if supabase:
        try:
            supabase.table("usuarios").insert({"usuario": str(usuario), "pwd": str(contrasena), "estado": "pending", "rol": "viewer", "planta_asignada": "Pendiente Asignar"}).execute()
            return True, "✅ Solicitud enviada. Espere a que el Administrador apruebe su cuenta."
        except: pass
    return False, f"❌ {db_estado}"

def crear_usuario_admin(correo, pwd, planta):
    if not supabase: return False, db_estado
    db = cargar_usuarios()
    if correo in db: return False, "⚠️ El usuario o correo electrónico ya existe en el sistema."
    try:
        supabase.table("usuarios").insert({
            "usuario": str(correo), "pwd": str(pwd), "estado": "active", "rol": "viewer", "planta_asignada": str(planta)
        }).execute()
        return True, "OK"
    except Exception as e:
        return False, str(e)

def actualizar_usuario_bd(usuario_id, nuevo_estado, nuevo_rol, nueva_planta, nueva_pwd=None):
    if supabase:
        datos = {"estado": str(nuevo_estado), "rol": str(nuevo_rol), "planta_asignada": str(nueva_planta)}
        if nueva_pwd: datos["pwd"] = str(nueva_pwd)
        try: supabase.table("usuarios").update(datos).eq("usuario", str(usuario_id)).execute()
        except: pass

def eliminar_usuario_bd(usuario_id):
    if supabase:
        try: supabase.table("usuarios").delete().eq("usuario", str(usuario_id)).execute()
        except: pass

def cargar_plantas():
    if supabase:
        try: return supabase.table("plantas").select("*").order("id").execute().data
        except: return []
    return []

def guardar_planta(nueva):
    if not supabase: return False, db_estado
    try: 
        supabase.table("plantas").insert(nueva).execute()
        return True, ""
    except Exception as e: 
        return False, str(e)

def actualizar_planta(idx_planta, p_edit):
    if not supabase: return False, db_estado
    try:
        datos = {k: str(v) for k, v in p_edit.items() if k not in ["id", "creado_en"]}
        supabase.table("plantas").update(datos).eq("id", p_edit["id"]).execute()
        return True, ""
    except Exception as e:
        return False, str(e)

def eliminar_planta(id_planta):
    if supabase:
        try:
            supabase.table("plantas").delete().eq("id", id_planta).execute()
        except: pass

def cargar_mantenimientos():
    if supabase:
        try:
            res = supabase.table("mantenimientos").select("*").order("id").execute()
            mants = {}
            for r in res.data:
                planta = r["planta_nombre"]
                if planta not in mants: mants[planta] = []
                mants[planta].append({"id": r["id"], "fecha": str(r["fecha"]), "tipo": r["tipo_tarea"], "resp": r["tecnico"], "notas": r["notas"], "estado": r["estado"]})
            return mants
        except: return {}
    return {}

def guardar_mantenimiento(planta, datos_mant):
    if supabase:
        try:
            supabase.table("mantenimientos").insert({
                "planta_nombre": str(planta), "fecha": str(datos_mant["fecha"]), "tipo_tarea": str(datos_mant["tipo"]),
                "tecnico": str(datos_mant["resp"]), "notas": str(datos_mant["notas"]), "estado": str(datos_mant["estado"])
            }).execute()
        except: pass

def actualizar_estado_mantenimiento(id_mant, nuevo_estado):
    if supabase:
        try:
            supabase.table("mantenimientos").update({"estado": str(nuevo_estado)}).eq("id", id_mant).execute()
        except: pass

def eliminar_mantenimiento(id_mant):
    if supabase:
        try:
            supabase.table("mantenimientos").delete().eq("id", id_mant).execute()
        except: pass
