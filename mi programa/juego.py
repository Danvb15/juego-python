import pygame
import random
import sys
import os

# =================================================
# CONFIG
# =================================================
ANCHO, ALTO = 1110, 600
FPS = 60

pygame.init()
pygame.mixer.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Juego Retro DanVB")
clock = pygame.time.Clock()

# =================================================
# RUTAS (PyInstaller)
# =================================================
def ruta_recurso(r):
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(".")
    return os.path.join(base, r)

def ruta_guardado(nombre):
    base = os.path.expanduser("~")
    carpeta = os.path.join(base, "JuegoRetroDanVB")
    os.makedirs(carpeta, exist_ok=True)
    return os.path.join(carpeta, nombre)

ARCHIVO_RECORD = ruta_guardado("record.txt")

# =================================================
# UTILIDADES
# =================================================
def cargar_imagen(nombre, escala=None):
    try:
        img = pygame.image.load(ruta_recurso(nombre)).convert_alpha()
        if escala:
            img = pygame.transform.scale(img, escala)
        return img
    except:
        surf = pygame.Surface(escala or (40, 40), pygame.SRCALPHA)
        surf.fill((200, 60, 60))
        return surf

def cargar_sonido(nombre):
    try:
        return pygame.mixer.Sound(ruta_recurso(nombre))
    except:
        return None

def leer_record():
    if os.path.exists(ARCHIVO_RECORD):
        with open(ARCHIVO_RECORD, "r") as f:
            return int(f.read())
    return 0

def guardar_record(p):
    if p > leer_record():
        with open(ARCHIVO_RECORD, "w") as f:
            f.write(str(p))

# =================================================
# IMÁGENES
# =================================================
fondo_menu = cargar_imagen("imagenes/fondo_menu.png", (ANCHO, ALTO))
fondo_juego = cargar_imagen("imagenes/fondo_juego.png", (ANCHO, ALTO))

# =================================================
# SONIDOS
# =================================================
sonido_disparo = cargar_sonido("sonidos/disparo.wav")
sonido_explosion = cargar_sonido("sonidos/explosion.wav")
sonido_daño = cargar_sonido("sonidos/daño.wav")
sonido_boss = cargar_sonido("sonidos/boss_hit.wav")

for s, v in [
    (sonido_disparo, 0.3),
    (sonido_explosion, 0.5),
    (sonido_daño, 0.4),
    (sonido_boss, 0.6)
]:
    if s:
        s.set_volume(v)

