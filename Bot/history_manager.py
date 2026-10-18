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

# history_manager.py
import sqlite3
import os

DB_PATH = "/app/shared_media/trono_historial.db"

def inicializar_db_historial():
    """Crea la tabla de rastreo numérico y el trigger de limpieza circular."""
    conexion = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conexion.cursor()

    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    
    # Tabla ultra ligera: solo IDs numéricos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            message_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Índice optimizado para búsquedas rápidas durante un Ban
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_busqueda_ban ON historial_mensajes(chat_id, user_id);")
    
    # 🔥 ESCUDO ANTI-DESBORDE: Trigger para mantener solo los últimos 100 mensajes por grupo
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS limpiar_bufer_circular
        AFTER INSERT ON historial_mensajes
        BEGIN
            DELETE FROM historial_mensajes 
            WHERE chat_id = NEW.chat_id 
            AND id NOT IN (
                SELECT id FROM historial_mensajes 
                WHERE chat_id = NEW.chat_id 
                ORDER BY id DESC 
                LIMIT 1000
            );
        END
    """)
    
    conexion.commit()
    conexion.close()

def registrar_mensaje_id(chat_id: int, user_id: int, message_id: int):
    """Registra de forma síncrona y veloz el ID de un mensaje común."""
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()
        
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        
        cursor.execute(
            "INSERT INTO historial_mensajes (chat_id, user_id, message_id) VALUES (?, ?, ?)",
            (chat_id, user_id, message_id)
        )
        conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"⚠️ Error al registrar mensaje en el búfer: {e}")

def obtener_y_limpiar_historial_usuario(chat_id: int, user_id: int) -> list:
    """Recupera todos los message_id de un infractor y limpia sus registros."""
    ids_a_borrar = []
    try:
        conexion = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conexion.cursor()

        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        
        # Buscamos los IDs de mensajes previos
        cursor.execute(
            "SELECT message_id FROM historial_mensajes WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        )
        ids_a_borrar = [fila[0] for fila in cursor.fetchall()]
        
        # Eliminamos sus registros de la DB inmediatamente (ya los tenemos en memoria para el bucle)
        cursor.execute(
            "DELETE FROM historial_mensajes WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        )
        
        conexion.commit()
        conexion.close()
    except Exception as e:
        print(f"⚠️ Error al extraer historial del infractor: {e}")
        
    return ids_a_borrar

# Inicialización automática al importar el módulo
if not os.path.exists(DB_PATH):
    inicializar_db_historial()