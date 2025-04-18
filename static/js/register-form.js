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

    // Configurar evento para el botón de registro
    const registerBtn = document.getElementById('register-btn');
    const usernameInput = document.getElementById('username-input');
    const emailInput = document.getElementById('email-input');
    const passwordInput = document.getElementById('password-input');
    const messageDiv = document.getElementById('register-message');

    if (registerBtn) {
        // Función para procesar el registro
        const handleRegister = async () => {
            // Validar campos
            const username = usernameInput.value.trim();
            const email = emailInput.value.trim().toLowerCase();
            const password = passwordInput.value;
            
            // Validación de nombre de usuario (solo letras, números y espacios)
            if (!username || !/^[a-zA-Z0-9\s]+$/.test(username)) {
                showToast(__('invalidUsername', 'El nombre de usuario solo puede contener letras, números y espacios.'), 'error');
                return;
            }
            
            // Validación de email
            if (!validateEmail(email)) {
                showToast(__('invalidEmail', 'Por favor, introduce un correo electrónico válido.'), 'error');
                return;
            }
            
            // Validación de contraseña
            if (password.length < 6) {
                showToast(__('passwordLength', 'La contraseña debe tener al menos 6 caracteres.'), 'error');
                return;
            }
            
            if (!/[A-Z]/.test(password)) {
                showToast(__('passwordUppercase', 'La contraseña debe contener al menos una letra mayúscula.'), 'error');
                return;
            }
            
            if (!/[a-z]/.test(password)) {
                showToast(__('passwordLowercase', 'La contraseña debe contener al menos una letra minúscula.'), 'error');
                return;
            }
            
            if (!/[0-9]/.test(password)) {
                showToast(__('passwordNumber', 'La contraseña debe contener al menos un número.'), 'error');
                return;
            }
            
            if (!/[_\W]/.test(password)) {
                showToast(__('passwordSpecial', 'La contraseña debe contener al menos un carácter especial (_,.!@#$%^&*).'), 'error');
                return;
            }
            
            // Desactivar botón y mostrar estado de carga
            registerBtn.disabled = true;
            registerBtn.textContent = __('Processing...', 'Procesando...');
            
            try {
                // Enviar solicitud de registro al servidor
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Registro exitoso
                    showToast(data.message || __('registrationSuccessful', '¡Registro exitoso! Ya puedes iniciar sesión con tus credenciales.'), 'success');
                    // Limpiar campos del formulario
                    usernameInput.value = '';
                    emailInput.value = '';
                    passwordInput.value = '';
                    // Opcional: redirigir al usuario a otra página después de un registro exitoso
                    // setTimeout(() => { window.location.href = '/'; }, 2000);
                } else {
                    // Error en el registro
                    showToast(data.message || __('An unexpected error occurred. Please try again.', 'Ocurrió un error inesperado. Por favor, inténtalo de nuevo.'), 'error');
                }
            } catch (err) {
                console.error('Error en el registro:', err);
                showToast(__('networkError', 'Error de red. Inténtalo de nuevo más tarde.'), 'error');
            } finally {
                // Restaurar el botón
                registerBtn.disabled = false;
                registerBtn.textContent = __('Register', 'Registrarse');
            }
        };

        // Asignar evento de clic al botón de registro
        registerBtn.addEventListener('click', handleRegister);
        
        // Añadir evento keydown a los campos de entrada
        const formInputs = [usernameInput, emailInput, passwordInput];
        formInputs.forEach(input => {
            input.addEventListener('keydown', function(e) {
                // Verificar si la tecla presionada es Enter
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleRegister();
                }
            });
        });
    }
});