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

# app.py
from flask import Flask, request, jsonify
from PIL import Image
import tensorflow as tf
import numpy as np
import random
import cv2
import os
import asyncio
import uuid

app = Flask(__name__)

# --- CARGA DEL MODELO NATIVO (OpenNSFW) ---
try:
    ruta_modelo = "./open_nsfw_saved_model"
    model_func = tf.saved_model.load(ruta_modelo)
    print("¡Ángel Guardián: Tronobot inicializado y cargado exitosamente!")
except Exception as e:
    print(f"ERROR CRÍTICO AL CARGAR EL MODELO TRONO: {e}")

SHARED_DIR = "/app/shared_media"
UPLOAD_FOLDER = 'static/uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def evaluar_imagen(ruta_imagen):
    """Procesamiento matemático puro (CPU Bound)."""
    img = Image.open(ruta_imagen).convert('RGB')
    img = img.resize((224, 224), resample=Image.BILINEAR)
    
    x = tf.keras.preprocessing.image.img_to_array(img)
    
    # Preprocesamiento Yahoo OpenNSFW (RGB -> BGR + Resta de media Caffe)
    x = x[:, :, ::-1]     
    x[:, :, 0] -= 104.0   
    x[:, :, 1] -= 117.0   
    x[:, :, 2] -= 123.0   
    
    x = np.expand_dims(x, axis=0)
    
    predictor = model_func.signatures["serving_default"]
    tensor_entrada = tf.convert_to_tensor(x, dtype=tf.float32)
    prediccion_cruda = predictor(input=tensor_entrada)
    
    nsfw_score = float(prediccion_cruda['predictions'][0][1]) 
    return nsfw_score


def evaluar_video_por_fotogramas(video_path, num_frames=5, umbral_corte=0.60):
    """Muestreo e inferencia en bloque (I/O y CPU Bound)."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Error al abrir el flujo de video con OpenCV")
        return 0.0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    muestras = min(num_frames, total_frames) if total_frames > 0 else 1
    indices_fotogramas = sorted(random.sample(range(total_frames), muestras)) if total_frames > muestras else [0]
    
    print(f"\n🎬 [ANALIZANDO MULTIMEDIA] Total frames: {total_frames} | Muestreando {len(indices_fotogramas)} cuadros (Corte Dinámico: {umbral_corte:.2f})...")
    
    max_score = 0.0
    id_unico = uuid.uuid4().hex
    ruta_temporal_frame = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_frame_{id_unico}.jpg")

    try:
        for i, frame_number in enumerate(indices_fotogramas, start=1):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            
            if not ret:
                continue
                
            cv2.imwrite(ruta_temporal_frame, frame)
            score_actual = evaluar_imagen(ruta_temporal_frame)
            
            print(f"  📌 Cuadro Muestreado #{i} (Frame Real: {frame_number}) -> Score NSFW: {score_actual:.4f}")
            
            if score_actual > max_score:
                max_score = score_actual
                
            if max_score >= umbral_corte:
                print(f"  🚨 [CORTOCIRCUITO] Deteniendo muestreo en frame {frame_number} por superar umbral dinámico configurado ({umbral_corte:.2f}).")
                break
    finally:
        cap.release()
        if os.path.exists(ruta_temporal_frame):
            os.remove(ruta_temporal_frame)
            
    return max_score


# 🔥 INTERCEPTOR DE SALUD / HEALTHCHECK INTEGRADO
@app.route("/", methods=["GET", "POST"])
def healthcheck():
    """Endpoint raíz para monitoreo rápido del bot y de la red de Docker."""
    return jsonify({"status": "online", "service": "ia_opennsfw_trono", "version": "2.0.0"}), 200


@app.route("/clasificar", methods=["POST"])
async def clasificar():
    # 🌟 VÍA A: Análisis perimetral sobre volumen compartido (JSON)
    if request.is_json:
        data = request.get_json()
        ruta_archivo = data.get("archivo_ruta")
        umbral_ban_dinamico = data.get("umbral_ban", 0.60)
        
        # 🔥 SOLUCIÓN AL FIN DE RED: Si el bot manda un string vacío, respondemos con salud en vez de error
        if ruta_archivo == "":
            return jsonify({"status": "online", "msg": "Ping de diagnóstico recibido con éxito"}), 200
        
        if not ruta_archivo or not os.path.exists(ruta_archivo):
            print(f"❌ [IA ERROR] Ruta JSON recibida pero el archivo no existe en el volumen: {ruta_archivo}")
            return jsonify({"error": "Archivo no encontrado"}), 400
            
        try:
            print(f"[IA LOG] Iniciando análisis perimetral v2.0.0 asíncrono...")
            score = await asyncio.to_thread(
                evaluar_video_por_fotogramas, ruta_archivo, 10, umbral_ban_dinamico
            )
            
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
                print(f"🧹 [IA LOG] Archivo pesado eliminado con éxito del volumen: {ruta_archivo}")
                
            print(f"[LOG TRONO DISCO] Inferencia finalizada de forma asíncrona. Score Máximo: {score:.4f}")
            return jsonify({"score_nsfw": float(score)})
            
        except Exception as e:
            if os.path.exists(ruta_archivo): os.remove(ruta_archivo)
            return jsonify({"error": str(e)}), 500

    # 🌟 VÍA B: Procesamiento tradicional por red HTTP (RAM)
    if 'file' not in request.files:
        return jsonify({"error": "No hay archivo"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Archivo vacío"}), 400

    umbral_ban_dinamico = float(request.form.get("umbral_ban", 0.60))

    if file:
        filename = file.filename.lower()
        token_archivo = uuid.uuid4().hex
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{token_archivo}_{file.filename}")
        
        if filename.endswith(('.mp4', '.webm', '.gif')):
            await asyncio.to_thread(file.save, filepath)
            try:
                score = await asyncio.to_thread(
                    evaluar_video_por_fotogramas, filepath, 5, umbral_ban_dinamico
                )
                if os.path.exists(filepath): 
                    os.remove(filepath) 
                    print(f"🗑️ [IA LOG] Caché local de video eliminada: {filepath}") # 👈 Añadido
                print(f"[LOG TRONO ANIMADO HTTP] Inferencia finalizada. Score: {score:.4f}")
                return jsonify({"score_nsfw": float(score)})
            except Exception as e:
                if os.path.exists(filepath): 
                    os.remove(filepath)
                    print(f"🧹 [IA LOG] Limpieza por excepción (Video HTTP): {filepath}") # 👈 Añadido
                return jsonify({"error": str(e)}), 500
                
        else:
            try:
                img = Image.open(file.stream)
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    fondo_blanco = Image.new('RGB', img.size, (255, 255, 255))
                    fondo_blanco.paste(img, (0, 0), img.convert('RGBA'))
                    img = fondo_blanco
                else:
                    img = img.convert('RGB')
                    
                await asyncio.to_thread(img.save, filepath, "JPEG")
                score = await asyncio.to_thread(evaluar_imagen, filepath)
                
                if os.path.exists(filepath): 
                    os.remove(filepath)
                    print(f"🧹 [IA LOG] Caché local de imagen liberada: {filepath}") # 👈 Añadido
                
                return jsonify({"score_nsfw": float(score)})
                
            except Exception as e:
                if os.path.exists(filepath): 
                    os.remove(filepath)
                    print(f"🧹 [IA LOG] Limpieza por excepción (Imagen HTTP): {filepath}") # 👈 Añadido
                return jsonify({"error": str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8081)