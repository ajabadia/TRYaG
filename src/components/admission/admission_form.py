# path: src/components/admission/admission_form.py
# Creado: 2025-11-24
"""
Formulario de admisión de pacientes con búsqueda automática y selección de sala mediante grid.
Se permite overbooking (plazas disponibles pueden ser negativas).
"""
import streamlit as st
from datetime import datetime, date
from typing import Dict, Any

# Servicios internos (importes relativos)
from services.patient_service import (
    buscar_paciente_existente,
    crear_paciente,
    actualizar_paciente_con_auditoria,
    validar_documento,
    calcular_edad,
)
from services.patient_flow_service import (
    crear_flujo_paciente,
    asignar_sala_triaje,
    rechazar_paciente,
    obtener_flujo_activo,
    reassign_patient_flow,
)
from ui.config_panel import load_centro_config, save_centro_config
from utils.icons import render_icon


from services.room_service import obtener_salas_por_tipo


def render_admission_form():
    """Renderiza el formulario completo de admisión de pacientes."""
    st.header("Admisión de Pacientes")

    # ---------- Estado de sesión ----------
    if 'admission_patient_data' not in st.session_state:
        st.session_state.admission_patient_data = None
    if 'admission_validated' not in st.session_state:
        st.session_state.admission_validated = False
    if 'admission_patient_code' not in st.session_state:
        st.session_state.admission_patient_code = None
    if 'sala_admision_selected' not in st.session_state:
        st.session_state.sala_admision_selected = None

    # ---------- Paso 1: Selección de Sala de Admisión (GRID) ----------
    st.subheader("1. Sala de Admisión")
    salas_adm = obtener_salas_por_tipo("admision")
    if not salas_adm:
        st.warning("No hay salas de admisión configuradas.")
        return

    # Mostrar grid (3 columnas por fila)
    cols_per_row = 3
    rows = (len(salas_adm) + cols_per_row - 1) // cols_per_row
    for r in range(rows):
        cols = st.columns(cols_per_row)
        for c_idx in range(cols_per_row):
            idx = r * cols_per_row + c_idx
            if idx >= len(salas_adm):
                break
            sala = salas_adm[idx]
            with cols[c_idx]:
                st.markdown(f"**{sala.get('nombre','')}**")
                st.caption(sala['label'])
                # Botón de selección (solo uno activo)
                if st.button("Seleccionar", key=f"sel_{sala.get('codigo')}"):
                    st.session_state.sala_admision_selected = sala.get('codigo')
    # Si no se ha seleccionado, detener flujo
    if not st.session_state.sala_admision_selected:
        st.info("Seleccione una sala de admisión para continuar.")
        return
    sala_admision_code = st.session_state.sala_admision_selected
    st.success(f"Sala seleccionada: {sala_admision_code}")
    st.divider()

    # ---------- Paso 2: Datos del Paciente ----------
    st.subheader("2. Datos del Paciente")
    # Búsqueda automática
    col_search_title, col_search_icon = st.columns([10, 0.5])
    with col_search_title:
        st.markdown("**Búsqueda Automática**")
    with col_search_icon:
        render_icon("search", size=20)
    st.caption("Introduzca SS o ID para buscar pacientes existentes")
    col_ss, col_id_tipo, col_id_num = st.columns([2, 1, 2])
    with col_ss:
        num_ss_input = st.text_input(
            "Número Seguridad Social (12 dígitos)", max_chars=12, key="num_ss_input"
        )
    with col_id_tipo:
        tipo_id_input = st.selectbox(
            "Tipo Identificación", options=["DNI", "NIE", "PASAPORTE"], key="tipo_id_input"
        )
    with col_id_num:
        num_id_input = st.text_input(
            f"Número {tipo_id_input}", key="num_id_input"
        ).upper()
    # Botón buscar
    if st.button("🔍 Buscar Paciente", use_container_width=True):
        if not num_ss_input and not num_id_input:
            st.error("Debe proporcionar SS o ID.")
        else:
            paciente = buscar_paciente_existente(
                num_ss=num_ss_input if num_ss_input else None,
                num_identificacion=num_id_input if num_id_input else None,
            )
            if paciente:
                st.session_state.admission_patient_data = paciente
                st.session_state.admission_validated = False
                # Actualizar los inputs del formulario explícitamente
                st.session_state['nombre_input'] = paciente['nombre']
                st.session_state['apellido1_input'] = paciente['apellido1']
                st.session_state['apellido2_input'] = paciente.get('apellido2', '')
                # Fecha de nacimiento: convertir datetime a date si es necesario
                fnac = paciente['fecha_nacimiento']
                if isinstance(fnac, datetime):
                    fnac = fnac.date()
                st.session_state['fecha_nac_input'] = fnac
                
                st.success(f"✅ Paciente encontrado: {paciente['patient_code']}")
            else:
                st.session_state.admission_patient_data = None
                st.session_state.edit_patient = True # Enable editing for new patient
                # Limpiar inputs para nuevo paciente
                st.session_state['nombre_input'] = ""
                st.session_state['apellido1_input'] = ""
                st.session_state['apellido2_input'] = ""
                st.session_state['fecha_nac_input'] = date(1990, 1, 1)
                
                st.info("ℹ️ No se encontró paciente, se creará uno nuevo.")
    st.divider()

    # ---------- Formulario de datos (read‑only / edit) ----------
    # Ensure flags exist
    if 'edit_patient' not in st.session_state:
        st.session_state.edit_patient = False
    edit_mode = st.session_state.edit_patient

    paciente_data = st.session_state.get('admission_patient_data')

    # ---------- Inicialización de inputs en Session State ----------
    if 'nombre_input' not in st.session_state:
        st.session_state.nombre_input = ""
    if 'apellido1_input' not in st.session_state:
        st.session_state.apellido1_input = ""
    if 'apellido2_input' not in st.session_state:
        st.session_state.apellido2_input = ""
    if 'fecha_nac_input' not in st.session_state:
        st.session_state.fecha_nac_input = date(1990, 1, 1)

    # If a patient is loaded and we are not in edit mode, show an Edit button
    if paciente_data and not edit_mode:
        if st.button("✏️ Editar datos", key="edit_btn"):
            st.session_state.edit_patient = True
            edit_mode = True

    col_nombre, col_ap1, col_ap2 = st.columns(3)
    with col_nombre:
        nombre = st.text_input(
            "Nombre *",
            key="nombre_input",
            disabled=not edit_mode,
        )
    with col_ap1:
        apellido1 = st.text_input(
            "Primer Apellido *",
            key="apellido1_input",
            disabled=not edit_mode,
        )
    with col_ap2:
        apellido2 = st.text_input(
            "Segundo Apellido",
            key="apellido2_input",
            disabled=not edit_mode,
        )
    # Fecha de nacimiento (editable only in edit mode)
    fecha_nacimiento = st.date_input(
        "Fecha de Nacimiento *",
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        key="fecha_nac_input",
        disabled=not edit_mode,
    )
    if fecha_nacimiento:
        edad = calcular_edad(datetime.combine(fecha_nacimiento, datetime.min.time()))
        st.caption(f"Edad: {edad} años")
    # Mostrar SS e ID como solo lectura (si hay paciente)
    if paciente_data:
        st.caption(f"**Número SS:** {paciente_data.get('num_ss', '')}")
        st.caption(f"**Identificación ({paciente_data.get('tipo_identificacion','')})**: {paciente_data.get('num_identificacion','')}")
    else:
        # No patient loaded – fields will be entered via search above
        pass
    st.divider()

    # ---------- Paso 3: Validación ----------
    st.subheader("3. Validación")
    if st.button("✓ Validar Datos", type="primary", use_container_width=True):
        errores = []
        if not nombre.strip():
            errores.append("Nombre obligatorio")
        if not apellido1.strip():
            errores.append("Primer apellido obligatorio")
        if not fecha_nacimiento:
            errores.append("Fecha de nacimiento obligatoria")
        if not num_id_input:
            errores.append("Número de identificación obligatorio")
        else:
            ok, msg = validar_documento(num_id_input, tipo_id_input)
            if not ok:
                errores.append(msg)
        if num_ss_input and (not num_ss_input.isdigit() or len(num_ss_input) != 12):
            errores.append("SS debe ser 12 dígitos")
        if errores:
            for e in errores:
                st.error(f"❌ {e}")
        else:
            # Crear o actualizar paciente
            try:
                if paciente_data:
                    # Si hubo cambios, actualizar con auditoría
                    cambios = (
                        nombre.strip() != paciente_data['nombre']
                        or apellido1.strip() != paciente_data['apellido1']
                        or apellido2.strip() != paciente_data.get('apellido2', '')
                    )
                    if cambios:
                        nuevo = actualizar_paciente_con_auditoria(
                            patient_code_anterior=paciente_data['patient_code'],
                            nombre=nombre.strip(),
                            apellido1=apellido1.strip(),
                            apellido2=apellido2.strip() if apellido2 else None,
                            fecha_nacimiento=datetime.combine(fecha_nacimiento, datetime.min.time()),
                            num_ss=num_ss_input if num_ss_input else None,
                            num_identificacion=num_id_input,
                            tipo_identificacion=tipo_id_input,
                        )
                        st.session_state.admission_patient_code = nuevo['patient_code']
                        st.success(f"✅ Paciente actualizado. Nuevo código: `{nuevo['patient_code']}`")
                    else:
                        st.session_state.admission_patient_code = paciente_data['patient_code']
                        st.success(f"✅ Datos validados. Código: `{paciente_data['patient_code']}`")
                else:
                    nuevo = crear_paciente(
                        nombre=nombre.strip(),
                        apellido1=apellido1.strip(),
                        apellido2=apellido2.strip() if apellido2 else None,
                        fecha_nacimiento=datetime.combine(fecha_nacimiento, datetime.min.time()),
                        num_ss=num_ss_input if num_ss_input else None,
                        num_identificacion=num_id_input,
                        tipo_identificacion=tipo_id_input,
                    )
                    st.session_state.admission_patient_code = nuevo['patient_code']
                    st.success(f"✅ Paciente creado. Código: `{nuevo['patient_code']}`")
                st.session_state.admission_validated = True
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    # Si aún no está validado, detener
    if not st.session_state.admission_validated:
        return
    st.divider()

    # ---------- Paso 4: Selección de Sala de Triaje (cards) ----------
    st.subheader("4. Sala de Triaje")
    salas_triaje = obtener_salas_por_tipo("triaje")
    if not salas_triaje:
        st.warning("No hay salas de triaje configuradas.")
        return
    # Mostrar como cards (3 columnas por fila)
    cols_per_row = 3
    rows = (len(salas_triaje) + cols_per_row - 1) // cols_per_row
    if 'sala_triaje_selected' not in st.session_state:
        st.session_state.sala_triaje_selected = None
    for r in range(rows):
        cols = st.columns(cols_per_row)
        for c_idx in range(cols_per_row):
            idx = r * cols_per_row + c_idx
            if idx >= len(salas_triaje):
                break
            sala = salas_triaje[idx]
            with cols[c_idx]:
                st.markdown(f"**{sala.get('nombre','')}**")
                st.caption(sala['label'])
                if st.button("Seleccionar", key=f"triaje_sel_{sala.get('codigo')}"):
                    st.session_state.sala_triaje_selected = sala.get('codigo')
    if not st.session_state.sala_triaje_selected:
        st.info("Seleccione una sala de triaje para continuar.")
        return
    sala_triaje_code = st.session_state.sala_triaje_selected
    st.success(f"Sala de triaje seleccionada: {sala_triaje_code}")
    st.divider()

    # ---------- Paso 5: Confirmar / Rechazar ----------
    st.subheader("5. Confirmar Admisión")

    # Estados locales de UI para este paso
    if 'admission_complete' not in st.session_state:
        st.session_state.admission_complete = False
    if 'rejection_mode' not in st.session_state:
        st.session_state.rejection_mode = False

    # Si ya se completó la admisión (éxito o rechazo), mostrar resumen y botón de reinicio
    if st.session_state.admission_complete:
        if st.session_state.get('admission_success'):
            st.success("✅ Paciente registrado y enviado a triaje correctamente.")
            with st.expander("📄 Resumen de Admisión", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Paciente:** {nombre} {apellido1} {apellido2 or ''}")
                    st.markdown(f"**Código:** `{st.session_state.admission_patient_code}`")
                    st.markdown(f"**Edad:** {edad} años")
                with col2:
                    st.markdown(f"**Sala Admisión:** {sala_admision_code}")
                    st.markdown(f"**Sala Triaje:** {sala_triaje_code}")
                    st.markdown("**Estado:** EN_ESPERA_TRIAJE")
        elif st.session_state.get('rejection_success'):
            st.warning("🚫 Paciente rechazado correctamente.")
            st.markdown(f"**Motivo:** {st.session_state.get('rejection_reason', 'No especificado')}")

        if st.button("🔄 Nueva Admisión", type="primary", use_container_width=True):
            # Limpiar todo el estado de admisión
            keys_to_clear = [
                "admission_patient_data", "admission_validated", "admission_patient_code",
                "sala_admision_selected", "sala_triaje_selected", "admission_complete",
                "admission_success", "rejection_success", "rejection_mode", "rejection_reason",
                "nombre_input", "apellido1_input", "apellido2_input", "fecha_nac_input",
                "num_ss_input", "num_id_input", "edit_patient"
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        return

    # Si estamos en modo rechazo
    if st.session_state.rejection_mode:
        st.warning("Proceso de rechazo de paciente")
        motivo = st.text_input("Motivo del rechazo *", key="motivo_rechazo_input")
        col_confirm_rech, col_cancel_rech = st.columns(2)
        with col_confirm_rech:
            if st.button("Confirmar Rechazo", type="primary", use_container_width=True):
                if not motivo:
                    st.error("Debe especificar un motivo.")
                else:
                    try:
                        rechazar_paciente(st.session_state.admission_patient_code, motivo)
                        # Crear registro de rechazo
                        crear_flujo_paciente(
                            patient_code=st.session_state.admission_patient_code,
                            sala_admision_code=sala_admision_code,
                            sala_triaje_code="RECHAZO",
                        )
                        st.session_state.admission_complete = True
                        st.session_state.rejection_success = True
                        st.session_state.rejection_reason = motivo
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al rechazar: {str(e)}")
        with col_cancel_rech:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.rejection_mode = False
                st.rerun()
        return

    # Botones principales de acción
    col_conf, col_rech = st.columns([1, 1])
    with col_conf:
        if st.button("📋 Registrar y Enviar a Triaje", type="primary", use_container_width=True):
            # Verificar si ya tiene flujo activo
            flujo_activo = obtener_flujo_activo(st.session_state.admission_patient_code)
            if flujo_activo:
                st.warning(f"⚠️ El paciente ya tiene un proceso activo en sala: {flujo_activo.get('sala_triaje_code') or flujo_activo.get('sala_admision_code')}")
                # Aquí podríamos manejar la reasignación, pero por simplicidad y robustez, 
                # pedimos resolverlo antes o mostramos error.
                # Para este fix, mostramos el error y no avanzamos.
                st.error("No se puede registrar: Paciente ya activo.")
            else:
                try:
                    crear_flujo_paciente(
                        patient_code=st.session_state.admission_patient_code,
                        sala_admision_code=sala_admision_code,
                        sala_triaje_code=sala_triaje_code,
                    )
                    st.session_state.admission_complete = True
                    st.session_state.admission_success = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al registrar: {str(e)}")

    with col_rech:
        if st.button("🚫 Rechazar Paciente", type="secondary", use_container_width=True):
            st.session_state.rejection_mode = True
            st.rerun()

# Fin del archivo
