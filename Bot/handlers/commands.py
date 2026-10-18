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

# handlers/commands.py
import httpx
import asyncio
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatType
from config_manager import obtener_config_grupo
from utils.security import verificar_permisos_usuario
from core.ia_client import IA_SERVICE_URL
from config.locales import obtener_texto  
from core.moderator import ejecutar_protocolo_failsafe

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando de bienvenida trilingüe con botón dinámico de invitación."""
    if not update.message:
        return
        
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    # 🔥 ESCUDO DE SEGURIDAD: Validamos si el usuario es Admin o Creador
    es_admin, _ = await verificar_permisos_usuario(context.bot, chat_id, user_id)
    if not es_admin:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        return
    
    idioma_nativo = "en"
    if update.message.from_user and update.message.from_user.language_code:
        idioma_nativo = update.message.from_user.language_code.lower()
        
    # 🔥 v2.0.0: Consulta asíncrona nativa a SQLite con await
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")
    
    texto_bienvenida = obtener_texto("bienvenida", lang)
    
    botones_idioma = {
        "es": "➕ Añadir a un grupo",
        "en": "➕ Add to a group",
        "ru": "➕ Добавить в группу"
    }
    texto_boton = botones_idioma.get(lang, botones_idioma["en"])
    
    bot_info = await context.bot.get_me()
    enlace_invitacion = f"https://t.me/{bot_info.username}?startgroup=true"
    
    keyboard = [[InlineKeyboardButton(texto_boton, url=enlace_invitacion)]]
    
    await update.message.reply_text(
        text=texto_bienvenida, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )


async def configurar_idioma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Despliega la botonera trilingüe para cambiar el idioma manualmente (Solo Admins)."""
    if not update.message:
        return
        
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    
    es_admin, _ = await verificar_permisos_usuario(context.bot, chat_id, user_id)
    if not es_admin:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        return

    # 🔥 CORRECCIÓN CRÍTICA v2.0.0: Se añade 'await' para resolver la corrutina de la DB
    config = await obtener_config_grupo(chat_id)
    lang = config.get("lang", "en")
    
    texto_menu = obtener_texto("seleccione_idioma", lang)
    
    keyboard = [
        [
            InlineKeyboardButton("🇪🇸 Español", callback_data="set_lang_es"),
            InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru")
        ]
    ]
    
    await update.message.reply_text(
        text=texto_menu, 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )


async def consultar_privacidad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mantiene la política legal visible en el idioma configurado para el grupo."""
    if not update.message:
        return
    
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    es_admin, _ = await verificar_permisos_usuario(context.bot, chat_id, user_id)
    if not es_admin:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        return
    
    idioma_nativo = "en"
    if update.message.from_user and update.message.from_user.language_code:
        idioma_nativo = update.message.from_user.language_code.lower()
    
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")
    
    politica = obtener_texto("politica_privacidad", lang)
    await update.message.reply_text(text=politica, parse_mode="Markdown")


async def verificar_conexion_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Verifica el estado de la IA de forma segura sin provocar falsos positivos de caída."""
    if not update.message:
        return
        
    chat = update.effective_chat
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    
    idioma_nativo = "en"
    if update.message.from_user and update.message.from_user.language_code:
        idioma_nativo = update.message.from_user.language_code.lower()
        
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")
    failsafe_habilitado = config.get("failsafe_active", 0) # Evaluación numérica nativa de SQLite

    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(text=obtener_texto("sistema_mensaje_privado", lang), parse_mode="Markdown")
        return
    
    es_admin, _ = await verificar_permisos_usuario(context.bot, chat_id, user_id)
    if not es_admin:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        return
    
    try:
        limites_timeout = httpx.Timeout(5.0, connect=2.0)
        
        async with httpx.AsyncClient(timeout=limites_timeout) as cliente_ia:
            # Apuntamos al endpoint de clasificación enviando el ping controlado
            respuesta = await cliente_ia.post(IA_SERVICE_URL, json={"archivo_ruta": ""})
        
        # 🔥 CORRECCIÓN v2.0.0: Ahora la IA responde estrictamente 200 OK si está viva
        if respuesta.status_code == 200:
            texto_online = obtener_texto("failsafe_online", lang)
            
            if failsafe_habilitado:
                print(f"[🛡️ RESTAURACIÓN] IA online detectada de manera segura. Devolviendo permisos en {chat_id}.")
                
                permisos_estandar = ChatPermissions(
                    can_send_messages=True,
                    can_send_audios=True,
                    can_send_documents=True,
                    can_send_photos=True,
                    can_send_videos=True,
                    can_send_video_notes=True,
                    can_send_voice_notes=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
                await context.bot.set_chat_permissions(chat_id=chat_id, permissions=permisos_estandar)
            
            await update.message.reply_text(text=texto_online, parse_mode="Markdown")
        
        # CASO 2: Error anómalo de infraestructura (500, 502, 503 o respuestas inesperadas)
        else:
            texto_offline = obtener_texto("failsafe_offline", lang)
            await update.message.reply_text(text=texto_offline, parse_mode="Markdown")
            
            if failsafe_habilitado:
                print(f"[🛡️ INTERRUPCIÓN] Estado anómalo crítico ({respuesta.status_code}). Aplicando Failsafe.")
                await ejecutar_protocolo_failsafe(context.bot, chat_id, lang=lang)
            
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        # 🔥 Aquí sí usamos "failsafe_estable" porque tu diccionario espera el parámetro 'status'
        detalle_error = type(e).__name__  # Captura si fue ConnectTimeout, ReadError, etc.
        texto_offline = obtener_texto("failsafe_estable", lang, status=detalle_error)
        await update.message.reply_text(text=texto_offline, parse_mode="Markdown")
        
        if failsafe_habilitado:
            print(f"[🛡️ INESTABILIDAD HTTPX] Servicio muerto ({detalle_error}). Forzando cierre del chat {chat_id}.")
            await ejecutar_protocolo_failsafe(context.bot, chat_id, lang=lang)

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Proporciona un resumen de comandos disponibles y su descripción en el idioma del grupo."""
    if not update.message:
        return

    chat = update.effective_chat    
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    if chat.type != ChatType.PRIVATE:
        es_admin, _ = await verificar_permisos_usuario(context.bot, chat_id, user_id)
        if not es_admin:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            return
    
    idioma_nativo = "en"
    if update.message.from_user and update.message.from_user.language_code:
        idioma_nativo = update.message.from_user.language_code.lower()
        
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")
    
    texto_ayuda = obtener_texto("ayuda_comandos", lang)
    await update.message.reply_text(text=texto_ayuda, parse_mode="Markdown")

async def DescripcionComando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Proporciona una descripción detallada de cada comando en el idioma del grupo."""
    if not update.message:
        return

    chat = update.effective_chat    
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    if chat.type != ChatType.PRIVATE:
        es_admin, _ = await verificar_permisos_usuario(context.bot, chat_id, user_id)
        if not es_admin:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
            return
    
    idioma_nativo = "en"
    if update.message.from_user and update.message.from_user.language_code:
        idioma_nativo = update.message.from_user.language_code.lower()
        
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")
    
    texto_descripcion = obtener_texto("descripcion_conf", lang)
    await update.message.reply_text(text=texto_descripcion, parse_mode="Markdown")