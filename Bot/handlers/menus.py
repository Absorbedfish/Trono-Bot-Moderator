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

# handlers/menus.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatType
from config_manager import obtener_config_grupo, actualizar_config_grupo
from utils.security import verificar_permisos_usuario
from config.locales import obtener_texto  # 🔥 Inyección del sistema de idiomas de la v1.1.0

async def despliega_menu_configuracion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera la interfaz visual del panel de control de umbrales en el idioma del grupo."""
    if not update.message:
        return
    
    chat = update.effective_chat
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    # Capturamos el idioma nativo del usuario por si el grupo o chat es completamente nuevo en la base de datos
    idioma_nativo = update.message.from_user.language_code.lower() if update.message.from_user and update.message.from_user.language_code else "en"
    
    # 🔥 CORRECCIÓN v2.0.0: Añadido el await correspondiente para resolver la corrutina de SQLite
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")
    
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(text=obtener_texto("sistema_mensaje_privado", lang), parse_mode="Markdown")
        return
    
    es_admin, _ = await verificar_permisos_usuario(context.bot, chat_id, user_id)
    if not es_admin:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        return
    
    # Mapeo visual de estados de Failsafe
    status_map = {"es": "🟢 ACTIVO" if config["failsafe_active"] else "🔴 APAGADO",
                  "en": "🟢 ACTIVE" if config["failsafe_active"] else "🔴 OFF",
                  "ru": "🟢 АКТИВЕН" if config["failsafe_active"] else "🔴 ВЫКЛ"}
    status_fs = status_map.get(lang, status_map["en"])

    # Mapeo visual de estados para Moderación de Administradores
    mod_admin_map = {"es": "🟢 SÍ" if config.get("mod_admin", 0) else "🔴 NO",
                     "en": "🟢 ON" if config.get("mod_admin", 0) else "🔴 OFF",
                     "ru": "🟢 ДА" if config.get("mod_admin", 0) else "🔴 НЕТ"}
    status_mod_admin = mod_admin_map.get(lang, mod_admin_map["en"])
    
    # Inyección dinámica de textos desde config/locales.py
    text = obtener_texto(
        "menu_titulo", 
        lang, 
        status=status_fs, 
        mod_admin=status_mod_admin,  # 🔥 Le pasamos el estado visual al texto
        adv=config['umbral_advertencia'], 
        ban=config['umbral_ban']
    )
    
    keyboard = [
        [InlineKeyboardButton(f"Failsafe: {status_fs}", callback_data="toggle_failsafe")],
        [InlineKeyboardButton(f"Mod Admins: {status_mod_admin}", callback_data="toggle_mod_admin")], # 🔥 Nuevo botón
        [
            InlineKeyboardButton("Adv -0.05", callback_data="sub_adv"),
            InlineKeyboardButton("Adv +0.05", callback_data="add_adv")
        ],
        [
            InlineKeyboardButton("Ban -0.05", callback_data="sub_ban"),
            InlineKeyboardButton("Ban +0.05", callback_data="add_ban")
        ]
    ]
    
    await update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def manejador_botones_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa los clics en la botonera de ajustes y el cambio manual de idiomas."""
    query = update.callback_query
    chat_id = query.message.chat.id
    user_id = query.from_user.id
    
    config = await obtener_config_grupo(chat_id)
    lang = config.get("lang", "en")
    
    es_admin, _ = await verificar_permisos_usuario(context.bot, chat_id, user_id)
    if not es_admin:
        # Alerta emergente en el idioma actual antes del clic
        txt_denegado = obtener_texto("btn_permiso_denegado", lang)
        await query.answer(txt_denegado, show_alert=True)
        return

    data = query.data

    # --- BLOQUE NUEVO v1.1.0: Procesamiento de Selección de Idioma Manual ---
    if data.startswith("set_lang_"):
        nuevo_idioma = data.split("_")[-1]  # Extrae 'es', 'en' o 'ru'
        await actualizar_config_grupo(chat_id, "lang", nuevo_idioma)
        
        # Enviamos la respuesta de confirmación ya renderizada en el nuevo idioma guardado
        texto_confirmacion = obtener_texto("idioma_cambiado", nuevo_idioma)
        await query.answer()
        await query.edit_message_text(text=texto_confirmacion, parse_mode="Markdown")
        return

    # --- Lógica de calibración de umbrales ---
    if data == "toggle_failsafe":
        await actualizar_config_grupo(chat_id, "failsafe_active", not config["failsafe_active"])
    elif data == "toggle_mod_admin": # 🔥 Interceptamos el clic para Mod Admin
        await actualizar_config_grupo(chat_id, "mod_admin", not config.get("mod_admin", 0))
    elif data == "add_adv":
        nuevo_valor = min(config["umbral_advertencia"] + 0.05, config["umbral_ban"] - 0.01)
        await actualizar_config_grupo(chat_id, "umbral_advertencia", round(nuevo_valor, 2))
    elif data == "sub_adv":
        nuevo_valor = max(config["umbral_advertencia"] - 0.05, 0.10)
        await actualizar_config_grupo(chat_id, "umbral_advertencia", round(nuevo_valor, 2))
    elif data == "add_ban":
        nuevo_valor = min(config["umbral_ban"] + 0.05, 0.99)
        await actualizar_config_grupo(chat_id, "umbral_ban", round(nuevo_valor, 2))
    elif data == "sub_ban":
        nuevo_valor = max(config["umbral_ban"] - 0.05, config["umbral_advertencia"] + 0.01)
        await actualizar_config_grupo(chat_id, "umbral_ban", round(nuevo_valor, 2))

    # Volvemos a leer la configuración refrescada para renderizar el menú actualizado
    config_actualizada = await obtener_config_grupo(chat_id)
    lang_actualizado = config_actualizada.get("lang", "en")
    
    # Recalculamos los estados visuales con los datos nuevos
    status_map = {"es": "🟢 ACTIVO" if config_actualizada["failsafe_active"] else "🔴 APAGADO",
                  "en": "🟢 ACTIVE" if config_actualizada["failsafe_active"] else "🔴 OFF",
                  "ru": "🟢 АКТИВЕН" if config_actualizada["failsafe_active"] else "🔴 ВЫКЛ"}
    status_fs = status_map.get(lang_actualizado, status_map["en"])

    mod_admin_map = {"es": "🟢 SÍ" if config_actualizada.get("mod_admin", 0) else "🔴 NO",
                     "en": "🟢 ON" if config_actualizada.get("mod_admin", 0) else "🔴 OFF",
                     "ru": "🟢 ДА" if config_actualizada.get("mod_admin", 0) else "🔴 НЕТ"}
    status_mod_admin = mod_admin_map.get(lang_actualizado, mod_admin_map["en"])
    
    nuevo_texto = obtener_texto(
        "menu_titulo", 
        lang_actualizado, 
        status=status_fs, 
        mod_admin=status_mod_admin,
        adv=config_actualizada['umbral_advertencia'], 
        ban=config_actualizada['umbral_ban']
    )
    
    keyboard = [
        [InlineKeyboardButton(f"Failsafe: {status_fs}", callback_data="toggle_failsafe")],
        [InlineKeyboardButton(f"Mod Admins: {status_mod_admin}", callback_data="toggle_mod_admin")], # 🔥 Refresco visual
        [
            InlineKeyboardButton("Adv -0.05", callback_data="sub_adv"),
            InlineKeyboardButton("Adv +0.05", callback_data="add_adv")
        ],
        [
            InlineKeyboardButton("Ban -0.05", callback_data="sub_ban"),
            InlineKeyboardButton("Ban +0.05", callback_data="add_ban")
        ]
    ]
    
    await query.answer()
    await query.edit_message_text(text=nuevo_texto, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")