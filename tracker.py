import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Estructura del historial
HISTORIAL_FILE = "historial_precios.json"

def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_historial(datos):
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def extraer_datos_producto(url, selector_nombre, selector_precio):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return None
    
    soup = BeautifulSoup(res.text, "html.parser")
    try:
        titulo = soup.select_one(selector_nombre).get_text(strip=True)
        precio_raw = soup.select_one(selector_precio).get_text(strip=True)
        # Limpieza básica para extraer solo el valor numérico
        precio_limpio = float(precio_raw.replace("€", "").replace(".", "").replace(",", ".").strip())
        return {"titulo": titulo, "precio": precio_limpio}
    except Exception as e:
        print(f"Error procesando {url}: {e}")
        return None

def analizar_chollos():
    historial = cargar_historial()
    
    # Lista de productos objetivo a rastrear en tiendas
    productos = [
        {
            "id": "pcc_01",
            "tienda": "PcComponentes",
            "url": "URL_DEL_PRODUCTO",
            "sel_nombre": "h1",
            "sel_precio": ".precio-main"
        },
        {
            "id": "mm_01",
            "tienda": "MediaMarkt",
            "url": "URL_DEL_PRODUCTO",
            "sel_nombre": "h1",
            "sel_precio": "[data-test='mms-price']"
        }
    ]

    chollos_hoy = []

    for item in productos:
        pid = item["id"]
        datos = extraer_datos_producto(item["url"], item["sel_nombre"], item["sel_precio"])
        
        if not datos:
            continue

        precio_actual = datos["precio"]
        hist = historial.get(pid, {"precios": [], "minimo": precio_actual})
        
        precio_anterior = hist["precios"][-1]["precio"] if hist["precios"] else precio_actual
        minimo_historico = min(hist.get("minimo", precio_actual), precio_actual)

        # Determinar si es una oportunidad relevante
        descuento = 0
        if precio_anterior > 0:
            descuento = round(((precio_anterior - precio_actual) / precio_anterior) * 100, 2)

        registro = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "precio": precio_actual
        }
        
        hist["precios"].append(registro)
        hist["minimo"] = minimo_historico
        historial[pid] = hist

        chollos_hoy.append({
            "titulo": datos["titulo"],
            "tienda": item["tienda"],
            "url": item["url"],
            "precio_actual": precio_actual,
            "precio_anterior": precio_anterior,
            "minimo_historico": minimo_historico,
            "es_minimo": precio_actual <= minimo_historico,
            "descuento": descuento
        })

    guardar_historial(historial)
    
    # Guardar estado actual para el Frontend
    with open("chollos.json", "w", encoding="utf-8") as f:
        json.dump(chollos_hoy, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    analizar_chollos()
