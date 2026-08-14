import random
import math
import pygame
from src.config import ANCHO, ALTO, ROJO, AZUL_CYAN, AMARILLO, VERDE
from src.utils import cargar_imagen, cargar_sonido

# Cargar sonidos una vez para sprites
sonido_disparo = cargar_sonido("disparo.wav", 0.3)
sonido_boss_hit = cargar_sonido("boss_hit.wav", 0.5)

class Jugador(pygame.sprite.Sprite):
    def __init__(self, grupo_balas=None, grupo_todos=None):
        super().__init__()
        self.image_original = cargar_imagen("jugador1.png", (50, 50))
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect(midbottom=(ANCHO // 2, ALTO - 25))
        
        self.grupo_balas = grupo_balas
        self.grupo_todos = grupo_todos
        
        self.vel_base = 6
        self.vel = self.vel_base
        self.vida_max = 100
        self.vida = self.vida_max
        self.cd = 0
        self.cd_max = 9  # Cadencia de disparo
        
        # Timers de Power-ups y Estados
        self.invulnerable_timer = 0
        self.disparo_triple_timer = 0
        self.velocidad_timer = 0
        self.escudo_activo = False

    def update(self, *args, **kwargs):
        # Timers
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
            if (self.invulnerable_timer // 4) % 2 == 0:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

        if self.disparo_triple_timer > 0:
            self.disparo_triple_timer -= 1

        if self.velocidad_timer > 0:
            self.velocidad_timer -= 1
            self.vel = self.vel_base + 3
        else:
            self.vel = self.vel_base

        if self.cd > 0:
            self.cd -= 1

        # Movimiento 4 Direcciones (Flechas + WASD)
        k = pygame.key.get_pressed()
        dx, dy = 0, 0
        if k[pygame.K_LEFT] or k[pygame.K_a]:
            dx -= self.vel
        if k[pygame.K_RIGHT] or k[pygame.K_d]:
            dx += self.vel
        if k[pygame.K_UP] or k[pygame.K_w]:
            dy -= self.vel
        if k[pygame.K_DOWN] or k[pygame.K_s]:
            dy += self.vel

        self.rect.x += dx
        self.rect.y += dy

        # Limitar dentro de los bordes de pantalla
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(ANCHO, self.rect.right)
        self.rect.top = max(10, self.rect.top)
        self.rect.bottom = min(ALTO - 10, self.rect.bottom)

        # AUTOFIRE: Dispara manteniendo presionado ESPACIO, J, Z, CTRL o Clic Izquierdo del Ratón
        mouse_down = pygame.mouse.get_pressed()[0]
        if k[pygame.K_SPACE] or k[pygame.K_j] or k[pygame.K_z] or k[pygame.K_LCTRL] or k[pygame.K_RCTRL] or mouse_down:
            self.disparar()

    def disparar(self, grupo_balas=None, grupo_todos=None):
        g_balas = grupo_balas if grupo_balas is not None else self.grupo_balas
        g_todos = grupo_todos if grupo_todos is not None else self.grupo_todos

        if self.cd == 0:
            self.cd = self.cd_max
            if sonido_disparo:
                sonido_disparo.play()

            if self.disparo_triple_timer > 0:
                # Disparo triple en abanico
                b1 = Bala(self.rect.centerx, self.rect.top, dx=-3)
                b2 = Bala(self.rect.centerx, self.rect.top, dx=0)
                b3 = Bala(self.rect.centerx, self.rect.top, dx=3)
                balas_creadas = [b1, b2, b3]
            else:
                # Disparo estándar único
                balas_creadas = [Bala(self.rect.centerx, self.rect.top)]

            if g_balas is not None:
                for b in balas_creadas:
                    g_balas.add(b)
            if g_todos is not None:
                for b in balas_creadas:
                    g_todos.add(b)

            return balas_creadas
        return []

    def recibir_danio(self, cantidad):
        if self.invulnerable_timer > 0:
            return False
            
        if self.escudo_activo:
            self.escudo_activo = False
            self.invulnerable_timer = 40
            return False

        self.vida -= cantidad
        self.invulnerable_timer = 50
        return True

    def activar_powerup(self, tipo):
        if tipo == "shield":
            self.vida = min(self.vida_max, self.vida + 35)
            self.escudo_activo = True
        elif tipo == "weapon":
            self.disparo_triple_timer = 360 # 6 segundos a 60FPS
        elif tipo == "speed":
            self.velocidad_timer = 360

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, dx=0, dy=-14):
        super().__init__()
        self.image = cargar_imagen("bala.png", (12, 22))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy

    def update(self, *args, **kwargs):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.bottom < -20 or self.rect.left < -20 or self.rect.right > ANCHO + 20:
            self.kill()

class BalaEnemigo(pygame.sprite.Sprite):
    def __init__(self, x, y, dx=0, dy=9):
        super().__init__()
        self.image = cargar_imagen("bala_enemigo.png", (12, 22))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy

    def update(self, *args, **kwargs):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.top > ALTO or self.rect.right < 0 or self.rect.left > ANCHO:
            self.kill()

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, nivel, dificultad, tipo="comun"):
        super().__init__()
        self.tipo = tipo
        self.dificultad = dificultad
        
        if self.tipo == "cazador":
            self.image = cargar_imagen("enemigo2.png", (42, 42))
            self.vel_x = 2.5 + nivel * 0.2 * dificultad
            self.timer_disparo_max = random.randint(80, 160) // dificultad
        else:
            self.image = cargar_imagen("enemigo1.png", (40, 40))
            self.vel_x = random.choice([-2.5, 2.5]) * (1 + nivel * 0.1 * dificultad)
            self.timer_disparo_max = random.randint(100, 200) // dificultad

        self.rect = self.image.get_rect(
            center=(random.randint(40, ANCHO - 40), random.randint(40, 180))
        )
        self.timer = self.timer_disparo_max

    def update(self, jugador_pos=None):
        if self.tipo == "cazador" and jugador_pos:
            # El cazador se alinea horizontalmente con el jugador
            jx, _ = jugador_pos
            if self.rect.centerx < jx - 5:
                self.rect.x += self.vel_x
            elif self.rect.centerx > jx + 5:
                self.rect.x -= self.vel_x
        else:
            # Movimiento en zig-zag estándar
            self.rect.x += self.vel_x
            if self.rect.left <= 10 or self.rect.right >= ANCHO - 10:
                self.vel_x *= -1

        self.timer -= 1
        if self.timer <= 0:
            self.timer = self.timer_disparo_max
            return BalaEnemigo(self.rect.centerx, self.rect.bottom)
        return None

class Boss(pygame.sprite.Sprite):
    def __init__(self, nivel, dificultad):
        super().__init__()
        self.image_base = cargar_imagen("boss.png", (190, 135))
        self.image = self.image_base.copy()
        self.rect = self.image.get_rect(midtop=(ANCHO // 2, -160))
        
        self.dificultad = dificultad
        self.vel = 3.5 + dificultad * 0.8
        self.vida_max = int(450 + nivel * 150 * dificultad)
        self.vida = self.vida_max
        
        self.timer_disparo = 40
        self.fase_ataque = 1
        self.flash_timer = 0

    def update(self):
        # Entrada suave a pantalla
        if self.rect.top < 35:
            self.rect.y += 3
            return []

        # Parpadeo de daño
        if self.flash_timer > 0:
            self.flash_timer -= 1
            if self.flash_timer == 0:
                self.image = self.image_base.copy()

        # Movimiento de lado a lado
        self.rect.x += self.vel
        if self.rect.left <= 20 or self.rect.right >= ANCHO - 20:
            self.vel *= -1

        # Patrones de ataque
        self.timer_disparo -= 1
        balas_creadas = []
        if self.timer_disparo <= 0:
            self.timer_disparo = max(20, 50 - self.dificultad * 8)
            
            # Alternar patrón según la vida restante
            if self.vida < self.vida_max * 0.4:
                # Fase furia: 5 proyectiles en abanico amplio
                for dx in (-50, -25, 0, 25, 50):
                    balas_creadas.append(BalaEnemigo(self.rect.centerx + dx, self.rect.bottom, dx=dx//10, dy=10))
            else:
                # Fase normal: 3 proyectiles
                for dx in (-35, 0, 35):
                    balas_creadas.append(BalaEnemigo(self.rect.centerx + dx, self.rect.bottom))

        return balas_creadas

    def recibir_danio(self, cantidad):
        self.vida -= cantidad
        self.flash_timer = 5
        # Crear tinte rojo de impacto
        tinte = self.image_base.copy()
        tinte.fill((255, 100, 100, 200), special_flags=pygame.BLEND_RGBA_MULT)
        self.image = tinte
        if sonido_boss_hit:
            sonido_boss_hit.play()
        if self.vida <= 0:
            self.kill()
            return True
        return False

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.tipo = random.choice(["shield", "weapon", "speed"])
        self.image = cargar_imagen(f"powerup_{self.tipo}.png", (30, 30))
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = 2.5

    def update(self):
        self.rect.y += self.vel_y
        if self.rect.top > ALTO:
            self.kill()

class Particula(pygame.sprite.Sprite):
    def __init__(self, x, y, color=None):
        super().__init__()
        size = random.randint(3, 7)
        self.image = pygame.Surface((size, size))
        self.color = color or random.choice([(255, 200, 50), (255, 80, 20), (255, 255, 255)])
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=(x, y))
        
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 7)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.vida = random.randint(15, 30)

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        self.vida -= 1
        if self.vida <= 0:
            self.kill()

class FondoEstrellas:
    """Fondo dinámico de estrellas estilo Parallax Scrolling."""
    def __init__(self):
        self.estrellas = []
        for _ in range(70):
            x = random.randint(0, ANCHO)
            y = random.randint(0, ALTO)
            vel = random.uniform(0.5, 3.0)
            tam = 1 if vel < 1.5 else 2 if vel < 2.5 else 3
            color = (180, 220, 255) if vel > 2.0 else (255, 255, 255) if vel > 1.0 else (120, 140, 180)
            self.estrellas.append([x, y, vel, tam, color])

    def update(self, superficie):
        superficie.fill((12, 12, 24)) # Fondo azul oscuro profundo
        for e in self.estrellas:
            e[1] += e[2] # Mover estrella hacia abajo
            if e[1] >= ALTO:
                e[1] = 0
                e[0] = random.randint(0, ANCHO)
            pygame.draw.circle(superficie, e[4], (int(e[0]), int(e[1])), e[3])
