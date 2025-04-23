/**
 * Sistema centralizado de notificaciones toast para UpdateMe
 * Ofrece una API unificada para mostrar notificaciones con diferentes estilos
 */

// Función principal para mostrar un toast
export function showToast(message, type = 'success', duration = 3000) {
    // Crear el toast con la clase correcta según su tipo
    let toast = document.createElement('div');
    toast.textContent = message;
    
    // Asegurarse de establecer la clase correcta según el tipo
    toast.className = 'toast';
    if (type === 'success') {
        toast.classList.add('toast-success');
    } else if (type === 'error') {
        toast.classList.add('toast-error');
    } else if (type === 'warning') {
        toast.style.backgroundColor = '#F59E0B'; // Color naranja para advertencias
    }
    
    // Crear botón de cierre
    const closeBtn = document.createElement('span');
    closeBtn.className = 'toast-close';
    closeBtn.innerHTML = '×';
    closeBtn.addEventListener('click', () => {
        hideToast(toast);
    });
    
    toast.appendChild(closeBtn);
    document.body.appendChild(toast);
    
    // Variables para manejar el timer
    let timer;
    let remainingTime = duration;
    let startTime;
    
    // Mostrar el toast con animación (en el siguiente frame para que la transición funcione)
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Iniciar el temporizador
    const startTimer = () => {
        startTime = Date.now();
        timer = setTimeout(() => hideToast(toast), remainingTime);
    };
    
    // Pausar el temporizador cuando el mouse está sobre el toast
    const pauseTimer = () => {
        clearTimeout(timer);
        remainingTime -= Date.now() - startTime;
    };
    
    // Eventos para pausar/reanudar el temporizador
    toast.addEventListener('mouseenter', pauseTimer);
    toast.addEventListener('mouseleave', startTimer);
    
    // Función para ocultar el toast
    function hideToast(toastElement) {
        toastElement.classList.remove('show');
        setTimeout(() => toastElement.remove(), 400); // Tiempo igual a la duración de la transición
    }
    
    // Iniciar el temporizador
    startTimer();
    
    return toast;
}

// Objeto con métodos específicos para cada tipo de toast
export const toast = {
    success: (message, duration = 3000) => showToast(message, 'success', duration),
    error: (message, duration = 3000) => showToast(message, 'error', duration),
    warning: (message, duration = 3000) => showToast(message, 'warning', duration)
};

// Exportamos ambas formas de usar los toasts:
// 1. showToast(mensaje, tipo, duración) - para compatibilidad con código existente
// 2. toast.success(mensaje, duración), toast.error(mensaje, duración) - API más moderna y clara