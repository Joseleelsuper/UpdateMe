tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: '#3B82F6',    // Azul principal
                secondary: '#10B981',  // Verde para acciones secundarias
                dark: '#1F2937',       // Color oscuro para fondos
                light: '#F9FAFB',      // Color claro para fondos
                accent: '#8B5CF6',     // Color de acento para destacados
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            spacing: {
                '128': '32rem',
            },
            borderRadius: {
                'xl': '1rem',
                '2xl': '2rem',
            }
        }
    }
}