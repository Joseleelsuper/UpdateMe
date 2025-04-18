/**
 * Script para añadir los elementos de borde animado a todos los inputs
 */
document.addEventListener('DOMContentLoaded', () => {
    // Selecciona todos los inputs de texto, email y password
    const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], .subscribe-input, .form-input');
    
    inputs.forEach(input => {
        // Añadir posición relativa si no la tiene
        if (window.getComputedStyle(input).position === 'static') {
            input.style.position = 'relative';
        }
        
        // Crear borde izquierdo
        const leftBorder = document.createElement('span');
        leftBorder.classList.add('input-border-left');
        input.appendChild(leftBorder);
        
        // Crear borde derecho
        const rightBorder = document.createElement('span');
        rightBorder.classList.add('input-border-right');
        input.appendChild(rightBorder);
    });
});