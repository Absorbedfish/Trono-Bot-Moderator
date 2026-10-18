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

# main.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ChatType

# Importaciones de la infraestructura modular v1.1.0
from config_manager import obtener_config_grupo
from history_manager import registrar_mensaje_id
from utils.security import traducir_ruta_local
from handlers.commands import start, consultar_privacidad, verificar_conexion_ia, configurar_idioma, ayuda, DescripcionComando 
from handlers.menus import despliega_menu_configuracion, manejador_botones_config
from config.locales import obtener_texto

load_dotenv(".env")
TOKEN = os.getenv("TELEGRAM_TOKEN")


# === Wrappers de Acoplamiento local para Handlers de Medios ===
async def h_moderar_imagenes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_id = update.effective_chat.id
    idioma_nativo = "en"
    if update.message.from_user and update.message.from_user.language_code:
        idioma_nativo = update.message.from_user.language_code.lower()
        
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(text=obtener_texto("mensaje_multimedia_privado", lang), parse_mode="Markdown")
        return
    if update.message and update.message.photo:
        try:
            foto = await context.bot.get_file(update.message.photo[-1].file_id)
            ruta_temporal = traducir_ruta_local(foto.file_path)
            nombre_real_archivo = os.path.basename(foto.file_path)
            
            with open(ruta_temporal, "rb") as f:
                foto_bytes = f.read()
                
            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)
                
            # 🔥 PARCHE v1.1.2: En lugar de ir directo a la IA, mandamos al coordinador de moderator.py
            from core.moderator import procesar_multimedia_entrante
            await procesar_multimedia_entrante(update, context, bytes_preparados=foto_bytes, nombre_archivo=nombre_real_archivo, tipo_medio="ram")
            
        except Exception as e:
            print(f"❌ Error en h_moderar_imagenes: {e}")


async def h_procesar_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_id = update.effective_chat.id
    idioma_nativo = "en"
    if update.message.from_user and update.message.from_user.language_code:
        idioma_nativo = update.message.from_user.language_code.lower()
        
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(text=obtener_texto("mensaje_multimedia_privado", lang), parse_mode="Markdown")
        return
    if update.message and update.message.sticker:
        if update.message.sticker.is_animated: return
        try:
            ext = "webm" if update.message.sticker.is_video else "webp"
            archivo_telegram = await context.bot.get_file(update.message.sticker.file_id)
            ruta_temporal = traducir_ruta_local(archivo_telegram.file_path)
            nombre_real_archivo = os.path.basename(archivo_telegram.file_path)

            with open(ruta_temporal, "rb") as f:
                sticker_bytes = f.read()
            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)
                
            # 🔥 PARCHE v1.1.2: Al coordinador asíncrono
            from core.moderator import procesar_multimedia_entrante
            await procesar_multimedia_entrante(update, context, bytes_preparados=sticker_bytes, nombre_archivo=f"{nombre_real_archivo}.{ext}", tipo_medio="ram")
            
        except Exception as e:
            print(f"❌ Error en h_procesar_sticker: {e}")


async def h_procesar_gif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_id = update.effective_chat.id
    idioma_nativo = "en"
    if update.message.from_user and update.message.from_user.language_code:
        idioma_nativo = update.message.from_user.language_code.lower()
        
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")

    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(text=obtener_texto("mensaje_multimedia_privado", lang), parse_mode="Markdown")
        return
    if update.message and update.message.animation:
        try:
            archivo_telegram = await context.bot.get_file(update.message.animation.file_id)
            ruta_temporal = traducir_ruta_local(archivo_telegram.file_path)
            nombre_real_archivo = os.path.basename(archivo_telegram.file_path)

            from core.moderator import procesar_multimedia_entrante
            if update.message.animation.file_size > 10485760:
                # 🔥 PARCHE v1.1.2: Pasamos la ruta física al coordinador
                await procesar_multimedia_entrante(update, context, ruta_fisica=ruta_temporal, nombre_archivo=nombre_real_archivo, tipo_medio="disco")
            else:
                with open(ruta_temporal, "rb") as f:
                    gif_bytes = f.read()
                if os.path.exists(ruta_temporal):
                    os.remove(ruta_temporal)
                # 🔥 PARCHE v1.1.2: Pasamos los bytes al coordinador
                await procesar_multimedia_entrante(update, context, bytes_preparados=gif_bytes, nombre_archivo=nombre_real_archivo, tipo_medio="ram")
        except Exception as e:
            print(f"❌ Error en h_procesar_gif: {e}")


