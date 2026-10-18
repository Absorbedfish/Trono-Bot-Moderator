# Trono Bot - Sistema Avanzado de Moderación NSFW por IA para Telegram
# Copyright (C) 2026 Manuel (@TronoModeradorBot) <https://github.com/Absorbedfish/Trono-Bot-Moderator>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# core/moderator.py 
import os
import io
import asyncio
from telegram import ChatPermissions, Update  
from telegram.ext import ContextTypes         
from config_manager import obtener_config_grupo
from history_manager import obtener_y_limpiar_historial_usuario, registrar_mensaje_id 
from utils.security import verificar_permisos_usuario, SHARED_DIR
from core.ia_client import consultar_ia_disco, consultar_ia_ram
from config.locales import obtener_texto  

# Diccionario asíncrono para agrupar ráfagas de media_group_id
ALBUMES_EN_PROCESO = {}

async def procesar_multimedia_entrante(update: Update, context: ContextTypes.DEFAULT_TYPE, bytes_preparados=None, ruta_fisica=None, nombre_archivo=None, tipo_medio=None):
    """Handler coordinador central. Agrupa álbumes eficientemente y los procesa en paralelo puro."""
    if not update.message:
        return

    chat_id = update.effective_chat.id
    message_id = update.message.message_id
    media_group_id = update.message.media_group_id
    user_id = update.message.from_user.id

    # 🛡️ REGISTRO INSTANTÁNEO EN SQLITE: Sin esperas en memoria
    registrar_mensaje_id(chat_id, user_id, message_id)

    paquete_mensaje = {
        "message": update.message,
        "bytes_preparados": bytes_preparados,
        "ruta_fisica": ruta_fisica,
        "nombre_archivo": nombre_archivo,
        "tipo_medio": tipo_medio # "ram" o "disco"
    }

    if not media_group_id:
        await ejecutar_evaluacion_directa(context.bot, paquete_mensaje)
        return

    # 🔥 DEBOUNCE OPTIMIZADO PARA PARALELISMO
    if media_group_id not in ALBUMES_EN_PROCESO:
        ALBUMES_EN_PROCESO[media_group_id] = {
            "paquetes": [],
            "tarea_coordinadora": None
        }
        
    ALBUMES_EN_PROCESO[media_group_id]["paquetes"].append(paquete_mensaje)

    if ALBUMES_EN_PROCESO[media_group_id]["tarea_coordinadora"]:
        ALBUMES_EN_PROCESO[media_group_id]["tarea_coordinadora"].cancel()

    async def espera_y_evaluacion_concurrente(mg_id):
        try:
            # Ventana reducida a 1.0s (con SQLite e hilos paralelos no necesitas más)
            await asyncio.sleep(1.0)
            
            datos_album = ALBUMES_EN_PROCESO.pop(mg_id, None)
            if not datos_album:
                return

            print(f"[🛡️ ARCHITECT v2.0.0] Evaluando concurrentemente {len(datos_album['paquetes'])} archivos del álbum {mg_id}.")
            
            # 🔥 PARALELISMO REAL: Se ejecutan todas las peticiones HTTPX simultáneamente hacia la IA
            tareas = [ejecutar_evaluacion_directa(context.bot, pkg) for pkg in datos_album["paquetes"]]
            await asyncio.gather(*tareas)
                
        except asyncio.CancelledError:
            pass

    tarea = asyncio.create_task(espera_y_evaluacion_concurrente(media_group_id))
    ALBUMES_EN_PROCESO[media_group_id]["tarea_coordinadora"] = tarea


async def ejecutar_evaluacion_directa(bot, pkg):
    """Enruta el paquete pre-descargado de forma atómica."""
    message = pkg["message"]
    try:
        if pkg["tipo_medio"] == "ram":
            await procesar_imagen_del_usuario(bot, message, pkg["bytes_preparados"], nombre_archivo=pkg["nombre_archivo"])
        elif pkg["tipo_medio"] == "disco":
            await procesar_archivo_en_disco(bot, message, pkg["nombre_archivo"], ruta_absoluta_ia=pkg["ruta_fisica"])
    except Exception as e:
        print(f"❌ Error en evaluación directa: {e}")


