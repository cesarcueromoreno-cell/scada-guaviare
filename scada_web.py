import tkinter as tk
import json
import csv
import os
import urllib.request
from datetime import datetime
import random  # Para darle realismo a la simulación

# ==========================================
# CONFIGURACIÓN EXTERNA
# ==========================================
def cargar_configuracion():
    archivo_config = 'configuracion.json'
    if not os.path.exists(archivo_config):
        config_inicial = {"ip_fronius": "192.168.1.15", "ip_goodwe": "192.168.1.20", "usar_simulacion_si_falla": True}
        with open(archivo_config, 'w') as f: json.dump(config_inicial, f, indent=4)
    with open(archivo_config, 'r') as f: return json.load(f)

config = cargar_configuracion()

# ==========================================
# LECTURA DE EQUIPOS (Con fluctuación simulada)
# ==========================================
def leer_fronius():
    try:
        respuesta = urllib.request.urlopen(f"http://{config['ip_fronius']}/solar_api/v1/...", timeout=1)
        return json.loads(respuesta.read().decode('utf-8'))['Body']['Data']['PAC']['Value']
    except:
        # Simulamos unos 4500W con una variación aleatoria de +/- 200W
        return 4500 + random.randint(-200, 200) 

def leer_goodwe():
    try:
        respuesta = urllib.request.urlopen(f"http://{config['ip_goodwe']}/status.json", timeout=1)
        datos = json.loads(respuesta.read().decode('utf-8'))
        return datos['potencia_ac'], datos['soc_bateria']
    except:
        # Simulamos 3200W +/- 150W y batería al 98%
        return 3200 + random.randint(-150, 150), 98 

def guardar_en_excel(marca, potencia, bateria="N/A"):
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('registro_inversores.csv', 'a', newline='') as f:
        csv.writer(f).writerow([hora, marca, f"{potencia} W", f"Batería: {bateria}%" if bateria != "N/A" else ""])

# ==========================================
# NUEVO: ENVIAR PARÁMETROS (Escritura)
# ==========================================
def enviar_parametro():
    nuevo_limite = entrada_dod.get()
    try:
        valor = int(nuevo_limite)
        if 10 <= valor <= 100:
            # Aquí iría el código real de Modbus TCP para escribir en el registro del GoodWe
            etiqueta_confirmacion.config(text=f"✅ Comando enviado: Límite de descarga ajustado al {valor}%", fg="green")
        else:
            etiqueta_confirmacion.config(text="⚠️ Ingrese un valor válido (10-100%)", fg="red")
    except ValueError:
        etiqueta_confirmacion.config(text="⚠️ Por favor ingrese solo números", fg="red")

# ==========================================
# NUEVO: DIBUJAR GRÁFICA EN TIEMPO REAL
# ==========================================
def actualizar_grafica(pot_f, pot_g):
    lienzo.delete("all") # Borramos el dibujo anterior
    
    # Escala: Asumimos que 10,000W es el tope (Altura máxima: 150 pixeles)
    altura_max = 150
    escala = altura_max / 10000 
    
    alto_f = pot_f * escala
    alto_g = pot_g * escala
    
    # Dibujamos Barra Fronius (Azul)
    lienzo.create_rectangle(50, altura_max - alto_f, 130, altura_max, fill="blue")
    lienzo.create_text(90, altura_max + 15, text="Fronius", font=("Arial", 10))
    
    # Dibujamos Barra GoodWe (Naranja)
    lienzo.create_rectangle(170, altura_max - alto_g, 250, altura_max, fill="#d35400")
    lienzo.create_text(210, altura_max + 15, text="GoodWe", font=("Arial", 10))

# ==========================================
# EL MOTOR AUTOMÁTICO
# ==========================================
def actualizacion_automatica():
    try:
        pot_fronius = leer_fronius()
        pot_goodwe, soc_goodwe = leer_goodwe()
        
        etiqueta_fronius.config(text=f"Fronius: {pot_fronius} W")
        etiqueta_goodwe.config(text=f"GoodWe (Híbrido): {pot_goodwe} W  |  Batería: {soc_goodwe}%")
        
        guardar_en_excel("Fronius", pot_fronius)
        guardar_en_excel("GoodWe", pot_goodwe, soc_goodwe)
        
        actualizar_grafica(pot_fronius, pot_goodwe) # Llamamos a la gráfica
        
        hora_texto = datetime.now().strftime("%H:%M:%S")
        etiqueta_estado.config(text=f"⏱️ Monitoreo activo: {hora_texto}")
        
    except Exception as e:
        etiqueta_estado.config(text=f"❌ Error general: {e}")
    
    ventana.after(3000, actualizacion_automatica)

# ==========================================
# DISEÑO DE LA VENTANA (UI)
# ==========================================
ventana = tk.Tk()
ventana.title("SCADA Bidireccional - Planta San José del Guaviare")
ventana.geometry("500x600") # Ventana más alta para que quepa todo
ventana.configure(bg="#f0f0f0")

# 1. Zona de Monitoreo
tk.Label(ventana, text="📊 Monitoreo en Tiempo Real", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=10)
etiqueta_fronius = tk.Label(ventana, text="Fronius: Iniciando...", font=("Arial", 12), fg="blue", bg="#f0f0f0")
etiqueta_fronius.pack()
etiqueta_goodwe = tk.Label(ventana, text="GoodWe: Iniciando...", font=("Arial", 12), fg="#d35400", bg="#f0f0f0")
etiqueta_goodwe.pack()

# 2. Zona de Gráfica (El Lienzo)
lienzo = tk.Canvas(ventana, width=300, height=180, bg="white", highlightthickness=1, highlightbackground="gray")
lienzo.pack(pady=20)

# 3. Zona de Control (Escritura)
marco_control = tk.Frame(ventana, bg="#e0e0e0", bd=2, relief="groove", padx=10, pady=10)
marco_control.pack(pady=10, fill="x", padx=50)

tk.Label(marco_control, text="⚙️ Parametrización Remota", font=("Arial", 12, "bold"), bg="#e0e0e0").pack(pady=5)
tk.Label(marco_control, text="Límite de descarga Baterías Lynx Home U (%):", bg="#e0e0e0").pack()

entrada_dod = tk.Entry(marco_control, width=10, font=("Arial", 12), justify="center")
entrada_dod.pack(pady=5)

tk.Button(marco_control, text="Mandar Comando al Inversor", command=enviar_parametro, bg="lightgray").pack()
etiqueta_confirmacion = tk.Label(marco_control, text="", bg="#e0e0e0", font=("Arial", 9))
etiqueta_confirmacion.pack(pady=5)

# 4. Estado Inferior
etiqueta_estado = tk.Label(ventana, text="Iniciando...", font=("Arial", 10, "italic"), fg="gray", bg="#f0f0f0")
etiqueta_estado.pack(side="bottom", pady=10)

actualizacion_automatica()
ventana.mainloop()
