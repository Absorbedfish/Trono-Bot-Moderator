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

# config/locales.py

STRINGS = {
    "es": {
        "bienvenida": (
            "🤖 **¡Hola! Soy TRONO Bot de Moderación Avanzada.**\n\n"
            "Protejo tus grupos manteniendo el chat limpio de material sensible mediante IA.\n\n"
            "Utiliza:\n/privacidad para los términos legales.\n/configuraridioma para cambiar el idioma.\n/ayuda para ver los comandos disponibles."
        ),
        "politica_privacidad": (
            "🔐 **Política de Privacidad e Higiene Digital (Trono Bot)**\n\n"
            "1. **Procesamiento Volátil:** Las imágenes y stickers se analizan directamente en la memoria RAM. Ningún archivo se guarda en almacenamiento persistente.\n"
            "2. **Archivos Pesados:** Los videos y GIFs de gran tamaño se descargan temporalmente en un volumen local aislado para el escaneo de la IA y se destruyen inmediatamente después.\n"
            "3. **Cero Historial:** El bot no almacena texto ni metadatos de las conversaciones, salvo los IDs numéricos necesarios para el búfer circular."
        ),
        "failsafe_active": "⚠️ **[PROTOCOLO FAILSAFE ACTIVADO]**\n\nEl sistema de moderación por IA está fuera de línea. El chat ha sido pausado automáticamente por seguridad.\n\nPrueba ejecutar /conexion.",
        "failsafe_online": "🟢 **[SISTEMA EN LÍNEA]**\n\nEl escudo Trono Bot está activo y el chat reabierto.",
        "failsafe_estable": "🔴 **[SERVICIO INESTABLE]** Código de error: {status}",
        "failsafe_offline": "🔴 **[SERVICIO FUERA DE LÍNEA]** La IA sigue sin responder.",
        "advertencia_creador": "⚠️ (Creador), detecté material sospechoso (Score: {score:.2f}).",
        "sospecha_usuario": "👁‍🗨 **[Verificación Requerida]** Se ha compartido un archivo con un índice de sospecha del {score:.1f}%.",
        "menu_titulo": "⚙️ **Panel de Ajustes de Trono Bot**\n\n🛡️ **Failsafe:** {status}\n👮 **Mod Admins:** {mod_admin}\n⚠️ **Umbral Adv:** {adv:.2f}\n🚫 **Umbral Ban:** {ban:.2f}",
        "btn_permiso_denegado": "❌ No tienes permisos para modificar la configuración.",
        "idioma_cambiado": "🌐 **Idioma actualizado:** El bot ahora se comunicará en Español.",
        "seleccione_idioma": "🌐 **Configuración de Idioma / Language Settings / Настройка языка**\n\nSelecciona el idioma para este chat:",
        "sistema_mensaje_privado": "⚠️ Este comando solo funciona en grupos.",
        "mensaje_multimedia_privado": "⚠️ Por favor no envies mensajes multimedia en este chat.",
        "ayuda_comandos": "📋 **Comandos Disponibles**\n\n- /start: Iniciar el bot\n- /ayuda: Mostrar esta ayuda\n- /ConfigDescripcion: Muestra una descripción de la configuración\n- /configurar: Acceder al panel de control (Solo en grupos)\n- /privacidad: Ver la política de privacidad\n- /configuraridioma: Cambiar el idioma\n- /conexion: Verificar conexión con la IA (Solo en grupos)",
        "descripcion_conf": "📝 **Descripción de opciones de Configuración**\n\n- Failsafe: Configurar el protocolo de seguridad anti ciadas del servicio\n- Mod Admins: Permite al bot moderar los mensajes multimedia de los administradores\n- Umbral Adv: Configurar el umbral de advertencia minimo para que el bot emita una advertencia en caso de detectar material potencialmente sencible\n- Umbral Ban: Configurar el umbral minimo de baneo para que el bot elimine y expulse al usuario infractor"
    },
    "en": {
        "bienvenida": (
            "🤖 **Hello! I am TRONO Advanced Moderation Bot.**\n\n"
            "I protect your groups by keeping the chat clean of sensitive material using AI.\n\n"
            "Use:\n/privacidad for legal terms.\n/configuraridioma to change the language.\n/ayuda to see available commands."
        ),
        "politica_privacidad": (
            "🔐 **Privacy & Digital Hygiene Policy (Trono Bot)**\n\n"
            "1. **Volatile Processing:** Images and stickers are analyzed directly in RAM. No files are saved to persistent storage.\n"
            "2. **Heavy Files:** Large videos and GIFs are temporarily downloaded to an isolated local volume for AI scanning and are destroyed immediately afterward.\n"
            "3. **Zero History:** The bot does not store text or conversation metadata, except for the numerical IDs required for the circular buffer."
        ),
        "failsafe_active": "⚠️ **[FAILSAFE PROTOCOL ACTIVATED]**\n\nThe AI moderation system is offline. The chat has been automatically paused for safety.\n\nTry running /conexion.",
        "failsafe_online": "🟢 **[SYSTEM ONLINE]**\n\nThe Trono Bot shield is active and the chat has been reopened.",
        "failsafe_estable": "🔴 **[UNSTABLE SERVICE]** Error code: {status}",
        "failsafe_offline": "🔴 **[SERVICE OFFLINE]** The AI is still not responding.",
        "advertencia_creador": "⚠️ (Creator), I detected suspicious material (Score: {score:.2f}).",
        "sospecha_usuario": "👁‍🗨 **[Verification Required]** A file has been shared with a suspicion rate of {score:.1f}%.",
        "menu_titulo": "⚙️ **Trono Bot Settings Panel**\n\n🛡️ **Failsafe:** {status}\n👮 **Mod Admins:** {mod_admin}\n⚠️ **Warn Threshold:** {adv:.2f}\n🚫 **Ban Threshold:** {ban:.2f}",
        "btn_permiso_denegado": "❌ You do not have permissions to modify settings.",
        "idioma_cambiado": "🌐 **Language updated:** The bot will now communicate in English.",
        "seleccione_idioma": "🌐 **Language Settings / Configuración de Idioma / Настройка языка**\n\nSelect the language for this chat:",
        "sistema_mensaje_privado": "⚠️ This command only works in groups.",
        "mensaje_multimedia_privado": "⚠️ Please do not send multimedia messages in this chat.",
        "ayuda_comandos": "📋 **Available Commands**\n\n- /start: Start the bot\n- /ayuda: Show this help\n- /ConfigDescripcion: Show configuration description\n- /configurar: Access the control panel(Only Groups)\n- /privacidad: View the privacy policy\n- /configuraridioma: Change the language\n- /conexion: Verify connection with the AI (Only Groups)",
        "descripcion_conf": "📝 **Configuration Descriptions**\n\n- Failsafe: Configure the failsafe protocol for the service\n- Mod Admins: Allow the bot to moderate multimedia messages from admins\n- Warn Threshold: Set the minimum warning threshold for the bot to issue a warning when detecting potentially sensitive material\n- Ban Threshold: Set the minimum ban threshold for the bot to remove and expel the offending user"
    },
    "ru": {
        "bienvenida": (
            "🤖 **Привет! Я TRONO — бот для продвинутой модерации.**\n\n"
            "Я защищаю ваши группы, очищая чат от нежелательного контента с помощью ИИ.\n\n"
            "Используйте:\n/privacidad для юридических условий.\n/configuraridioma для изменения языка.\n/ayuda для просмотра доступных команд."
        ),
        "politica_privacidad": (
            "🔐 **Политика конфиденциальности и цифровой гигиены (Трон-Бот)**\n\n"
            "1. **Временная обработка:** Изображения и стикеры анализируются непосредственно в оперативной памяти (RAM). Файлы не сохраняются на постоянный диск.\n"
            "2. **Большие файлы:** Большие видео и GIF временно загружаются в изолированное локальное хранилище для сканирования ИИ и удаляются сразу после анализа.\n"
            "3. **Отсутствие истории:** Бот не хранит текст или метаданные разговоров, за исключением числовых ID, необходимых для циклического буфера."
        ),
        "failsafe_active": "⚠️ **[АКТИВИРОВАН ПРОТОКОЛ FAILSAFE]**\n\nСистема модерации ИИ отключена. Чат автоматически приостановлен в целях безопасности.\n\nПопробуйте запустить /conexion.",
        "failsafe_online": "🟢 **[СИСТЕМА В СЕТИ]**\n\nЗащита Трон-Бота активна, чат снова открыт.",
        "failsafe_estable": "🔴 **[НЕСТАБИЛЬНАЯ РАБОТА СЛУЖБЫ]** Код ошибки: {status}",
        "failsafe_offline": "🔴 **[СЛУЖБА ОФЛАЙН]** ИИ по-прежнему не отвечает.",
        "advertencia_creador": "⚠️ (Создатель), я обнаружил подозрительный материал (Оценка: {score:.2f}).",
        "sospecha_usuario": "👁‍🗨 **[Требуется проверка]** Был отправлен файл с уровнем подозрения {score:.1f}%.",
        "menu_titulo": "⚙️ **Панеel настроек Трон-Бота**\n\n🛡️ **Failsafe:** {status}\n👮 **Мод Админов:** {mod_admin}\n⚠️ **Порог предупреждения:** {adv:.2f}\n🚫 **Порог бана:** {ban:.2f}",
        "btn_permiso_denegado": "❌ У вас нет прав для изменения настроек.",
        "idioma_cambiado": "🌐 **Язык обновлен:** Теперь бот будет общаться на русском языке.",
        "seleccione_idioma": "🌐 **Настройка языка / Language Settings / Configuración de Idioma**\n\nВыберите язык для этого чата:",
        "sistema_mensaje_privado": "⚠️ Эта команда работает только в группах.",
        "mensaje_multimedia_privado": "⚠️ Пожалуйста, не отправляйте мультимедийные сообщения в этот чат.",
        "ayuda_comandos": "📋 **Доступные команды**\n\n- /start: Запустить бота\n- /ayuda: Показать эту справку\n- /ConfigDescripcion: Показать описание конфигурации\n- /configurar: Доступ к панели управления (Только в группах)\n- /privacidad: Просмотр политики конфиденциальности\n- /configuraridioma: Изменить язык\n- /conexion: Проверить подключение к ИИ (Только в группах)",
        "descripcion_conf": "📝 **Описание команд**\n\n- Failsafe: Настроить протокол аварийного режима для сервиса\n- Мод Админов: Разрешить боту модерировать мультимедийные сообщения от администраторов\n- Порог предупреждения: Установить минимальный порог предупреждений для того, чтобы бот выдавал предупреждение при обнаружении потенциально чувствительного материала\n- Порог бана: Установить минимальный порог бана для того, чтобы бот удалял и исключал нарушающего пользователя"
    }
}

def obtener_texto(clave: str, lang: str = "en", **kwargs) -> str:
    """Devuelve el texto formateado según el idioma del grupo (Failsafe: inglés)."""
    idioma = lang if lang in STRINGS else "en"
    texto_base = STRINGS[idioma].get(clave, STRINGS["en"].get(clave, f"[{clave}]"))
    return texto_base.format(**kwargs)