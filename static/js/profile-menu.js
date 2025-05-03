document.addEventListener('DOMContentLoaded', () => {
    const profileMenu = document.querySelector('.profile-menu');
    const profileDropdown = document.getElementById('profile-dropdown');
    
    if (!profileMenu || !profileDropdown) return;
    
    let timeoutId;
    
    // Función para mostrar el menú
    const showMenu = () => {
        if (timeoutId) clearTimeout(timeoutId);
        profileDropdown.classList.add('show');
    };
    
    // Función para ocultar el menú con un retraso
    const hideMenuWithDelay = () => {
        timeoutId = setTimeout(() => {
            profileDropdown.classList.remove('show');
        }, 300); // 300ms para una experiencia más responsive
    };
    
    // Mostrar/ocultar desplegable al hacer hover
    profileMenu.addEventListener('mouseenter', showMenu);
    profileMenu.addEventListener('mouseleave', hideMenuWithDelay);
    
    // Mantener el menú abierto si el ratón se mueve al contenido desplegable
    profileDropdown.addEventListener('mouseenter', () => {
        if (timeoutId) clearTimeout(timeoutId);
    });
    
    // Ocultar al salir del menú desplegable
    profileDropdown.addEventListener('mouseleave', hideMenuWithDelay);
});