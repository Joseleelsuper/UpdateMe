document.addEventListener('DOMContentLoaded', function() {
    const profileMenu = document.querySelector('.profile-menu');
    const profileIcon = document.getElementById('profile-icon');
    const profileDropdown = document.getElementById('profile-dropdown');
    
    if (!profileMenu || !profileIcon || !profileDropdown) return;
    
    let timeoutId;
    
    // Función para mostrar el menú
    const showMenu = () => {
        // Limpiar cualquier timeout pendiente
        if (timeoutId) clearTimeout(timeoutId);
        profileDropdown.classList.add('show');
    };
    
    // Función para ocultar el menú con un retraso
    const hideMenuWithDelay = () => {
        // Establecer un retraso antes de ocultar el menú (500ms = 0.5 segundos)
        timeoutId = setTimeout(() => {
            profileDropdown.classList.remove('show');
        }, 500);
    };
    
    // Evento al hacer clic en el icono del perfil
    profileIcon.addEventListener('click', (e) => {
        e.stopPropagation();
        
        // Si el menú está visible, lo ocultamos, si no, lo mostramos
        if (profileDropdown.classList.contains('show')) {
            profileDropdown.classList.remove('show');
        } else {
            showMenu();
        }
    });
    
    // Eventos para detectar cuando el mouse entra al menú o al icono
    profileMenu.addEventListener('mouseenter', showMenu);
    
    // Eventos para detectar cuando el mouse sale del menú o del icono
    profileMenu.addEventListener('mouseleave', hideMenuWithDelay);
    
    // Evitar que el menú se cierre al hacer clic dentro de él
    profileDropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });
    
    // Al hacer hover en el menú desplegable, cancelamos el timeout
    profileDropdown.addEventListener('mouseenter', () => {
        if (timeoutId) clearTimeout(timeoutId);
    });
    
    // Al salir del menú desplegable, iniciamos el timeout
    profileDropdown.addEventListener('mouseleave', hideMenuWithDelay);
    
    // Cerrar el menú al hacer clic fuera de él
    document.addEventListener('click', () => {
        profileDropdown.classList.remove('show');
    });
});