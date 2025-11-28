# path: src/ui/config/salas_manager.py
# Creado: 2025-11-25
"""
UI para gestión de salas con grid responsive y guardado individual.
Modular y reutilizable.
"""
import streamlit as st
from datetime import datetime
from db.repositories.salas import (
    get_all_salas,
    get_salas_by_tipo,
    save_sala,
    delete_sala,
)

# Colores por tipo (para UI)
TYPE_COLORS = {
    "admision": "#28a745",
    "triaje": "#17a2b8",
    "box": "#ffc107",
    "consulta": "#6c757d",
}


def render_sala_card(sala: dict):
    """Renderiza una tarjeta de sala con acciones de edición y borrado."""
    tipo = sala.get("tipo", "sin_tipo")
    color = TYPE_COLORS.get(tipo, "#6c757d")
    
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"<h4 style='color:{color};margin:0;'>{sala.get('codigo', '-')}: {sala.get('nombre', '-')}</h4>", unsafe_allow_html=True)
            st.caption(f"Tipo: {tipo} • Subtipo: {sala.get('subtipo', '-')}")
            st.caption(f"Capacidad: {sala.get('capacidad', '-')}, Activa: {sala.get('activa', True)}")
        with col2:
            if st.button("✏️", key=f"edit_{sala.get('codigo')}"):
                edit_sala_dialog(sala)
            if st.button("🗑️", key=f"del_{sala.get('codigo')}"):
                if st.confirm(f"¿Eliminar la sala {sala.get('codigo')}?"):
                    if delete_sala(sala.get('codigo')):
                        st.success("Sala eliminada")
                        st.rerun()
                    else:
                        st.error("Error al eliminar")
        st.divider()



@st.dialog("Editar Sala", width="large")
def edit_sala_dialog(sala: dict):
    """Muestra un modal para editar los campos de la sala."""
    # Si es nueva sala (sin código), permitir editar código
    is_new = not sala.get('codigo')
    
    with st.form(key=f"form_sala_{sala.get('codigo', 'new')}"):
        if is_new:
            codigo = st.text_input("Código", value="", help="Código único de la sala (ej: ADM-01)")
        else:
            codigo = st.text_input("Código", value=sala.get('codigo', ''), disabled=True)
            
        nombre = st.text_input("Nombre", value=sala.get('nombre', ''))
        tipo = st.selectbox("Tipo", options=list(TYPE_COLORS.keys()), index=list(TYPE_COLORS.keys()).index(sala.get('tipo', 'admision')))
        subtipo = st.selectbox("Subtipo", options=["atención", "espera"], index=["atención", "espera"].index(sala.get('subtipo', 'atención')) if sala.get('subtipo') in ["atención", "espera"] else 0)
        capacidad = st.number_input("Capacidad", min_value=1, max_value=500, value=sala.get('capacidad', 1))
        activa = st.checkbox("Activa", value=sala.get('activa', True))
        
        if st.form_submit_button("💾 Guardar Cambios"):
            if is_new and not codigo:
                st.error("El código es obligatorio")
                return

            updated = {
                "codigo": codigo,
                "nombre": nombre,
                "tipo": tipo,
                "subtipo": subtipo,
                "capacidad": capacidad,
                "activa": activa,
                "updated_at": datetime.now()
            }
            if save_sala(updated):
                st.success("Sala guardada")
                st.rerun()
            else:
                st.error("Error al guardar")



def render_salas_manager(existing_salas: list = None):
    """Componente principal que muestra todas las salas.
    Si se proporciona `existing_salas` (lista de dicts) se usa esa lista,
    de lo contrario se obtienen las salas desde la base de datos.
    """
    st.markdown("### 🏢 Gestión de Salas")
    st.caption("Vista en grid por tipo de sala, con edición y borrado individual.")
    
    # Botón para crear nueva sala
    if st.button("➕ Añadir Sala", type="primary"):
        edit_sala_dialog({"codigo": "", "nombre": "", "tipo": "admision", "subtipo": "", "capacidad": 1, "activa": True})
    
    # Obtener salas
    if existing_salas is None:
        all_salas = get_all_salas()
    else:
        all_salas = existing_salas
    
    # Deduplicar salas por código para evitar errores de claves duplicadas
    # Se usa un diccionario para mantener la última versión encontrada de cada código
    unique_salas = {}
    for s in all_salas:
        code = s.get('codigo')
        if code:
            unique_salas[code] = s
    all_salas = list(unique_salas.values())
    
    tipos = sorted({s.get('tipo', 'sin_tipo') for s in all_salas})
    for tipo in tipos:
        st.subheader(f"{tipo.title()}")
        salas_tipo = [s for s in all_salas if s.get('tipo') == tipo]
        for sala in salas_tipo:
            render_sala_card(sala)
