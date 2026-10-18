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

# core/ia_client.py
import httpx

IA_SERVICE_URL = "http://ia-opennsfw-trono:8081/clasificar"

# 🔥 INSTANCIA DEL CLIENTE ASÍNCRONO REUTILIZABLE (Keep-Alive habilitado por defecto)
# Definimos los límites de timeout globales para todas las llamadas a la IA
limites_timeout = httpx.Timeout(15.0, connect=5.0)
cliente_ia = httpx.AsyncClient(timeout=limites_timeout)

async def consultar_ia_disco(ruta_absoluta: str, umbral_ban: float) -> float:
    """Envía la ruta física del archivo en el volumen a la IA de forma 100% asíncrona."""
    payload = {"archivo_ruta": ruta_absoluta, "umbral_ban": umbral_ban}
    
    try:
        # 🔥 Petición no bloqueante usando await
        respuesta = await cliente_ia.post(IA_SERVICE_URL, json=payload)
        
        if respuesta.status_code == 200:
            return respuesta.json().get("score_nsfw", 0.0)
        raise ValueError(f"Código de error en respuesta de IA: {respuesta.status_code}")
        
    except httpx.RequestError as exc:
        print(f"❌ Error de red/comunicación HTTPX en disco: {exc}")
        raise


async def consultar_ia_ram(archivo_bytes, nombre_archivo: str, content_type: str, umbral_ban: float) -> float:
    """Envía los bytes retenidos en memoria RAM directamente a la IA sin congelar el Event Loop."""
    # Aseguramos que el puntero del BytesIO/archivo esté al inicio
    if hasattr(archivo_bytes, 'seek'):
        archivo_bytes.seek(0)
        
    files = {'file': (nombre_archivo, archivo_bytes, content_type)}
    payload_form = {'umbral_ban': str(umbral_ban)}
    
    try:
        # 🔥 Envío de multipart/form-data asíncrono
        respuesta = await cliente_ia.post(IA_SERVICE_URL, files=files, data=payload_form)
        
        if respuesta.status_code == 200:
            return respuesta.json().get("score_nsfw", 0.0)
        raise ValueError(f"Código de error en respuesta de IA: {respuesta.status_code}")
        
    except httpx.RequestError as exc:
        print(f"❌ Error de red/comunicación HTTPX en RAM: {exc}")
        raise

# Método opcional de cierre limpio de sockets para los ciclos de parada del bot
async def cerrar_cliente_ia():
    await cliente_ia.aclose()