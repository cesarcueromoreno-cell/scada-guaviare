# utils.py
import random
import math
import pandas as pd
import re
from datetime import datetime, timedelta
from fpdf import FPDF
import tempfile
import time

def subir_imagen_simulado(uploaded_file):
    if uploaded_file is not None:
        time.sleep(1) 
        return "https://images.unsplash.com/photo-1508514177221-188b1c77eca0?auto=format&fit=crop&w=800&q=80" 
    return ""

def get_data(pl):
    cap_val = pl.get("capacidad", "5")
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val))[0]) * 1000 if re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val)) else 5000
    p_sol = int(cap * random.uniform(0.1, 0.8))
    e_dia = round((p_sol * random.uniform(3.5, 5.0)) / 1000, 1)
    soc = random.randint(15, 99) 
    return {"solar": p_sol, "casa": int(p_sol*0.4) + random.randint(500, 1500), "soc": soc, "hoy": e_dia, "alertas": []}

def simular_historico_24h_avanzado(planta):
    cap_val = planta.get("capacidad", "30")
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val))[0]) if re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val)) else 30.0
    inicio_dia = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    datos = []
    
    for m in range(0, 24 * 60, 15):
        t = inicio_dia + timedelta(minutes=m)
        h = t.hour + t.minute/60.0
        gen = max(0, cap * math.exp(-0.5 * ((h - 13) / 2.5)**2) * random.uniform(0.9, 1.1)) if 6 <= h <= 18 else 0
        con = max(cap * 0.15, cap * 0.3 * math.exp(-0.5 * ((h - 8) / 2)**2) + cap * 0.4 * math.exp(-0.5 * ((h - 19) / 2.5)**2)) * random.uniform(0.9, 1.1)
        diff = gen - con
        grid_purchase = max(0, -diff) if planta.get('tipo_sistema', 'Híbrido') != 'Off-Grid' else 0
        
        datos.append({
            "timestamp": t,
            "Potencia solar": round(gen * 1000, 2),
            "Consumo": round(con * 1000, 2),
            "Red": round(grid_purchase * 1000, 2)
        })
    return pd.DataFrame(datos)

def simular_produccion_mensual(planta):
    cap_val = planta.get("capacidad", "30")
    cap = float(re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val))[0]) if re.findall(r"[-+]?\d*\.\d+|\d+", str(cap_val)) else 30.0
    datos = []
    mes_actual = datetime.now().month
    for i in range(1, 13):
        val = cap * random.uniform(0.6, 0.9) if i <= mes_actual else 0
        datos.append({"Mes": str(i), "Producción solar mensual": round(val, 1)})
    return pd.DataFrame(datos)

def generar_pdf(planta, datos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, "CV INGENIERIA SAS", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(52, 152, 219)
    pdf.cell(0, 10, "REPORTE DE GENERACION SOLAR", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(50, 10, "Planta:")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(planta.get('nombre', 'N/A')), ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Ubicacion:")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(planta.get('ubicacion', 'N/A')), ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Tipo de Sistema:")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(planta.get('tipo_sistema', 'Híbrido')), ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Fecha de Reporte:")
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, datetime.now().strftime("%Y-%m-%d %H:%M"), ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 10, "  Resumen de Rendimiento (Hoy)", ln=True, fill=True)
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.cell(80, 10, "Energia Solar Generada:")
    pdf.set_text_color(39, 174, 96) 
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"{datos['hoy']} kWh", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(80, 10, "Consumo Aproximado:")
    pdf.set_text_color(230, 126, 34) 
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"{round(datos['hoy']*0.45,1)} kWh", ln=True)
    pdf.set_text_color(0, 0, 0)
    
    if planta.get('tipo_sistema', 'Híbrido') in ['Híbrido', 'Off-Grid']:
        pdf.set_font("Arial", '', 12)
        pdf.cell(80, 10, "Nivel de Baterias (SOC):")
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{datos['soc']} %", ln=True)
        
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.set_text_color(127, 140, 141)
    pdf.cell(0, 10, "Este es un documento generado automaticamente por MONISOLAR APP.", ln=True, align='C')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            pdf_bytes = f.read()
    return pdf_bytes
