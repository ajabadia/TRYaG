import streamlit as st
import os
import time
from datetime import datetime
from utils.file_handler import save_file_to_temp, TempFileWrapper
from utils.tornado_server import mount_video_upload_route

# Montar la ruta al importar (o llamar explícitamente)
mount_video_upload_route()

def render_webcam_video(key_prefix="webcam_video"):
    """
    Renderiza un componente de grabación de video usando WebRTC.
    Devuelve un objeto TempFileWrapper si se ha grabado un video, o None.
    """
    
    # Configuración de WebRTC
    # Usamos SENDRECV para poder ver el video en pantalla (espejo)
    # y procesarlo si fuera necesario, aunque aquí solo queremos grabar.
    
    # NOTA: streamlit-webrtc no tiene un "grabador" nativo simple que devuelva un archivo al final
    # sin configurar un MediaRecorder en el lado del cliente o procesar frames en el servidor.
    # Procesar frames en servidor (Python) es pesado y puede tener lag.
    # La mejor opción para "grabar y guardar" es usar el MediaRecorder del navegador
    # y enviar el blob. streamlit-webrtc soporta esto via 'media_stream_recorder' pero es complejo.
    
    # VAMOS A INTENTAR UNA APROXIMACIÓN HÍBRIDA MÁS SIMPLE:
    # Usar un componente HTML/JS puro que envía los datos a un componente de Streamlit
    # PERO como no podemos crear componentes custom fácilmente sin build,
    # usaremos streamlit-webrtc solo si es estrictamente necesario.
    
    # SI EL USUARIO QUIERE "GRABAR DE VERDAD", LA MEJOR OPCIÓN SIN COMPONENTES CUSTOM ES WEBRTC.
    # Pero la implementación de grabación en servidor con webrtc es:
    # 1. Recibir frames.
    # 2. Escribir a contenedor (av.open).
    
    st.warning("⚠️ La grabación nativa de video está en fase experimental.")
    
    # Por simplicidad y robustez en esta iteración, vamos a usar un enfoque de 
    # "File Uploader" mejorado con instrucciones claras, ya que implementar
    # un grabador WebRTC robusto desde cero requiere mucho código boilerplate (AudioProcessor, VideoProcessor, threading).
    
    # REVISIÓN: El usuario pidió explícitamente "grabar de verdad".
    # Vamos a usar un script HTML5 inyectado con `st.components.v1.html`
    # Y usaremos un truco para enviar los datos de vuelta:
    # Crear un link de descarga automático o intentar comunicar.
    
    # DADO QUE NO PODEMOS RECIBIR DATOS DE VUELTA FÁCILMENTE DE HTML PURO:
    # Vamos a usar `streamlit-webrtc` pero solo para el streaming, y si es muy complejo guardar,
    # volveremos al uploader.
    
    # INTENTO CON WEBRTC SIMPLE (SOLO VISUALIZACIÓN POR AHORA PARA NO ROMPER):
    # Realmente, para grabar, lo más estable en Streamlit "puro" es el uploader con capture="camcorder".
    # En Desktop, eso abre el explorador.
    
    # VOY A IMPLEMENTAR UNA SOLUCIÓN CON JAVASCRIPT QUE "EMPUJA" LOS DATOS A UN COMPONENTE INVISIBLE
    # O MEJOR: Usar `streamlit_webrtc` con un `MediaRecorder` del lado del cliente si la librería lo soporta fácil.
    # La librería tiene `client_settings` pero la grabación suele ser server-side.
    
    pass

# CAMBIO DE ESTRATEGIA:
# Voy a crear un componente HTML/JS que graba y ofrece "Descargar Video".
# Luego el usuario sube ese video al uploader de abajo.
# Es un paso extra pero funciona 100% sin servidor de señalización complejo.
# "Graba aquí -> Descarga -> Sube abajo".
# Es un poco "hacky" pero cumple "grabar de la webcam".

