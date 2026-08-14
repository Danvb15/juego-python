import sys
import pygame
from src.config import ANCHO, ALTO, FPS, NEGRO, BLANCO, ROJO, VERDE, AZUL_CYAN, AMARILLO, DIFICULTADES
from src.utils import (
    leer_record, leer_opciones, guardar_opciones,
    aplicar_volumen_musica, aplicar_volumen_sfx
)

def render_texto(pantalla, texto, tamano, color, x, y, centrado=True, fuente_nombre="Arial", negrita=True):
    fuente = pygame.font.SysFont(fuente_nombre, tamano, bold=negrita)
    t = fuente.render(texto, True, color)
    rect = t.get_rect()
    if centrado:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    pantalla.blit(t, rect)
    return rect

def draw_hud(pantalla, jugador, nivel, puntos, record):
    """Dibuja la interfaz de usuario durante la partida (PUNTOS Y NIVEL SIEMPRE VISIBLES)."""
    # 1. Barra de Vida del Jugador
    x_life, y_life = 15, 15
    w_life, h_life = 220, 20
    pct = max(0, jugador.vida / jugador.vida_max)
    color_vida = VERDE if pct > 0.5 else AMARILLO if pct > 0.25 else ROJO
    
    pygame.draw.rect(pantalla, (30, 30, 40), (x_life, y_life, w_life, h_life), border_radius=5)
    pygame.draw.rect(pantalla, color_vida, (x_life, y_life, int(w_life * pct), h_life), border_radius=5)
    pygame.draw.rect(pantalla, BLANCO, (x_life, y_life, w_life, h_life), 2, border_radius=5)
    
    render_texto(pantalla, f"SALUD: {int(jugador.vida)}%", 14, BLANCO, x_life + 10, y_life + 2, centrado=False, negrita=True)

    # 2. Información de Juego (SIEMPRE VISIBLE)
    render_texto(pantalla, f"PUNTOS: {puntos}", 20, BLANCO, 15, 45, centrado=False)
    render_texto(pantalla, f"NIVEL: {nivel}", 20, AZUL_CYAN, 15, 70, centrado=False)
    render_texto(pantalla, f"RÉCORD: {record}", 18, AMARILLO, 15, 95, centrado=False)

    # 3. Badges de Power-ups Activos
    x_badge = 15
    y_badge = 125
    if jugador.escudo_activo:
        pygame.draw.rect(pantalla, AZUL_CYAN, (x_badge, y_badge, 110, 24), border_radius=12)
        render_texto(pantalla, "🛡️ ESCUDO", 14, NEGRO, x_badge + 10, y_badge + 3, centrado=False)
        x_badge += 120

    if jugador.disparo_triple_timer > 0:
        pygame.draw.rect(pantalla, AMARILLO, (x_badge, y_badge, 120, 24), border_radius=12)
        render_texto(pantalla, f"⚡ TRIPLE ({jugador.disparo_triple_timer//60}s)", 14, NEGRO, x_badge + 8, y_badge + 3, centrado=False)
        x_badge += 130

    if jugador.velocidad_timer > 0:
        pygame.draw.rect(pantalla, VERDE, (x_badge, y_badge, 120, 24), border_radius=12)
        render_texto(pantalla, f"🚀 VELOZ ({jugador.velocidad_timer//60}s)", 14, NEGRO, x_badge + 8, y_badge + 3, centrado=False)

    # 4. Guía de Controles en esquina inferior derecha
    draw_guia_controles(pantalla, ANCHO - 240, ALTO - 110)

