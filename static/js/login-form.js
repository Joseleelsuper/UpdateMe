import { validateEmail, showToast, loadTranslations, __ } from './subscribe.js';

document.addEventListener('DOMContentLoaded', async () => {
    // Cargar traducciones antes de configurar el formulario
    await loadTranslations();
    
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

    // Configurar evento para el botón de login
    const loginBtn = document.getElementById('login-btn');
    const emailInput = document.getElementById('email-input');
    const passwordInput = document.getElementById('password-input');
    const messageDiv = document.getElementById('login-message');

    if (loginBtn) {
        // Función para procesar el login
        const handleLogin = async () => {
            // Validar campos
            const email = emailInput.value.trim().toLowerCase();
            const password = passwordInput.value;
            
            // Validación de email
            if (!validateEmail(email)) {
                showToast(__('invalidEmail', 'Por favor, introduce un correo electrónico válido.'), 'error');
                return;
            }
            
            // Validación básica de contraseña (que no esté vacía)
            if (!password) {
                showToast(__('emptyPassword', 'Por favor, introduce tu contraseña.'), 'error');
                return;
            }
            
            // Desactivar botón y mostrar estado de carga
            loginBtn.disabled = true;
            loginBtn.textContent = __('Processing...', 'Procesando...');
            
            try {
                // Enviar solicitud de login al servidor
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Login exitoso
                    showToast(data.message || __('loginSuccessful', '¡Inicio de sesión exitoso!'), 'success');
                    
                    // Limpiar campos del formulario
                    emailInput.value = '';
                    passwordInput.value = '';
                    
                    // Redireccionar al usuario al dashboard o página principal
                    setTimeout(() => { 
                        window.location.href = data.redirect || '/dashboard'; 
                    }, 1000);
                } else {
                    // Error en el login
                    showToast(data.message || __('loginError', 'Email o contraseña incorrectos.'), 'error');
                }
            } catch (err) {
                console.error('Error en el login:', err);
                showToast(__('networkError', 'Error de red. Inténtalo de nuevo más tarde.'), 'error');
            } finally {
                // Restaurar el botón
                loginBtn.disabled = false;
                loginBtn.textContent = __('Sign in', 'Iniciar sesión');
            }
        };

        // Asignar evento de clic al botón de login
        loginBtn.addEventListener('click', handleLogin);
        
        // Añadir evento keydown a los campos de entrada
        const formInputs = [emailInput, passwordInput];
        formInputs.forEach(input => {
            input.addEventListener('keydown', function(e) {
                // Verificar si la tecla presionada es Enter
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleLogin();
                }
            });
        });
    }
});