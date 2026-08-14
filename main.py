#!/usr/bin/env python3
"""
Juego Retro DanVB
Punto de entrada principal del juego.
"""

import sys
import pygame
from src.config import ANCHO, ALTO, TITULO_JUEGO, FPS
from src.game import JuegoController

def main():
    # Inicialización de Pygame y Mezclador de Audio
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception as e:
        print(f"Advertencia: No se pudo inicializar el mezclador de audio: {e}")

    # Configuración de Ventana y Reloj
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption(TITULO_JUEGO)
    clock = pygame.time.Clock()

    # Iniciar el controlador principal del juego
    controlador = JuegoController(pantalla, clock)
    controlador.iniciar()

if __name__ == "__main__":
    main()
