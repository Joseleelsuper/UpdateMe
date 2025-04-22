/**
 * Script para carga diferida de imágenes
 * Mejora el rendimiento de carga de la página aplicando lazy-loading
 * a las imágenes y estableciendo el tamaño correcto de las imágenes
 * para evitar saltos en el layout de la página.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Implementación de lazy loading para todas las imágenes con attr data-src
  const lazyImages = document.querySelectorAll('img[data-src]');
  
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const image = entry.target;
          image.src = image.dataset.src;
          
          // También cargamos srcset si está disponible
          if (image.dataset.srcset) {
            image.srcset = image.dataset.srcset;
          }
          
          image.classList.add('loaded');
          imageObserver.unobserve(image);
        }
      });
    });
    
    lazyImages.forEach(img => {
      imageObserver.observe(img);
    });
  } else {
    // Fallback para navegadores que no soportan Intersection Observer
    let active = false;
    
    const lazyLoad = () => {
      if (active === false) {
        active = true;
        
        setTimeout(() => {
          lazyImages.forEach(img => {
            if ((img.getBoundingClientRect().top <= window.innerHeight && img.getBoundingClientRect().bottom >= 0) && getComputedStyle(img).display !== 'none') {
              img.src = img.dataset.src;
              
              if (img.dataset.srcset) {
                img.srcset = img.dataset.srcset;
              }
              
              img.classList.add('loaded');
              
              lazyImages.forEach((image, index) => {
                if (image.classList.contains('loaded')) {
                  delete lazyImages[index];
                }
              });
              
              if (lazyImages.length === 0) {
                document.removeEventListener('scroll', lazyLoad);
                window.removeEventListener('resize', lazyLoad);
                window.removeEventListener('orientationchange', lazyLoad);
              }
            }
          });
          
          active = false;
        }, 200);
      }
    };
    
    document.addEventListener('scroll', lazyLoad);
    window.addEventListener('resize', lazyLoad);
    window.addEventListener('orientationchange', lazyLoad);
    lazyLoad();
  }
});