import os
import json
import requests
from datetime import datetime

HISTORIAL_FILE = "historial_precios.json"

def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_historial(datos):
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def analizar_chollos():
    historial = cargar_historial()
    
    # Productos de ejemplo a supervisar
    productos = [
        {
            "id": "prod_01",
            "tienda": "PcComponentes",
            "url": "https://www.pccomponentes.com/",
            "titulo": "Portátil Ejemplo PcComponentes",
            "precio_ejemplo": 499.00
        },
        {
            "id": "prod_02",
            "tienda": "MediaMarkt",
            "url": "https://www.mediamarkt.es/",
            "titulo": "Televisor Ejemplo MediaMarkt",
            "precio_ejemplo": 299.00
        }
    ]

    chollos_hoy = []

    for item in productos:
        pid = item["id"]
        precio_actual = item["precio_ejemplo"]
        
        hist = historial.get(pid, {"precios": [], "minimo": precio_actual})
        precio_anterior = hist["precios"][-1]["precio"] if hist["precios"] else (precio_actual + 50.0)
        minimo_historico = min(hist.get("minimo", precio_actual), precio_actual)

        hist["precios"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "precio": precio_actual})
        hist["minimo"] = minimo_historico
        historial[pid] = hist

        chollos_hoy.append({
            "titulo": item["titulo"],
            "tienda": item["tienda"],
            "url": item["url"],
            "precio_actual": precio_actual,
            "precio_anterior": precio_anterior,
            "minimo_historico": minimo_historico,
            "es_minimo": precio_actual <= minimo_historico
        })

    guardar_historial(historial)
    
    with open("chollos.json", "w", encoding="utf-8") as f:
        json.dump(chollos_hoy, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    analizar_chollos()
