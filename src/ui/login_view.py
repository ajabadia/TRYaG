import streamlit as st
from db.repositories.users import get_users_repository
from utils.icons import render_icon
from utils.ui_utils import load_css

def render_login_view():
    """
    Renderiza la pantalla de login simulado.
    """
    # Cargar estilos específicos si es necesario
    # load_css("src/assets/css/pages/login.css") # Si existiera
    
    st.markdown(
        """
        <style>
        .login-container {
            max_width: 800px;
            margin: 0 auto;
            padding-top: 50px;
            text-align: center;
        }
        .user-card {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 20px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            text-align: center;
            height: 100%;
        }
        .user-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-color: #28a745;
        }
        .user-card.selected {
            background-color: #e8f5e9;
            border-color: #28a745;
            border-width: 2px;
        }
        .user-avatar {
            font-size: 40px;
            margin-bottom: 10px;
        }
        .user-name {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
            color: #333;
        }
        .user-role {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Título y Logo
    col_logo, col_title = st.columns([1, 4])
    with col_title:
        st.title("Asistente de Triaje IA")
        st.markdown("##### Piloto de Traumatología")
    
    st.divider()
    
    if "login_selected_user" not in st.session_state:
        st.session_state.login_selected_user = None

    # 1. Selección de Usuario
    st.subheader("1. Seleccione su usuario")
    
    repo = get_users_repository()
    users = repo.get_all_users(active_only=True)
    
    if not users:
        st.error("No hay usuarios activos en el sistema.")
        return

    # Grid de usuarios (3 por fila)
    cols = st.columns(3)
    for i, user in enumerate(users):
        with cols[i % 3]:
            # Determinar si está seleccionado
            is_selected = st.session_state.login_selected_user and st.session_state.login_selected_user["_id"] == user["_id"]
            card_class = "user-card selected" if is_selected else "user-card"
            
            # Nombre a mostrar
            display_name = user.get('nombre_completo')
            if not display_name:
                parts = [user.get('nombre', ''), user.get('apellidos', '')]
                display_name = " ".join(p for p in parts if p).strip() or user['username']
            
            # Rol
            rol = user.get('rol', 'Usuario')
            
            # Renderizar tarjeta como botón
            if st.button(f"{display_name}\n{rol}", key=f"user_btn_{i}", use_container_width=True):
                st.session_state.login_selected_user = user
                st.rerun()

    # 2. Autenticación (Solo si hay usuario seleccionado)
    if st.session_state.login_selected_user:
        st.divider()
        st.subheader(f"Hola, {st.session_state.login_selected_user.get('nombre', 'Usuario')}")
        
        with st.form("login_form"):
            # Password (Internal ID)
            password = st.text_input("Contraseña (ID de Empleado)", type="password")
            
            # Disclaimer
            st.markdown(
                """
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border: 1px solid #ffeeba; margin: 15px 0;">
                    <strong>⚠️ AVISO LEGAL IMPORTANTE</strong><br>
                    Esta herramienta es un sistema de apoyo a la decisión clínica basado en Inteligencia Artificial.
                    <strong>NO sustituye el juicio clínico profesional.</strong><br>
                    Al acceder, usted acepta la responsabilidad de verificar todas las sugerencias de la IA.
                </div>
                """,
                unsafe_allow_html=True
            )
            
            disclaimer_check = st.checkbox("He leído y acepto las condiciones de uso y responsabilidad.")
            
            submit = st.form_submit_button("Entrar al Sistema", type="primary", use_container_width=True)
            
            if submit:
                # Validar contraseña (internal_id)
                correct_id = st.session_state.login_selected_user.get('internal_id')
                
                # Preparar repositorio de logs
                try:
                    from db.repositories.login_logs import get_login_logs_repository
                    log_repo = get_login_logs_repository()
                except Exception:
                    log_repo = None

                # Obtener IP del cliente
                from utils.network_utils import get_client_ip
                client_ip = get_client_ip()
                
                # --- CHECK LOCKOUT ---
                current_attempts = st.session_state.login_selected_user.get("failed_login_attempts", 0)
                locked_until = st.session_state.login_selected_user.get("locked_until")
                
                from datetime import datetime
                if locked_until and locked_until > datetime.now():
                    st.error(f"⛔ Usuario bloqueado temporalmente por seguridad hasta {locked_until.strftime('%H:%M')}.")
                    if log_repo:
                        log_repo.log_login(
                            user_id=st.session_state.login_selected_user["_id"],
                            username=st.session_state.login_selected_user.get("username", "unknown"),
                            success=False,
                            ip_address=client_ip,
                            details={"reason": "account_locked", "locked_until": locked_until.isoformat()}
                        )
                    return # Stop execution
                # ---------------------

                if not correct_id:
                    if log_repo:
                        log_repo.log_login(
                            user_id=st.session_state.login_selected_user["_id"],
                            username=st.session_state.login_selected_user.get("username", "unknown"),
                            success=False,
                            ip_address=client_ip,
                            details={"reason": "configuration_error", "message": "User has no internal_id"}
                        )
                    st.error("Error de configuración: Este usuario no tiene ID interno asignado.")
                elif password == correct_id:
                    if disclaimer_check:
                        # LOGIN EXITOSO
                        st.session_state.current_user = st.session_state.login_selected_user
                        
                        # Resetear contador de fallos
                        repo.reset_failed_attempts(st.session_state.current_user["_id"])
                        
                        # Registrar Log Exitoso
                        if log_repo:
                            log_repo.log_login(
                                user_id=st.session_state.current_user["_id"],
                                username=st.session_state.current_user.get("username", "unknown"),
                                success=True,
                                ip_address=client_ip,
                                details={"method": "simulated_internal_id"}
                            )

                        st.success("Acceso concedido. Cargando...")
                        st.rerun()
                    else:
                        # Fallo por Disclaimer
                        if log_repo:
                            log_repo.log_login(
                                user_id=st.session_state.login_selected_user["_id"],
                                username=st.session_state.login_selected_user.get("username", "unknown"),
                                success=False,
                                ip_address=client_ip,
                                details={"reason": "disclaimer_rejected"}
                            )
                        st.warning("Debe aceptar el aviso legal para continuar.")
                else:
                    # Fallo por Contraseña
                    
                    # Incrementar contador
                    new_count = repo.increment_failed_attempts(st.session_state.login_selected_user["_id"])
                    
                    # Bloquear si llega a 5
                    if new_count >= 5:
                        minutes_locked = repo.apply_exponential_lockout(st.session_state.login_selected_user["_id"])
                        st.error(f"⛔ Demasiados intentos fallidos. Usuario bloqueado por {minutes_locked} minutos.")
                        details_reason = "account_locked_max_attempts"
                    else:
                        st.error(f"Contraseña incorrecta. Intentos restantes: {5 - new_count}")
                        details_reason = "incorrect_password"

                    if log_repo:
                        log_repo.log_login(
                            user_id=st.session_state.login_selected_user["_id"],
                            username=st.session_state.login_selected_user.get("username", "unknown"),
                            success=False,
                            ip_address=client_ip,
                            details={
                                "reason": details_reason, 
                                "input_length": len(password),
                                "attempt_count": new_count
                            }
                        )

    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.get("developer_mode", False):
        st.markdown('<div class="debug-footer">src/ui/login_view.py</div>', unsafe_allow_html=True)
