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

# utils/security.py
import os
from telegram import Bot, ChatPermissions

SHARED_DIR = "/app/shared_media"

def traducir_ruta_local(ruta_completa_telegram):
    """Limpia la URL HTTP del servidor local y la traduce a una ruta física."""
    if not ruta_completa_telegram:
        return None
    
    if "//" in ruta_completa_telegram:
        ruta_disco_pura = "/" + ruta_completa_telegram.split("//")[-1]
    else:
        ruta_disco_pura = ruta_completa_telegram

    return ruta_disco_pura.replace("/var/lib/telegram-bot-api", SHARED_DIR)


async def verificar_permisos_usuario(bot: Bot, chat_id: int, user_id: int) -> tuple[bool, bool]:
    """
    Verifica el rango de un usuario en el chat.
    Devuelve una tupla: (es_admin, es_creador)
    """
    try:
        chat = await bot.get_chat(chat_id)
        if chat.type == "private":
            return True, False

        chat_administrators = await bot.get_chat_administrators(chat_id)
        es_creador = any(admin.status == 'creator' and admin.user.id == user_id for admin in chat_administrators)
        es_admin = any(admin.user.id == user_id for admin in chat_administrators)
        
        return es_admin, es_creador
    except Exception as e:
        print(f"⚠️ Error al verificar jerarquía de usuario {user_id} en chat {chat_id}: {e}")
        return False, False