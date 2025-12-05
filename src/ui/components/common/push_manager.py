
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from db.repositories.people import get_people_repository
import os

def render_push_manager(user_id: str):
    """
    Componente para gestionar la suscripción a notificaciones push.
    """
    st.markdown("### 🔔 Notificaciones Push")
    
    # Obtener clave pública
    vapid_public_key = st.secrets.get("vapid", {}).get("public_key") or os.getenv("VAPID_PUBLIC_KEY")
    
    if not vapid_public_key:
        st.warning("⚠️ VAPID Public Key no configurada. Revisa st.secrets o variables de entorno.")
        return

    # Verificar estado actual
    repo = get_people_repository()
    user_data = repo.get_by_id(user_id)
    subscriptions = user_data.get("push_subscriptions", []) if user_data else []
    is_subscribed = len(subscriptions) > 0

    if is_subscribed:
        st.success(f"✅ Notificaciones Activas ({len(subscriptions)} dispositivos)")
        
        # Estado explícito
        st.caption("Estado: **Activado** - Recibirás notificaciones en este dispositivo.")
        
        if st.button("🔕 Desactivar en este dispositivo (Reset)", key="btn_disable_push"):
            # Por simplicidad, en esta versión borramos todas las suscripciones del usuario
            # Idealmente deberíamos identificar la suscripción actual del navegador
            repo.update_person(user_id, {"push_subscriptions": []})
            st.warning("Suscripciones eliminadas.")
            st.rerun()
    else:
        st.info("Activa las notificaciones para recibir alertas incluso cuando la app está cerrada.")
        
        # Estado explícito
        st.caption("Estado: **Desactivado** - No recibirás notificaciones.")
        
        # Usamos un botón para iniciar el proceso
        if st.button("📱 Activar Notificaciones en este dispositivo", key="btn_enable_push"):
            st.session_state.request_push_sub = True
            st.toast("Solicitando permiso de notificaciones...", icon="⏳")

    if st.session_state.get("request_push_sub"):
        # Ejecutar JS para suscribirse
        # Nota: Esto requiere que push_notifications.js esté cargado en el parent
        # Embed JS code directly to avoid scope issues
        js_code = f"""
        (async function() {{
            const vapidPublicKey = '{vapid_public_key}';
            
            function urlBase64ToUint8Array(base64String) {{
                const padding = '='.repeat((4 - base64String.length % 4) % 4);
                const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
                const rawData = window.atob(base64);
                const outputArray = new Uint8Array(rawData.length);
                for (let i = 0; i < rawData.length; ++i) {{ outputArray[i] = rawData.charCodeAt(i); }}
                return outputArray;
            }}

            try {{
                if (!('serviceWorker' in navigator) || !('PushManager' in window)) {{
                    return {{ error: "Push messaging is not supported in this browser" }};
                }}

                // Intentar obtener la registración
                // Primero buscamos en window.parent.pwaRegistration (si existe)
                let registration = window.parent.pwaRegistration;
                
                if (!registration) {{
                     // Buscamos explícitamente en el scope app/static/
                     registration = await navigator.serviceWorker.getRegistration('app/static/');
                }}
                
                if (!registration) {{
                    // Fallback a ready
                    registration = await navigator.serviceWorker.ready;
                }}

                if (!registration) {{
                    return {{ error: "No Service Worker registration found. Try reloading the page." }};
                }}

                const existingSubscription = await registration.pushManager.getSubscription();
                if (existingSubscription) {{
                    return existingSubscription.toJSON();
                }}

                const permission = await Notification.requestPermission();
                if (permission !== 'granted') {{
                    return {{ error: "Permission not granted for Notification" }};
                }}

                const subscribeOptions = {{
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
                }};

                const subscription = await registration.pushManager.subscribe(subscribeOptions);
                return subscription.toJSON();

            }} catch (error) {{
                return {{ error: error.toString() }};
            }}
        }})()
        """
        
        subscription = streamlit_js_eval(
            js_expressions=js_code,
            want_output=True,
            key="js_push_sub"
        )
        
        if subscription:
            # Debug: Mostrar respuesta raw en expander (o temporalmente)
            # st.write(f"JS Response: {subscription}") 

            if isinstance(subscription, dict) and "error" in subscription:
                st.error(f"❌ Error al suscribirse: {subscription['error']}")
                if "not supported" in subscription['error']:
                    st.warning("Nota: Las notificaciones Push requieren HTTPS o localhost.")
            else:
                try:
                    if repo.add_push_subscription(user_id, subscription):
                        st.success("✅ Dispositivo suscrito correctamente!")
                        st.toast("Notificaciones activadas", icon="🔔")
                        st.rerun()
                    else:
                        st.info("ℹ️ Dispositivo ya estaba suscrito.")
                except Exception as e:
                    st.error(f"Error al guardar suscripción: {e}")
            
            # Limpiar estado
            st.session_state.request_push_sub = False
            
    st.divider()
    
    # Sección de Prueba (Solo para verificar)
    col_test, col_debug = st.columns([2, 1])
    with col_test:
        if st.button("📨 Enviar Notificación de Prueba", help="Envía una notificación push a ti mismo para probar"):
            from services.notification_service import create_notification, NotificationChannel, NotificationPriority
            
            try:
                # Debug log
                print(f"Enviando push a {user_id} con {len(subscriptions)} suscripciones")
                
                result = create_notification(
                    title="Prueba de Triaje IA",
                    message="¡Si ves esto, las notificaciones push funcionan correctamente! 🚀",
                    priority=NotificationPriority.HIGH,
                    channels=[NotificationChannel.PUSH],
                    recipients=[user_id],
                    action_url="/?test=true"
                )
                st.success("Notificación enviada. Deberías recibirla en breve.")
            except Exception as e:
                st.error(f"Error al enviar prueba: {e}")
                
    with col_debug:
        with st.expander("🔍 Debug Info"):
            st.write(f"**User ID:** {user_id}")
            st.write(f"**Subs Count:** {len(subscriptions)}")
            st.write(f"**VAPID Key:** {vapid_public_key[:10]}...")
            
            if st.session_state.get("js_push_sub"):
                 st.write("**Last JS Response:**")
                 st.json(st.session_state.get("js_push_sub"))

            if st.button("Check Logs"):
                st.info("Revisa la consola del servidor para más detalles.")

    st.markdown('<div class="debug-footer">src/ui/components/common/push_manager.py</div>', unsafe_allow_html=True)
