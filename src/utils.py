import os
import json
import pygame
import array
import math
from src.config import IMG_DIR, SONIDOS_DIR, ARCHIVO_RECORD, ARCHIVO_OPCIONES, OPCIONES_DEFAULT, ANCHO, ALTO

class DummySound:
    """Clase de respaldo si un efecto de sonido no se puede cargar."""
    def play(self, *args, **kwargs):
        pass
    def set_volume(self, vol):
        pass

# Almacén de sonidos activos para actualizar volumen en tiempo real
SONIDOS_REGISTRADOS = []

def crear_sprite_fallback(nombre, escala=None):
    """Genera sprites vectoriales procedurales de alta calidad como respaldo si falta un archivo de imagen."""
    w, h = escala if escala else (40, 40)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    
    if "jugador" in nombre:
        pygame.draw.polygon(surf, (0, 180, 255), [(w//2, 2), (2, h-4), (w//3, h-10), (w//2, h-2), (2*w//3, h-10), (w-2, h-4)])
        pygame.draw.polygon(surf, (220, 240, 255), [(w//2, 6), (w//4, h-12), (w//2, h-14), (3*w//4, h-12)])
        pygame.draw.ellipse(surf, (255, 200, 50), (w//2 - 6, h//3, 12, 16))
        pygame.draw.polygon(surf, (255, 100, 0), [(w//2 - 4, h-6), (w//2, h), (w//2 + 4, h-6)])
    elif "enemigo2" in nombre or "cazador" in nombre:
        pygame.draw.polygon(surf, (220, 40, 90), [(w//2, h-2), (2, 4), (w//3, 12), (w//2, 2), (2*w//3, 12), (w-2, 4)])
        pygame.draw.circle(surf, (0, 255, 200), (w//2, h//2), 5)
    elif "enemigo" in nombre:
        pygame.draw.polygon(surf, (50, 220, 80), [(w//2, h-2), (2, 6), (w//3, 14), (w//2, 4), (2*w//3, 14), (w-2, 6)])
        pygame.draw.rect(surf, (255, 255, 255), (w//3, h//3, w//3, h//4))
    elif "boss" in nombre:
        pygame.draw.polygon(surf, (180, 40, 220), [(w//2, h-4), (4, 10), (w//4, 30), (w//2, 10), (3*w//4, 30), (w-4, 10)])
        pygame.draw.ellipse(surf, (255, 50, 50), (w//3, h//4, w//3, h//3))
        pygame.draw.circle(surf, (255, 255, 0), (w//2, h//2), 12)
    elif "bala_enemigo" in nombre:
        pygame.draw.ellipse(surf, (255, 50, 50), (0, 0, w, h))
        pygame.draw.ellipse(surf, (255, 255, 200), (w//4, h//4, w//2, h//2))
    elif "bala" in nombre:
        pygame.draw.ellipse(surf, (0, 240, 255), (0, 0, w, h))
        pygame.draw.ellipse(surf, (255, 255, 255), (w//4, h//4, w//2, h//2))
    elif "shield" in nombre:
        pygame.draw.circle(surf, (0, 150, 255, 200), (w//2, h//2), w//2 - 1)
        pygame.draw.circle(surf, (255, 255, 255), (w//2, h//2), w//2 - 1, 2)
        pygame.draw.polygon(surf, (255, 255, 255), [(w//2, 5), (w-6, 9), (w-6, 16), (w//2, h-5), (6, 16), (6, 9)])
    elif "weapon" in nombre:
        pygame.draw.circle(surf, (255, 180, 0, 200), (w//2, h//2), w//2 - 1)
        pygame.draw.circle(surf, (255, 255, 255), (w//2, h//2), w//2 - 1, 2)
        pygame.draw.rect(surf, (255, 255, 255), (w//2 - 2, 6, 4, 16))
        pygame.draw.rect(surf, (255, 255, 255), (w//2 - 8, 10, 4, 12))
        pygame.draw.rect(surf, (255, 255, 255), (w//2 + 4, 10, 4, 12))
    elif "speed" in nombre:
        pygame.draw.circle(surf, (50, 220, 80, 200), (w//2, h//2), w//2 - 1)
        pygame.draw.circle(surf, (255, 255, 255), (w//2, h//2), w//2 - 1, 2)
        pygame.draw.polygon(surf, (255, 255, 255), [(w//2, 4), (w-6, 14), (w//2 + 2, 14), (w//2 + 2, h-5), (w//2 - 2, h-5), (w//2 - 2, 14), (6, 14)])
    elif "fondo_menu" in nombre:
        surf = pygame.Surface((w, h))
        for y in range(h):
            ratio = y / h
            r = int(10 * (1 - ratio) + 5 * ratio)
            g = int(20 * (1 - ratio) + 40 * ratio)
            b = int(50 * (1 - ratio) + 90 * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
    elif "fondo_juego" in nombre:
        surf = pygame.Surface((w, h))
        surf.fill((10, 10, 20))
    else:
        surf.fill((150, 150, 150))

    return surf

def cargar_imagen(nombre_relativo, escala=None):
    """Carga una imagen desde assets/imagenes o devuelve un fallback procedural sin crash."""
    path = os.path.join(IMG_DIR, nombre_relativo) if not os.path.isabs(nombre_relativo) else nombre_relativo
    nombre_base = os.path.basename(nombre_relativo)
    
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            if escala:
                img = pygame.transform.scale(img, escala)
            return img
        except Exception:
            pass
            
    return crear_sprite_fallback(nombre_base, escala)

def generar_sonido_sintetico(fuerza="explosion"):
    """Genera un efecto de sonido retro sintético de 8-bits si falta el archivo .wav."""
    try:
        sample_rate = 22050
        duration = 0.25
        num_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * num_samples)
        
        for i in range(num_samples):
            t = float(i) / sample_rate
            if fuerza == "explosion":
                val = int(32767 * (math.exp(-t * 12)) * (math.sin(t * 200) * (i % 7 - 3) / 3))
            elif fuerza == "disparo":
                freq = 800 - (t / duration) * 600
                val = int(16384 * (math.exp(-t * 20)) * math.sin(2 * math.pi * freq * t))
            else:
                val = int(16384 * math.sin(2 * math.pi * 440 * t))
            buf[i] = max(-32767, min(32767, val))
            
        sound = pygame.mixer.Sound(buffer=buf)
        return sound
    except Exception:
        return DummySound()

def cargar_sonido(nombre_relativo, volumen=None):
    """Carga un sonido o devuelve un generador sintético/DummySound seguro."""
    opciones = leer_opciones()
    vol_base = volumen if volumen is not None else opciones.get("volumen_sfx", 0.40)
    
    nombre_clean = nombre_relativo.replace("daño", "dano")
    path = os.path.join(SONIDOS_DIR, nombre_clean)
    
    if not os.path.exists(path):
        alt_path = os.path.join(SONIDOS_DIR, nombre_relativo)
        if os.path.exists(alt_path):
            path = alt_path

    snd = None
    if os.path.exists(path):
        try:
            snd = pygame.mixer.Sound(path)
        except Exception:
            pass
            
    if snd is None:
        tipo = "explosion" if "explosion" in nombre_relativo else "disparo" if "disparo" in nombre_relativo else "beep"
        snd = generar_sonido_sintetico(tipo)

    snd.set_volume(vol_base)
    SONIDOS_REGISTRADOS.append((snd, vol_base))
    return snd

def aplicar_volumen_sfx(multiplicador):
    """Actualiza el volumen de todos los efectos de sonido registrados."""
    for snd, vol_base in SONIDOS_REGISTRADOS:
        try:
            snd.set_volume(vol_base * multiplicador)
        except Exception:
            pass

def aplicar_volumen_musica(volumen):
    """Actualiza el volumen de la música de fondo en Pygame Mixer."""
    try:
        pygame.mixer.music.set_volume(volumen)
    except Exception:
        pass

def iniciar_musica_fondo(volumen=None):
    """Carga y reproduce la canción de fondo espacial en bucle continuo."""
    opciones = leer_opciones()
    vol = volumen if volumen is not None else opciones.get("volumen_musica", 0.25)
    
    posibles_nombres = ["musica_fondo.wav", "musica_fondo.mp3"]
    for nombre in posibles_nombres:
        path = os.path.join(SONIDOS_DIR, nombre)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(vol)
                pygame.mixer.music.play(-1)
                return True
            except Exception:
                pass
    return False

# =================================================
# PERSISTENCIA DE OPCIONES Y RÉCORDS
# =================================================
def leer_opciones():
    """Carga las opciones guardadas del usuario o devuelve las por defecto."""
    if os.path.exists(ARCHIVO_OPCIONES):
        try:
            with open(ARCHIVO_OPCIONES, "r", encoding="utf-8") as f:
                data = json.load(f)
                opts = OPCIONES_DEFAULT.copy()
                opts.update(data)
                return opts
        except Exception:
            pass
    return OPCIONES_DEFAULT.copy()

def guardar_opciones(opciones):
    """Guarda las opciones del usuario en opciones.json."""
    try:
        with open(ARCHIVO_OPCIONES, "w", encoding="utf-8") as f:
            json.dump(opciones, f, indent=4)
    except Exception:
        pass

def leer_record():
    """Lee el récord histórico desde el archivo del usuario."""
    if os.path.exists(ARCHIVO_RECORD):
        try:
            with open(ARCHIVO_RECORD, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except Exception:
            return 0
    return 0

def guardar_record(puntos):
    """Guarda el récord si supera el actual."""
    record_actual = leer_record()
    if puntos > record_actual:
        try:
            with open(ARCHIVO_RECORD, "w", encoding="utf-8") as f:
                f.write(str(puntos))
        except Exception:
            pass
