import streamlit as st
import streamlit.components.v1 as components
import json
import time
from datetime import datetime
from db.repositories.triage import get_triage_repository


def render_offline_sync():
    """
    Renderiza el componente de sincronización offline en la sidebar.
    Permite exportar datos locales (IndexedDB) a JSON y subirlos al servidor.
    """
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("📡 Sincronización Offline", expanded=False):
        
        # 1. Botón para buscar y exportar datos locales (JS)
        st.markdown("##### 1. Exportar datos locales")
        st.caption("Si trabajaste sin conexión, descarga tus registros aquí.")
        
        # Script para leer IndexedDB y generar un archivo de descarga
        export_js = """
        <script>
        function exportOfflineData() {
            const DB_NAME = 'TryageOfflineDB';
            const STORE_NAME = 'triage_records';
            
            const request = indexedDB.open(DB_NAME, 1);
            
            request.onerror = (event) => {
                console.error("Error abriendo DB:", event);
                alert("Error accediendo a datos locales.");
            };
            
            request.onsuccess = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    alert("No se encontró base de datos offline.");
                    return;
                }
                
                const transaction = db.transaction([STORE_NAME], "readonly");
                const store = transaction.objectStore(STORE_NAME);
                const getAll = store.getAll();
                
                getAll.onsuccess = () => {
                    const records = getAll.result;
                    if (records.length === 0) {
                        alert("No hay registros offline pendientes.");
                        return;
                    }
                    
                    // Crear blob y descargar
                    const dataStr = JSON.stringify(records, null, 2);
                    const blob = new Blob([dataStr], {type: "application/json"});
                    const url = URL.createObjectURL(blob);
                    
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `triaje_offline_${new Date().toISOString().slice(0,19).replace(/:/g,"-")}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                };
            };
        }
        </script>
        <button onclick="exportOfflineData()" style="
            background-color: #f0f2f6;
            border: 1px solid #d6d6d8;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-size: 14px;
            cursor: pointer;
            width: 100%;
            margin-bottom: 10px;
        ">📥 Descargar Registros Pendientes</button>
        """
        components.html(export_js, height=60)
        
        # 2. Uploader para importar los datos al servidor (Python)
        st.markdown("##### 2. Sincronizar con Servidor")
        uploaded_file = st.file_uploader("Sube el archivo JSON descargado", type=["json"], key="offline_sync_uploader")
        
        if uploaded_file is not None:
            try:
                records = json.load(uploaded_file)
                if not isinstance(records, list):
                    st.error("Formato inválido: Se esperaba una lista de registros.")
                else:
                    if st.button(f"Sincronizar {len(records)} registros"):
                        success_count = 0
                        errors = []
                        
                        progress_bar = st.progress(0)
                        
                        for i, record in enumerate(records):
                            try:
                                # Adaptar campos del frontend (JS) al backend (Python)
                                # El JS guarda campos como 'nombre', 'motivo', etc.
                                # El backend espera estructura de TriageRecord o similar.
                                
                                # Mapeo básico
                                paciente_data = {
                                    "nombre": record.get("nombre", "Desconocido"),
                                    "edad": int(record.get("edad", 0)) if record.get("edad") else None,
                                    "motivo": record.get("motivo", ""),
                                    "signos_vitales": {
                                        "fc": int(record.get("fc")) if record.get("fc") else None,
                                        "sato2": int(record.get("sat")) if record.get("sat") else None,
                                        "tas": int(record.get("tas")) if record.get("tas") else None,
                                    },
                                    "offline_id": record.get("id"),
                                    "timestamp_offline": record.get("timestamp")
                                }
                                
                                # Usar TriageService para crear el caso
                                # Nota: Esto creará un nuevo registro. 
                                # Idealmente deberíamos marcarlo como 'importado_offline'
                                
                                # Simulamos creación directa por ahora para no complicar con dependencias
                                # En producción usaríamos TriageService.create_triage(...)
                                
                                # Guardamos en DB directamente para asegurar integridad
                                # Asumiendo que tenemos un repositorio o servicio disponible
                                
                                # Opción A: Usar create_triage_record (repo)
                                # Necesitamos construir el objeto completo.
                                
                                # Opción B: Guardar como "Borrador" o "Pendiente de Clasificación"
                                # Vamos a guardarlo como un registro básico para que aparezca en Auditoría/Triaje
                                
                                # Enriquecer datos
                                new_record = {
                                    "paciente": {
                                        "nombre": paciente_data["nombre"],
                                        "edad": paciente_data["edad"]
                                    },
                                    "motivo_consulta": paciente_data["motivo"],
                                    "signos_vitales": paciente_data["signos_vitales"],
                                    "source": "offline_sync",
                                    "created_at": datetime.now(),
                                    "status": "pending_triage" # Para que salga en la lista de pendientes
                                }
                                
                                # Insertar en DB (usando repo genérico o específico)
                                # Por simplicidad y robustez, usamos la colección 'triage_records' directamente via repo
                                repo = get_triage_repository()
                                result = repo.create(new_record)
                                
                                if result:
                                    success_count += 1
                                
                            except Exception as e:
                                errors.append(f"Reg {i+1}: {str(e)}")
                            
                            progress_bar.progress((i + 1) / len(records))
                            
                        if success_count > 0:
                            st.success(f"✅ {success_count} registros sincronizados correctamente.")
                            time.sleep(1)
                            # Opcional: Limpiar uploader
                            
                        if errors:
                            with st.expander("Errores de sincronización"):
                                for err in errors:
                                    st.error(err)
                                    
            except json.JSONDecodeError:
                st.error("Error al leer el archivo JSON.")
            except Exception as e:
                st.error(f"Error inesperado: {str(e)}")
