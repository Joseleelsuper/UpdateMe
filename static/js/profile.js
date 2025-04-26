document.addEventListener('DOMContentLoaded', async function() {
    // Importar el módulo de toasts
    const toastModule = await import('/static/js/utils/toasts.js');
    const toast = toastModule.toast;
    
    // Referencias a elementos del DOM
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const profileForm = document.getElementById('profile-form');
    const passwordForm = document.getElementById('password-form');
    const newPasswordInput = document.getElementById('new-password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const deactivateBtn = document.getElementById('deactivate-account-btn');
    const reactivateBtn = document.getElementById('reactivate-account-btn');
    const deleteBtn = document.getElementById('delete-account-btn');
    const manageSubscriptionBtn = document.getElementById('manage-subscription-btn');
    
    // Referencias a elementos de los modales
    const deactivateModal = document.getElementById('deactivate-modal');
    const reactivateModal = document.getElementById('reactivate-modal');
    const deleteModal = document.getElementById('delete-modal');
    const closeDeactivateModal = document.getElementById('close-deactivate-modal');
    const closeReactivateModal = document.getElementById('close-reactivate-modal');
    const closeDeleteModal = document.getElementById('close-delete-modal');
    const cancelDeactivate = document.getElementById('cancel-deactivate');
    const cancelReactivate = document.getElementById('cancel-reactivate');
    const cancelDelete = document.getElementById('cancel-delete');
    const confirmDeactivate = document.getElementById('confirm-deactivate');
    const confirmReactivate = document.getElementById('confirm-reactivate');
    const confirmDelete = document.getElementById('confirm-delete');
    
    // Gestión de pestañas
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.dataset.tab;
            
            // Desactivar todos los botones y paneles
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Activar el botón y panel seleccionado
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Función para validar la robustez de la contraseña
    function validatePassword(password) {
        const reqLength = document.getElementById('req-length');
        const reqUppercase = document.getElementById('req-uppercase');
        const reqLowercase = document.getElementById('req-lowercase');
        const reqNumber = document.getElementById('req-number');
        const reqSpecial = document.getElementById('req-special');
        
        // Requisito: Al menos 6 caracteres
        if (password.length >= 6) {
            reqLength.classList.add('valid');
        } else {
            reqLength.classList.remove('valid');
        }
        
        // Requisito: Al menos una letra mayúscula
        if (/[A-Z]/.test(password)) {
            reqUppercase.classList.add('valid');
        } else {
            reqUppercase.classList.remove('valid');
        }
        
        // Requisito: Al menos una letra minúscula
        if (/[a-z]/.test(password)) {
            reqLowercase.classList.add('valid');
        } else {
            reqLowercase.classList.remove('valid');
        }
        
        // Requisito: Al menos un número
        if (/[0-9]/.test(password)) {
            reqNumber.classList.add('valid');
        } else {
            reqNumber.classList.remove('valid');
        }
        
        // Requisito: Al menos un carácter especial
        if (/[_\W]/.test(password)) {
            reqSpecial.classList.add('valid');
        } else {
            reqSpecial.classList.remove('valid');
        }
        
        // Comprobar si se cumplen todos los requisitos
        return password.length >= 6 && 
               /[A-Z]/.test(password) && 
               /[a-z]/.test(password) && 
               /[0-9]/.test(password) && 
               /[_\W]/.test(password);
    }
    
    // Evento para validar la contraseña mientras se escribe
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', function() {
            validatePassword(this.value);
        });
    }
    
    // Envío del formulario de perfil
    if (profileForm) {
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim().toLowerCase();
            const language = document.getElementById('language').value;
            
            // Validación básica
            if (!username) {
                toast.error(window.translations.profileUpdateError || 'Username cannot be empty');
                return;
            }
            
            if (!email || !validateEmail(email)) {
                toast.error(window.translations.profileUpdateError || 'Please enter a valid email');
                return;
            }
            
            try {
                const response = await fetch('/api/user/profile', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username,
                        email,
                        language
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    toast.success(window.translations.profileUpdateSuccess || 'Profile updated successfully');
                    
                    // Si el idioma ha cambiado, recargar la página
                    const currentLanguage = document.getElementById('language').getAttribute('data-current');
                    if (language !== currentLanguage) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }
                } else {
                    toast.error(data.message || window.translations.profileUpdateError || 'Error updating profile');
                }
            } catch (error) {
                console.error('Error updating profile:', error);
                toast.error(window.translations.connectionError || 'Connection error');
            }
        });
    }
    
    // Envío del formulario de cambio de contraseña
    if (passwordForm) {
        passwordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const currentPassword = document.getElementById('current-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            // Validación básica
            if (!currentPassword) {
                toast.error(window.translations.passwordChangeError || 'Current password cannot be empty');
                return;
            }
            
            if (newPassword !== confirmPassword) {
                toast.error(window.translations.passwordMismatch || 'Passwords do not match');
                return;
            }
            
            if (!validatePassword(newPassword)) {
                toast.error(window.translations.passwordWeak || 'Password is too weak');
                return;
            }
            
            try {
                const response = await fetch('/api/user/password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        currentPassword,
                        newPassword
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    toast.success(window.translations.passwordChangeSuccess || 'Password changed successfully');
                    
                    // Limpiar el formulario
                    passwordForm.reset();
                    document.querySelectorAll('.password-requirements li').forEach(li => {
                        li.classList.remove('valid');
                    });
                } else {
                    toast.error(data.message || window.translations.passwordChangeError || 'Error changing password');
                }
            } catch (error) {
                console.error('Error changing password:', error);
                toast.error(window.translations.connectionError || 'Connection error');
            }
        });
    }
    
    // Funciones para manejar modales
    function openModal(modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden'; // Prevenir scroll
    }
    
    function closeModal(modal) {
        modal.classList.remove('show');
        document.body.style.overflow = ''; // Restaurar scroll
    }
    
    // Eventos para abrir modales
    if (deactivateBtn) {
        deactivateBtn.addEventListener('click', function() {
            openModal(deactivateModal);
        });
    }

    if (reactivateBtn) {
        reactivateBtn.addEventListener('click', function() {
            openModal(reactivateModal);
        });
    }
    
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            openModal(deleteModal);
        });
    }
    
    // Eventos para cerrar modales
    if (closeDeactivateModal) {
        closeDeactivateModal.addEventListener('click', function() {
            closeModal(deactivateModal);
        });
    }
    
    if (closeReactivateModal) {
        closeReactivateModal.addEventListener('click', function() {
            closeModal(reactivateModal);
        });
    }
    
    if (closeDeleteModal) {
        closeDeleteModal.addEventListener('click', function() {
            closeModal(deleteModal);
        });
    }
    
    if (cancelDeactivate) {
        cancelDeactivate.addEventListener('click', function() {
            closeModal(deactivateModal);
        });
    }

    if (cancelReactivate) {
        cancelReactivate.addEventListener('click', function() {
            closeModal(reactivateModal);
        });
    }
    
    if (cancelDelete) {
        cancelDelete.addEventListener('click', function() {
            closeModal(deleteModal);
        });
    }
    
    // Cerrar los modales al hacer clic fuera del contenido
    window.addEventListener('click', function(e) {
        if (e.target === deactivateModal) {
            closeModal(deactivateModal);
        }
        if (e.target === reactivateModal) {
            closeModal(reactivateModal);
        }
        if (e.target === deleteModal) {
            closeModal(deleteModal);
        }
    });
    
    // Acción para desactivar cuenta
    if (confirmDeactivate) {
        confirmDeactivate.addEventListener('click', async function() {
            try {
                // Mostrar indicador de carga
                confirmDeactivate.disabled = true;
                confirmDeactivate.textContent = '...';
                
                const response = await fetch('/api/user/deactivate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Cerrar el modal
                    closeModal(deactivateModal);
                    
                    toast.success(window.translations.accountDeactivationSuccess || 'Account deactivated successfully');
                    
                    // Redirigir al usuario a la página de logout después de unos segundos
                    setTimeout(() => {
                        window.location.href = '/logout';
                    }, 2000);
                } else {
                    closeModal(deactivateModal);
                    toast.error(data.message || window.translations.accountDeactivationError || 'Error deactivating account');
                }
            } catch (error) {
                console.error('Error deactivating account:', error);
                closeModal(deactivateModal);
                toast.error(window.translations.connectionError || 'Connection error');
            } finally {
                confirmDeactivate.disabled = false;
                confirmDeactivate.textContent = window.translations?.deactivate || 'Deactivate';
            }
        });
    }

    // Acción para reactivar cuenta
    if (confirmReactivate) {
        confirmReactivate.addEventListener('click', async function() {
            try {
                // Mostrar indicador de carga
                confirmReactivate.disabled = true;
                confirmReactivate.textContent = '...';
                
                const response = await fetch('/api/user/reactivate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Cerrar el modal
                    closeModal(reactivateModal);
                    
                    toast.success(window.translations.accountReactivationSuccess || 'Account reactivated successfully');
                    
                    // Recargar la página después de unos segundos para reflejar los cambios
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000);
                } else {
                    closeModal(reactivateModal);
                    toast.error(data.message || window.translations.accountReactivationError || 'Error reactivating account');
                }
            } catch (error) {
                console.error('Error reactivating account:', error);
                closeModal(reactivateModal);
                toast.error(window.translations.connectionError || 'Connection error');
            } finally {
                confirmReactivate.disabled = false;
                confirmReactivate.textContent = window.translations?.reactivate || 'Reactivate';
            }
        });
    }
    
    // Acción para eliminar cuenta
    if (confirmDelete) {
        confirmDelete.addEventListener('click', async function() {
            try {
                // Mostrar indicador de carga
                confirmDelete.disabled = true;
                confirmDelete.textContent = '...';
                
                const response = await fetch('/api/user/delete', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Cerrar el modal
                    closeModal(deleteModal);
                    
                    toast.success(window.translations.accountDeletionSuccess || 'Account deleted successfully');
                    
                    // Redirigir al usuario a la página principal después de unos segundos
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 2000);
                } else {
                    closeModal(deleteModal);
                    toast.error(data.message || window.translations.accountDeletionError || 'Error deleting account');
                }
            } catch (error) {
                console.error('Error deleting account:', error);
                closeModal(deleteModal);
                toast.error(window.translations.connectionError || 'Connection error');
            } finally {
                confirmDelete.disabled = false;
                confirmDelete.textContent = window.translations?.deletePermanently || 'Delete Permanently';
            }
        });
    }
    
    // Manejo de suscripción
    if (manageSubscriptionBtn) {
        manageSubscriptionBtn.addEventListener('click', async function() {
            try {
                // Importamos el módulo de suscripción dinámicamente
                const subscriptionModule = await import('/static/js/subscription.js');
                subscriptionModule.manageSubscription();
            } catch (error) {
                console.error('Error managing subscription:', error);
                toast.error(window.translations.connectionError || 'Connection error');
            }
        });
    }
    
    // Función para validar email
    function validateEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }
});