# =================================================
# CLASES
# =================================================
class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = cargar_imagen("imagenes/jugador1.png", (48, 48))
        self.rect = self.image.get_rect(midbottom=(ANCHO//2, ALTO-20))
        self.vel = 6
        self.vida = 100
        self.cd = 0

    def update(self):
        k = pygame.key.get_pressed()
        if k[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.vel
        if k[pygame.K_RIGHT] and self.rect.right < ANCHO:
            self.rect.x += self.vel
        if self.cd > 0:
            self.cd -= 1

    def disparar(self):
        if self.cd == 0:
            b = Bala(self.rect.centerx, self.rect.top)
            balas.add(b)
            todos.add(b)
            self.cd = 8
            if sonido_disparo:
                sonido_disparo.play()

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = cargar_imagen("imagenes/bala.png", (12, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = -18

    def update(self):
        self.rect.y += self.vel
        if self.rect.bottom < 0:
            self.kill()

class BalaEnemigo(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = cargar_imagen("imagenes/bala_enemigo.png", (12, 20))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = 10

    def update(self):
        self.rect.y += self.vel
        if self.rect.top > ALTO:
            self.kill()

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, nivel, dificultad):
        super().__init__()
        self.image = cargar_imagen("imagenes/enemigo1.png", (40, 40))
        self.rect = self.image.get_rect(
            center=(random.randint(40, ANCHO-40), random.randint(40, 160))
        )
        self.vel = random.choice([-2, 2]) + nivel * 0.3
        self.timer = random.randint(90, 200) // dificultad

    def update(self):
        self.rect.x += self.vel
        if self.rect.left <= 0 or self.rect.right >= ANCHO:
            self.vel *= -1

        self.timer -= 1
        if self.timer <= 0:
            b = BalaEnemigo(self.rect.centerx, self.rect.bottom)
            balas_enemigas.add(b)
            todos.add(b)
            self.timer = random.randint(90, 200)

class Boss(pygame.sprite.Sprite):
    def __init__(self, nivel, dificultad):
        super().__init__()
        self.image = cargar_imagen("imagenes/boss.png", (180, 130))
        self.rect = self.image.get_rect(midtop=(ANCHO//2, -150))
        self.dificultad = dificultad
        self.vel = 4 + dificultad
        self.vida_max = 400 + nivel * 120 * dificultad
        self.vida = self.vida_max
        self.timer = 45 - dificultad * 5

    def update(self):
        if self.rect.top < 40:
            self.rect.y += 3
            return

        self.rect.x += self.vel
        if self.rect.left <= 0 or self.rect.right >= ANCHO:
            self.vel *= -1

        self.timer -= 1
        if self.timer <= 0:
            for dx in (-30, 0, 30):
                b = BalaEnemigo(self.rect.centerx + dx, self.rect.bottom)
                balas_enemigas.add(b)
                todos.add(b)
            self.timer = 45 - self.dificultad * 5

    def daño(self, d):
        self.vida -= d
        if self.vida <= 0:
            self.kill()

# =================================================
# HUD + PANTALLAS
# =================================================
def draw_text(text, size, color, y):
    font = pygame.font.SysFont("courier new", size, bold=True)
    t = font.render(text, True, color)
    pantalla.blit(t, t.get_rect(center=(ANCHO//2, y)))

def guia_controles(x, y):
    font = pygame.font.SysFont("Arial", 18)
    color = (220, 220, 220)

    controles = [
        "←  →   MOVER",
        "ESPACIO  DISPARAR",
        "P  PAUSA",
        "ESC  SALIR"
    ]

    for i, texto in enumerate(controles):
        t = font.render(texto, True, color)
        pantalla.blit(t, (x, y + i * 22))


def pantalla_pausa():
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    return
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pantalla.fill((20,20,20))
        draw_text("PAUSA", 80, (255,255,0), 250)
        draw_text("P = CONTINUAR", 36, (255,255,255), 330)
        draw_text("ESC = SALIR", 30, (200,200,200), 380)

        pygame.display.flip()
        clock.tick(FPS)

def pantalla_game_over(puntos):
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pantalla.fill((0,0,0))
        draw_text("GAME OVER", 90, (255,0,0), 240)
        draw_text(f"PUNTOS: {puntos}", 40, (255,255,255), 320)
        draw_text("R = REINICIAR", 32, (200,200,200), 380)
        draw_text("ESC = SALIR", 30, (200,200,200), 420)

        pygame.display.flip()
        clock.tick(FPS)

def pantalla_victoria(puntos):
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    return
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pantalla.fill((0,0,0))
        draw_text("¡VICTORIA!", 90, (0,255,0), 240)
        draw_text(f"PUNTOS: {puntos}", 40, (255,255,255), 320)
        draw_text("R = JUGAR OTRA VEZ", 32, (200,200,200), 380)
        draw_text("ESC = SALIR", 30, (200,200,200), 420)

        pygame.display.flip()
        clock.tick(FPS)
        
def barra_vida(x, y, vida):
    pygame.draw.rect(pantalla, (40,40,40), (x,y,200,18))
    pygame.draw.rect(pantalla, (0,200,0), (x,y,max(0,vida)*2,18))
    pygame.draw.rect(pantalla, (0,0,0), (x,y,200,18),2)

def barra_boss(b):
    w = 500
    x = ANCHO//2 - w//2
    pygame.draw.rect(pantalla,(40,40,40),(x,20,w,22))
    pygame.draw.rect(
        pantalla,
        (255,50,50),
        (x,20,int(w*(b.vida/b.vida_max)),22)
    )
    pygame.draw.rect(pantalla,(0,0,0),(x,20,w,22),3)


# =================================================
# MENÚ
# =================================================
def pantalla_inicio():
    fuente = pygame.font.SysFont("courier new", 80, bold=True)
    btn_font = pygame.font.SysFont("Arial", 36, True)

    botones = [
        ("FÁCIL", 1, pygame.Rect(ANCHO//2-160, 300, 320, 60)),
        ("NORMAL", 2, pygame.Rect(ANCHO//2-160, 370, 320, 60)),
        ("DIFÍCIL", 3, pygame.Rect(ANCHO//2-160, 440, 320, 60))
    ]

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                for t, d, r in botones:
                    if r.collidepoint(e.pos):
                        return d

        pantalla.blit(fondo_menu,(0,0))
        t = fuente.render("JUEGO RETRO DANVB", True, (0,200,255))
        pantalla.blit(t, t.get_rect(center=(ANCHO//2,200)))

        for txt, d, r in botones:
            color = (60,180,75) if d==1 else (200,170,40) if d==2 else (200,60,60)
            pygame.draw.rect(pantalla,color,r,border_radius=20)
            pygame.draw.rect(pantalla,(0,0,0),r,3,border_radius=20)
            tt = btn_font.render(txt,True,(255,255,255))
            pantalla.blit(tt,tt.get_rect(center=r.center))

        pygame.display.flip()
        clock.tick(FPS)

# =================================================
# JUEGO
# =================================================
def juego(dificultad):
    global todos, balas, enemigos, balas_enemigas

    todos = pygame.sprite.Group()
    balas = pygame.sprite.Group()
    enemigos = pygame.sprite.Group()
    balas_enemigas = pygame.sprite.Group()

    jugador = Jugador()
    todos.add(jugador)

    nivel = 1
    puntos = 0
    boss = None

    def crear_nivel():
        nonlocal boss
        if nivel % 5 == 0:
            boss = Boss(nivel, dificultad)
            todos.add(boss)
        else:
            for _ in range(6 + nivel * dificultad):
                e = Enemigo(nivel, dificultad)
                enemigos.add(e)
                todos.add(e)

    crear_nivel()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                guardar_record(puntos)
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    jugador.disparar()
                if e.key == pygame.K_p:
                    pantalla_pausa()

        todos.update()

        for _ in pygame.sprite.groupcollide(enemigos, balas, True, True):
            puntos += 5
            if sonido_explosion:
                sonido_explosion.play()

        if boss:
            hits = pygame.sprite.spritecollide(boss, balas, True)
            for _ in hits:
                boss.daño(12)
                puntos += 2
                if sonido_boss:
                    sonido_boss.play()
            if not boss.alive():
                pantalla_victoria(puntos)
                boss = None
                nivel += 1
                crear_nivel()


        if not enemigos and not boss:
            nivel += 1
            crear_nivel()

        if pygame.sprite.spritecollide(jugador, balas_enemigas, True):
            jugador.vida -= 6 * dificultad
            if sonido_daño:
                sonido_daño.play()

        if jugador.vida <= 0:
            guardar_record(puntos)
            pantalla_game_over(puntos)
            return

        pantalla.blit(fondo_juego,(0,0))
        todos.draw(pantalla)
        guia_controles(ANCHO - 220, ALTO - 110)

        # HUD
        barra_vida(10, 10, jugador.vida)

        if boss:
                barra_boss(boss)

                hud = pygame.font.SysFont("Arial",22)
                pantalla.blit(hud.render(f"Puntos: {puntos}",True,(255,255,255)),(10,35))
                pantalla.blit(hud.render(f"Nivel: {nivel}",True,(255,255,255)),(10,55))
                pantalla.blit(hud.render(f"Récord: {leer_record()}",True,(255,255,0)),(10,75))
                
        pygame.display.flip()
        clock.tick(FPS)

# =================================================
# MAIN
# =================================================
def main():
    pygame.mixer.music.load(ruta_recurso("sonidos/musica_fondo.mp3"))
    pygame.mixer.music.set_volume(0.35)
    pygame.mixer.music.play(-1)

    while True:
        dificultad = pantalla_inicio()
        juego(dificultad)

if __name__ == "__main__":
    main()