async def ejecutar_protocolo_failsafe(bot, chat_id: int, lang: str = "en"):
    """Aplica restricciones inmediatas de escritura si la infraestructura cae."""
    try:
        permisos_mutear = ChatPermissions(can_send_messages=False)
        await bot.set_chat_permissions(chat_id=chat_id, permissions=permisos_mutear)
        
        texto_fs = obtener_texto("failsafe_active", lang)
        await bot.send_message(chat_id=chat_id, text=texto_fs, parse_mode="Markdown")
    except Exception as err:
        print(f"❌ Fallo al aplicar restricciones Failsafe: {err}")


async def ejecutar_purgado_y_ban(bot, chat_id: int, user_id: int, message):
    """Purga retroactiva letal aprovechando los índices relacionales de la DB."""
    print(f"[🛡️ LIMPIEZA] Extrayendo historial SQLITE para el usuario {user_id}...")
    
    # Obtenemos todos los mensajes registrados por los hilos hermanos concurrentes de la DB
    mensajes_antiguos = obtener_y_limpiar_historial_usuario(chat_id, user_id)
    
    if message.message_id not in mensajes_antiguos:
        mensajes_antiguos.append(message.message_id)
    
    # Borrado masivo asíncrono no bloqueante
    tareas_borrado = []
    for msg_id in mensajes_antiguos:
        tareas_borrado.append(bot.delete_message(chat_id=chat_id, message_id=msg_id))
        
    # Ejecutamos ráfaga masiva de eliminación en la API de Telegram
    await asyncio.gather(*tareas_borrado, return_exceptions=True)
            
    # Ban fulminante y revocación de colas residuales en la API
    await bot.ban_chat_member(chat_id=chat_id, user_id=user_id, revoke_messages=True)
    print(f"[🛡️ COMPLETO] Usuario {user_id} neutralizado. Historial purgado de la DB.")


async def procesar_archivo_en_disco(bot, message, nombre_archivo_temporal, ruta_absoluta_ia=None):
    """Procesamiento atómico para archivos pesados (Videos/GIFs) validados en disco."""
    if not ruta_absoluta_ia:
        ruta_absoluta_ia = f"{SHARED_DIR}/{nombre_archivo_temporal}"
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    idioma_nativo = message.from_user.language_code.lower() if message.from_user and message.from_user.language_code else "en"
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    
    u_adv = config["umbral_advertencia"]
    u_ban = config["umbral_ban"]
    failsafe_habilitado = config["failsafe_active"]
    lang = config.get("lang", "en")
    mod_admin = config.get("mod_admin", 0)
    
    try:
        # 1. VERIFICACIÓN DE JERARQUÍA (Antes de usar recursos de la IA)
        es_admin, es_creador = await verificar_permisos_usuario(bot, chat_id, user_id)
        es_privilegiado = es_admin or es_creador

        # 2. CORTOCIRCUITO DE INMUNIDAD
        if es_privilegiado and mod_admin == 0:
            # Tienen inmunidad total. Salimos sin procesar el video para ahorrar CPU.
            return 
            
        # 3. EJECUCIÓN DE LA IA
        score = await consultar_ia_disco(ruta_absoluta_ia, u_ban)
        print(f"[BOT LOG] Análisis Disco ({nombre_archivo_temporal}). Score: {score:.4f}")
        
        # 4. MANEJO DE ADMINISTRADORES
        if es_privilegiado and mod_admin == 1:
            if u_adv <= score < u_ban:
                txt_adv_creador = obtener_texto("advertencia_creador", lang, score=score)
                await bot.send_message(chat_id=chat_id, text=txt_adv_creador, reply_to_message_id=message.message_id)
            elif score >= u_ban:
                await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            return

        # 5. MANEJO DE USUARIOS MORTALES
        if u_adv <= score < u_ban:
            txt_sospecha = obtener_texto("sospecha_usuario", lang, score=score*100)
            await bot.send_message(chat_id=chat_id, text=txt_sospecha, reply_to_message_id=message.message_id, parse_mode="Markdown")
        elif score >= u_ban:
            await ejecutar_purgado_y_ban(bot, chat_id, user_id, message)
            
    except Exception as e:
        print(f"❌ Error en pipeline de disco: {e}")
        if failsafe_habilitado:
            await ejecutar_protocolo_failsafe(bot, chat_id, lang=lang)
    finally:
        # Esto asegura que el video se borre de la carpeta uploads 
        # incluso si el bot ignoró al admin en el paso 2
        try:
            if os.path.exists(ruta_absoluta_ia):
                os.remove(ruta_absoluta_ia)
        except Exception as err:
            print(f"⚠️ Error al limpiar caché de disco: {err}")


