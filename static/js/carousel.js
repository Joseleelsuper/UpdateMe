/**
 * Enhanced carousel functionality for the homepage
 * Based on Chrome Carousel Configurator best practices
 */
document.addEventListener('DOMContentLoaded', () => {
  const carouselContainer = document.querySelector('.carousel-container');
  const carouselWrapper = document.querySelector('.carousel-wrapper');
  const carousel = document.querySelector('.carousel');
  const slides = document.querySelectorAll('.carousel-slide');
  const dots = document.querySelectorAll('.carousel-dot');
  const prevButton = document.querySelector('.carousel-button-prev');
  const nextButton = document.querySelector('.carousel-button-next');
  
  // Check if carousel exists on the page
  if (!carousel) return;
  
  // Polyfill for the inert attribute if needed
  if (!('inert' in document.createElement('div'))) {
    // Simple polyfill - in production, use a complete polyfill
    Array.from(document.querySelectorAll('[inert]')).forEach(el => {
      el.setAttribute('aria-hidden', 'true');
      el.style.pointerEvents = 'none';
      el.style.userSelect = 'none';
    });
  }
  
  let currentIndex = 0;
  const slideCount = slides.length;
  let autoScrollInterval = null;
  const autoScroll = carousel.dataset.autoScroll === 'true';
  const scrollInterval = parseInt(carousel.dataset.scrollInterval) || 5000;
  
  // Initialize carousel
  initCarousel();
  
  // Set up auto-scrolling if enabled
  if (autoScroll) {
    startAutoScroll();
    
    // Pause auto-scroll when user interacts with carousel
    carouselContainer.addEventListener('mouseenter', stopAutoScroll);
    carouselContainer.addEventListener('mouseleave', startAutoScroll);
    carouselContainer.addEventListener('touchstart', stopAutoScroll);
    carouselContainer.addEventListener('touchend', startAutoScroll);
  }
  
  // Navigation button events
  prevButton.addEventListener('click', () => {
    navigateCarousel((currentIndex - 1 + slideCount) % slideCount);
  });
  
  nextButton.addEventListener('click', () => {
    navigateCarousel((currentIndex + 1) % slideCount);
  });
  
  // Add keyboard navigation
  carouselContainer.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') {
      navigateCarousel((currentIndex - 1 + slideCount) % slideCount);
      e.preventDefault();
    } else if (e.key === 'ArrowRight') {
      navigateCarousel((currentIndex + 1) % slideCount);
      e.preventDefault();
    }
  });
  
  // Add click event to dots for manual navigation
  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      navigateCarousel(index);
    });
  });
  
  // Initialize carousel state
  function initCarousel() {
    updateCarousel();
    carouselContainer.setAttribute('tabindex', '0');
    setupImageOverlay();
  }
  
  // Configurar el overlay para imágenes clicables
  function setupImageOverlay() {
    const overlay = document.getElementById('image-overlay');
    const overlayImage = overlay.querySelector('.overlay-image');
    const overlayCaption = overlay.querySelector('.overlay-caption');
    const closeButton = overlay.querySelector('.overlay-close');
    
    // Hacer clicables las imágenes del carrusel
    slides.forEach(slide => {
      const img = slide.querySelector('img');
      const caption = slide.querySelector('.carousel-caption');
      
      slide.addEventListener('click', () => {
        // Comprobar si estamos en móvil o pantalla pequeña
        if (window.innerWidth < 768) {
          // Actualizar overlay con la imagen y texto actuales
          overlayImage.src = img.src;
          overlayImage.alt = img.alt;
          overlayCaption.textContent = caption.textContent;
          
          // Mostrar overlay
          overlay.classList.add('active');
          
          // Desactivar scroll en el body
          document.body.style.overflow = 'hidden';
        }
      });
    });
    
    // Cerrar overlay al hacer clic en el botón o fuera de la imagen
    closeButton.addEventListener('click', closeOverlay);
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        closeOverlay();
      }
    });
    
    // Cerrar con tecla ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && overlay.classList.contains('active')) {
        closeOverlay();
      }
    });
    
    function closeOverlay() {
      overlay.classList.remove('active');
      document.body.style.overflow = '';
    }
  }
  
  // Start auto-scrolling
  function startAutoScroll() {
    if (!autoScroll) return;
    
    stopAutoScroll(); // Clear any existing intervals
    autoScrollInterval = setInterval(() => {
      navigateCarousel((currentIndex + 1) % slideCount);
    }, scrollInterval);
  }
  
  // Stop auto-scrolling
  function stopAutoScroll() {
    if (autoScrollInterval) {
      clearInterval(autoScrollInterval);
    }
  }
  
  // Navigate to a specific slide
  function navigateCarousel(index) {
    currentIndex = index;
    updateCarousel();
    
    // Anunciar para lectores de pantalla sin afectar la vista visual
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.classList.add('visually-hidden');
    liveRegion.textContent = `Slide ${index + 1} of ${slides.length}`; // Texto que no se muestra visualmente
    document.body.appendChild(liveRegion); // Añadirlo al body en lugar del container
    
    // Eliminar después de anunciar
    setTimeout(() => {
      document.body.removeChild(liveRegion);
    }, 1000);
    
    // Reset timer when manually navigating
    if (autoScroll) {
      stopAutoScroll();
      startAutoScroll();
    }
  }
  
  // Update carousel position and accessibility attributes
  function updateCarousel() {
    // Verificar si el navegador soporta scroll-snap
    const supportsScrollSnap = CSS.supports('scroll-snap-type: x mandatory');
    
    if (!supportsScrollSnap) {
      // Fallback para navegadores que no soportan scroll-snap
      carousel.style.transform = `translateX(-${currentIndex * 100}%)`;
    } else {
      // Usar scroll behavior nativo si está disponible
      const slideElement = slides[currentIndex];
      if (slideElement && carouselWrapper) {
        slideElement.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
          inline: 'center'
        });
      }
    }
    
    // Update slides state
    slides.forEach((slide, index) => {
      const isActive = index === currentIndex;
      
      // Update data attributes and inert status
      slide.dataset.active = isActive.toString();
      
      if (isActive) {
        slide.removeAttribute('inert');
        slide.setAttribute('aria-hidden', 'false');
      } else {
        slide.setAttribute('inert', '');
        slide.setAttribute('aria-hidden', 'true');
      }
    });
    
    // Update navigation dots with animation
    dots.forEach((dot, index) => {
      const isActive = index === currentIndex;
      dot.classList.toggle('active', isActive);
      dot.setAttribute('aria-selected', isActive.toString());
      
      // Visual enhancement para los puntos de navegación
      if (isActive) {
        dot.style.width = '30px';
      } else {
        dot.style.width = '20px';
      }
    });
    
    // Update button states y animación sutil
    prevButton.disabled = false;
    nextButton.disabled = false;
    
    // Añadir una pequeña animación a los botones al hacer clic
    const activeButton = currentIndex === 0 ? prevButton : 
                         currentIndex === slideCount - 1 ? nextButton : null;
    
    if (activeButton) {
      activeButton.classList.add('button-pulse');
      setTimeout(() => {
        activeButton.classList.remove('button-pulse');
      }, 300);
    }
  }
});