async def h_procesar_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_id = update.effective_chat.id
    idioma_nativo = "en"
    if update.message.from_user and update.message.from_user.language_code:
        idioma_nativo = update.message.from_user.language_code.lower()
        
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")

    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(text=obtener_texto("mensaje_multimedia_privado", lang), parse_mode="Markdown")
        return
    if not update.message: return
    obj_multimedia = update.message.video or update.message.video_note
    if not obj_multimedia: return
    try:
        archivo_telegram = await context.bot.get_file(obj_multimedia.file_id)
        ruta_temporal = traducir_ruta_local(archivo_telegram.file_path)
        nombre_real_archivo = os.path.basename(archivo_telegram.file_path)
        
        # 🔥 PARCHE v1.1.2: Al coordinador mediante disco local
        from core.moderator import procesar_multimedia_entrante
        await procesar_multimedia_entrante(update, context, ruta_fisica=ruta_temporal, nombre_archivo=nombre_real_archivo, tipo_medio="disco")
    except Exception as e:
        print(f"❌ Error en h_procesar_video: {e}")


async def h_procesar_documento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_id = update.effective_chat.id
    idioma_nativo = "en"
    if update.message.from_user and update.message.from_user.language_code:
        idioma_nativo = update.message.from_user.language_code.lower()
        
    config = await obtener_config_grupo(chat_id, idioma_telegram=idioma_nativo)
    lang = config.get("lang", "en")
    if chat.type == ChatType.PRIVATE:
        await update.message.reply_text(text=obtener_texto("mensaje_multimedia_privado", lang), parse_mode="Markdown")
        return
    if update.message and update.message.document:
        nombre_original = update.message.document.file_name.lower() if update.message.document.file_name else ""
        if nombre_original.endswith(('.mp4', '.webm', '.gif')):
            try:
                archivo_telegram = await context.bot.get_file(update.message.document.file_id)
                ruta_temporal = traducir_ruta_local(archivo_telegram.file_path)
                nombre_real_archivo = os.path.basename(archivo_telegram.file_path)
                
                # 🔥 PARCHE v1.1.2: Al coordinador mediante disco local
                from core.moderator import procesar_multimedia_entrante
                await procesar_multimedia_entrante(update, context, ruta_fisica=ruta_temporal, nombre_archivo=nombre_real_archivo, tipo_medio="disco")
            except Exception as e:
                print(f"❌ Error en h_procesar_documento: {e}")


# === Grupo 1: Registro Silencioso para Búfer Circular (SOLO TEXTO) ===
async def escuchar_y_registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return
    if update.message and update.message.from_user:
        registrar_mensaje_id(
            chat_id=update.message.chat.id,
            user_id=update.message.from_user.id,
            message_id=update.message.message_id
        )


async def inicializar_servidor_local(app: Application):
    bot_info = await app.bot.get_me()
    print(f"✅ Ecosistema Trilingüe v2.1.0 activo. Registrado como: @{bot_info.username}")


def main():
    if not TOKEN:
        print("[CRÍTICO] No se encontró la variable de entorno TELEGRAM_TOKEN")
        return

    application = (
        Application.builder()
        .token(TOKEN)
        .base_url("http://telegram-bot-api:8081/bot") 
        .base_file_url("http://telegram-bot-api:8081/file/bot")
        .local_mode(True) 
        .read_timeout(300)       
        .connect_timeout(300)    
        .post_init(inicializar_servidor_local)
        .build()
    )

    # === Grupo 0: Escudos Principales de Análisis (IA) ===
    application.add_handler(MessageHandler(filters.PHOTO, h_moderar_imagenes))
    application.add_handler(MessageHandler(filters.Sticker.ALL, h_procesar_sticker))
    application.add_handler(MessageHandler(filters.ANIMATION, h_procesar_gif))
    application.add_handler(MessageHandler(filters.VIDEO, h_procesar_video))
    application.add_handler(MessageHandler(filters.Document.ALL, h_procesar_documento))
    application.add_handler(MessageHandler(filters.VIDEO_NOTE, h_procesar_video))

    # === Grupo 1: Rastreador Numérico Circular (SQLite) ===
    # 🔥 PARCHE v1.1.2: Removemos los filtros multimedia del Grupo 1.
    # El contenido multimedia se registra de inmediato y de forma síncrona en el Grupo 0
    # evitando condiciones de carrera asíncronas entre handlers concurrentes.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, escuchar_y_registrar), group=1)

    # === Comandos y Configuración ===
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("privacidad", consultar_privacidad))
    application.add_handler(CommandHandler("configurar", despliega_menu_configuracion))
    application.add_handler(CommandHandler("conexion", verificar_conexion_ia))
    application.add_handler(CommandHandler("configuraridioma", configurar_idioma))
    application.add_handler(CommandHandler("ayuda", ayuda))
    application.add_handler(CommandHandler("ConfigDescripcion", DescripcionComando))

    application.add_handler(CallbackQueryHandler(manejador_botones_config))
    
    print("🤖 Trono Bot v2.1.0 iniciado con éxito. Soporte Trilingüe listo...")
    application.run_polling()


if __name__ == '__main__':
    main()