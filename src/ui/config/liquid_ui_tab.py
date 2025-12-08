import streamlit as st
import pandas as pd
from db.repositories.ui_rules_repository import get_ui_rules_repository
from db.models_rules import UIRule, RuleCondition, RuleAction, LogicOperator, ConditionOperator, ActionType, RuleStatus
from services.dynamic_ui_rules_engine import DynamicRulesEngine

def render_liquid_ui_tab():
    repo = get_ui_rules_repository()
    
    st.title("🧩 Gestión de Interface Líquida (Dynamic Rules)")
    st.info("Define reglas para que la interfaz se adapte automáticamente al contexto del paciente.")

    # --- LISTADO DE REGLAS ---
    rules = repo.get_all_rules()

    if not rules:
        st.warning("⚠️ No se han encontrado reglas en la base de datos.")
        if st.button("🔄 Cargar Reglas por Defecto (Migración Inicial)"):
            # Instantiating the engine triggers the auto-migration check
            DynamicRulesEngine() 
            st.success("Reglas cargadas correctamente. Recarga la página.")
            st.rerun()
    
    # KPIs Rápidos
    c1, c2, c3 = st.columns(3)
    c1.metric("Reglas Totales", len(rules))
    c2.metric("Activas", len([r for r in rules if r.status == RuleStatus.ACTIVE]))
    c3.metric("Borradores", len([r for r in rules if r.status == RuleStatus.DRAFT]))

    st.divider()

    # Selector de Regla para Editar / Nueva
    rule_options = {f"{r.name} (v{r.version}) {'🟢' if r.status==RuleStatus.ACTIVE else '⚪'}": r.id for r in rules}
    rule_options["➕ Crear Nueva Regla"] = "new"
    
    selected_label = st.selectbox("Seleccionar Regla", list(rule_options.keys()))
    selected_id = rule_options[selected_label]

    if selected_id == "new":
        st.subheader("Nueva Regla")
        with st.form("new_rule_form"):
            new_name = st.text_input("Nombre de la Regla", placeholder="Ej: Alerta Ébola")
            new_desc = st.text_area("Descripción")
            
            if st.form_submit_button("Crear Borrador"):
                new_rule = UIRule(
                    name=new_name,
                    description=new_desc,
                    conditions=RuleCondition(logic=LogicOperator.AND, rules=[]),
                    actions=[]
                )
                repo.create_rule(new_rule)
                st.success("Regla creada!")
                st.rerun()
    else:
        # --- EDICIÓN DE REGLA EXISTENTE ---
        rule = repo.get_rule_by_id(selected_id)
        if not rule:
            st.error("Error cargando regla.")
            return

        c_edit_1, c_edit_2 = st.columns([3, 1])
        with c_edit_1:
            st.subheader(f"Editando: {rule.name}")
        with c_edit_2:
            current_status = rule.status
            if current_status == RuleStatus.DRAFT:
                if st.button("🚀 Publicar", type="primary"):
                    repo.publish_version(rule.id)
                    st.success("Regla activada.")
                    st.rerun()
            elif current_status == RuleStatus.ACTIVE:
                if st.button("⏸️ Desactivar"):
                    repo.update_rule(rule.id, {"status": "DRAFT"}) # Back to draft
                    st.rerun()
        
        # Metadata Básica
        with st.expander("Metadatos", expanded=False):
            new_name_edit = st.text_input("Nombre", value=rule.name)
            new_desc_edit = st.text_area("Descripción", value=rule.description)
            if new_name_edit != rule.name or new_desc_edit != rule.description:
                if st.button("Guardar Cambios Meta"):
                    repo.update_rule(rule.id, {"name": new_name_edit, "description": new_desc_edit})
                    st.rerun()

        # --- CONSTRUCTOR DE CONDICIONES ---
        st.markdown("#### 1. Condiciones (Logic Builder)")
        st.caption("Define cuándo se activa esta regla. Soporta lógica anidada simple.")
        
        # Visualizer simplificado (solo nivel 1 por ahora para UI No-Code)
        # Para soporte completo anidado, se requeriría un componente recursivo complejo.
        # Aquí implementamos un editor plano de condiciones "AND" o "OR" de nivel superior.
        
        logic_op = st.radio("Lógica Global", [LogicOperator.AND.value, LogicOperator.OR.value], 
                          index=0 if rule.conditions.logic == LogicOperator.AND else 1,
                          horizontal=True, key=f"logic_{rule.id}")
        
        # Save logic change
        if logic_op != rule.conditions.logic:
             # Update logic operator
             repo.update_active_logic(rule.id, logic_op) # This method needs to exist or use update_rule manually
             # Como es un objeto anidado, actualizamos todo el objeto conditions
             updated_conditions = rule.conditions.model_dump()
             updated_conditions['logic'] = logic_op
             repo.update_rule(rule.id, {"conditions": updated_conditions})
             st.rerun()

        # Listado de Sub-reglas (solo nivel 1)
        if rule.conditions.rules is None:
             rule.conditions.rules = []
             
        for i, sub_rule in enumerate(rule.conditions.rules):
            with st.container(border=True):
                c_field, c_op, c_val, c_del = st.columns([3, 2, 3, 1])
                
                # Field
                # Retrieve available fields from DB
                from db.repositories.ui_fields_repository import get_ui_fields_repository
                fields_repo = get_ui_fields_repository()
                available_db_fields = fields_repo.get_all_fields()
                
                # Create friendly options: "Presión Arterial (vital_signs.bp)"
                field_options = {}
                for f in available_db_fields:
                    label = f.display_name.get('es', f.internal_name)
                    # Show help text in tooltip if possible? Streamlit selectbox doesn't support per-item tooltip easily.
                    # Just combine in label
                    option_label = f"{label} 🔹 {f.internal_name}"
                    field_options[option_label] = f.internal_name
                
                # Add current value if not in options (handling custom/legacy fields)
                current_field = sub_rule.field or ""
                current_label = next((k for k, v in field_options.items() if v == current_field), None)
                
                if current_field and not current_label:
                     # Custom/Unknown field
                     custom_label = f"{current_field} (Custom/Legacy)"
                     field_options[custom_label] = current_field
                     current_label = custom_label

                # Add option to type manual? 
                # For now, let's stick to Selectbox. If "Custom" is needed, we might need a toggle.
                # Let's add a special "✏️ Manual Input..." option? 
                # Simpler: Just allow selecting from list.
                
                with c_field:
                    # Sort options for better UX
                    sorted_labels = sorted(list(field_options.keys()))
                    if not sorted_labels:
                        sorted_labels = ["⚠️ No fields loaded"]
                        field_options["⚠️ No fields loaded"] = ""

                    # Ensure current is selected
                    idx = sorted_labels.index(current_label) if current_label in sorted_labels else 0
                    
                    selected_label_field = st.selectbox(f"Campo #{i+1}", sorted_labels, index=idx, key=f"field_{rule.id}_{i}", help="Selecciona un campo detectado o escribe uno nuevo si seleccionas 'Manual'")
                    new_field = field_options.get(selected_label_field, "")

                
                with c_op:
                    ops = [op.value for op in ConditionOperator]
                    current_op_idx = ops.index(sub_rule.operator) if sub_rule.operator in ops else 0
                    new_op = st.selectbox("Operador", ops, index=current_op_idx, key=f"op_{rule.id}_{i}", label_visibility="collapsed")
                
                with c_val:
                    # Intenta inferir tipo para input adecuado
                    val_val = sub_rule.value
                    if isinstance(val_val, (int, float)):
                        new_val = st.number_input("Valor", value=float(val_val), key=f"val_{rule.id}_{i}", label_visibility="collapsed")
                    else:
                        new_val = st.text_input("Valor", value=str(val_val) if val_val else "", key=f"val_{rule.id}_{i}", label_visibility="collapsed")
                
                with c_del:
                    if st.button("🗑️", key=f"del_{rule.id}_{i}"):
                        # Remove logic
                        updated_rules = rule.conditions.rules.copy()
                        updated_rules.pop(i)
                        updated_cond = rule.conditions.model_dump()
                        updated_cond['rules'] = [r.model_dump() for r in updated_rules] # Serializar
                        repo.update_rule(rule.id, {"conditions": updated_cond})
                        st.rerun()

                # Detect changes and save (auto-save on interaction ideally, but button here for simplicity)
                # This is tricky in Streamlit loops. 
                # Let's add a global "Guardar Condiciones" button below.

        if st.button("➕ Añadir Condición"):
            new_cond = RuleCondition(field="nuevo_campo", operator=ConditionOperator.EQUALS, value="valor")
            updated_rules = rule.conditions.rules.copy()
            updated_rules.append(new_cond)
            updated_cond = rule.conditions.model_dump()
            updated_cond['rules'] = [r.model_dump() for r in updated_rules]
            repo.update_rule(rule.id, {"conditions": updated_cond})
            st.rerun()

        # --- CONSTRUCTOR DE ACCIONES ---
        st.markdown("#### 2. Acciones (Efectos UI)")
        
        for i, action in enumerate(rule.actions):
             with st.container(border=True):
                c_act_type, c_act_detail, c_act_del = st.columns([2, 4, 1])
                
                with c_act_type:
                    st.caption(f"Acción #{i+1}")
                    st.write(f"**{action.type}**")
                
                with c_act_detail:
                    if action.type == ActionType.ALERT:
                        st.write(f"Level: `{action.level}`")
                        st.write(f"Msg: {action.message}")
                    elif action.type == ActionType.HIGHLIGHT:
                        st.write(f"Fields: {action.fields}")
                    elif action.type == ActionType.SUGGEST:
                        st.write(f"Protocol: {action.protocol}")
                
                with c_act_del:
                     if st.button("🗑️", key=f"del_act_{rule.id}_{i}"):
                        updated_actions = rule.actions.copy()
                        updated_actions.pop(i)
                        repo.update_rule(rule.id, {"actions": [a.model_dump() for a in updated_actions]})
                        st.rerun()
        
        # Formulario para añadir acción
        with st.expander("➕ Añadir Nueva Acción"):
            new_act_type = st.selectbox("Tipo", [t.value for t in ActionType], key="new_act_type")
            
            act_params = {}
            if new_act_type == ActionType.ALERT:
                act_params['level'] = st.selectbox("Nivel", ["info", "warning", "critical"])
                act_params['message'] = st.text_input("Mensaje Alerta")
            elif new_act_type == ActionType.HIGHLIGHT:
                act_params['fields'] = st.text_input("Campos (sep por coma)").split(',')
            elif new_act_type == ActionType.SUGGEST:
                act_params['protocol'] = st.text_input("Protocolo Sugerido")
            
            if st.button("Añadir Acción"):
                new_action_obj = RuleAction(type=new_act_type, **act_params)
                updated_actions = rule.actions.copy()
                updated_actions.append(new_action_obj)
                repo.update_rule(rule.id, {"actions": [a.model_dump() for a in updated_actions]})
                st.rerun()

        # JSON RAW VIEW
        with st.expander("🛠️ Debug JSON (Avanzado)"):
            st.json(rule.model_dump(by_alias=True))

    st.divider()
    with st.expander("⚙️ Mantenimiento de Campos (Field Discovery)", expanded=False):
        st.info("El sistema escanea automáticamente el código en busca de llamadas `st.input` para poblar el catálogo de campos.")
        
        from db.repositories.ui_fields_repository import get_ui_fields_repository
        f_repo = get_ui_fields_repository()
        total_fields = f_repo.collection.count_documents({})
        st.write(f"**Campos Registrados:** {total_fields}")
        
        if st.button("🔄 Escanear Código y Actualizar Campos"):
            with st.spinner("Analizando código fuente (AST)..."):
                from services.field_discovery_service import get_field_discovery_service
                svc = get_field_discovery_service()
                count = svc.scan_and_register_fields()
            st.success(f"Escaneo completado. {count} campos procesados.")
            st.rerun()

    # Footer Dev
    st.markdown('<div class="debug-footer">src/ui/config/liquid_ui_tab.py</div>', unsafe_allow_html=True)
