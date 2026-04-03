# config.py

css_global = """
<style>
[data-testid="stAppViewContainer"] { background-image: url("https://images.unsplash.com/photo-1509391366360-2e959784a276?auto=format&fit=crop&q=80&w=1920"); background-size: cover; background-position: center; background-attachment: fixed; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
.stApp > header + div > div > div > div > h1, .stApp > header + div > div > div > div > h3 { color: #ffffff !important; text-shadow: 2px 2px 5px rgba(0, 0, 0, 1) !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #112027 0%, #1a323c 50%, #162a33 100%) !important; border-right: 1px solid #2c5364 !important; }
[data-testid="stSidebar"] * { color: #ffffff !important; text-shadow: none !important; }
[data-testid="stSidebar"] button { background-color: rgba(255,255,255,0.1) !important; border: 1px solid rgba(255,255,255,0.3) !important; }
[data-testid="stSidebar"] button p { color: #ffffff !important; font-weight: bold !important; }
[data-testid="stSidebar"] button:hover { background-color: rgba(231, 76, 60, 0.8) !important; }
.block-container { background-color: rgba(244, 247, 249, 0.95) !important; padding: 2rem !important; border-radius: 12px; margin-top: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
.block-container h1, .block-container h2, .block-container h3, .block-container h4, .block-container h5, .block-container p, .block-container span, .block-container label, .block-container div { color: #2c3e50 !important; text-shadow: none !important; }
[data-testid="stForm"] { background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(10px) !important; border-radius: 12px !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important; }
[data-testid="stForm"] p, [data-testid="stForm"] label { color: white !important; text-shadow: 1px 1px 3px black !important; }
.block-container [data-testid="stForm"] { background: #ffffff !important; backdrop-filter: none !important; border: 1px solid #eaeaea !important; box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important; }
.block-container [data-testid="stForm"] p, .block-container [data-testid="stForm"] label, .block-container input, .block-container select { color: #2c3e50 !important; text-shadow: none !important; }
.block-container button[kind="primary"] p { color: white !important; }
div.solarman-card { background: #ffffff !important; border-radius: 8px !important; padding: 20px !important; box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important; text-align: center !important; border: 1px solid #eaeaea !important; height: 100%; display: flex; flex-direction: column; justify-content: center; }
div.solarman-card div.solarman-val { font-size: 28px !important; font-weight: bold !important; margin-bottom: 5px !important; color: #2c3e50 !important; }
div.solarman-card div.solarman-lbl { font-size: 13px !important; color: #7f8c8d !important; }
div.solarman-card span.solarman-lbl-sm { color: #7f8c8d !important; font-size: 11px !important; }
.tarjeta-dash-pro { background-color: #ffffff !important; padding: 15px !important; border-radius: 8px !important; margin-bottom: 10px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important; display: flex !important; align-items: center !important; justify-content: space-between !important; border: 1px solid #eaeaea !important;}
.tarjeta-label-pro { font-size: 11px !important; color: #7f8c8d !important; text-transform: uppercase !important; margin-bottom: 2px !important; white-space: nowrap !important; }
.tarjeta-dato-pro { font-size: 16px !important; font-weight: bold !important; color: #2c3e50 !important; white-space: nowrap !important; }
div[data-testid="stTabs"] > div[data-baseweb="tab-list"] { border-bottom: 1px solid #e0e0e0 !important; gap: 15px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"] p, div[data-testid="stTabs"] button[data-baseweb="tab"] span { color: #7f8c8d !important; font-weight: 600 !important; font-size: 16px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"] { background-color: transparent !important; border: none !important; border-bottom: 3px solid transparent !important; border-radius: 0 !important; box-shadow: none !important; padding-bottom: 10px !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] { border-bottom: 3px solid #e74c3c !important; }
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p, div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] span { color: #2c3e50 !important; }
div[data-testid="stButton"] button[kind="primary"] { background-color: #2d8cf0 !important; border-color: #2d8cf0 !important; border-radius: 4px !important; }
div[data-testid="stButton"] button[kind="primary"] p { color: white !important; }
div[data-testid="stButton"] button[kind="primary"]:hover { background-color: #57a3f3 !important; }
div[data-testid="stButton"] button[kind="secondary"] { border-color: #2d8cf0 !important; border-radius: 4px !important; background-color: white !important; }
div[data-testid="stButton"] button[kind="secondary"] p { color: #2d8cf0 !important; }
.diag-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; font-size: 13px; color: #2c3e50; padding: 10px; }
.diag-grid div { margin-bottom: 10px; }
.diag-lbl { color: #7f8c8d; display: block; margin-bottom: 2px; }
</style>
"""

PLANTA_HEADERS = ["nombre", "ubicacion", "capacidad", "inversores", "datalogger", "tipo_sistema", "smart_meter", "imagen_url"]
OPCIONES_SISTEMA = ["Híbrido", "On-Grid", "Off-Grid"]
OPCIONES_METERS = ["Ninguno", "Deye/Chint Meter", "Fronius Smart Meter", "Eastron SDM", "GoodWe HomeKit", "Huawei Smart Power"]