def draw_boss_hud(pantalla, boss):
    """Dibuja la barra de vida superior del Jefe de nivel."""
    w = 550
    h = 24
    x = ANCHO // 2 - w // 2
    y = 20
    pct = max(0, boss.vida / boss.vida_max)
    
    render_texto(pantalla, "⚠️ ¡JEFE ESPACIAL! ⚠️", 18, ROJO, ANCHO // 2, y - 10, centrado=True)
    
    pygame.draw.rect(pantalla, (40, 40, 40), (x, y + 8, w, h), border_radius=6)
    pygame.draw.rect(pantalla, ROJO, (x, y + 8, int(w * pct), h), border_radius=6)
    pygame.draw.rect(pantalla, BLANCO, (x, y + 8, w, h), 2, border_radius=6)
    render_texto(pantalla, f"{int(pct * 100)}%", 14, BLANCO, ANCHO // 2, y + 12, centrado=True)

def draw_guia_controles(pantalla, x, y):
    """Guía visual de controles."""
    controles = [
        "← → ↑ ↓ / WASD : MOVER",
        "ESPACIO / J / Z / CLIC : DISPARAR",
        "F11 : PANTALLA COMPLETA",
        "P : PAUSA | ESC : SALIR"
    ]
    box_rect = pygame.Rect(x - 10, y - 5, 245, 110)
    s = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 160))
    pantalla.blit(s, box_rect.topleft)
    pygame.draw.rect(pantalla, AZUL_CYAN, box_rect, 1, border_radius=6)

    for i, txt in enumerate(controles):
        render_texto(pantalla, txt, 12, BLANCO, x, y + i * 25, centrado=False)

