export function validateEmail(email) {
    // Debe coincidir con la expresión regular del backend
    return /^[\w\.-]+@[\w\.-]+\.\w+$/.test(email);
}

export async function subscribeWithEmail(email) {
    const response = await fetch('/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });
    return response.json();
}

export async function showToast(message, type = 'success', duration = 3000) {
    // Crear el toast
    let toast = document.createElement('div');
    toast.textContent = message;
    toast.className = `toast ${type === 'success' ? 'toast-success' : 'toast-error'}`;
    
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
    let remainingTime = duration; // Duración personalizable
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
}
