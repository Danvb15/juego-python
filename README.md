# Juego Retro DanVB

**Juego Retro DanVB** es un videojuego de disparos espacial de corte arcade (*Shoot 'em up*) desarrollado en Python utilizando la librería Pygame. Diseñado con una arquitectura modular orientada a objetos, ofrece un rendimiento optimizado a 60 FPS, control continuo de disparo, variedad de enemigos, enfrentamientos contra jefes finales, sistema de mejoras (*power-ups*) y persistencia de configuraciones de usuario.

---

## 📌 Tabla de Contenidos
- [Manual de Juego y Mecánicas](#-manual-de-juego-y-mecánicas)
- [Guía de Controles](#-guía-de-controles)
- [Menú de Configuración y Opciones](#-menú-de-configuración-y-opciones)
- [Modos de Ejecución](#-modos-de-ejecución)
- [Empaquetado y Compilación](#-empaquetado-y-compilación)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Licencia](#-licencia)

---

## 🎮 Manual de Juego y Mecánicas

### Objetivo Principal
El objetivo del jugador es maniobrar su nave espacial a través de oleadas de naves enemigas, esquivar proyectiles hostiles, acumular la mayor puntuación posible y derrotar a los Jefes Espaciales que aparecen cada 5 niveles.

### Nivel de Dificultad
Al iniciar la partida se puede seleccionar entre tres modos de dificultad:
- **Fácil:** Multiplicador de daño reducido y menor velocidad de proyectiles enemigos.
- **Normal:** Experiencia equilibrada de juego arcade.
- **Difícil:** Mayor frecuencia de disparos enemigos, enemigos más veloces y daño incrementado.

### Variedad de Naves Enemigas
1. **Nave Estándar:** Realiza patrullas horizontales constantes a través del sector superior de la pantalla y dispara proyectiles verticales.
2. **Nave Cazadora (Hunter):** Sigue la posición horizontal del jugador de forma activa, buscando alinearse para efectuar disparos directos.
3. **Jefe Espacial (Boss):** Aparece cada 5 niveles con una barra de salud dedicada. Posee múltiples patrones de ataque (disparo triple y ráfagas en abanico) y entra en fase de furia cuando su salud cae por debajo del 40%.

### Sistema de Mejoras (Power-Ups)
Al eliminar naves enemigas existe la probabilidad de que caigan módulos de mejora:
- 🛡️ **Módulo de Escudo:** Restaura salud e incrementa la resistencia de la nave.
- ⚡ **Módulo de Disparo Triple:** Permite disparar 3 proyectiles simultáneos en abanico durante un periodo determinado.
- 🚀 **Módulo de Velocidad:** Otorga mayor agilidad de desplazamiento horizontal y vertical.

---

## 🕹️ Guía de Controles

El juego permite control mediante teclado y ratón con compatibilidad para disparo automático continuo (*Autofire*).

| Acción | Teclas Compatibles |
| :--- | :--- |
| **Mover Nave** | `Flechas de Dirección` (`←` `→` `↑` `↓`) o teclas `WASD` |
| **Disparo Continuo** | `ESPACIO`, `J`, `Z`, `CTRL` o `Clic Izquierdo del Ratón` |
| **Pantalla Completa** | Tecla `F11` (Alterna entre modo ventana y pantalla completa) |
| **Pausar Partida** | Tecla `P` |
| **Menú de Opciones** | Tecla `O` o clic en el botón `⚙️ OPCIONES` |
| **Salir / Menú Principal** | Tecla `ESC` |

---

## ⚙️ Menú de Configuración y Opciones

El juego incluye un menú de opciones persistente que guarda las preferencias en el archivo `opciones.json`:

- **Volumen de Música:** Ajuste en tiempo real de la banda sonora chiptune de fondo (0% a 100%).
- **Volumen de Efectos (SFX):** Ajuste del volumen de disparos, impactos y explosiones (0% a 100%).
- **Modo de Pantalla:** Alternancia entre el modo ventana nativo (`1110x600`) y Pantalla Completa.

---

## 🚀 Modos de Ejecución

### Modo 1: Ejecutable Independiente (Recomendado para Usuarios)
No requiere instalar Python ni librerías adicionales.

1. Navegar a la carpeta `dist/JuegoRetroDanVB/`.
2. Ejecutar el archivo `JuegoRetroDanVB.exe`.

### Modo 2: Entorno de Desarrollo (Para Programadores)
Requiere Python 3.9 o superior.

1. Clonar o descargar el repositorio.
2. Instalar la librería Pygame:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar el script principal:
   ```bash
   python main.py
   ```

---

## 📦 Empaquetado y Compilación

Para generar una versión ejecutable ejecute el script de automatización incluido:

```bash
python build_exe.py
```

El proceso compilará el código fuente y empaquetará los recursos multimedia dentro de la carpeta `dist/JuegoRetroDanVB/`.

---

## 📁 Estructura del Proyecto

```text
juego-python/
├── assets/                  # Recursos multimedia
│   ├── imagenes/            # Sprites vectoriales, íconos y fondos
│   └── sonidos/             # Efectos de audio de 8-bits y música chiptune
├── src/                     # Código fuente del sistema
│   ├── config.py            # Constantes globales, colores y rutas de guardado
│   ├── utils.py             # Carga segura de recursos, sintetizador de audio y persistencia
│   ├── sprites.py           # Entidades del juego (Jugador, Enemigos, Boss, PowerUps, Partículas)
│   ├── ui.py                # Interfaz de usuario, HUD, menú principal y opciones
│   └── game.py              # Bucle de juego, física de proyectiles y colisiones
├── main.py                  # Punto de entrada principal
├── build_exe.py             # Script de empaquetado PyInstaller
├── requirements.txt         # Lista de dependencias del proyecto
├── LICENSE                  # Licencia MIT del software
└── README.md                # Documentación oficial
```

---

## 📄 Licencia

Este proyecto está licenciado bajo los términos de la **Licencia MIT**. Consulte el archivo [LICENSE](LICENSE) para obtener más detalles.

**Desarrollado por DanVB.**