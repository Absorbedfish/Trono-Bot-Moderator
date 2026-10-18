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

# config_manager.py
import sqlite3
import asyncio

# Ruta persistente de la base de datos dentro del volumen compartido
DB_FILE = "/app/shared_media/angel_guardian.db"

VALORES_POR_DEFECTO = {
    "failsafe_active": 0,       # 0 = Desactivado, 1 = Activado (SQLite maneja enteros)
    "umbral_advertencia": 0.50,
    "umbral_ban": 0.60,
    "mod_admin": 0,              # 0 = Desactivado, 1 = Activado
    "lang": "en"                # Idioma base global
}

def inicializar_db_config():
    """Crea la tabla de configuración si no existe aplicando pragmas WAL de alta velocidad."""
    conn = sqlite3.connect(DB_FILE)
    try:
        cursor = conn.cursor()
        # Motores transaccionales de alto rendimiento para evitar bloqueos concurrentes
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracion_grupos (
                chat_id INTEGER PRIMARY KEY,
                failsafe_active INTEGER DEFAULT 0,
                umbral_advertencia REAL DEFAULT 0.50,
                umbral_ban REAL DEFAULT 0.60,
                mod_admin INTEGER DEFAULT 0,
                lang TEXT DEFAULT 'en',
                registrado_el TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"❌ Error crítico al inicializar la base de datos de configuración: {e}")
    finally:
        conn.close()

def _db_obtener_config(chat_id: int, idioma_telegram: str) -> dict:
    """Consulta directa a la DB ejecutada en el pool de hilos para no bloquear el Event Loop."""
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    conn.row_factory = sqlite3.Row # Mapea las columnas directo a llaves de diccionario
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT failsafe_active, umbral_advertencia, umbral_ban, lang, mod_admin
            FROM configuracion_grupos WHERE chat_id = ?
        """, (chat_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
            
        # Si el grupo no está registrado, se inserta inmediatamente con sus valores iniciales
        lang_final = idioma_telegram if idioma_telegram in ["es", "en", "ru"] else "en"
            
        cursor.execute("""
            INSERT INTO configuracion_grupos (chat_id, failsafe_active, umbral_advertencia, umbral_ban, lang, mod_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chat_id, VALORES_POR_DEFECTO["failsafe_active"], VALORES_POR_DEFECTO["umbral_advertencia"], VALORES_POR_DEFECTO["umbral_ban"], lang_final, VALORES_POR_DEFECTO["mod_admin"]))
        conn.commit()
        
        print(f"🌐 [DATABASE] Configuración inicial creada para el chat {chat_id} (Idioma: {lang_final}).")
        return {
            "failsafe_active": VALORES_POR_DEFECTO["failsafe_active"],
            "umbral_advertencia": VALORES_POR_DEFECTO["umbral_advertencia"],
            "umbral_ban": VALORES_POR_DEFECTO["umbral_ban"],
            "lang": lang_final,
            "mod_admin": VALORES_POR_DEFECTO["mod_admin"]
        }
    finally:
        conn.close()

def _db_actualizar_config(chat_id: int, clave: str, valor) -> None:
    """Escritura directa en la DB libre de sobrecargas por hilos."""
    if isinstance(valor, bool):
        valor = 1 if valor else 0

    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    try:
        cursor = conn.cursor()
        # Asegura la existencia del registro antes de actualizar
        cursor.execute("INSERT OR IGNORE INTO configuracion_grupos (chat_id) VALUES (?)", (chat_id,))
        
        # Validación perimetral de columnas permitidas antes de la inyección estructurada
        if clave in ["failsafe_active", "umbral_advertencia", "umbral_ban", "lang", "mod_admin"]:
            cursor.execute(f"UPDATE configuracion_grupos SET {clave} = ? WHERE chat_id = ?", (valor, chat_id))
            conn.commit()
            print(f"📝 [DATABASE] Cambios guardados para {chat_id} -> {clave}: {valor}")
    finally:
        conn.close()

# ─── CAPA DE ABSTRACCIÓN ASÍNCRONA PÚBLICA ───

async def obtener_config_grupo(chat_id: int, idioma_telegram: str = "en") -> dict:
    """Llamada asíncrona no bloqueante para recuperar la configuración de un chat."""
    return await asyncio.to_thread(_db_obtener_config, chat_id, idioma_telegram)

async def actualizar_config_grupo(chat_id: int, clave: str, valor) -> None:
    """Llamada asíncrona no bloqueante para modificar parámetros del chat."""
    await asyncio.to_thread(_db_actualizar_config, chat_id, clave, valor)

# Inicialización de la estructura relacional al cargar el módulo
inicializar_db_config()