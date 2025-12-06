
/**
 * push_notifications.js
 * Gestiona la suscripción a Web Push Notifications.
 */

// Utilidad para convertir VAPID key
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

async function subscribeUser(vapidPublicKey) {
    console.log("Starting subscribeUser...");

    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Push messaging is not supported');
        return { error: "Push messaging is not supported in this browser" };
    }

    try {
        // Intentar obtener la registración explícita (porque el scope puede no incluir esta página)
        let registration = window.pwaRegistration;

        if (!registration) {
            // Si no está en global, intentar buscarla
            registration = await navigator.serviceWorker.getRegistration('app/static/');
        }

        if (!registration) {
            // Fallback: esperar a ready (puede colgarse si el scope no coincide)
            console.log("Waiting for SW ready...");
            registration = await navigator.serviceWorker.ready;
        }

        if (!registration) {
            throw new Error("No Service Worker registration found.");
        }

        // Verificar si ya está suscrito
        const existingSubscription = await registration.pushManager.getSubscription();
        if (existingSubscription) {
            console.log('User is already subscribed:', existingSubscription);
            return existingSubscription.toJSON();
        }

        // Solicitar permiso (si no se ha concedido ya)
        const permission = await Notification.requestPermission();
        if (permission !== 'granted') {
            console.error('Permission not granted for Notification');
            return { error: "Permission not granted for Notification" };
        }

        // Suscribirse
        const subscribeOptions = {
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
        };

        const subscription = await registration.pushManager.subscribe(subscribeOptions);
        console.log('User Subscribed:', subscription);
        return subscription.toJSON();

    } catch (error) {
        console.error('Failed to subscribe the user: ', error);
        return { error: error.toString() };
    }
}

// Expose to parent window (since this script runs in an iframe)
if (window.parent) {
    window.parent.subscribeUser = subscribeUser;
    console.log("subscribeUser attached to window.parent");
}
