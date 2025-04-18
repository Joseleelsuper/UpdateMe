document.addEventListener('DOMContentLoaded', () => {
    // Añadir los elementos para los bordes laterales a cada input
    const inputs = document.querySelectorAll('.subscribe-input');
    
    inputs.forEach(input => {
        // Crear borde izquierdo
        const leftBorder = document.createElement('span');
        leftBorder.classList.add('subscribe-input-left');
        input.appendChild(leftBorder);
        
        // Crear borde derecho
        const rightBorder = document.createElement('span');
        rightBorder.classList.add('subscribe-input-right');
        input.appendChild(rightBorder);
    });

    // Configurar evento para el botón de registro
    const registerBtn = document.getElementById('register-btn');
    const usernameInput = document.getElementById('username-input');
    const emailInput = document.getElementById('email-input');
    const passwordInput = document.getElementById('password-input');
    const messageDiv = document.getElementById('register-message');

    if (registerBtn) {
        registerBtn.addEventListener('click', async () => {
            // Aquí se implementará la lógica de registro cuando esté lista
            // Por ahora solo mostrar un mensaje de ejemplo
            messageDiv.textContent = 'Funcionalidad de registro en desarrollo...';
            messageDiv.style.color = 'var(--color-primary)';
        });
    }
});