/**
 * Carousel functionality for the homepage
 */
document.addEventListener('DOMContentLoaded', () => {
  const carousel = document.querySelector('.carousel');
  const slides = document.querySelectorAll('.carousel-slide');
  const dots = document.querySelectorAll('.carousel-dot');
  
  // Check if carousel exists on the page
  if (!carousel) return;
  
  let currentIndex = 0;
  const slideCount = slides.length;
  
  // Initialize carousel
  updateCarousel();
  
  // Auto advance slides every 5 seconds
  const interval = setInterval(() => {
    currentIndex = (currentIndex + 1) % slideCount;
    updateCarousel();
  }, 5000);
  
  // Add click event to dots for manual navigation
  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      currentIndex = index;
      updateCarousel();
      // Reset timer when manually navigating
      clearInterval(interval);
      setInterval(() => {
        currentIndex = (currentIndex + 1) % slideCount;
        updateCarousel();
      }, 5000);
    });
  });
  
  // Update carousel position and active dot
  function updateCarousel() {
    // Update carousel position
    carousel.style.transform = `translateX(-${currentIndex * 100}%)`;
    
    // Update active dot
    dots.forEach((dot, index) => {
      dot.classList.toggle('active', index === currentIndex);
    });
  }
});
