#!/usr/bin/env python3
"""
Script de automatización para compilar el juego en un ejecutable Windows (.exe) portable.
"""

import os
import sys
import subprocess

# Configurar encoding de salida para Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def generar_icono():
    """Genera el archivo icon.ico a partir de icon.png usando Pillow."""
    png_path = os.path.join("assets", "imagenes", "icon.png")
    ico_path = os.path.join("assets", "imagenes", "icon.ico")
    
    if os.path.exists(png_path):
        try:
            from PIL import Image
            img = Image.open(png_path)
            img.save(ico_path, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64)])
            print(f"[+] Icono generado con exito en: {ico_path}")
            return ico_path
        except Exception as e:
            print(f"[-] No se pudo generar .ico con Pillow: {e}")
    return None

def compilar():
    """Ejecuta PyInstaller para empaquetar el juego."""
    print("[+] Iniciando empaquetado con PyInstaller...")
    
    ico_path = generar_icono()
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "JuegoRetroDanVB",
        "--add-data", "assets;assets"
    ]
    
    if ico_path and os.path.exists(ico_path):
        cmd.extend(["--icon", ico_path])
        
    cmd.append("main.py")
    
    print(f"[+] Ejecutando comando: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        dist_dir = os.path.abspath(os.path.join("dist", "JuegoRetroDanVB"))
        exe_path = os.path.join(dist_dir, "JuegoRetroDanVB.exe")
        print("\n" + "="*60)
        print("[SUCCESS] EMPAQUETADO COMPLETADO CON EXITO!")
        print(f"[-] Carpeta de salida: {dist_dir}")
        print(f"[-] Ejecutable listo: {exe_path}")
        print("="*60)
    else:
        print(f"[ERROR] Fallo al empaquetar con PyInstaller. Codigo: {result.returncode}")

if __name__ == "__main__":
    compilar()
