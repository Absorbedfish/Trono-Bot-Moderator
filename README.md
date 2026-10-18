# 🛡️ Trono Bot v2.1.0 — Sistema Avanzado de Moderación NSFW por IA para Telegram

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram_Bot_API-v22.7_(Local)-blue)](https://core.telegram.org/bots/api)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16.1-orange.svg)](https://www.tensorflow.org/)
[![Docker Compose](https://img.shields.io/badge/Docker_Compose-Multi--Container-2496ED)](https://www.docker.com/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Bot Telegram](https://img.shields.io/badge/Telegram_Bot-@TronoModeradorBot-2CA5E0?logo=telegram)](https://t.me/TronoModeradorBot)

**Trono Bot** es una solución integral y de alto rendimiento para la moderación automatizada y en tiempo real de contenidos visuales sensibles (NSFW / pornografía / desnudez) en grupos y supergrupos de Telegram. 

Combina un microservicio de Inteligencia Artificial basado en redes neuronales convolucionales (**Yahoo OpenNSFW** sobre TensorFlow), una instancia local desacoplada de la **Telegram Bot API** (permitiendo el procesamiento de archivos multimedia de hasta 2 GB sin pasar por servidores externos) y un bot asíncrono desarrollado con arquitectura limpia, reactiva y tolerante a fallos.

---

> [!TIP]
> ### ⚡ ¿Solo deseas proteger tu grupo sin desplegar infraestructura?
> Puedes usar directamente el bot oficial listo para producción mantenido por el creador:
> 👉 **[@TronoModeradorBot](https://t.me/TronoModeradorBot)** 👈
> 
> Solo agrégalo como administrador a tu grupo con permisos para eliminar mensajes y restringir usuarios. ¡Funcionará de inmediato con toda la potencia de la IA!

---

## 📌 Tabla de Contenidos
- [⚡ Uso Directo del Bot Oficial](#-uso-directo-del-bot-oficial)
- [📖 Descripción General](#-descripción-general)
- [🏗️ Arquitectura del Sistema](#-arquitectura-del-sistema)
- [💻 Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [✨ Características Principales](#-características-principales)
- [🔒 Privacidad e Higiene Digital](#-privacidad-e-higiene-digital)
- [⌨️ Comandos y Panel de Control](#-comandos-y-panel-de-control)
- [🛠️ Guía Paso a Paso para Desarrolladores](#️-guía-paso-a-paso-para-desarrolladores)
  - [1. Clonar el Repositorio](#1-clonar-el-repositorio)
  - [2. Obtención de Credenciales y Claves](#2-obtención-de-credenciales-y-claves)
  - [3. Configuración del Archivo `.env`](#3-configuración-del-archivo-env)
  - [4. Configuración en `docker-compose.yml`](#4-configuración-en-docker-composeyml)
  - [5. Preparación de Directorios y Permisos](#5-preparación-de-directorios-y-permisos)
  - [6. Despliegue con Docker Compose](#6-despliegue-con-docker-compose)
  - [7. Verificación y Pruebas del Servicio](#7-verificación-y-pruebas-del-servicio)
- [📜 Historial de Versiones](#-historial-de-versiones)
- [🚦 Estado Actual del Proyecto](#-estado-actual-del-proyecto)
- [📄 Licencia](#-licencia)

---

## ⚡ Uso Directo del Bot Oficial

Si eres administrador de una comunidad en Telegram y no deseas gestionar servidores, Docker ni modelos de Machine Learning, puedes invitar al bot oficial operativo:

1. Entra a **[@TronoModeradorBot](https://t.me/TronoModeradorBot)** en Telegram.
2. Pulsa en **Añadir a un grupo** (o agrégalo manualmente desde la administración del chat).
3. Otórgale los siguientes permisos de Administrador:
   - ✅ **Eliminar mensajes** (requerido para borrar contenido NSFW).
   - ✅ **Banear / Restringir usuarios** (requerido para expulsar infractores y pausar el chat en modo Failsafe).
4. Ejecuta `/start` o `/configurar` en el grupo para ajustar los umbrales de sensibilidad a tu medida.

---

## 📖 Descripción General

En comunidades multitudinarias de Telegram, las invasiones de spam y difusión de material sensible (NSFW/pornografía) suelen ocurrir mediante ráfagas masivas (álbumes), videos de alta definición o videonotas. Las soluciones tradicionales suelen depender de la nube pública de Telegram (limitada a 20 MB por archivo) o presentan bloqueos en el hilo de ejecución al procesar archivos multimedia pesados.

**Trono Bot** soluciona estos problemas mediante:
1. **Inspección multinivel:** Procesa imágenes, stickers estáticos y animados (WebP / WebM), animaciones GIF, videonotas circulares, videos de alta definición y documentos multimedia.
2. **Ecosistema Local de 2 GB:** Al conectarse con un servidor local de Telegram Bot API (`telegram-bot-api`), elimina el cuello de botella de 20 MB y procesa archivos de hasta 2 GB con acceso de ultra baja latencia en volumen compartido.
3. **Escudo Anti-Fallas (Protocolo Failsafe):** Si la IA pierde conectividad o se cae, el bot puede bloquear temporalmente el envío de mensajes en el grupo para evitar brechas de seguridad.
4. **Purga retroactiva atómica:** Cuando un usuario infractor publica material no permitido, el bot no solo lo expulsa, sino que elimina todo su historial reciente de mensajes en el grupo usando un búfer circular en SQLite.

---

## 🏗️ Arquitectura del Sistema

El proyecto opera como un ecosistema multi-contenedor orquestado mediante [`docker-compose.yml`](./docker-compose.yml):

```
                                  ┌────────────────────────┐
                                  │   Cliente Telegram     │
                                  └───────────┬────────────┘
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │    telegram-bot-api (Local)     │
                             │  (aiogram/telegram-bot-api)     │
                             │  Soporte de archivos hasta 2GB  │
                             └──────────────┬──────────────────┘
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     │ Volumen Compartido (/app/shared_media)      │
                     │  - angel_guardian.db (Configuración SQLite) │
                     │  - trono_historial.db (Búfer circular IDs)  │
                     │  - Archivos pesados temporales (Videos/GIF) │
                     └──────────────────────┬──────────────────────┘
                                            │
               ┌────────────────────────────┴───────────────────────────┐
               │                                                        │
               ▼                                                        ▼
┌───────────────────────────────┐                       ┌───────────────────────────────┐
│   telegram-bot-trono (Bot)    │                       │   ia-opennsfw-trono (IA)      │
│  - Python 3.12 + PTB v22.7    │ ── HTTPX (Async) ───► │  - Flask Async + Gunicorn     │
│  - Orquestador de Moderación  │ ◄── Score NSFW ────── │  - TensorFlow + OpenNSFW      │
│  - Debounce de Álbumes        │                       │  - OpenCV (Cortocircuito CPU) │
│  - Soporte Trilingüe          │                       │  - Inferencia RAM y Disco     │
└───────────────────────────────┘                       └───────────────────────────────┘
```

### Componentes de la Solución:

1. **[`telegram-bot-api`](./docker-compose.yml):** Servidor local oficial de la API de Telegram que descarga y almacena los medios directamente en el host montado, permitiendo manejar archivos de hasta 2 GB.
2. **[`ia-opennsfw-trono`](./IA):** Microservicio en Python con Flask y servidor Gunicorn `gthread`. Procesa imágenes directamente en memoria RAM y analiza videos cuadro por cuadro con cortocircuito dinámico.
3. **[`telegram-bot-trono`](./Bot):** Orquestador principal modularizado que intercepta eventos, coordina el análisis asíncrono con `httpx`, ejecuta sanciones y gestiona la interacción con administradores.

---

## 💻 Tecnologías Utilizadas

### Núcleo del Bot (`/Bot`)
- **Lenguaje:** Python 3.12 (imagen Docker `python:3.12-slim`).
- **Framework de Bot:** [`python-telegram-bot` v22.7](./Bot/requirements.txt) (totalmente asíncrono con corrutinas y `asyncio`).
- **Cliente HTTP Asíncrono:** [`httpx` v0.27.0](./Bot/requirements.txt) con *Keep-Alive* y timeouts perimetrales.
- **Bases de Datos Locales:** `sqlite3` embebido con modos de alto rendimiento:
  - `PRAGMA journal_mode=WAL;` (Write-Ahead Logging para lectura/escritura concurrente sin bloqueos).
  - `PRAGMA synchronous=NORMAL;` para óptima latencia de disco.
  - Delegación de I/O bloqueante al pool de subprocesos con `asyncio.to_thread()`.
- **Configuración y Entornos:** `python-dotenv`.

### Núcleo de Inteligencia Artificial (`/IA`)
- **Framework Web & WSGI:** Flask 3.0.3 `[async]` ejecutado sobre [Gunicorn v22.0.0](./IA/requirements.txt) con worker class `gthread` (2 hilos por proceso).
- **Motor de Inferencia:** [TensorFlow v2.16.1](./IA/requirements.txt) cargando el modelo pre-entrenado SavedModel `open_nsfw_saved_model`.
- **Procesamiento de Video y Fotogramas:** `opencv-python-headless` (OpenCV) y `Pillow` (PIL) para extracción, muestreo de fotogramas e interpolación bilineal 224x224.
- **Cálculo Numérico:** `NumPy` v1.26.4.

### Infraestructura y Despliegue
- **Contenedores:** Docker & Docker Compose.
- **Servidor Telegram Local:** Imagen oficial `aiogram/telegram-bot-api:latest`.

---

## ✨ Características Principales

### 1. Inferencia Bimodal Inteligente (RAM vs. Disco)
- **Vía Rápida en RAM:** Fotos, stickers y GIFs pequeños (<10 MB) se transfieren en flujos de memoria `io.BytesIO` sin tocar el almacenamiento secundario, ofreciendo respuestas casi instantáneas.
- **Vía Perimetral en Disco:** Videos de gran tamaño, animaciones pesadas y videonotas circulares se leen de forma directa desde el volumen compartido montado, eliminando la sobrecarga de transferencias por red.

### 2. Muestreo de Video con Cortocircuito de CPU
El análisis de videos no requiere decodificar el 100% del archivo. El motor muestrea fotogramas distribuidos a lo largo del metraje. Si un solo fotograma sobrepasa el umbral de baneo, la inferencia se interrumpe de inmediato (**cortocircuito dinámico**), ahorrando ciclos de CPU/GPU y sancionando al instante.

### 3. Coordinación y Anti-Exploit para Álbumes (Debounce Asíncrono)
Para neutralizar la vulnerabilidad en la que atacantes envían ráfagas de imágenes (*Media Groups*) esperando que una sanción temprana interrumpa el análisis del resto, el módulo [`Bot/core/moderator.py`](./Bot/core/moderator.py) incorpora:
- Agrupación por `media_group_id`.
- Ventana de *Debounce* de 1.0s.
- Inferencia masiva paralela mediante `asyncio.gather()`.
- Retención y registro preventivo síncrono en base de datos previo a la evaluación.

### 4. Protocolo Failsafe de Alta Disponibilidad
Monitorea la salud del contenedor de IA mediante pings controlados a `/clasificar` y `/`. Si el microservicio de IA no está disponible:
- El bot aplica restricciones automáticas mutando temporalmente el chat (`can_send_messages=False`).
- Alerta al grupo sobre la activación del protocolo de seguridad.
- Al recuperarse la IA (verificable con `/conexion`), restablece de inmediato todos los permisos estándar del chat.

### 5. Moderación Jerárquica y Modo `Mod Admins`
- **Inmunidad por Defecto:** Los administradores y el creador del grupo están exentos de escaneo para ahorrar recursos computacionales.
- **Mod Admins Activable:** Si se habilita desde el menú `/configurar`, el bot revisará los archivos multimedia de los administradores. En caso de infracción, borrará el contenido o emitirá advertencias, pero **nunca expulsará al administrador o creador**.

### 6. Sistema Trilingüe con Detección Automática
Soporte completo en tres idiomas:
- 🇪🇸 **Español**
- 🇬🇧 **Inglés**
- 🇷🇺 **Ruso**

El bot detecta automáticamente el idioma del usuario que lo invoca mediante `language_code` y permite forzar manualmente el idioma del grupo con [`/configuraridioma`](./Bot/handlers/commands.py).

---

## 🔒 Privacidad e Higiene Digital

Trono Bot implementa una política estricta de **cero almacenamiento persistente de contenido**:

1. **Datos Numéricos Opacos:** La base de datos [`trono_historial.db`](./Bot/history_manager.py) guarda únicamente enteros (`chat_id`, `user_id`, `message_id`). No almacena texto, nombres, alias ni metadatos personales.
2. **Trigger Circular Anti-Desborde:** Un trigger SQLite mantiene como máximo los últimos 1000 mensajes por grupo, eliminando los registros antiguos automáticamente.
3. **Destrucción Efímera de Archivos:** Todo archivo pesado descargado temporalmente en `/app/shared_media` es eliminado del disco físico tan pronto culmina la inferencia en el bloque `finally`.
4. **Protección en Mensajería Privada:** Por seguridad y conservación de ancho de banda, el bot bloquea el procesamiento de multimedia en chats directos privados.

---

## ⌨️ Comandos y Panel de Control

Todos los comandos administrativos cuentan con verificación de jerarquía. Si un usuario sin rango los invoca, el mensaje es eliminado silenciosamente para evitar spam visual.

| Comando | Ámbito | Descripción |
| :--- | :---: | :--- |
| `/start` | Privado / Grupos | Presentación del bot con botón directo para añadir a grupos. |
| `/configurar` | Solo Grupos (Admins) | Despliega el panel de control interactivo en línea con botones Callback. |
| `/configuraridioma`| Grupos / Admins | Selector visual para fijar el idioma del bot (Español, Inglés o Ruso). |
| `/conexion` | Solo Grupos (Admins) | Comprueba la conectividad con la IA y reabre el chat si estaba en Failsafe. |
| `/privacidad` | General | Muestra las garantías de privacidad y tratamiento de datos del bot. |
| `/ayuda` | General | Lista de comandos disponibles y su funcionamiento. |
| `/ConfigDescripcion`| General | Explicación detallada de los parámetros del panel de ajustes. |

### ⚙️ Panel Interactivo (`/configurar`)
Permite calibrar en caliente sin reiniciar los contenedores:
- **Failsafe:** Activar / Desactivar el protocolo de cierre automático.
- **Mod Admins:** Alternar la moderación de multimedia para administradores (ON/OFF).
- **Umbral Advertencia (`Adv`):** Ajuste fino en pasos de ±0.05 (Default: `0.50`).
- **Umbral Sanción (`Ban`):** Ajuste fino en pasos de ±0.05 (Default: `0.60`).

---

## 🛠️ Guía Paso a Paso para Desarrolladores

Si deseas desplegar tu propia instancia de Trono Bot en tu propio servidor o infraestructura local, sigue estos pasos:

### 1. Clonar el Repositorio
Abre tu terminal y descarga el proyecto desde GitHub:
```bash
git clone https://github.com/Absorbedfish/Trono-Bot-Moderator.git
cd Trono-Bot-Moderator
```

### 2. Obtención de Credenciales y Claves
Necesitas tres valores fundamentales:

1. **`TELEGRAM_TOKEN`**:
   - Inicia conversación con [@BotFather](https://t.me/BotFather) en Telegram.
   - Envía `/newbot`, asigna nombre y alias a tu bot.
   - BotFather te entregará un token con formato: `1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ12345678`.
2. **`TELEGRAM_API_ID`** y **`TELEGRAM_API_HASH`**:
   - Inicia sesión con tu número de teléfono en [https://my.telegram.org](https://my.telegram.org).
   - Accede a **"API development tools"**.
   - Crea una nueva aplicación (puedes poner cualquier nombre).
   - Obtendrás tu `api_id` (número entero) y `api_hash` (cadena hexadecimal de 32 caracteres).

### 3. Configuración del Archivo `.env`
Copia la plantilla [`.env.example`](./.env.example) para generar tu archivo local [`.env`](./.env):

```bash
cp .env.example .env
```

Edita el archivo `.env` con tu editor preferido (e.g., `nano .env`):
```env
# ==============================================================================
# CONFIGURACIÓN DE PRODUCCIÓN - TRONO BOT
# ==============================================================================

# 1. Token de tu bot entregado por @BotFather
TELEGRAM_TOKEN=1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ12345678

# 2. Credenciales de la API de Telegram obtenidas en https://my.telegram.org
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=0123456789abcdef0123456789abcdef

# 3. Ruta absoluta en el disco físico del servidor para el volumen compartido
# IMPORTANTE: Cambia esta ruta por un directorio real existente en tu servidor
TELEGRAM_DATA_DIR=/var/www/trono_bot/telegram_data
```

### 4. Configuración en `docker-compose.yml`
El archivo [`docker-compose.yml`](./docker-compose.yml) ya está parametrizado para leer de forma segura las variables de entorno del `.env`:

```yaml
services:
  telegram-bot-api:
    image: aiogram/telegram-bot-api:latest
    container_name: telegram_bot_api_local
    restart: always
    environment:
      - TELEGRAM_API_ID=${TELEGRAM_API_ID}
      - TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
      - TELEGRAM_LOCAL=1
    volumes:
      - ${TELEGRAM_DATA_DIR}:/var/lib/telegram-bot-api
    ports:
      - "8082:8081"

  ia-opennsfw-trono:
    build: ./IA
    container_name: ia_opennsfw_trono
    restart: always
    environment:
      - TZ=Europe/Moscow
      - TF_CPP_MIN_LOG_LEVEL=2
      - PYTHONUNBUFFERED=1
    volumes:
      - ${TELEGRAM_DATA_DIR}:/app/shared_media

  telegram-bot-trono:
    build: ./Bot
    container_name: trono_bot_container
    restart: always
    env_file:
      - .env
    depends_on:
      - ia-opennsfw-trono
      - telegram-bot-api
    volumes:
      - ${TELEGRAM_DATA_DIR}:/app/shared_media
```

> [!IMPORTANT]
> **No modifiques las credenciales directamente en `docker-compose.yml`**. Colócalas únicamente en tu archivo `.env`, el cual está protegido y excluido de los commits públicos de Git.

### 5. Preparación de Directorios y Permisos
Crea la carpeta física en tu servidor indicada en `TELEGRAM_DATA_DIR` y asígnale permisos adecuados para que los contenedores puedan escribir bases de datos y descargar medios:

```bash
# Ejemplo usando la ruta /var/www/trono_bot/telegram_data
sudo mkdir -p /var/www/trono_bot/telegram_data
sudo chmod -R 777 /var/www/trono_bot/telegram_data
```

### 6. Despliegue con Docker Compose
Construye las imágenes Docker y levanta los 3 servicios en segundo plano:

```bash
docker compose up -d --build
```

### 7. Verificación y Pruebas del Servicio

1. **Comprobar estado de los contenedores:**
   ```bash
   docker compose ps
   ```
   Los tres contenedores (`telegram_bot_api_local`, `ia_opennsfw_trono`, `trono_bot_container`) deben figurar en estado `Up`.

2. **Verificar logs del Bot:**
   ```bash
   docker compose logs -f telegram-bot-trono
   ```
   Deberías observar el mensaje de confirmación:
   `🤖 Trono Bot v2.1.0 iniciado con éxito. Soporte Trilingüe listo...`

3. **Verificar microservicio de IA:**
   ```bash
   docker compose logs -f ia-opennsfw-trono
   ```
   Deberías ver la carga exitosa del modelo:
   `¡Ángel Guardián: Tronobot inicializado y cargado exitosamente!`

4. **Prueba final en Telegram:**
   - Abre un chat con tu bot y escribe `/start`.
   - Agrégalo a un grupo de pruebas y escribe `/conexion` como administrador para verificar la conexión con la IA.

---

## 📜 Historial de Versiones

A continuación se presenta un resumen de la evolución técnica del proyecto. Para consultar el registro completo y detallado con todas las métricas, problemas solventados y fuentes, consulte el documento:

👉 **[Evolución técnica del proyecto Trono Bot (v0.1.0 a v2.1.0).xlsx](./Evolución%20técnica%20del%20proyecto%20Trono%20Bot%20(v0.1.0%20a%20v2.1.0).xlsx)**

| Versión | Hitos y Características Principales | Soporte e Infraestructura | Mitigaciones y Seguridad |
| :--- | :--- | :--- | :--- |
| **v0.1.0** | Nacimiento del núcleo base; comandos básicos e inferencia síncrona/lineal con umbrales fijos (0.50 / 0.60). | Fotos hasta 20 MB en nube Telegram. | Datos puramente en memoria volátil; pérdida de registros al reiniciar. |
| **v0.2.0** | Umbrales dinámicos por grupo vía menú interactivo `/configurar` con botones en línea. | Soporte extendido a stickers, GIFs y videos (límite 20 MB). | Superación de límites estáticos de configuración. |
| **v0.3.0** | Migración a servidor local de Telegram (`telegram-bot-api`). Creación del protocolo Failsafe. | Archivos pesados de hasta 2 GB (videos y videonotas). | Aislamiento automático del chat si la IA pierde conexión. Limpieza de caché. |
| **v0.4.0** | Rediseño perimetral. Guardado de umbrales en JSON. Menú con auto-borrado para no administradores. | Videonotas circulares; volumen Docker compartido `/app/shared_media`. | Eliminación física obligatoria de disco tras lectura en RAM. |
| **v0.4.1** | Parche de estabilidad y optimización de asincronía ante ráfagas de mensajes. | Sincronización de rutas en volúmenes Docker de producción. | Destrucción de punteros de archivos tras inferencia para mitigar fugas de RAM. |
| **v0.5.0** | Mitigación retroactiva estricta de historial en grupos pequeños (<200 miembros). Comando `/privacidad`. | Creación de `history_manager.py` con SQLite y Trigger circular (últimos 1000 msgs). | Purga masiva en bucle previo al ban. Almacenamiento exclusivo de enteros opacos. |
| **v1.0.0** | **Gran Refactorización y Modularización (SRP).** Desacoplamiento en carpetas `core/`, `handlers/` y `utils/`. `main.py` reducido de 677 a 176 líneas. | Ecosistema Docker de 3 contenedores. Persistencia híbrida (JSON + SQLite). | Centralización de utilidades de seguridad e inyección de clientes desacoplados. |
| **v1.1.0** | Soporte trilingüe dinámico desacoplado (`config/locales.py`: Español, Inglés, Ruso) y comando `/configuraridioma`. | Persistencia de idioma por grupo. | Detección de colisiones y *race conditions* en ráfagas de álbumes. |
| **v1.1.1** | Mecanismo de *Debounce* asíncrono (1.5s) para acumular imágenes de un mismo álbum (`media_group_id`). | Diccionario en memoria `ALBUMES_EN_PROCESO`. | Registro previo de identificadores en SQLite antes de la evaluación. |
| **v1.1.2** | Solución definitiva al exploit de álbumes. Unificación de registro síncrono en Grupo 0 y supresión de filtros multimedia en Grupo 1. | Despacho unificado a `procesar_multimedia_entrante()`. | Retraso táctico de sincronización de 1.0s para permitir que fotos lentas entren a la purga. |
| **v2.0.0** | **Asincronía total y arquitectura masiva.** Migración a `httpx`, Gunicorn `gthread` en IA y SQLite WAL en `angel_guardian.db`. | Cortocircuito dinámico de CPU en video (OpenCV). Healthcheck `/`. | Eliminación total de bloqueos en Event Loop y errores de `database is locked`. |
| **v2.1.0** *(Actual)* | Moderación opcional para administradores (`mod_admin`). Bloqueo higiénico de multimedia en privados. | Migración automática de esquema SQLite (`ALTER TABLE`). Menú interactivo renovado. | Cortocircuito de inmunidad para admins (cero consumo de GPU/RAM si no se moderan). |

---

## 🚦 Estado Actual del Proyecto

| Parámetro | Estado | Observaciones |
| :--- | :---: | :--- |
| **Versión Actual** | `v2.1.0` | Versión estable de producción en despliegue. |
| **Estabilidad de Concurrencia** | 🟢 Alta | Arquitectura no bloqueante con HTTPX, Gunicorn multi-hilo y SQLite en modo WAL. |
| **Protección contra Exploits** | 🟢 Blindada | Control total de condiciones de carrera en álbumes (*Media Groups*) y purga retroactiva. |
| **Consumo de Recursos** | 🟢 Optimizado | Cortocircuito de inferencia en video e inmunidad de administradores previa a la inferencia. |
| **Soporte Multilingüe** | 🟢 Operativo | Español, Inglés y Ruso completamente implementados. |
| **Mantenimiento y Deuda Técnica** | 🟢 Limpia | Código modularizado bajo Principio de Responsabilidad Única (SRP); separación en `core/`, `handlers/`, `utils/` y `config/`. |

---

## 📄 Licencia

Este proyecto está distribuido bajo la licencia **GNU Affero General Public License v3.0 (GNU AGPLv3)**.

Para conocer el análisis detallado de por qué se eligió esta licencia y cómo protege el software libre en servicios de red, consulta:
- 📖 [RECOMENDACION_LICENCIA.txt](./RECOMENDACION_LICENCIA.txt)
- ⚖️ [LICENSE](./LICENSE)