async def procesar_imagen_del_usuario(bot, message, foto_bytes, nombre_archivo="imagen_usuario.jpg"):
    """Inferencia directa en RAM para procesamiento de ultra velocidad."""
    archivo_en_memoria = io.BytesIO(foto_bytes)
    
    content_type = 'image/jpeg'
    if nombre_archivo.endswith('.webm'): content_type = 'video/webm'
    elif nombre_archivo.endswith('.mp4'): content_type = 'video/mp4'
    elif nombre_archivo.endswith('.webp'): content_type = 'image/webp'
        
    chat_id = message.chat.id
    user_id = message.from_user.id

    idioma_nativo = message.from_user.language_code.lower() if message.from_user and message.from_user.language_code else "en"
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    
    u_adv = config["umbral_advertencia"]
    u_ban = config["umbral_ban"]
    failsafe_habilitado = config["failsafe_active"]
    lang = config.get("lang", "en")
    mod_admin = config.get("mod_admin", 0)

    try:
        # 1. VERIFICACIÓN DE JERARQUÍA (Antes de usar recursos de la IA)
        es_admin, es_creador = await verificar_permisos_usuario(bot, chat_id, user_id)
        es_privilegiado = es_admin or es_creador

        # 2. CORTOCIRCUITO DE INMUNIDAD
        if es_privilegiado and mod_admin == 0:
            # Tienen inmunidad total y la configuración dice que no los moderemos.
            # Salimos inmediatamente. Cero gasto de RAM/GPU.
            return 
        
        # 3. EJECUCIÓN DE LA IA
        score = await consultar_ia_ram(archivo_en_memoria, nombre_archivo, content_type, u_ban)
        print(f"[BOT LOG] Análisis RAM ({nombre_archivo}). Score: {score:.4f}")
        
        # 4. MANEJO DE ADMINISTRADORES (Sin purgas ni bans, solo advertencias y borrados)
        if es_privilegiado and mod_admin == 1:
            if u_adv <= score < u_ban:
                txt_adv_creador = obtener_texto("advertencia_creador", lang, score=score)
                await bot.send_message(chat_id=chat_id, text=txt_adv_creador, reply_to_message_id=message.message_id)
            elif score >= u_ban:
                # Trono solo borra el mensaje, no banea a sus superiores
                await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            return # Termina el flujo para privilegiados.

        # 5. MANEJO DE USUARIOS MORTALES
        if u_adv <= score < u_ban:
            txt_sospecha = obtener_texto("sospecha_usuario", lang, score=score*100)
            await bot.send_message(chat_id=chat_id, text=txt_sospecha, reply_to_message_id=message.message_id, parse_mode="Markdown")
        elif score >= u_ban:
            await ejecutar_purgado_y_ban(bot, chat_id, user_id, message)
            
    except Exception as e:
        print(f"❌ Error en pipeline de RAM: {e}")
        if failsafe_habilitado:
            await ejecutar_protocolo_failsafe(bot, chat_id, lang=lang)
    finally:
        archivo_en_memoria.close()