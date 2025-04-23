// Importación de módulos con el nuevo sistema de toasts
import { validateEmail, subscribeWithEmail, loadTranslations, __ } from './subscribe.js';
import('/static/js/utils/toasts.js').then(module => {
    window.toastModule = module; // Guardar en una variable global para facilitar el acceso
});

document.addEventListener('DOMContentLoaded', async () => {
    // Cargar traducciones antes de configurar el formulario
    await loadTranslations();
    
    const emailInput = document.getElementById('email-input');
    const subscribeBtn = document.getElementById('subscribe-btn');

    // Función para procesar la suscripción
    const handleSubscribe = async () => {
        const email = emailInput.value.trim().toLowerCase();
        if (!validateEmail(email)) {
            // Usar el nuevo módulo de toasts si está disponible, sino usar el fallback
            if (window.toastModule) {
                window.toastModule.toast.error(__('validEmail', 'Por favor, introduce un correo válido.'));
            } else {
                // Fallback al método antiguo si el módulo aún no se cargó
                import('./subscribe.js').then(module => module.showToast(__('validEmail', 'Por favor, introduce un correo válido.'), 'error'));
            }
            return;
        }
        subscribeBtn.disabled = true;
        subscribeBtn.textContent = __('processing', 'Procesando...');
        try {
            const data = await subscribeWithEmail(email);
            if (data.success) {
                // Mostrar un mensaje más informativo usando el nuevo sistema
                if (window.toastModule) {
                    window.toastModule.toast.success(data.message, 5000);
                } else {
                    // Fallback al método antiguo
                    import('./subscribe.js').then(module => module.showToast(data.message, 'success', 5000));
                }
                emailInput.value = '';
            } else {
                if (window.toastModule) {
                    window.toastModule.toast.error(data.message);
                } else {
                    import('./subscribe.js').then(module => module.showToast(data.message, 'error'));
                }
            }
        } catch (err) {
            if (window.toastModule) {
                window.toastModule.toast.error(__('networkError', 'Error de red. Inténtalo de nuevo más tarde.'));
            } else {
                import('./subscribe.js').then(module => 
                    module.showToast(__('networkError', 'Error de red. Inténtalo de nuevo más tarde.'), 'error')
                );
            }
        }
        subscribeBtn.disabled = false;
        subscribeBtn.textContent = __('subscribeButton', 'Suscribirse');
    };

    // Asignar la función al clic del botón
    subscribeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        handleSubscribe();
    });

    // Añadir evento keydown para el campo de email
    emailInput.addEventListener('keydown', function(e) {
        // Verificar si la tecla presionada es Enter
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSubscribe();
        }
    });
});