def pantalla_inicio(pantalla, clock, fondo_menu, callback_opciones=None):
    """Pantalla principal de inicio con selección de dificultad y botón de Opciones."""
    record = leer_record()
    btn_w, btn_h = 320, 50
    botones = [
        ("FÁCIL", 1, pygame.Rect(ANCHO // 2 - btn_w // 2, 275, btn_w, btn_h)),
        ("NORMAL", 2, pygame.Rect(ANCHO // 2 - btn_w // 2, 340, btn_w, btn_h)),
        ("DIFÍCIL", 3, pygame.Rect(ANCHO // 2 - btn_w // 2, 405, btn_w, btn_h)),
        ("⚙️ OPCIONES", "OPCIONES", pygame.Rect(ANCHO // 2 - btn_w // 2, 470, btn_w, btn_h)),
    ]

    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for txt, val, rect in botones:
                    if rect.collidepoint((mx, my)):
                        if val == "OPCIONES":
                            if callback_opciones:
                                callback_opciones()
                        else:
                            return val
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    return 1
                if e.key == pygame.K_2:
                    return 2
                if e.key == pygame.K_3:
                    return 3
                if e.key == pygame.K_o:
                    if callback_opciones:
                        callback_opciones()
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pantalla.blit(fondo_menu, (0, 0))
        
        render_texto(pantalla, "JUEGO RETRO DANVB", 72, NEGRO, ANCHO // 2 + 4, 144, fuente_nombre="courier new")
        render_texto(pantalla, "JUEGO RETRO DANVB", 72, AZUL_CYAN, ANCHO // 2, 140, fuente_nombre="courier new")
        render_texto(pantalla, f"🏆 RÉCORD MÁXIMO: {record} PUNTOS", 22, AMARILLO, ANCHO // 2, 225)

        for txt, val, rect in botones:
            hover = rect.collidepoint((mx, my))
            if val == "OPCIONES":
                color_base = (70, 90, 120)
            else:
                color_base = DIFICULTADES[val]["color"]
                
            color = (min(255, color_base[0] + 40), min(255, color_base[1] + 40), min(255, color_base[2] + 40)) if hover else color_base
            
            pygame.draw.rect(pantalla, color, rect, border_radius=18)
            pygame.draw.rect(pantalla, BLANCO if hover else NEGRO, rect, 3, border_radius=18)
            render_texto(pantalla, txt, 26, BLANCO, rect.centerx, rect.centery)

        render_texto(pantalla, "Haz clic en una opción o presiona 1, 2, 3 u O (Opciones)", 15, BLANCO, ANCHO // 2, 545)

        pygame.display.flip()
        clock.tick(FPS)

def pantalla_opciones(pantalla, clock, fondo_menu, callback_fullscreen_toggle=None):
    """Menú de configuración y opciones de Audio y Pantalla."""
    opts = leer_opciones()
    vol_musica = opts.get("volumen_musica", 0.25)
    vol_sfx = opts.get("volumen_sfx", 0.40)
    pantalla_completa = opts.get("pantalla_completa", False)

    btn_w, btn_h = 45, 45
    btn_fs_w, btn_fs_h = 320, 50
    btn_back_w, btn_back_h = 280, 50

    while True:
        mx, my = pygame.mouse.get_pos()
        
        # Rectángulos de botones interconectados
        rect_m_down = pygame.Rect(ANCHO // 2 + 60, 220, btn_w, btn_h)
        rect_m_up = pygame.Rect(ANCHO // 2 + 220, 220, btn_w, btn_h)
        
        rect_sfx_down = pygame.Rect(ANCHO // 2 + 60, 300, btn_w, btn_h)
        rect_sfx_up = pygame.Rect(ANCHO // 2 + 220, 300, btn_w, btn_h)
        
        rect_fs = pygame.Rect(ANCHO // 2 - btn_fs_w // 2, 380, btn_fs_w, btn_fs_h)
        rect_back = pygame.Rect(ANCHO // 2 - btn_back_w // 2, 465, btn_back_w, btn_back_h)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                guardar_opciones({"volumen_musica": vol_musica, "volumen_sfx": vol_sfx, "pantalla_completa": pantalla_completa})
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if rect_m_down.collidepoint((mx, my)):
                    vol_musica = max(0.0, round(vol_musica - 0.05, 2))
                    aplicar_volumen_musica(vol_musica)
                elif rect_m_up.collidepoint((mx, my)):
                    vol_musica = min(1.0, round(vol_musica + 0.05, 2))
                    aplicar_volumen_musica(vol_musica)
                elif rect_sfx_down.collidepoint((mx, my)):
                    vol_sfx = max(0.0, round(vol_sfx - 0.05, 2))
                    aplicar_volumen_sfx(vol_sfx / 0.40 if vol_sfx > 0 else 0)
                elif rect_sfx_up.collidepoint((mx, my)):
                    vol_sfx = min(1.0, round(vol_sfx + 0.05, 2))
                    aplicar_volumen_sfx(vol_sfx / 0.40)
                elif rect_fs.collidepoint((mx, my)):
                    pantalla_completa = not pantalla_completa
                    if callback_fullscreen_toggle:
                        callback_fullscreen_toggle(pantalla_completa)
                elif rect_back.collidepoint((mx, my)):
                    guardar_opciones({"volumen_musica": vol_musica, "volumen_sfx": vol_sfx, "pantalla_completa": pantalla_completa})
                    return

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11:
                    pantalla_completa = not pantalla_completa
                    if callback_fullscreen_toggle:
                        callback_fullscreen_toggle(pantalla_completa)
                if e.key == pygame.K_ESCAPE or e.key == pygame.K_RETURN:
                    guardar_opciones({"volumen_musica": vol_musica, "volumen_sfx": vol_sfx, "pantalla_completa": pantalla_completa})
                    return

        pantalla.blit(fondo_menu, (0, 0))
        
        # Panel translúcido de opciones
        panel_rect = pygame.Rect(ANCHO // 2 - 340, 60, 680, 480)
        s_panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        s_panel.fill((15, 15, 25, 220))
        pantalla.blit(s_panel, panel_rect.topleft)
        pygame.draw.rect(pantalla, AZUL_CYAN, panel_rect, 2, border_radius=16)

        render_texto(pantalla, "⚙️ OPCIONES Y CONFIGURACIÓN", 36, AMARILLO, ANCHO // 2, 110)

        # 1. Volumen de Música
        render_texto(pantalla, "🎶 VOLUMEN MÚSICA:", 22, BLANCO, ANCHO // 2 - 280, 240, centrado=False)
        render_texto(pantalla, f"{int(vol_musica * 100)}%", 22, AZUL_CYAN, ANCHO // 2 + 140, 240)
        
        pygame.draw.rect(pantalla, ROJO if rect_m_down.collidepoint((mx, my)) else (100, 100, 100), rect_m_down, border_radius=8)
        render_texto(pantalla, "-", 26, BLANCO, rect_m_down.centerx, rect_m_down.centery)
        
        pygame.draw.rect(pantalla, VERDE if rect_m_up.collidepoint((mx, my)) else (100, 100, 100), rect_m_up, border_radius=8)
        render_texto(pantalla, "+", 26, BLANCO, rect_m_up.centerx, rect_m_up.centery)

        # 2. Volumen de Efectos SFX
        render_texto(pantalla, "🔊 EFECTOS DE SONIDO (SFX):", 22, BLANCO, ANCHO // 2 - 280, 320, centrado=False)
        render_texto(pantalla, f"{int(vol_sfx * 100)}%", 22, AZUL_CYAN, ANCHO // 2 + 140, 320)
        
        pygame.draw.rect(pantalla, ROJO if rect_sfx_down.collidepoint((mx, my)) else (100, 100, 100), rect_sfx_down, border_radius=8)
        render_texto(pantalla, "-", 26, BLANCO, rect_sfx_down.centerx, rect_sfx_down.centery)
        
        pygame.draw.rect(pantalla, VERDE if rect_sfx_up.collidepoint((mx, my)) else (100, 100, 100), rect_sfx_up, border_radius=8)
        render_texto(pantalla, "+", 26, BLANCO, rect_sfx_up.centerx, rect_sfx_up.centery)

        # 3. Pantalla Completa Toggle
        hover_fs = rect_fs.collidepoint((mx, my))
        txt_fs = "🖥️ PANTALLA COMPLETA: SI" if pantalla_completa else "📺 PANTALLA COMPLETA: NO"
        color_fs = (0, 180, 220) if hover_fs else (40, 60, 90)
        pygame.draw.rect(pantalla, color_fs, rect_fs, border_radius=14)
        pygame.draw.rect(pantalla, BLANCO, rect_fs, 2, border_radius=14)
        render_texto(pantalla, txt_fs, 20, BLANCO, rect_fs.centerx, rect_fs.centery)

        # 4. Botón Volver
        hover_back = rect_back.collidepoint((mx, my))
        color_back = (60, 180, 75) if hover_back else (40, 120, 50)
        pygame.draw.rect(pantalla, color_back, rect_back, border_radius=14)
        pygame.draw.rect(pantalla, BLANCO, rect_back, 2, border_radius=14)
        render_texto(pantalla, "💾 GUARDAR Y VOLVER", 22, BLANCO, rect_back.centerx, rect_back.centery)

        pygame.display.flip()
        clock.tick(FPS)

def pantalla_pausa(pantalla, clock):
    """Pantalla de pausa."""
    s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    s.fill((0, 0, 0, 180))
    pantalla.blit(s, (0, 0))
    
    render_texto(pantalla, "PAUSA", 80, AMARILLO, ANCHO // 2, 220)
    render_texto(pantalla, "Presiona 'P' para continuar", 32, BLANCO, ANCHO // 2, 320)
    render_texto(pantalla, "Presiona 'ESC' para salir", 26, (180, 180, 180), ANCHO // 2, 380)

    pygame.display.flip()
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p or e.key == pygame.K_SPACE:
                    return
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)

def pantalla_game_over(pantalla, clock, puntos):
    """Pantalla de fin de juego (Game Over)."""
    s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    s.fill((20, 0, 0, 220))
    pantalla.blit(s, (0, 0))
    
    render_texto(pantalla, "GAME OVER", 90, ROJO, ANCHO // 2, 200)
    render_texto(pantalla, f"PUNTUACIÓN FINAL: {puntos}", 38, BLANCO, ANCHO // 2, 300)
    render_texto(pantalla, f"MÁXIMO RÉCORD: {leer_record()}", 24, AMARILLO, ANCHO // 2, 350)
    render_texto(pantalla, "Presiona 'R' para jugar de nuevo", 30, AZUL_CYAN, ANCHO // 2, 420)
    render_texto(pantalla, "Presiona 'ESC' para volver al menú", 24, (180, 180, 180), ANCHO // 2, 470)

    pygame.display.flip()
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return "REINICIAR"
                if e.key == pygame.K_ESCAPE:
                    return "MENU"
        clock.tick(FPS)

def pantalla_victoria(pantalla, clock, puntos):
    """Pantalla de victoria tras derrotar al Boss."""
    s = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    s.fill((0, 20, 0, 220))
    pantalla.blit(s, (0, 0))
    
    render_texto(pantalla, "¡VICTORIA!", 90, VERDE, ANCHO // 2, 200)
    render_texto(pantalla, f"¡JEFE DERROTADO! PUNTOS: {puntos}", 36, BLANCO, ANCHO // 2, 300)
    render_texto(pantalla, "Presiona 'R' para avanzar al siguiente nivel", 30, AMARILLO, ANCHO // 2, 400)
    render_texto(pantalla, "Presiona 'ESC' para salir al menú", 24, (180, 180, 180), ANCHO // 2, 460)

    pygame.display.flip()
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return "CONTINUAR"
                if e.key == pygame.K_ESCAPE:
                    return "MENU"
        clock.tick(FPS)
