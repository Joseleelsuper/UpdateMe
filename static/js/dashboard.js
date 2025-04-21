import { showToast } from './subscribe.js';

document.addEventListener('DOMContentLoaded', function() {
    // Tab functionality
    const tabHeaders = document.querySelectorAll('.tab-header');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabHeaders.forEach(header => {
        header.addEventListener('click', () => {
            // Remove active class from all headers and panes
            tabHeaders.forEach(h => h.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked header
            header.classList.add('active');
            
            // Show corresponding pane
            const tabId = header.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Provider selection
    const aiProviderOptions = document.querySelectorAll('.ai-provider .provider-option');
    const searchProviderOptions = document.querySelectorAll('.search-provider .provider-option');
    
    aiProviderOptions.forEach(option => {
        option.addEventListener('click', () => {
            // Remove selected class from all options
            aiProviderOptions.forEach(o => o.classList.remove('selected'));
            
            // Add selected class to clicked option
            option.classList.add('selected');
            
            // Send provider update to server
            const provider = option.getAttribute('data-provider');
            updateUserPreference('ai_provider', provider);
        });
    });
    
    searchProviderOptions.forEach(option => {
        option.addEventListener('click', () => {
            // Remove selected class from all options
            searchProviderOptions.forEach(o => o.classList.remove('selected'));
            
            // Add selected class to clicked option
            option.classList.add('selected');
            
            // Send provider update to server
            const provider = option.getAttribute('data-provider');
            updateUserPreference('search_provider', provider);
        });
    });
    
    // Save prompts
    document.getElementById('save-prompts').addEventListener('click', () => {
        const promptsData = {
            openai_prompt: document.getElementById('openai-prompt').value,
            groq_prompt: document.getElementById('groq-prompt').value,
            deepseek_prompt: document.getElementById('deepseek-prompt').value,
            tavily_prompt: document.getElementById('tavily-prompt').value,
            serpapi_prompt: document.getElementById('serpapi-prompt').value
        };
        
        savePrompts(promptsData);
    });
    
    // Reset prompts to defaults
    document.getElementById('reset-prompts').addEventListener('click', () => {
        if (confirm(__('confirmResetPrompts', '¿Estás seguro de que quieres restablecer todos los prompts a los valores predeterminados?'))) {
            resetPrompts();
        }
    });
    
    // Helper functions
    function updateUserPreference(key, value) {
        fetch('/api/user/preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ [key]: value }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(__('preferenceUpdated', 'Preferencia actualizada correctamente'), 'success');
            } else {
                showToast(__('errorUpdatingPreference', 'Error actualizando preferencia: ') + data.message, 'error');
            }
        })
        .catch(error => {
            showToast(__('connectionError', 'Error de conexión: ') + error.message, 'error');
        });
    }
    
    function savePrompts(promptsData) {
        fetch('/api/user/prompts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(promptsData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(__('promptsSaved', 'Prompts guardados correctamente'), 'success');
            } else {
                showToast(__('errorSavingPrompts', 'Error guardando prompts: ') + data.message, 'error');
            }
        })
        .catch(error => {
            showToast(__('connectionError', 'Error de conexión: ') + error.message, 'error');
        });
    }
    
    function resetPrompts() {
        fetch('/api/user/prompts/reset', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(__('promptsReset', 'Prompts restablecidos correctamente'), 'success');
                // Reload page to show default prompts
                window.location.reload();
            } else {
                showToast(__('errorResettingPrompts', 'Error restableciendo prompts: ') + data.message, 'error');
            }
        })
        .catch(error => {
            showToast(__('connectionError', 'Error de conexión: ') + error.message, 'error');
        });
    }
    
    // Handle profile dropdown for mobile and desktop
    const profileIcon = document.getElementById('profile-icon');
    const profileDropdown = document.getElementById('profile-dropdown');
    
    if (profileIcon && profileDropdown) {
        // Toggle dropdown on icon click (for mobile)
        profileIcon.addEventListener('click', (e) => {
            e.stopPropagation();
            profileDropdown.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            profileDropdown.classList.remove('show');
        });
    }
    
    // Translation helper function (similar to the one in other JS files)
    function __(key, fallback) {
        // Try to get the translation from the window.translations object that's populated by the template
        if (window.translations && window.translations[key]) {
            return window.translations[key];
        }
        // Return fallback text if no translation is found
        return fallback;
    }
});