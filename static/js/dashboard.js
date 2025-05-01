document.addEventListener('DOMContentLoaded', function() {
    // Importación de la utilidad de toasts
    import('/static/js/utils/toasts.js').then(toastModule => {
        const { showToast, toast } = toastModule;
        
        // Selecciona los elementos del DOM
        const providerOptions = document.querySelectorAll('.provider-option');
        const savePromptsBtn = document.getElementById('save-prompts');
        const resetPromptsBtn = document.getElementById('reset-prompts');
        const tabHeaders = document.querySelectorAll('.tab-header');
        const tavilyPrompt = document.getElementById('tavily-prompt');
        const tavilyCharCount = document.getElementById('tavily-char-count');
        
        // Referencias al modal y sus elementos
        const resetModal = document.getElementById('reset-prompts-modal');
        const closeModalBtn = resetModal.querySelector('.modal-close');
        const cancelModalBtn = resetModal.querySelector('.modal-cancel');
        const confirmModalBtn = resetModal.querySelector('.modal-confirm');
        
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
            openaiSearchDisabled: 'OpenAI uses its own integrated search provider, it is not possible to change this option.',
            premiumUserOnly: 'This feature is only available for premium users.',
            tavilyPromptTooLong: 'Tavily prompt exceeds the 400 character limit.'
        };
        
        // Detectar si el usuario es free
        const isFreeUser = window.isFreeUser === true || window.isFreeUser === 'true';
        
        // Inicializar contador de caracteres para Tavily
        if (tavilyPrompt && tavilyCharCount) {
            // Actualizar contador inicial
            updateCharacterCount();
            
            // Escuchar cambios en el prompt
            tavilyPrompt.addEventListener('input', updateCharacterCount);
            
            function updateCharacterCount() {
                const count = tavilyPrompt.value.length;
                tavilyCharCount.textContent = count;
                
                // Actualizar estilo según si se acerca al límite
                const charCounter = tavilyCharCount.parentElement;
                if (count > 380) {
                    charCounter.classList.add('limit-reached');
                } else {
                    charCounter.classList.remove('limit-reached');
                }
            }
        }
        
        // Maneja los clics en las opciones de proveedor - SOLUCIÓN SIMPLIFICADA
        providerOptions.forEach(option => {
            option.addEventListener('click', function() {
                const isPremiumFeature = option.closest('section').classList.contains('disabled') || 
                                         !!option.closest('section').querySelector('.premium-only-msg');
                                         
                const isOpenAIDisabled = this.classList.contains('disabled') && 
                                        option.closest('section').classList.contains('search-provider') && 
                                        !isPremiumFeature;
                
                if (isPremiumFeature) {
                    toast.warning(translations.premiumUserOnly);
                    return;
                } else if (isOpenAIDisabled) {
                    toast.warning(translations.openaiSearchDisabled);
                    return;
                }
                
                // El resto del manejo de eventos continúa aquí
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
        
        if (isFreeUser) {
            // Interceptar edición en textareas, inputs y selects de la sección de prompts
            const promptsSection = document.querySelector('.prompts-section.disabled');
            if (promptsSection) {
                promptsSection.querySelectorAll('textarea, input, select').forEach(el => {
                    const showPremiumToast = (e) => {
                        toast.warning(translations.premiumUserOnly || 'Esta función solo está disponible para usuarios premium.');
                        e.preventDefault();
                        if (el.blur) el.blur();
                    };
                    el.addEventListener('focus', showPremiumToast);
                    el.addEventListener('mousedown', showPremiumToast);
                    el.addEventListener('keydown', showPremiumToast);
                    el.addEventListener('input', showPremiumToast);
                    el.addEventListener('change', showPremiumToast);
                });
            }
        }

        // Función para actualizar preferencias en el servidor
        function updatePreference(preferenceType, value) {
            fetch('/api/user/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ [preferenceType]: value })
            })
            .then(async response => {
                let data = {};
                try { data = await response.json(); } catch {}
                if (!response.ok) {
                    // Si es 403, mostrar el mensaje del backend o el de premium
                    if (response.status === 403 && data.message) {
                        toast.warning(data.message);
                    } else if (response.status === 403) {
                        toast.warning(translations.premiumUserOnly || 'Esta función solo está disponible para usuarios premium.');
                    } else {
                        toast.error(`${translations.errorUpdatingPreference} ${data.message || response.status}`);
                    }
                    throw new Error(`HTTP error ${response.status}`);
                }
                return data;
            })
            .then(data => {
                if (data.success) {
                    toast.success(translations.preferenceUpdated);
                } else {
                    toast.error(`${translations.errorUpdatingPreference} ${data.message}`);
                }
            })
            .catch(error => {
                if (error.message && error.message.startsWith('HTTP error 403')) return; // Ya mostrado como warning
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
        savePromptsBtn.addEventListener('click', function(e) {
            if (isFreeUser) {
                toast.warning(translations.premiumUserOnly || 'Esta función solo está disponible para usuarios premium.');
                e.preventDefault();
                return;
            }
            
            // Verificar el límite de caracteres para el prompt de Tavily
            const tavilyPromptValue = document.getElementById('tavily-prompt').value;
            if (tavilyPromptValue.length > 400) {
                toast.warning(translations.tavilyPromptTooLong || 'El prompt de Tavily excede el límite de 400 caracteres.');
                e.preventDefault();
                return;
            }
            
            // Recopilar los valores de los prompts
            const promptData = {
                openai_prompt: document.getElementById('openai-prompt').value,
                groq_prompt: document.getElementById('groq-prompt').value,
                deepseek_prompt: document.getElementById('deepseek-prompt').value,
                tavily_prompt: tavilyPromptValue,
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
                    max_results: parseInt(document.getElementById('serpapi-max-results').value) || 10,
                    search_type: document.getElementById('serpapi-search-type').value,
                    safe_search: document.getElementById('serpapi-safe-search').value,
                    time_range: document.getElementById('serpapi-time-range').value,
                    location: document.getElementById('serpapi-location').value,
                    gl: document.getElementById('serpapi-gl').value,
                    hl: document.getElementById('serpapi-hl').value,
                    device: document.getElementById('serpapi-device').value,
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
                    // Si es 403 (usuario free), mostrar warning en vez de error
                    if (response.status === 403) {
                        response.json().then(data => {
                            toast.warning(data.message || translations.premiumUserOnly || 'Esta función solo está disponible para usuarios premium.');
                        });
                        throw new Error(`HTTP error ${response.status}`);
                    }
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
        
        // Funciones para manejar el modal
        function openModal() {
            resetModal.classList.add('show');
        }
        
        function closeModal() {
            resetModal.classList.remove('show');
        }
        
        // Cerrar el modal al hacer clic en la X
        closeModalBtn.addEventListener('click', closeModal);
        
        // Cerrar el modal al hacer clic en Cancelar
        cancelModalBtn.addEventListener('click', closeModal);
        
        // Cerrar el modal al hacer clic fuera del contenido
        resetModal.addEventListener('click', function(e) {
            if (e.target === resetModal) {
                closeModal();
            }
        });
        
        // Función para resetear prompts
        function resetPrompts() {
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
        
        // Confirmar reset al hacer clic en el botón del modal
        confirmModalBtn.addEventListener('click', function() {
            closeModal();
            resetPrompts();
        });
        
        // Restablecer los prompts a los valores predeterminados
        resetPromptsBtn.addEventListener('click', function(e) {
            if (isFreeUser) {
                toast.warning(translations.premiumUserOnly || 'Esta función solo está disponible para usuarios premium.');
                e.preventDefault();
                return;
            }
            
            // Abrir el modal en lugar de usar confirm()
            openModal();
        });
    }).catch(error => {
        console.error('Error cargando el módulo de toasts:', error);
    });
});