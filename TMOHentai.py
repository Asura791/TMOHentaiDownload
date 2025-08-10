#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TMOHentai Downloader - by YourName
Versión minimalista con estilo para Termux
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

# ─── CONSTANTES DE DISEÑO ─────────────────────────────────────────────────
COLOR_PRIMARIO = "\033[1;35m"  # Magenta brillante
COLOR_SECUNDARIO = "\033[1;36m"  # Cian brillante
COLOR_EXITO = "\033[1;32m"  # Verde brillante
COLOR_ERROR = "\033[1;31m"  # Rojo brillante
COLOR_ADVERTENCIA = "\033[1;33m"  # Amarillo brillante
RESET = "\033[0m"  # Resetear color

# ─── BANNER Y DISEÑO ──────────────────────────────────────────────────────
def mostrar_banner():
    print(f"""{COLOR_PRIMARIO}
████████╗███╗   ███╗ ██████╗ ██╗  ██╗███████╗███╗   ██╗████████╗ █████╗ ██╗
╚══██╔══╝████╗ ████║██╔═══██╗██║  ██║██╔════╝████╗  ██║╚══██╔══╝██╔══██╗██║
   ██║   ██╔████╔██║██║   ██║███████║█████╗  ██╔██╗ ██║   ██║   ███████║██║
   ██║   ██║╚██╔╝██║██║   ██║██╔══██║██╔══╝  ██║╚██╗██║   ██║   ██╔══██║██║
   ██║   ██║ ╚═╝ ██║╚██████╔╝██║  ██║███████╗██║ ╚████║   ██║   ██║  ██║███████╗
   ╚═╝   ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝
{COLOR_SECUNDARIO}► Descargador de PDF para TMOhentai ◄
{COLOR_ADVERTENCIA}► Versión 2.0 ◄
{RESET}""")

def animar_carga(mensaje):
    for i in range(3):
        sys.stdout.write(f"\r{COLOR_SECUNDARIO}{mensaje}{'.' * i}{' ' * (3-i)}{RESET}")
        sys.stdout.flush()
        time.sleep(0.5)
    print()

# ─── FUNCIONES PRINCIPALES ────────────────────────────────────────────────
def descargar_imagen(link, carpeta, i, headers):
    try:
        ext = link.split(".")[-1].split("?")[0]
        nombre_archivo = os.path.join(carpeta, f"{str(i).zfill(3)}.{ext}")
        
        resp = requests.get(link, headers=headers)
        if resp.status_code == 200 and resp.content:
            with open(nombre_archivo, "wb") as f:
                f.write(resp.content)
            return f"{COLOR_EXITO}✓{RESET} Imagen {i:03d} descargada"
        else:
            return f"{COLOR_ERROR}✗{RESET} Error {resp.status_code} en imagen {i:03d}"
    except Exception as e:
        return f"{COLOR_ERROR}✗{RESET} Error en imagen {i:03d}: {str(e)[:30]}"

def convertir_a_pdf(carpeta, nombre_pdf):
    animar_carga("Convirtiendo a PDF")
    imagenes = []
    for archivo in sorted(os.listdir(carpeta)):
        if archivo.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            ruta = os.path.join(carpeta, archivo)
            try:
                img = Image.open(ruta).convert("RGB")
                imagenes.append(img)
            except Exception as e:
                print(f"{COLOR_ADVERTENCIA}!{RESET} Error procesando {archivo}: {str(e)[:30]}")

    if imagenes:
        pdf_path = os.path.join(carpeta, nombre_pdf)
        imagenes[0].save(pdf_path, save_all=True, append_images=imagenes[1:])
        print(f"{COLOR_EXITO}✓{RESET} PDF creado: {COLOR_SECUNDARIO}{pdf_path}{RESET}")
    else:
        print(f"{COLOR_ERROR}✗{RESET} No se encontraron imágenes para convertir")

def descargar_manga():
    mostrar_banner()
    
    try:
        url_original = input(f"{COLOR_SECUNDARIO}► Ingresa el enlace del manga:{RESET} ").strip()
        manga_id = url_original.split("/")[-1]

        url_cascade = f"https://tmohentai.com/index.php/reader/{manga_id}/cascade?image-width=normal-width"
        print(f"{COLOR_SECUNDARIO}► URL generada:{RESET} {url_cascade}")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": url_original
        }

        animar_carga("Conectando con TMOhentai")
        resp = requests.get(url_cascade, headers=headers)
        if resp.status_code != 200:
            print(f"{COLOR_ERROR}✗{RESET} Error al acceder a la página: {resp.status_code}")
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        imagenes = []
        for img in soup.find_all("img", class_="content-image"):
            link = img.get("data-original") or img.get("src")
            if link and link.startswith("http") and link not in imagenes:
                imagenes.append(link)

        print(f"{COLOR_EXITO}✓{RESET} Encontradas {COLOR_SECUNDARIO}{len(imagenes)}{RESET} imágenes")

        carpeta = f"TMOHentai_{manga_id}"
        os.makedirs(carpeta, exist_ok=True)

        print(f"{COLOR_SECUNDARIO}► Descargando imágenes...{RESET}")
        with ThreadPoolExecutor(max_workers=8) as executor:
            futuros = {executor.submit(descargar_imagen, link, carpeta, i+1, headers): i for i, link in enumerate(imagenes)}
            for futuro in as_completed(futuros):
                print(futuro.result())

        print(f"{COLOR_EXITO}✓{RESET} Descarga completada en {COLOR_SECUNDARIO}'{carpeta}'{RESET}")
        convertir_a_pdf(carpeta, f"{manga_id}.pdf")

    except KeyboardInterrupt:
        print(f"\n{COLOR_ADVERTENCIA}!{RESET} Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"{COLOR_ERROR}✗{RESET} Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        descargar_manga()
    except KeyboardInterrupt:
        print(f"\n{COLOR_ADVERTENCIA}!{RESET} Programa interrumpido")
        sys.exit(0)