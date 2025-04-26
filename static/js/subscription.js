// Stripe public key from environment variables
const stripePublicKey = document.querySelector('meta[name="stripe-public-key"]')?.content;

// Import utilities
import('/static/js/utils/toasts.js').then(module => {
    window.toastModule = module;
});

document.addEventListener('DOMContentLoaded', function() {
    // Find subscription buttons
    const subscribeMonthlyBtn = document.querySelector('.subscribe-monthly');
    const subscribeYearlyBtn = document.querySelector('.subscribe-yearly');
    
    // Track if prices are being loaded
    let loadingPrices = false;
    // Store prices once they're loaded
    let prices = null;
    
    // Get subscription prices from server
    const fetchPrices = async () => {
        if (loadingPrices || prices) return;
        
        try {
            loadingPrices = true;
            const response = await fetch('/api/subscription/prices');
            const data = await response.json();
            
            if (data.success && data.prices) {
                prices = data.prices;
            } else {
                throw new Error(data.error || 'Failed to load prices');
            }
        } catch (error) {
            console.error('Error loading subscription prices:', error);
            if (window.toastModule) {
                window.toastModule.toast.error('Error loading subscription prices. Please try again later.');
            }
        } finally {
            loadingPrices = false;
        }
    };
    
    // Initial fetch of prices
    fetchPrices();
    
    // Handle monthly subscription click
    if (subscribeMonthlyBtn) {
        subscribeMonthlyBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            // Check if user is logged in
            if (!isLoggedIn()) {
                window.location.href = loginUrl;
                return;
            }
            
            // Make sure prices are loaded
            if (!prices || !prices.monthly || !prices.monthly.id) {
                await fetchPrices();
                
                if (!prices || !prices.monthly || !prices.monthly.id) {
                    if (window.toastModule) {
                        window.toastModule.toast.error('Could not load subscription prices. Please try again later.');
                    }
                    return;
                }
            }
            
            // Create checkout session for monthly subscription
            createCheckoutSession(prices.monthly.id);
        });
    }
    
    // Handle yearly subscription click
    if (subscribeYearlyBtn) {
        subscribeYearlyBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            // Check if user is logged in
            if (!isLoggedIn()) {
                window.location.href = loginUrl;
                return;
            }
            
            // Make sure prices are loaded
            if (!prices || !prices.yearly || !prices.yearly.id) {
                await fetchPrices();
                
                if (!prices || !prices.yearly || !prices.yearly.id) {
                    if (window.toastModule) {
                        window.toastModule.toast.error('Could not load subscription prices. Please try again later.');
                    }
                    return;
                }
            }
            
            // Create checkout session for yearly subscription
            createCheckoutSession(prices.yearly.id);
        });
    }
    
    // Create Stripe checkout session
    const createCheckoutSession = async (priceId) => {
        try {
            // Show loading indicator
            const button = priceId === prices.monthly.id ? subscribeMonthlyBtn : subscribeYearlyBtn;
            const originalText = button.textContent;
            button.disabled = true;
            button.textContent = 'Processing...';
            
            // Make API request to create checkout session
            const response = await fetch('/api/subscription/checkout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ priceId })
            });
            
            const data = await response.json();
            if (data.success && data.checkoutUrl) {
                // Redirect to Stripe checkout
                window.location.href = data.checkoutUrl;
            } else {
                throw new Error(data.error || 'Failed to create checkout session');
            }
        } catch (error) {
            console.error('Error creating checkout session:', error);
            if (window.toastModule) {
                window.toastModule.toast.error('Error creating checkout. Please try again later.');
            }
            
            // Reset buttons
            if (subscribeMonthlyBtn) subscribeMonthlyBtn.disabled = false;
            if (subscribeYearlyBtn) subscribeYearlyBtn.disabled = false;
            
            if (priceId === prices?.monthly?.id && subscribeMonthlyBtn) {
                subscribeMonthlyBtn.textContent = originalText;
            } else if (priceId === prices?.yearly?.id && subscribeYearlyBtn) {
                subscribeYearlyBtn.textContent = originalText;
            }
        }
    };
    
    // Helper to check if user is logged in
    function isLoggedIn() {
        return document.querySelector('meta[name="user-logged-in"]')?.content === 'true';
    }
});

// Function to manage subscription (can be called from other pages)
export async function manageSubscription() {
    try {
        const response = await fetch('/api/subscription/portal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        if (data.success && data.portalUrl) {
            window.location.href = data.portalUrl;
        } else {
            if (window.toastModule) {
                window.toastModule.toast.error(data.error || 'Failed to access subscription portal');
            }
        }
    } catch (error) {
        console.error('Error accessing subscription portal:', error);
        if (window.toastModule) {
            window.toastModule.toast.error('Error connecting to server. Please try again later.');
        }
    }
}