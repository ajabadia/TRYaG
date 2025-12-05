# Mapa de Archivos del Proyecto

Este documento lista los archivos principales del proyecto, su propósito y su estado.

| Ruta del Archivo | Descripción | Invocado Por | Estado |
| :--- | :--- | :--- | :--- |
| **src/app.py** | Punto de entrada principal. Configura Streamlit y el enrutamiento. | `streamlit run` | Activo |
| **src/core/config.py** | Configuraciones globales y constantes. | Varios | Activo |
| **src/ui/main_view.py** | Orquestador de la vista "Asistente de Triaje". | `src/app.py` | Activo |
| **src/ui/admission_view.py** | Vista principal de Admisión. | `src/app.py` | Activo |
| **src/ui/boxes_view.py** | Vista de Gestión de Boxes (Atención). | `src/app.py` | Activo |
| **src/ui/admission_management_view.py** | Vista de Gestión de Consultas. | `src/app.py` | Activo |
| **src/ui/config_panel.py** | Panel de Configuración del Centro. | `src/app.py` | Activo |
| **src/ui/room_orchestrator.py** | Vista de Control de Salas (Orquestador). | `src/app.py` | Activo |
| **src/ui/attention_view.py** | Vista de Atención (Boxes). | `src/app.py` | Activo |
| **src/ui/multi_center_dashboard.py** | Dashboard Multi-centro. | `src/app.py` | Activo |
| **src/ui/room_manager_view.py** | Vista de Gestión de Salas (Configuración/Estado). | `src/app.py` | Activo |
| **src/ui/room_metrics_dashboard.py** | Dashboard de Métricas de Salas. | `src/app.py` | Activo |
| **src/ui/audit_panel/main_panel_v2.py** | Versión 2 de panel principal. | `src/app.py` | Activo |
| **src/components/analytics/concordance_analysis.py** | Análisis de concordancia IA vs Humano. | `src/ui/audit_panel/analysis_panel.py` | Activo |
| **src/ui/config/asignacion_turnos.py** | UI para asignación de turnos. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/datos_generales.py** | UI para datos generales del centro. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/equipment_config.py** | UI para configuración de equipamiento. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/notification_config_ui.py** | UI para configuración de notificaciones. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/people_manager.py** | UI para gestión de personas (Staff). | `src/ui/config_panel.py` | Activo |
| **src/ui/config/roles_manager.py** | UI para gestión de roles. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/salas_manager.py** | UI para gestión de salas (CRUD). | `src/ui/config_panel.py` | Activo |
| **src/ui/config/staff_conflicts_viewer.py** | Visualizador de conflictos de personal. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/usuarios_manager.py** | UI para gestión de usuarios del sistema. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/vital_signs_config.py** | UI para configuración de rangos de signos vitales. | `src/ui/config/general_tab.py` | Activo |
| **src/ui/config/center_groups_manager.py** | UI para gestión de grupos de centros. | `src/ui/config/centro_tab.py` | Activo |
| **src/components/triage/input_form.py** | Formulario de entrada de datos (Triaje). | `src/components/triage/step_triage_process.py` | Activo |
| **src/components/triage/step_triage_process.py** | Paso de proceso de triaje. | `src/ui/main_view.py` | Activo |
| **src/components/triage/media_cards.py** | Tarjetas de visualización de medios. | `src/components/triage/input_form.py` | Activo |
| **src/components/triage/results_display.py** | Visualización de resultados de IA. | `src/components/triage/step_triage_process.py` | Activo |
| **src/components/triage/step_disposition.py** | Paso de disposición final. | `src/ui/main_view.py` | Activo |
| **src/components/triage/step_patient_selection.py** | Paso de selección de paciente. | `src/ui/main_view.py` | Activo |
| **src/components/triage/step_sala_selection.py** | Paso de selección de sala. | `src/ui/main_view.py` | Activo |
| **src/components/triage/validation_form.py** | Formulario de validación de datos. | `src/components/triage/step_triage_process.py` | Activo |
| **src/components/common/webcam_manager.py** | Componente reutilizable de webcam. | Varios | Activo |
| **src/components/common/audio_recorder.py** | Componente reutilizable de audio. | Varios | Activo |
| **src/components/common/file_importer.py** | Componente reutilizable de importación. | Varios | Activo |
| **src/components/common/feedback_button.py** | Botón de reporte de feedback. | Varios | Activo |
| **src/components/common/stepper.py** | Componente de navegación por pasos. | Vistas principales | Activo |
| **src/components/common/active_flow_manager.py** | Gestión de flujos activos. | Varios | Activo |
| **src/components/common/media_viewer.py** | Visor de medios (imágenes/PDF). | Varios | Activo |
| **src/components/common/patient_selection_card.py** | Tarjeta de selección de paciente. | Varios | Activo |
| **src/components/common/pwa_installer.py** | Componente de instalación PWA. | `src/app.py` | Activo |
| **src/components/common/rejection_form.py** | Formulario de rechazo de paciente. | Varios | Activo |
| **src/components/common/room_card.py** | Tarjeta de visualización de sala. | Varios | Activo |
| **src/components/common/user_selector.py** | Selector de usuario. | Varios | Activo |
| **src/components/config/prompt_editor.py** | Editor de prompts de sistema. | `src/ui/config_panel.py` | Activo |
| **src/db/connection.py** | Gestión de conexión a MongoDB. | Repositorios | Activo |
| **src/db/models.py** | Modelos Pydantic de datos. | Varios | Activo |
| **src/db/repositories/audit.py** | Repositorio de Auditoría. | Servicios/UI | Activo |
| **src/db/repositories/base.py** | Clase base para repositorios. | Repositorios | Activo |
| **src/db/repositories/centros.py** | Repositorio de Centros. | Servicios/UI | Activo |
| **src/db/repositories/config.py** | Repositorio de Configuración. | Servicios/UI | Activo |
| **src/db/repositories/files.py** | Repositorio de Archivos. | Servicios/UI | Activo |
| **src/db/repositories/funciones.py** | Repositorio de Funciones. | Servicios/UI | Activo |
| **src/db/repositories/notification_config.py** | Repositorio de Config. Notificaciones. | Servicios/UI | Activo |
| **src/db/repositories/people.py** | Repositorio de Personas. | Servicios/UI | Activo |
| **src/db/repositories/prompts.py** | Repositorio de Prompts. | Servicios/UI | Activo |
| **src/db/repositories/report_config.py** | Repositorio de Config. Reportes. | Servicios/UI | Activo |
| **src/db/repositories/roles.py** | Repositorio de Roles. | Servicios/UI | Activo |
| **src/db/repositories/salas.py** | Repositorio de Salas. | Servicios/UI | Activo |
| **src/db/repositories/tests.py** | Repositorio de Tests. | Servicios/UI | Activo |
| **src/db/repositories/transcriptions.py** | Repositorio de Transcripciones. | Servicios/UI | Activo |
| **src/db/repositories/triage.py** | Repositorio de Triaje. | Servicios/UI | Activo |
| **src/db/repositories/turnos.py** | Repositorio de Turnos. | Servicios/UI | Activo |
| **src/db/repositories/users.py** | Repositorio de Usuarios. | Servicios/UI | Activo |
| **src/db/repositories/center_groups.py** | Repositorio de Grupos de Centros. | Servicios/UI | Activo |
| **src/services/feedback_service.py** | Servicio de persistencia de feedback. | UI | Activo |
| **src/services/patient_service.py** | Gestión de pacientes (CRUD). | UI | Activo |
| **src/services/flow_manager.py** | Gestión del flujo de pacientes. | UI | Activo |
| **src/services/export_service.py** | Servicio de exportación de datos. | UI | Activo |
| **src/services/ml_predictive_service.py** | Servicio de predicciones ML. | UI | Activo |
| **src/services/notification_helpers.py** | Helpers para notificaciones. | Servicios | Activo |
| **src/services/notification_service.py** | Servicio de envío de notificaciones. | Varios | Activo |
| **src/services/patient_flow_service.py** | Servicio de flujo de pacientes (Lógica). | UI | Activo |
| **src/services/permissions_service.py** | Servicio de permisos y roles. | UI | Activo |
| **src/services/room_metrics_service.py** | Servicio de métricas de salas. | UI | Activo |
| **src/services/room_service.py** | Servicio de gestión de salas. | UI | Activo |
| **src/services/room_suggestion_service.py** | Servicio de sugerencia de salas. | UI | Activo |
| **src/services/scheduled_reports.py** | Servicio de reportes programados. | Background | Activo |
| **src/services/simulated_ia.py** | Simulación de respuesta IA. | UI | Activo |
| **src/services/staff_assignment_service.py** | Servicio de asignación de personal. | UI | Activo |
| **src/services/transcription_service.py** | Servicio de transcripción de audio. | UI | Activo |
| **src/services/triage_service.py** | Servicio de lógica de triaje. | UI | Activo |
| **src/services/recommendation_service.py** | Servicio de generación de recomendaciones. | `src/components/triage/risk_analysis_panel.py` | Activo |
| **src/services/ml_training_service.py** | Servicio de entrenamiento de modelos ML. | `src/ui/ml_predictions_panel.py` | Activo |
| **src/utils/file_handler.py** | Manejador de archivos (guardado/carga). | Varios | Activo |
| **src/utils/file_utils.py** | Utilidades generales de archivos. | Varios | Activo |
| **src/utils/icon_utils.py** | Utilidades para iconos. | UI | Activo |
| **src/utils/icons.py** | Definición de iconos. | UI | Activo |
| **src/utils/image_utils.py** | Procesamiento de imágenes. | Varios | Activo |
| **src/utils/patient_utils.py** | Utilidades para datos de pacientes. | Varios | Activo |
| **src/utils/pdf_utils.py** | Generación/Manejo de PDFs. | Varios | Activo |
| **src/utils/session_utils.py** | Manejo de sesión de Streamlit. | UI | Activo |
| **src/utils/setup_indexes.py** | Script de configuración de índices DB. | Setup | Activo |
| **src/components/admission/admission_form.py** | Formulario de admisión. | `src/ui/admission_view.py` | Activo |
| **src/components/admission/step_confirmation.py** | Paso de confirmación de admisión. | `src/ui/admission_view.py` | Activo |
| **src/components/admission/step_patient_data.py** | Paso de datos del paciente. | `src/ui/admission_view.py` | Activo |
| **src/components/admission/step_sala_admision.py** | Paso de selección de sala de admisión. | `src/ui/admission_view.py` | Activo |
| **src/components/admission/step_sala_triaje.py** | Paso de selección de sala de triaje. | `src/ui/admission_view.py` | Activo |
| **src/components/boxes/step_attention.py** | Paso de atención en box. | `src/ui/boxes_view.py` | Activo |
| **src/components/boxes/step_patient_selection.py** | Paso de selección de paciente en box. | `src/ui/boxes_view.py` | Activo |
| **src/components/boxes/step_sala_selection.py** | Paso de selección de sala en box. | `src/ui/boxes_view.py` | Activo |
| **src/core/data_handler.py** | Manejador de datos core. | Varios | Activo |
| **src/core/prompt_manager.py** | Gestor de prompts. | Varios | Activo |
| **src/core/transcription_handler.py** | Manejador de transcripciones. | Varios | Activo |
| **src/components/triage/admin_data_form.py** | Formulario de datos administrativos. | `src/components/triage/input_form.py` | Activo |
| **src/components/triage/clinical_context.py** | Formulario de contexto clínico. | `src/components/triage/input_form.py` | Activo |
| **src/components/triage/extended_history.py** | Historia clínica integral. | `src/components/triage/input_form.py` | Activo |
| **src/components/triage/guided_interview.py** | Entrevista guiada inteligente. | `src/components/triage/input_form.py` | Activo |
| **src/components/triage/hda_form.py** | Formulario de Historia de la Enfermedad Actual. | `src/components/triage/input_form.py` | Activo |
| **src/components/triage/nursing_form.py** | Valoración de enfermería. | `src/components/triage/step_triage_process.py` | Activo |
| **src/components/triage/patient_background_form.py** | Antecedentes del paciente. | `src/components/triage/input_form.py` | Activo |
| **src/components/triage/ptr_logic.py** | Lógica de Puntuación Total de Riesgo (PTR). | `src/components/triage/input_form.py` | Activo |
| **src/components/triage/risk_analysis_panel.py** | Panel de análisis de riesgos y alertas. | `src/components/triage/input_form.py` | Activo |
| **src/components/triage/step_final_disposition.py** | Paso de disposición final (Nuevo). | `src/ui/main_view.py` | Activo |
| **src/components/triage/triage_logic.py** | Lógica core de triaje (NEWS2, Worst Case). | `src/components/triage/input_form.py` | Activo |
| **src/components/triage/recommendations_card.py** | Tarjeta de recomendaciones de autocuidado. | `src/components/triage/risk_analysis_panel.py` | Activo |
| **src/components/common/body_map.py** | Mapa corporal interactivo. | `src/components/triage/guided_interview.py` | Activo |
| **src/ui/components/common/user_menu.py** | Menú de usuario global (Header). | `src/ui/main_view.py` | Activo |
| **src/scripts/check_models.py** | Script de comprobación de modelos. | CLI | Script |
| **src/scripts/debug_predictive_error.py** | Debug de errores predictivos. | CLI | Script |
| **src/scripts/debug_triage_data.py** | Debug de datos de triaje. | CLI | Script |
| **src/scripts/init_vital_signs_db.py** | Inicialización de DB de signos vitales. | CLI | Script |
| **src/scripts/inspect_vital_signs.py** | Inspección de signos vitales. | CLI | Script |
| **src/scripts/inspect_vital_signs_db.py** | Inspección de DB de signos vitales. | CLI | Script |
| **src/scripts/migrate_general_config.py** | Migración de configuración general. | CLI | Script |
| **src/scripts/migrate_salas.py** | Migración de salas. | CLI | Script |
| **src/scripts/seed_clinical_options.py** | Seed de opciones clínicas. | CLI | Script |
| **src/scripts/seed_vital_signs.py** | Seed de signos vitales. | CLI | Script |
| **src/scripts/test_gemini_model.py** | Test de modelo Gemini. | CLI | Script |
| **src/scripts/test_new_model_import.py** | Test de importación de nuevos modelos. | CLI | Script |
| **src/scripts/test_pdf_gen.py** | Test de generación de PDF. | CLI | Script |
| **src/scripts/test_queue_logic.py** | Test de lógica de colas. | CLI | Script |
| **src/scripts/test_triage_models.py** | Test de modelos de triaje. | CLI | Script |
| **src/scripts/test_vital_signs_logic.py** | Test de lógica de signos vitales. | CLI | Script |
| **src/scripts/update_prompts_model.py** | Actualización de modelos de prompts. | CLI | Script |
| **src/scripts/update_triage_data.py** | Actualización de datos de triaje. | CLI | Script |
| **src/scripts/verify_ai_model_management.py** | Verificación de gestión de modelos IA. | CLI | Script |
| **src/templates/email_templates.py** | Plantillas de email. | `src/services/notification_service.py` | Activo |
| **src/ui/audit_panel/tab_transcriptions_v2.py** | Versión 2 de pestaña transcripciones. | `src/ui/audit_panel/raw_data_panel_v2.py` | Activo |
| **src/ui/audit_panel/analysis_panel_modular.py** | Orquestador modular de Análisis Gráfico. | `src/ui/audit_panel/main_panel_v2.py` | Activo |
| **src/ui/audit_panel/debug_panel_modular.py** | Orquestador modular de Debug MongoDB. | `src/ui/audit_panel/main_panel_v2.py` | Activo |
| **src/ui/audit_panel/debug_modules/collection_inspector.py** | Inspector genérico de colecciones. | `src/ui/audit_panel/debug_panel_modular.py` | Activo |
| **src/components/analytics/modules/kpis.py** | Módulo independiente de KPIs. | `src/ui/audit_panel/analysis_panel_modular.py` | Activo |
| **src/components/analytics/modules/evolution.py** | Módulo independiente de Evolución. | `src/ui/audit_panel/analysis_panel_modular.py` | Activo |
| **src/components/analytics/modules/triage_analysis.py** | Módulo independiente de Análisis de Triaje. | `src/ui/audit_panel/analysis_panel_modular.py` | Activo |
| **src/components/analytics/modules/file_analysis.py** | Módulo independiente de Análisis de Archivos. | `src/ui/audit_panel/analysis_panel_modular.py` | Activo |
| **src/components/analytics/modules/transcription_analysis.py** | Módulo independiente de Análisis de Transcripciones. | `src/ui/audit_panel/analysis_panel_modular.py` | Activo |
| **src/components/analytics/modules/relational_analysis.py** | Módulo independiente de Análisis Relacional. | `src/ui/audit_panel/analysis_panel_modular.py` | Activo |
| **src/components/analytics/modules/prompt_analysis.py** | Módulo independiente de Análisis de Prompts. | `src/ui/audit_panel/analysis_panel_modular.py` | Activo |
| **src/components/analytics/modules/feedback_analysis.py** | Módulo independiente de Análisis de Feedback. | `src/ui/audit_panel/analysis_panel_modular.py` | Activo |
| **src/components/analytics/modules/concordance_analysis.py** | Módulo independiente de Concordancia. | `src/ui/audit_panel/analysis_panel_modular.py` | Activo |
| **src/components/audit/generic_log_view.py** | Vista genérica de logs con detalles. | `src/ui/audit_panel/raw_data_panel_v2.py` | Activo |
| **deprecated_files/generate_synthetic_data.py** | Script de generación de datos sintéticos. | CLI | Deprecado |
| **deprecated_files/apply_debug_footers.py** | Script de debug. | CLI | Deprecado |
| **deprecated_files/check_db_status.py** | Script de chequeo de estado. | CLI | Deprecado |
| **deprecated_files/check_debug_footers.py** | Script de chequeo de debug. | CLI | Deprecado |
| **deprecated_files/extract_clinical_options.py** | Script de extracción. | CLI | Deprecado |
| **deprecated_files/extract_vital_signs.py** | Script de extracción. | CLI | Deprecado |
| **deprecated_files/generate_synthetic_audit_logs.py** | Script de generación de logs. | CLI | Deprecado |
| **deprecated_files/inspect_db_values.py** | Script de inspección. | CLI | Deprecado |
| **deprecated_files/inspect_option_structure.py** | Script de inspección. | CLI | Deprecado |
| **deprecated_files/inspect_vital_signs_structure.py** | Script de inspección. | CLI | Deprecado |
| **deprecated_files/verify_refactor.py** | Script de verificación. | CLI | Deprecado |
| **src/ui/login_view.py** | Vista de Login Simulado. | `src/app.py` | Activo |
| **src/ui/shift_manager_advanced.py** | Gestor avanzado de turnos (Calendario, Conflictos). | `src/ui/config_panel.py` | Activo |
| **src/ui/components/common/offline_sync.py** | Componente de sincronización offline. | `src/app.py` | Activo |
| **src/ui/components/reports/report_viewer.py** | Visor de reportes PDF. | Varios | Activo |
| **src/db/repositories/login_logs.py** | Repositorio de Logs de Login. | `src/ui/login_view.py` | Activo |
| **src/utils/network_utils.py** | Utilidades de red (IP). | `src/ui/login_view.py` | Activo |
| **src/scripts/check_login_logs.py** | Script de verificación de logs de login. | CLI | Script |
| **src/scripts/init_lockout_fields.py** | Script de inicialización de campos de bloqueo. | CLI | Script |
| **src/scripts/inspect_users_lockout.py** | Script de inspección de bloqueos de usuario. | CLI | Script |
| **src/scripts/test_login_logging.py** | Script de test de logging de login. | CLI | Script |
| **src/scripts/generate_icons.py** | Script de generación de iconos. | CLI | Script |
