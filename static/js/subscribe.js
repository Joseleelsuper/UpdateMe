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

export function showToast(message, type = 'success') {
    let toast = document.createElement('div');
    toast.textContent = message;
    toast.className = `fixed top-6 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 rounded-lg shadow-lg text-white text-lg transition-opacity duration-300 ${type === 'success' ? 'bg-green-600' : 'bg-red-600'}`;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}