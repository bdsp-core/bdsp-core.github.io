// Enhance team page image loading
document.addEventListener('DOMContentLoaded', function() {
  // Get all team member images
  const teamImages = document.querySelectorAll('#gridid img');
  
  // Add loaded class when images finish loading
  teamImages.forEach(function(img) {
    if (img.complete) {
      img.classList.add('loaded');
    } else {
      img.addEventListener('load', function() {
        this.classList.add('loaded');
      });
    }
    
    // Handle error cases
    img.addEventListener('error', function() {
      console.error('Failed to load image:', this.src);
      this.style.opacity = '0.5';
      this.style.backgroundColor = '#f0f0f0';
    });
  });
  
  // Intersection Observer for true lazy loading enhancement
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver(function(entries, observer) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.classList.add('loading');
          observer.unobserve(img);
        }
      });
    });
    
    teamImages.forEach(function(img) {
      imageObserver.observe(img);
    });
  }
});