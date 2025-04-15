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
    toast.className = `toast ${type === 'success' ? 'toast-success' : 'toast-error'}`;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}