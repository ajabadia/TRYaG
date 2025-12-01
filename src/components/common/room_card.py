# path: src/components/common/room_card.py
# Creado: 2025-11-24
# Actualizado: 2025-11-26 - Integrado servicio unificado de asignación de personal
"""
Componente reutilizable para mostrar cards de salas con información de ocupación.
"""
import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime
from services.patient_flow_service import obtener_pacientes_en_espera
from services.staff_assignment_service import get_room_staff
from db.repositories.funciones import get_funcion_by_code

from utils.ui_utils import get_room_color

def render_assigned_users(sala_code: str):
    """
    Renderiza usuarios asignados a la sala.
    Considera tanto asignaciones fijas como turnos temporales.
    """
    # Usar servicio unificado que resuelve prioridad entre turnos y asignación fija
    staff = get_room_staff(sala_code)
    
    if staff:
        st.markdown("---")
        st.markdown("**👥 Personal Asignado:**")
        for user in staff:
            # Badge con función y nombre
            funciones = user.get("funciones", [])
            main_func = funciones[0] if funciones else "unknown"
            func_def = get_funcion_by_code(main_func)
            
            color = func_def["color"] if func_def else "#6c757d"
            
            # Indicador de tipo de asignación
            assignment_type = user.get("assignment_type", "fija")
            type_badge = "🕐" if assignment_type == "turno" else "📌"
            type_text = "Turno" if assignment_type == "turno" else "Fija"
            
            # Usamos HTML para un badge compacto
            st.markdown(
                f"""
                <div style="
                    display: flex; 
                    align-items: center; 
                    gap: 8px; 
                    background-color: rgba(0,0,0,0.05); 
                    padding: 4px 8px; 
                    border-radius: 4px; 
                    margin-bottom: 4px;
                    font-size: 0.85rem;">
                    <span style="color: {color}; font-size: 1.2em;">●</span>
                    <span style="font-weight: 500;">{user.get('nombre_completo', 'Sin nombre')}</span>
                    <span style="color: #666; font-size: 0.8em;">({main_func.capitalize()})</span>
                    <span style="margin-left: auto; font-size: 0.75em; opacity: 0.7;" title="{type_text}">{type_badge}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

def render_room_card(
    sala: Dict[str, Any],
    is_selected: bool,
    button_key: str,
    on_select_callback: Optional[callable] = None,
    show_select_button: bool = True,
    button_label_selected: str = "Seleccionada",
    button_label_unselected: str = "Seleccionar",
    pacientes: Optional[list] = None,
    render_patient_func: Optional[callable] = None
) -> bool:
    """
    Renderiza una card de sala con información de ocupación y lista de pacientes.
    
    Args:
        sala: Diccionario con información de la sala
        is_selected: Si la sala está actualmente seleccionada
        button_key: Key única para el botón de Streamlit
        on_select_callback: Función a ejecutar cuando se selecciona (opcional)
        show_select_button: Si mostrar el botón de selección
        button_label_selected: Etiqueta del botón cuando está seleccionada
        button_label_unselected: Etiqueta del botón cuando no está seleccionada
        pacientes: Lista de pacientes (opcional, si no se pasa se busca en servicio)
        render_patient_func: Función para renderizar cada paciente (opcional)
    
    Returns:
        bool: True si se pulsó el botón de selección, False en caso contrario
    """
    # Obtener información de la sala
    codigo = sala.get('codigo', '')
    nombre = sala.get('nombre', '')
    plazas_totales = sala.get('plazas', 0)
    tipo = sala.get('tipo', 'sin_tipo')
    
    # Obtener color
    color = get_room_color(tipo)
    
    # Obtener pacientes en la sala
    if pacientes is None:
        pacientes_en_sala = obtener_pacientes_en_espera(codigo)
    else:
        pacientes_en_sala = pacientes
        
    num_pacientes = len(pacientes_en_sala)
    
    # Calcular plazas libres
    plazas_libres = max(0, plazas_totales - num_pacientes)
    
    # Determinar si la sala está llena
    sala_llena = plazas_libres == 0
    
    # Card de la sala
    with st.container(border=True):
        # Título de la sala con color
        if is_selected:
            st.markdown(f"#### <span style='color:{color}'>✓ {nombre}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"#### <span style='color:{color}'>{nombre}</span>", unsafe_allow_html=True)
        
        # Código de la sala
        st.caption(f"**Código:** {codigo}")
        
        # Mostrar Tipo y Subtipo
        tipo_lbl = sala.get('tipo', '').replace('_', ' ').title()
        subtipo_lbl = sala.get('subtipo', '').replace('_', ' ').title()
        
        if subtipo_lbl:
            st.caption(f"🏷️ {tipo_lbl} • {subtipo_lbl}")
        else:
            st.caption(f"🏷️ {tipo_lbl}")
        
        st.divider()
        
        # Información de ocupación
        col_plazas, col_pacientes = st.columns(2)
        with col_plazas:
            if sala_llena:
                st.error(f"**Plazas:** {plazas_libres}/{plazas_totales}")
            elif plazas_libres <= 2:
                st.warning(f"**Plazas:** {plazas_libres}/{plazas_totales}")
            else:
                st.info(f"**Plazas:** {plazas_libres}/{plazas_totales}")
        
        with col_pacientes:
            st.metric("En sala", num_pacientes)
            
        # Mostrar usuarios asignados
        render_assigned_users(codigo)
        
        # Lista de pacientes si hay
        if pacientes_en_sala:
            st.markdown("---")
            st.markdown(f"**👥 Pacientes ({num_pacientes}):**")
            
            # Si hay muchos pacientes, usamos expander para no alargar demasiado la card
            # Si son pocos (ej. < 3), mostramos directo
            container_wrapper = st.container()
            if num_pacientes > 3:
                container_wrapper = st.expander("Ver lista completa", expanded=False)
            
            with container_wrapper:
                for p in pacientes_en_sala:
                    # Si se pasa una función de renderizado custom (Control Tower)
                    if render_patient_func:
                        render_patient_func(p, codigo)
                        continue

                    # Lógica estándar de visualización unificada
                    from ui.components.common.patient_card import render_patient_card
                    
                    render_patient_card(
                        patient=p,
                        show_triage_level=True,
                        show_wait_time=True,
                        show_location=False,
                        is_in_room=True,
                        key_prefix=f"room_{codigo}"
                    )
        else:
            st.markdown("---")
            st.caption("_Sala vacía_")
        
        # Botón de selección
        button_clicked = False
        if show_select_button:
            button_type = "primary" if is_selected else "secondary"
            button_label = button_label_selected if is_selected else button_label_unselected
            
            # Deshabilitar si está seleccionada o si está llena
            is_disabled = is_selected or sala_llena
            
            if st.button(button_label, key=button_key, 
                       type=button_type, disabled=is_disabled, use_container_width=True):
                button_clicked = True
                if on_select_callback:
                    on_select_callback(codigo)
            
            # Advertencia si está llena
            if sala_llena and not is_selected:
                st.error("🚫 Sala llena - No disponible")
        
        st.markdown('<div style="color: #ccc; font-size: 0.6em; text-align: right; margin-top: 5px;">src/components/common/room_card.py</div>', unsafe_allow_html=True)
    
    return button_clicked


def render_room_grid(
    salas: list,
    selected_code: Optional[str],
    button_key_prefix: str,
    on_select_callback: Optional[callable] = None,
    cols_per_row: int = 2,
    **card_kwargs
) -> Optional[str]:
    """
    Renderiza un grid de cards de salas.
    
    Args:
        salas: Lista de salas a mostrar
        selected_code: Código de la sala seleccionada (si hay)
        button_key_prefix: Prefijo para las keys de los botones
        on_select_callback: Función a ejecutar cuando se selecciona una sala
        cols_per_row: Número de columnas por fila
        **card_kwargs: Argumentos adicionales para render_room_card
    
    Returns:
        str: Código de la sala seleccionada si se pulsó algún botón, None en caso contrario
    """
    rows = (len(salas) + cols_per_row - 1) // cols_per_row
    
    selected_sala_code = None
    
    for row_idx in range(rows):
        cols = st.columns(cols_per_row)
        start_idx = row_idx * cols_per_row
        end_idx = min(start_idx + cols_per_row, len(salas))
        
        for col_idx, sala in enumerate(salas[start_idx:end_idx]):
            with cols[col_idx]:
                sala_code = sala.get('codigo')
                is_selected = (sala_code == selected_code)
                
                button_clicked = render_room_card(
                    sala=sala,
                    is_selected=is_selected,
                    button_key=f"{button_key_prefix}_{sala_code}",
                    on_select_callback=on_select_callback,
                    **card_kwargs
                )
                
                if button_clicked:
                    selected_sala_code = sala_code
    
    return selected_sala_code
