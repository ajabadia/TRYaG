# Mapa de Archivos del Proyecto

Este documento lista los archivos principales del proyecto, su propósito y su estado.

| Ruta del Archivo | Descripción | Invocado Por | Estado |
| :--- | :--- | :--- | :--- |
| **src/app.py** | Punto de entrada principal. Configura Streamlit y el enrutamiento. | `streamlit run` | Activo |
| **src/config.py** | Configuraciones globales y constantes. | Varios | Activo |
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
| **src/ui/shift_manager.py** | Gestión de Turnos (Básico). | - | Obsoleto |
| **src/ui/shift_manager_advanced.py** | Gestión de Turnos (Avanzado). | `src/app.py` | Activo |
| **src/ui/ml_predictions_panel.py** | Panel de Predicciones ML. | `src/app.py` | Activo |
| **src/ui/loading_indicator.py** | Componente visual de carga. | Varios | Activo |
| **src/ui/connection_status.py** | Indicador de estado de conexión. | `src/app.py` | Activo |
| **src/ui/audit_panel/main_panel.py** | Panel de Auditoría (Orquestador). | `src/app.py` | Activo |
| **src/ui/audit_panel/raw_data_panel.py** | Panel de Datos en Bruto (Auditoría). | `src/ui/audit_panel/main_panel.py` | Activo |
| **src/ui/audit_panel/analysis_panel.py** | Panel de Análisis Gráfico (Auditoría). | `src/ui/audit_panel/main_panel.py` | Activo |
| **src/ui/audit_panel/analysis_panel.py.backup** | Backup antiguo de análisis. | - | Obsoleto |
| **src/ui/audit_panel/debug_panel.py** | Panel de Debug MongoDB. | `src/ui/audit_panel/main_panel.py` | Activo |
| **src/ui/audit_panel/feedback_list.py** | Lista de reportes de feedback. | `src/ui/audit_panel/raw_data_panel.py` | Activo |
| **src/ui/audit_panel/tab_audit.py** | Pestaña de Registros de Auditoría. | `src/ui/audit_panel/raw_data_panel.py` | Activo |
| **src/ui/audit_panel/tab_files.py** | Pestaña de Log de Ficheros. | `src/ui/audit_panel/raw_data_panel.py` | Activo |
| **src/ui/audit_panel/tab_transcriptions.py** | Pestaña de Log de Transcripciones. | `src/ui/audit_panel/raw_data_panel.py` | Activo |
| **src/ui/audit_panel/components.py** | Componentes reutilizables (Action Bar, Filters, Date Selector). | `src/ui/audit_panel/*.py` | Activo |
| **src/components/analytics/feedback_analysis.py** | Análisis gráfico de feedback. | `src/ui/audit_panel/analysis_panel.py` | Activo |
| **src/ui/config/asignacion_turnos.py** | UI para asignación de turnos. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/datos_generales.py** | UI para datos generales del centro. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/equipment_config.py** | UI para configuración de equipamiento. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/notification_config_ui.py** | UI para configuración de notificaciones. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/people_manager.py** | UI para gestión de personas (Staff). | `src/ui/config_panel.py` | Activo |
| **src/ui/config/roles_manager.py** | UI para gestión de roles. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/salas_manager.py** | UI para gestión de salas (CRUD). | `src/ui/config_panel.py` | Activo |
| **src/ui/config/staff_conflicts_viewer.py** | Visualizador de conflictos de personal. | `src/ui/config_panel.py` | Activo |
| **src/ui/config/usuarios_manager.py** | UI para gestión de usuarios del sistema. | `src/ui/config_panel.py` | Activo |
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
| **src/utils/file_handler.py** | Manejador de archivos (guardado/carga). | Varios | Activo |
| **src/utils/file_utils.py** | Utilidades generales de archivos. | Varios | Activo |
| **src/utils/icon_utils.py** | Utilidades para iconos. | UI | Activo |
| **src/utils/icons.py** | Definición de iconos. | UI | Activo |
| **src/utils/image_utils.py** | Procesamiento de imágenes. | Varios | Activo |
| **src/utils/patient_utils.py** | Utilidades para datos de pacientes. | Varios | Activo |
| **src/utils/pdf_utils.py** | Generación/Manejo de PDFs. | Varios | Activo |
| **src/utils/session_utils.py** | Manejo de sesión de Streamlit. | UI | Activo |
| **src/utils/setup_indexes.py** | Script de configuración de índices DB. | Setup | Activo |
| **src/components/audit/details.py** | Detalles de registros de auditoría. | `src/ui/audit_panel/tab_audit.py` | Activo |
| **src/components/audit/file_log.py** | Componente de log de ficheros. | `src/ui/audit_panel/tab_files.py` | Activo |
| **src/components/audit/filters.py** | Filtros específicos de auditoría. | `src/ui/audit_panel/*.py` | Activo |
| **src/components/audit/prompt_log.py** | Componente de log de prompts. | `src/ui/audit_panel/raw_data_panel.py` | Activo |
| **src/components/audit/table.py** | Tabla de registros de auditoría. | `src/ui/audit_panel/tab_audit.py` | Activo |
| **src/components/audit/transcription_log.py** | Componente de log de transcripciones. | `src/ui/audit_panel/tab_transcriptions.py` | Activo |
| **src/components/admission/admission_form.py** | Formulario de admisión. | `src/ui/admission_view.py` | Activo |
| **src/components/admission/step_confirmation.py** | Paso de confirmación de admisión. | `src/ui/admission_view.py` | Activo |
| **src/components/admission/step_patient_data.py** | Paso de datos del paciente. | `src/ui/admission_view.py` | Activo |
| **src/components/admission/step_sala_admision.py** | Paso de selección de sala de admisión. | `src/ui/admission_view.py` | Activo |
| **src/components/admission/step_sala_triaje.py** | Paso de selección de sala de triaje. | `src/ui/admission_view.py` | Activo |
| **src/components/analytics/evolution.py** | Gráfico de evolución temporal. | `src/ui/audit_panel/analysis_panel.py` | Activo |
| **src/components/analytics/file_analysis.py** | Análisis de archivos importados. | `src/ui/audit_panel/analysis_panel.py` | Activo |
| **src/components/analytics/kpis.py** | KPIs generales. | `src/ui/audit_panel/analysis_panel.py` | Activo |
| **src/components/analytics/prompt_analysis.py** | Análisis de prompts. | `src/ui/audit_panel/analysis_panel.py` | Activo |
| **src/components/analytics/relational_analysis.py** | Análisis relacional. | `src/ui/audit_panel/analysis_panel.py` | Activo |
| **src/components/analytics/transcription_analysis.py** | Análisis de transcripciones. | `src/ui/audit_panel/analysis_panel.py` | Activo |
| **src/components/analytics/triage_analysis.py** | Análisis de triaje. | `src/ui/audit_panel/analysis_panel.py` | Activo |
| **src/components/audit/temp_file_log_view.py** | Vista temporal de logs de archivos. | - | Posible Obsoleto |
| **src/components/boxes/step_attention.py** | Paso de atención en box. | `src/ui/boxes_view.py` | Activo |
| **src/components/boxes/step_patient_selection.py** | Paso de selección de paciente en box. | `src/ui/boxes_view.py` | Activo |
| **src/components/boxes/step_sala_selection.py** | Paso de selección de sala en box. | `src/ui/boxes_view.py` | Activo |
| **src/core/data_handler.py** | Manejador de datos core. | Varios | Activo |
| **src/core/prompt_manager.py** | Gestor de prompts. | Varios | Activo |
| **src/core/transcription_handler.py** | Manejador de transcripciones. | Varios | Activo |
| **src/scripts/check_models.py** | Script de comprobación de modelos. | CLI | Script |
| **src/scripts/complete_phase1_setup.py** | Script de setup fase 1. | CLI | Script |
| **src/scripts/consolidate_db.py** | Script de consolidación de DB. | CLI | Script |
| **src/scripts/create_flow_indexes.py** | Script de creación de índices de flujo. | CLI | Script |
| **src/scripts/migrate_centros_to_mongodb.py** | Script de migración de centros. | CLI | Script |
| **src/scripts/migrate_salas_config.py** | Script de migración de salas. | CLI | Script |
| **src/scripts/migrate_subtipo.py** | Script de migración de subtipos. | CLI | Script |
| **src/templates/email_templates.py** | Plantillas de email. | `src/services/notification_service.py` | Activo |
| **src/ui/audit_panel/feedback_list_v2.py** | Versión 2 de lista de feedback. | - | Backup/WIP |
| **src/ui/audit_panel/main_panel_v2.py** | Versión 2 de panel principal. | - | Backup/WIP |
| **src/ui/audit_panel/raw_data_panel_v2.py** | Versión 2 de panel de datos brutos. | - | Backup/WIP |
| **src/ui/audit_panel/tab_audit_v2.py** | Versión 2 de pestaña auditoría. | - | Backup/WIP |
| **src/ui/audit_panel/tab_files_v2.py** | Versión 2 de pestaña archivos. | - | Backup/WIP |
| **src/ui/audit_panel/tab_transcriptions_v2.py** | Versión 2 de pestaña transcripciones. | - | Backup/WIP |
