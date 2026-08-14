import random
import sys
import pygame
from src.config import ANCHO, ALTO, FPS, DIFICULTADES
from src.utils import (
    cargar_imagen, cargar_sonido, iniciar_musica_fondo,
    leer_record, guardar_record, leer_opciones, guardar_opciones
)
from src.sprites import (
    Jugador, Enemigo, Boss, Bala, BalaEnemigo,
    PowerUp, Particula, FondoEstrellas
)
from src.ui import (
    pantalla_inicio, pantalla_opciones, pantalla_pausa, pantalla_game_over,
    pantalla_victoria, draw_hud, draw_boss_hud
)

# Cargar efectos de sonido de juego
sonido_explosion = cargar_sonido("explosion.wav", 0.4)
sonido_dano = cargar_sonido("dano.wav", 0.4)
sonido_inicio = cargar_sonido("inicio.wav", 0.5)
sonido_powerup = cargar_sonido("boss_hit.wav", 0.35)

class JuegoController:
    def __init__(self, pantalla, clock):
        self.pantalla = pantalla
        self.clock = clock
        self.fondo_menu = cargar_imagen("fondo_menu.png", (ANCHO, ALTO))
        self.fondo_estrellas = FondoEstrellas()
        
        # Aplicar modo de pantalla al iniciar según opciones guardadas
        opts = leer_opciones()
        if opts.get("pantalla_completa", False):
            self.toggle_fullscreen(True)

    def toggle_fullscreen(self, es_fullscreen):
        """Alterna entre pantalla completa y ventana."""
        opts = leer_opciones()
        opts["pantalla_completa"] = es_fullscreen
        guardar_opciones(opts)

        if es_fullscreen:
            self.pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
        else:
            self.pantalla = pygame.display.set_mode((ANCHO, ALTO))

    def iniciar(self):
        """Bucle principal de la aplicación."""
        iniciar_musica_fondo()

        while True:
            def abir_opciones():
                pantalla_opciones(self.pantalla, self.clock, self.fondo_menu, callback_fullscreen_toggle=self.toggle_fullscreen)

            dificultad_id = pantalla_inicio(self.pantalla, self.clock, self.fondo_menu, callback_opciones=abir_opciones)
            if sonido_inicio:
                sonido_inicio.play()
            res = self.ejecutar_partida(dificultad_id)
            if res == "SALIR":
                break

    def crear_explosion(self, x, y, cantidad=15, color=None):
        for _ in range(cantidad):
            p = Particula(x, y, color)
            self.particulas.add(p)
            self.todos.add(p)

    def ejecutar_partida(self, dificultad_id):
        config_dif = DIFICULTADES[dificultad_id]
        mult_dif = config_dif["multiplicador_danio"]
        
        # Grupos de Sprites
        self.todos = pygame.sprite.Group()
        self.balas = pygame.sprite.Group()
        self.enemigos = pygame.sprite.Group()
        self.balas_enemigas = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.particulas = pygame.sprite.Group()

        # Instanciar jugador con referencia directa a los grupos de disparos
        jugador = Jugador(grupo_balas=self.balas, grupo_todos=self.todos)
        self.todos.add(jugador)

        nivel = 1
        puntos = 0
        boss = None

        def crear_nivel():
            nonlocal boss
            for b in self.balas_enemigas:
                b.kill()

            if nivel % 5 == 0:
                boss = Boss(nivel, mult_dif)
                self.todos.add(boss)
            else:
                boss = None
                cant_enemigos = 5 + nivel * 2
                for i in range(cant_enemigos):
                    tipo = "cazador" if i % 3 == 0 and nivel >= 2 else "comun"
                    e = Enemigo(nivel, mult_dif, tipo=tipo)
                    self.enemigos.add(e)
                    self.todos.add(e)

        crear_nivel()

        mantiene_jugando = True
        while mantiene_jugando:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    guardar_record(puntos)
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key in (pygame.K_SPACE, pygame.K_j, pygame.K_z, pygame.K_LCTRL, pygame.K_RCTRL):
                        jugador.disparar()
                    if e.key == pygame.K_F11:
                        opts = leer_opciones()
                        self.toggle_fullscreen(not opts.get("pantalla_completa", False))
                    if e.key == pygame.K_p:
                        pantalla_pausa(self.pantalla, self.clock)
                    if e.key == pygame.K_ESCAPE:
                        guardar_record(puntos)
                        return "MENU"
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    jugador.disparar()

            # Actualización de Entidades
            self.fondo_estrellas.update(self.pantalla)

            # Actualizar enemigos y capturar proyectiles lanzados
            for e in self.enemigos:
                nueva_bala = e.update(jugador_pos=jugador.rect.center)
                if nueva_bala:
                    self.balas_enemigas.add(nueva_bala)
                    self.todos.add(nueva_bala)

            if boss:
                nuevas_balas_boss = boss.update()
                for b in nuevas_balas_boss:
                    self.balas_enemigas.add(b)
                    self.todos.add(b)

            # Actualizar jugador, proyectiles y efectos
            jugador.update()
            self.balas.update()
            self.balas_enemigas.update()
            self.powerups.update()
            self.particulas.update()

            # Colisiones: Balas -> Enemigos
            colis_enemigos = pygame.sprite.groupcollide(self.enemigos, self.balas, True, True)
            for enemigo_hit, _ in colis_enemigos.items():
                puntos += 10
                self.crear_explosion(enemigo_hit.rect.centerx, enemigo_hit.rect.centery, cantidad=12)
                if sonido_explosion:
                    sonido_explosion.play()

                if random.random() < 0.20:
                    pw = PowerUp(enemigo_hit.rect.centerx, enemigo_hit.rect.centery)
                    self.powerups.add(pw)
                    self.todos.add(pw)

            # Balas -> Boss
            if boss:
                hits_boss = pygame.sprite.spritecollide(boss, self.balas, True)
                for _ in hits_boss:
                    puntos += 3
                    self.crear_explosion(boss.rect.centerx + random.randint(-40, 40), boss.rect.bottom, cantidad=4)
                    boss_muerto = boss.recibir_danio(14)
                    if boss_muerto:
                        puntos += 300
                        self.crear_explosion(boss.rect.centerx, boss.rect.centery, cantidad=60)
                        if sonido_explosion:
                            sonido_explosion.play()
                        guardar_record(puntos)
                        res_vic = pantalla_victoria(self.pantalla, self.clock, puntos)
                        if res_vic == "CONTINUAR":
                            nivel += 1
                            jugador.vida = min(jugador.vida_max, jugador.vida + 40)
                            crear_nivel()
                        else:
                            return "MENU"

            # Balas Enemigas -> Jugador
            hits_jugador = pygame.sprite.spritecollide(jugador, self.balas_enemigas, True)
            for _ in hits_jugador:
                danio_recibido = int(8 * mult_dif)
                fue_danado = jugador.recibir_danio(danio_recibido)
                if fue_danado:
                    self.crear_explosion(jugador.rect.centerx, jugador.rect.centery, cantidad=8, color=(255, 100, 100))
                    if sonido_dano:
                        sonido_dano.play()

            # Enemigo directo -> Jugador
            colis_directa = pygame.sprite.spritecollide(jugador, self.enemigos, True)
            for enemigo_hit in colis_directa:
                self.crear_explosion(enemigo_hit.rect.centerx, enemigo_hit.rect.centery, cantidad=15)
                jugador.recibir_danio(int(20 * mult_dif))

            # Jugador -> PowerUps
            hits_powerup = pygame.sprite.spritecollide(jugador, self.powerups, True)
            for pw in hits_powerup:
                jugador.activar_powerup(pw.tipo)
                puntos += 15
                if sonido_powerup:
                    sonido_powerup.play()

            # Muerte del Jugador
            if jugador.vida <= 0:
                guardar_record(puntos)
                self.crear_explosion(jugador.rect.centerx, jugador.rect.centery, cantidad=40)
                res_go = pantalla_game_over(self.pantalla, self.clock, puntos)
                if res_go == "REINICIAR":
                    return self.ejecutar_partida(dificultad_id)
                else:
                    return "MENU"

            # Avance de Nivel
            if not self.enemigos and not boss:
                nivel += 1
                jugador.vida = min(jugador.vida_max, jugador.vida + 20)
                crear_nivel()

            # Renderizado
            self.todos.draw(self.pantalla)

            record_actual = leer_record()
            draw_hud(self.pantalla, jugador, nivel, puntos, max(puntos, record_actual))

            if boss:
                draw_boss_hud(self.pantalla, boss)

            pygame.display.flip()
            self.clock.tick(FPS)

        return "MENU"
