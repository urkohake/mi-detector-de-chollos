import os
import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HISTORIAL_FILE = "historial_precios.json"

def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_historial(datos):
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def obtener_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }
    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            return res.text
    except Exception as e:
        print(f"Error consultando {url}: {e}")
    return None

def analizar_chollos():
    historial = cargar_historial()
    
    # LISTA DE PRODUCTOS A MONITOREAR
    # Puedes añadir todas las URLs de PcComponentes, MediaMarkt u Outlet PC que quieras aquí:
    productos = [
        {
            "id": "pcc_01",
            "tienda": "PcComponentes",
            "url": "https://www.pccomponentes.com/portatiles",
            "titulo_fallback": "Portátil PcComponentes en Oferta",
            "precio_defecto": 499.00
        },
        {
            "id": "mm_01",
            "tienda": "MediaMarkt",
            "url": "https://www.mediamarkt.es/es/category/televisores-142.html",
            "titulo_fallback": "TV Smart MediaMarkt",
            "precio_defecto": 349.00
        },
        {
            "id": "opc_01",
            "tienda": "Outlet PC",
            "url": "https://outlet-pc.es/",
            "titulo_fallback": "Electrodoméstico Outlet PC",
            "precio_defecto": 199.00
        }
    ]

    chollos_hoy = []

    for item in productos:
        pid = item["id"]
        html = obtener_html(item["url"])
        
        titulo = item["titulo_fallback"]
        precio_actual = item["precio_defecto"]

        if html:
            soup = BeautifulSoup(html, "html.parser")
            
            # Intenta extraer título real del HTML
            if soup.title and soup.title.string:
                titulo_clean = soup.title.string.split("|")[0].split("-")[0].strip()
                if len(titulo_clean) > 5:
                    titulo = titulo_clean

            # Intenta extraer precio numérico del HTML
            precios_encontrados = re.findall(r'(\d+[.,]\d{2})\s*€', html)
            if precios_encontrados:
                try:
                    val = float(precios_encontrados[0].replace(",", "."))
                    if 10 <= val <= 3000:
                        precio_actual = val
                except ValueError:
                    pass

        # Cálculo de historial, mínimo histórico y precio anterior
        hist = historial.get(pid, {"precios": [], "minimo": precio_actual})
        precios_pasados = [p["precio"] for p in hist.get("precios", [])]
        
        precio_anterior = precios_pasados[-1] if precios_pasados else round(precio_actual * 1.2, 2)
        minimo_historico = min(min(precios_pasados) if precios_pasados else precio_actual, precio_actual)

        # Guardar en el histórico
        hist["precios"].append({
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "precio": precio_actual
        })
        hist["minimo"] = minimo_historico
        historial[pid] = hist

        # Descuento % respecto al precio anterior
        descuento = round(((precio_anterior - precio_actual) / precio_anterior) * 100) if precio_anterior > precio_actual else 0

        chollos_hoy.append({
            "id": pid,
            "titulo": titulo,
            "tienda": item["tienda"],
            "url": item["url"],
            "precio_actual": precio_actual,
            "precio_anterior": precio_anterior,
            "minimo_historico": minimo_historico,
            "es_minimo": precio_actual <= minimo_historico,
            "descuento": descuento
        })

    guardar_historial(historial)

    with open("chollos.json", "w", encoding="utf-8") as f:
        json.dump(chollos_hoy, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    analizar_chollos()
