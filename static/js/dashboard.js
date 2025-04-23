document.addEventListener('DOMContentLoaded', function() {
    // Importación de la utilidad de toasts
    import('/static/js/utils/toasts.js').then(toastModule => {
        const { showToast, toast } = toastModule;
        
        // Selecciona los elementos del DOM
        const providerOptions = document.querySelectorAll('.provider-option');
        const savePromptsBtn = document.getElementById('save-prompts');
        const resetPromptsBtn = document.getElementById('reset-prompts');
        const tabHeaders = document.querySelectorAll('.tab-header');
        
        // Traducciones
        const translations = window.translations || {
            preferenceUpdated: 'Preference updated successfully',
            errorUpdatingPreference: 'Error updating preference: ',
            promptsSaved: 'Prompts saved successfully',
            errorSavingPrompts: 'Error saving prompts: ',
            promptsReset: 'Prompts reset successfully',
            errorResettingPrompts: 'Error resetting prompts: ',
            connectionError: 'Connection error: ',
            confirmResetPrompts: 'Are you sure you want to reset all prompts to default values?',
            openaiSearchDisabled: 'OpenAI uses its own integrated search provider, it is not possible to change this option.'
        };
        
        // Maneja los clics en las opciones de proveedor
        providerOptions.forEach(option => {
            option.addEventListener('click', function() {
                // Si el elemento está deshabilitado, no hacer nada
                if (this.classList.contains('disabled')) {
                    toast.warning(translations.openaiSearchDisabled);
                    return;
                }
                
                const parentSection = this.closest('section');
                const providerType = parentSection.classList.contains('ai-provider') ? 'ai_provider' : 'search_provider';
                const provider = this.dataset.provider;
                
                // Actualizar visualmente
                parentSection.querySelectorAll('.provider-option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                this.classList.add('selected');
                
                // Si se selecciona OpenAI como proveedor de IA, deshabilitar la selección de proveedor de búsqueda
                if (providerType === 'ai_provider' && provider === 'openai') {
                    const searchProviderSection = document.querySelector('.search-provider');
                    searchProviderSection.classList.add('disabled');
                    searchProviderSection.querySelectorAll('.provider-option').forEach(opt => {
                        opt.classList.add('disabled');
                    });
                } else if (providerType === 'ai_provider') {
                    // Si se selecciona otro proveedor de IA, habilitar la selección de proveedor de búsqueda
                    const searchProviderSection = document.querySelector('.search-provider');
                    searchProviderSection.classList.remove('disabled');
                    searchProviderSection.querySelectorAll('.provider-option').forEach(opt => {
                        opt.classList.remove('disabled');
                    });
                }
                
                // Enviar la preferencia al servidor
                updatePreference(providerType, provider);
            });
        });
        
        // Función para actualizar preferencias en el servidor
        function updatePreference(preferenceType, value) {
            fetch('/api/user/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ [preferenceType]: value })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    toast.success(translations.preferenceUpdated);
                } else {
                    toast.error(`${translations.errorUpdatingPreference} ${data.message}`);
                }
            })
            .catch(error => {
                toast.error(`${translations.connectionError} ${error.message}`);
            });
        }
        
        // Maneja las pestañas de prompts
        tabHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const tabId = this.dataset.tab;
                
                // Actualizar clases activas en encabezados
                document.querySelectorAll('.tab-header').forEach(h => {
                    h.classList.remove('active');
                });
                this.classList.add('active');
                
                // Mostrar el contenido de la pestaña seleccionada
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('active');
                });
                document.getElementById(tabId).classList.add('active');
            });
        });
        
        // Guardar los prompts personalizados
        savePromptsBtn.addEventListener('click', function() {
            // Recopilar los valores de los prompts
            const promptData = {
                openai_prompt: document.getElementById('openai-prompt').value,
                groq_prompt: document.getElementById('groq-prompt').value,
                deepseek_prompt: document.getElementById('deepseek-prompt').value,
                tavily_prompt: document.getElementById('tavily-prompt').value,
                serpapi_prompt: document.getElementById('serpapi-prompt').value
            };
            
            // Recopilar las configuraciones de búsqueda
            if (document.getElementById('tavily-max-results')) {
                promptData.tavily_config = {
                    max_results: parseInt(document.getElementById('tavily-max-results').value) || 5,
                    topic: document.getElementById('tavily-topic').value,
                    search_depth: document.getElementById('tavily-search-depth').value,
                    time_range: document.getElementById('tavily-time-range').value,
                    include_raw_content: true,
                    include_domains: [],
                    exclude_domains: []
                };
            }
            
            if (document.getElementById('serpapi-max-results')) {
                promptData.serpapi_config = {
                    max_results: parseInt(document.getElementById('serpapi-max-results').value) || 5,
                    search_type: document.getElementById('serpapi-search-type').value,
                    safe_search: document.getElementById('serpapi-safe-search').value,
                    time_range: document.getElementById('serpapi-time-range').value,
                    include_domains: [],
                    exclude_domains: []
                };
            }
            
            // Enviar los datos al servidor
            fetch('/api/user/prompts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(promptData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    toast.success(translations.promptsSaved);
                } else {
                    toast.error(`${translations.errorSavingPrompts} ${data.message}`);
                }
            })
            .catch(error => {
                toast.error(`${translations.connectionError} ${error.message}`);
            });
        });
        
        // Restablecer los prompts a los valores predeterminados
        resetPromptsBtn.addEventListener('click', function() {
            if (confirm(translations.confirmResetPrompts)) {
                fetch('/api/user/prompts/reset', {
                    method: 'POST'
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        toast.success(translations.promptsReset);
                        // Recargar la página para mostrar los valores predeterminados
                        window.location.reload();
                    } else {
                        toast.error(`${translations.errorResettingPrompts} ${data.message}`);
                    }
                })
                .catch(error => {
                    toast.error(`${translations.connectionError} ${error.message}`);
                });
            }
        });
    }).catch(error => {
        console.error('Error cargando el módulo de toasts:', error);
    });
});