def render_js_recorder(filename_prefix="video_triaje", key="recorder"):
    # Generar nombre único para esta sesión de grabación y persistirlo
    session_key = f"{key}_filename"
    if session_key not in st.session_state:
        st.session_state[session_key] = f"{filename_prefix}_{int(time.time())}.webm"
    
    unique_filename = st.session_state[session_key]
    
    html_code = """
    <div style="display: flex; flex-direction: column; align-items: center; gap: 10px; font-family: sans-serif; padding: 10px;">
        <div style="position: relative; width: 100%; max-width: 800px; background: #000; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            <video id="preview" style="width: 100%; max-height: 500px; display: block; object-fit: contain;" autoplay muted playsinline></video>
            <div id="rec-indicator" style="position: absolute; top: 15px; right: 15px; width: 12px; height: 12px; background: red; border-radius: 50%; display: none; box-shadow: 0 0 5px rgba(255,0,0,0.8);"></div>
        </div>
        
        <div style="display: flex; gap: 15px; width: 100%; justify-content: center;">
            <button id="btn-start" onclick="startRecording()" style="background: #ff4b4b; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 16px; transition: background 0.2s;">⏺️ Grabar</button>
            <button id="btn-stop" onclick="stopRecording()" disabled style="background: #e0e0e0; color: #888; border: none; padding: 12px 24px; border-radius: 6px; cursor: not-allowed; font-weight: bold; font-size: 16px; transition: all 0.2s;">⏹️ Parar</button>
        </div>

        <div id="status-area" style="display: none; text-align: center; padding: 15px; border-radius: 8px; width: 100%; max-width: 600px; margin-top: 10px;">
            <p id="status-text" style="margin: 0; font-weight: bold;"></p>
        </div>
        
        <div id="error-msg" style="display: none; color: red; margin-top: 10px; font-weight: bold;"></div>
    </div>

    <style>
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        #rec-indicator { animation: blink 1.5s infinite; }
        button:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
        button:active:not(:disabled) { transform: translateY(0); }
    </style>

    <script>
    let preview = document.getElementById("preview");
    let startBtn = document.getElementById("btn-start");
    let stopBtn = document.getElementById("btn-stop");
    let statusArea = document.getElementById("status-area");
    let statusText = document.getElementById("status-text");
    let recIndicator = document.getElementById("rec-indicator");
    let errorMsg = document.getElementById("error-msg");
    
    let recorder;
    let stream;
    let chunks = [];
    let targetFilename = "__FILENAME__";

    async function startRecording() {
        try {
            errorMsg.style.display = "none";
            statusArea.style.display = "none";
            
            stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            preview.srcObject = stream;
            
            // Preferir codecs con mejor compresión y ajustar bitrate
            let options = { 
                mimeType: 'video/webm;codecs=vp9,opus',
                videoBitsPerSecond: 1000000 // 1 Mbps
            };
            
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options = { 
                    mimeType: 'video/webm',
                    videoBitsPerSecond: 1000000
                }; 
            }
            
            recorder = new MediaRecorder(stream, options);
            
            recorder.ondataavailable = e => {
                if (e.data.size > 0) chunks.push(e.data);
            };
            
            recorder.onstop = async e => {
                let blob = new Blob(chunks, { type: "video/webm" });
                chunks = [];
                
                recIndicator.style.display = "none";
                stream.getTracks().forEach(track => track.stop());
                preview.srcObject = null;
                
                // Subir automáticamente
                statusArea.style.display = "block";
                statusArea.style.background = "#fff3cd";
                statusText.innerText = "⏳ Subiendo video al servidor...";
                statusText.style.color = "#856404";
                
                // Intentar obtener cookie XSRF por si acaso
                function getCookie(n) {
                    let a = `; ${document.cookie}`.match(`;\\s*${n}=([^;]+)`);
                    return a ? a[1] : '';
                }
                
                try {
                    let headers = {};
                    let xsrf = getCookie('_xsrf');
                    if (xsrf) {
                        headers['X-XSRFToken'] = xsrf;
                    }

                    let response = await fetch('/upload_video_v7?filename=' + targetFilename, {
                        method: 'POST',
                        headers: headers,
                        body: blob
                    });
                    
                    if (response.ok) {
                        statusArea.style.background = "#d4edda";
                        statusText.innerText = "✅ Video guardado. Pulsa 'Procesar' abajo (puede tardar unos segundos).";
                        statusText.style.color = "#155724";
                    } else {
                        throw new Error("Error en subida: " + response.statusText);
                    }
                } catch (uploadErr) {
                    console.error(uploadErr);
                    statusArea.style.background = "#f8d7da";
                    statusText.innerText = "❌ Error subiendo: " + uploadErr.message;
                    statusText.style.color = "#721c24";
                }

                // Reset UI
                startBtn.disabled = false;
                stopBtn.disabled = true;
                stopBtn.style.background = "#e0e0e0";
                stopBtn.style.color = "#888";
                stopBtn.style.cursor = "not-allowed";
                
                startBtn.innerText = "⏺️ Grabar Nuevo";
            };
            
            recorder.start();
            
            // UI Update
            startBtn.disabled = true;
            stopBtn.disabled = false;
            stopBtn.style.background = "#333";
            stopBtn.style.color = "white";
            stopBtn.style.cursor = "pointer";
            
            recIndicator.style.display = "block";
            
        } catch (err) {
            console.error(err);
            errorMsg.innerText = "Error: " + err.message;
            errorMsg.style.display = "block";
        }
    }

    function stopRecording() {
        if (recorder && recorder.state !== "inactive") {
            recorder.stop();
        }
    }
    </script>
    """
    import streamlit.components.v1 as components
    components.html(html_code.replace("__FILENAME__", unique_filename), height=550)
    return unique_filename
