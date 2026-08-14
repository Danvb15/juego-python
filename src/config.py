import os
import sys

# =================================================
# CONFIGURACIÓN DE PANTALLA Y RENDIMIENTO
# =================================================
ANCHO = 1110
ALTO = 600
FPS = 60
TITULO_JUEGO = "Juego Retro DanVB"

# =================================================
# PALETA DE COLORES (RGB)
# =================================================
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS_OSCURO = (30, 30, 35)
GRIS_CLARO = (200, 200, 200)
ROJO = (240, 50, 50)
VERDE = (50, 220, 80)
AZUL_CYAN = (0, 200, 255)
AMARILLO = (255, 215, 0)
NARANJA = (255, 120, 0)
PURPURA = (180, 50, 230)

# =================================================
# DIFICULTAD
# =================================================
DIFICULTADES = {
    1: {"nombre": "FÁCIL", "multiplicador_vida": 1.0, "multiplicador_danio": 0.8, "velocidad_enemigo": 1.0, "color": (60, 180, 75)},
    2: {"nombre": "NORMAL", "multiplicador_vida": 1.0, "multiplicador_danio": 1.0, "velocidad_enemigo": 1.3, "color": (200, 170, 40)},
    3: {"nombre": "DIFÍCIL", "multiplicador_vida": 1.2, "multiplicador_danio": 1.4, "velocidad_enemigo": 1.6, "color": (200, 60, 60)},
}

# =================================================
# RUTAS DE RECURSOS Y ARCHIVOS DE USUARIO
# =================================================
def get_base_dir():
    """Devuelve el directorio base del proyecto o del ejecutable PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "imagenes")
SONIDOS_DIR = os.path.join(ASSETS_DIR, "sonidos")

def get_save_path(filename="record.txt"):
    """Devuelve la ruta segura de guardado de datos del usuario."""
    user_home = os.path.expanduser("~")
    save_folder = os.path.join(user_home, "JuegoRetroDanVB")
    os.makedirs(save_folder, exist_ok=True)
    return os.path.join(save_folder, filename)

ARCHIVO_RECORD = get_save_path("record.txt")
ARCHIVO_OPCIONES = get_save_path("opciones.json")

# Opciones por defecto
OPCIONES_DEFAULT = {
    "volumen_musica": 0.25,
    "volumen_sfx": 0.40,
    "pantalla_completa": False
}
