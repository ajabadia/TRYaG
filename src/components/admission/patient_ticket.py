import streamlit as st
import urllib.parse
from datetime import datetime
import json

def render_ticket_modal(patient_data):
    """
    Renderiza un ticket/pulsera de identificación para el paciente.
    Usa una API pública para generar el QR.
    """
    # Preparar datos para el QR
    qr_payload = {
        "id": str(patient_data.get("_id", "unknown")),
        "nhc": patient_data.get("identification_number", ""),
        "name": f"{patient_data.get('nombre', '')} {patient_data.get('apellidos', '')}",
        "arrival": datetime.now().isoformat()
    }
    qr_data = json.dumps(qr_payload)
    
    # Delegar generación de URL al servicio independiente
    from services.qr_service import generate_qr_url
    qr_url = generate_qr_url(qr_data, size="150x150")

    # --- 1. Obtener Configuración del Centro ---
    from ui.config.config_loader import load_centro_config
    centro_config = load_centro_config()
    nombre_centro = centro_config.get('denominacion', "HOSPITAL GENERAL")
    logo_path = centro_config.get('logo_path')
    
    # --- 2. Calcular Edad ---
    from services.patient_service import calcular_edad
    edad = patient_data.get('edad')
    if edad is None or edad == '?' or edad == 'N/A':
        fnac = patient_data.get('fecha_nacimiento')
        if fnac:
            if isinstance(fnac, str):
                try: fnac = datetime.fromisoformat(fnac.replace('Z', '+00:00'))
                except: pass
            if isinstance(fnac, datetime):
                if fnac.tzinfo: fnac = fnac.replace(tzinfo=None)
                edad = calcular_edad(fnac)
            else:
                edad = "?"
        else:
            edad = "?"

    # --- 3. Recuperar Alergias Históricas ---
    alergias = patient_data.get('medical_background', {}).get('allergies', [])
    if not alergias:
        # Intentar buscar en triajes previos
        try:
            from db.repositories.triage import get_triage_repository
            repo_triage = get_triage_repository()
            # Buscar último triaje completado de este paciente que tenga alergias
            last_triage = repo_triage.collection.find_one(
                {
                    "patient_id": patient_data.get("patient_code"),
                    "status": "completed",
                    "medical_background.allergies": {"$exists": True, "$ne": []}
                },
                sort=[("timestamp", -1)]
            )
            if last_triage:
                 alergias = last_triage.get('medical_background', {}).get('allergies', [])
        except Exception as e:
            print(f"Error fetching historical allergies: {e}")

    # Estilos CSS para el ticket
    st.markdown("""
        <style>
        .ticket-container {
            border: 2px dashed #333;
            padding: 20px;
            background-color: #fff;
            color: #000;
            font-family: 'Courier New', Courier, monospace;
            max_width: 400px;
            margin: 0 auto;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
        }
        .ticket-header {
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
        .ticket-logo {
            max-height: 50px;
            display: block;
            margin: 0 auto 5px auto;
        }
        .ticket-body {
            font-size: 14px;
            line-height: 1.4;
        }
        .ticket-field {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }
        .ticket-highlight {
            font-weight: bold;
            font-size: 16px;
        }
        .ticket-allergies {
            color: white;
            background-color: black;
            padding: 5px;
            margin-top: 10px;
            text-align: center;
            font-weight: bold;
        }
        .ticket-footer {
            text-align: center;
            margin-top: 15px;
            font-size: 10px;
            border-top: 1px dotted #000;
            padding-top: 5px;
        }
        .cut-line {
            border-top: 1px dashed red;
            margin-top: 20px;
            position: relative;
        }
        .cut-line::after {
            content: "✂️ Cortar aquí";
            position: absolute;
            top: -10px;
            right: 0;
            background: white;
            color: red;
            font-size: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Renderizar Ticket
    st.markdown('<div class="ticket-container">', unsafe_allow_html=True)
    
    # Helper para Base64 local
    import base64
    import os
    
    def get_base64_logo(path):
        if not path: return ""
        # Normalizar path (ej: src/assets... -> absoluto o relativo correcto)
        # Si viene de DB como src\assets\logos\logo.png, hay que ver donde estamos
        # Estamos en src/components/admission, la app corre en src/
        # path suele ser relativo a root
        full_path = os.path.abspath(path)
        if not os.path.exists(full_path):
             # Intentar relativo a cwd (src/)
             full_path = os.path.abspath(os.path.join(os.getcwd(), path))
        
        if os.path.exists(full_path):
            with open(full_path, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode()
                # Adivinar mime simple
                ext = path.split('.')[-1].lower()
                mime = "image/png" if ext == "png" else "image/jpeg"
                return f"data:{mime};base64,{b64_string}"
        return ""

    logo_b64 = get_base64_logo(logo_path)
    logo_html = f'<img src="{logo_b64}" class="ticket-logo">' if logo_b64 else ''
    
    # Nombre Centro (Fallback si DB dice "HOSPITAL GENERAL" genérico)
    nombre_mostrar = nombre_centro if nombre_centro and nombre_centro != "HOSPITAL GENERAL" else "Viamed Madrid Centro"

    st.markdown(f"""
        <div class="ticket-header">
            {logo_html}
            <h3>{nombre_mostrar}</h3>
            <p>ADMISIÓN DE URGENCIAS</p>
        </div>
    """, unsafe_allow_html=True)

    # QR y Datos Principales
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(qr_url, width=120)
        
    with c2:
        # NOMBRE GRANDE
        st.markdown(f"<div style='font-size:18px; font-weight:bold; line-height:1.2; margin-bottom:5px;'>{patient_data.get('nombre', 'Desc.')} {patient_data.get('apellido1', '')}</div>", unsafe_allow_html=True)
        
        # NHC
        st.markdown(f"**NHC:** <code>{patient_data.get('identification_number', '---')}</code>", unsafe_allow_html=True)
        
        # CODIGO PACIENTE (Solicitado: Debajo del NHC y MAS GRANDE)
        p_code = patient_data.get('patient_code', '---')
        st.markdown(f"<div style='font-size:32px; font-weight:900; color:#333; margin-top:10px; border-bottom: 2px solid #ddd; display:inline-block;'>{p_code}</div>", unsafe_allow_html=True)
        
    # Alergias (Crítico)
    if alergias:
        alergias_str = ", ".join(alergias) if isinstance(alergias, list) else str(alergias)
        st.markdown(f'<div class="ticket-allergies">⚠️ ALERGIAS: {alergias_str.upper()}</div>', unsafe_allow_html=True)
    else:
         st.markdown(f'<div style="text-align:center; margin-top:10px; border:1px solid #ccc;">Sin Alergias Conocidas (Reg.)</div>', unsafe_allow_html=True)

    # Footer
    st.markdown(f"""
        <div class="ticket-footer">
            Entrada: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
            Conserve este ticket durante toda su estancia.
        </div>
        <div class="cut-line"></div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Botón de "Imprimir" (Simulado)
    if st.button("🖨️ Enviar a Impresora", use_container_width=True, key="print_ticket_job"):
        st.toast("Enviando trabajo de impresión... (Simulado)", icon="🖨️")

