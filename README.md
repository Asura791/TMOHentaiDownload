# TMOHentai Downloader

## Descripción  
Script para descargar mangas de TMOhentai y convertirlos a PDF. Versión minimalista para Termux/PC.

## Requisitos
- Python 3.8+
- Pip instalado

## Instalación
```bash
pkg update && pkg upgrade
pkg install python
pkg install python-pip
pip install --upgrade pip
pip install requests beautifulsoup4 pillow
pkg install git nano
termux-setup-storage

git clone https://github.com/Asura791/TMOHentaiDownload
python TMOHentai.py
