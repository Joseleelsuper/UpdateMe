import { validateEmail, subscribeWithEmail, showToast } from './subscribe.js';

document.addEventListener('DOMContentLoaded', () => {
    const emailInput = document.getElementById('email-input');
    const subscribeBtn = document.getElementById('subscribe-btn');

    subscribeBtn.addEventListener('click', async function (e) {
        e.preventDefault();
        const email = emailInput.value.trim().toLowerCase();
        if (!validateEmail(email)) {
            showToast('Por favor, introduce un correo válido.', 'error');
            return;
        }
        subscribeBtn.disabled = true;
        subscribeBtn.textContent = 'Procesando...';
        try {
            const data = await subscribeWithEmail(email);
            if (data.success) {
                // Mostrar un mensaje más informativo
                showToast(data.message, 'success', 5000); // Aumentar tiempo a 5 segundos
                emailInput.value = '';
            } else {
                showToast(data.message, 'error');
            }
        } catch (err) {
            showToast('Error de red. Inténtalo de nuevo más tarde.', 'error');
        }
        subscribeBtn.disabled = false;
        subscribeBtn.textContent = 'Suscribirse';
    });
});