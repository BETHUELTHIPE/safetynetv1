/**
 * Performance optimization script for Kings Park CPF website
 * Implements lazy loading, code splitting, and performance monitoring
 */

// Lazy load images and iframes
document.addEventListener('DOMContentLoaded', function() {
    // Initialize lazy loading for images and iframes
    const lazyImages = [].slice.call(document.querySelectorAll('img.lazy, iframe.lazy'));
    
    if ('IntersectionObserver' in window) {
        let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    let lazyImage = entry.target;
                    if (lazyImage.dataset.src) {
                        lazyImage.src = lazyImage.dataset.src;
                        lazyImage.removeAttribute('data-src');
                    }
                    if (lazyImage.dataset.srcset) {
                        lazyImage.srcset = lazyImage.dataset.srcset;
                        lazyImage.removeAttribute('data-srcset');
                    }
                    lazyImage.classList.remove('lazy');
                    lazyImageObserver.unobserve(lazyImage);
                }
            });
        });
        
        lazyImages.forEach(function(lazyImage) {
            lazyImageObserver.observe(lazyImage);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        let active = false;
        
        const lazyLoad = function() {
            if (active === false) {
                active = true;
                
                setTimeout(function() {
                    lazyImages.forEach(function(lazyImage) {
                        if ((lazyImage.getBoundingClientRect().top <= window.innerHeight && lazyImage.getBoundingClientRect().bottom >= 0) && getComputedStyle(lazyImage).display !== 'none') {
                            if (lazyImage.dataset.src) {
                                lazyImage.src = lazyImage.dataset.src;
                                lazyImage.removeAttribute('data-src');
                            }
                            if (lazyImage.dataset.srcset) {
                                lazyImage.srcset = lazyImage.dataset.srcset;
                                lazyImage.removeAttribute('data-srcset');
                            }
                            lazyImage.classList.remove('lazy');
                            
                            lazyImages = lazyImages.filter(function(image) {
                                return image !== lazyImage;
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

// Implement efficient event handling
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Optimize scrolling events
const optimizedScroll = debounce(function() {
    // Handle scroll events efficiently
    const scrollPosition = window.scrollY;
    
    // Navbar visibility on scroll
    const navbar = document.querySelector('header');
    if (navbar) {
        if (scrollPosition > 100) {
            navbar.classList.add('compact');
        } else {
            navbar.classList.remove('compact');
        }
    }
    
    // Back to top button visibility
    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        if (scrollPosition > 300) {
            backToTop.classList.add('show');
        } else {
            backToTop.classList.remove('show');
        }
    }
}, 15); // Small delay to ensure smooth performance

// Attach optimized scroll event
window.addEventListener('scroll', optimizedScroll);

// Implement preloading for linked pages
document.addEventListener('DOMContentLoaded', function() {
    // Preload linked pages when hovering over links
    const preloadLinks = document.querySelectorAll('a.preload');
    
    preloadLinks.forEach(link => {
        link.addEventListener('mouseover', function() {
            const href = this.getAttribute('href');
            
            // Check if this link hasn't been preloaded yet
            if (!this.dataset.preloaded && href && !href.startsWith('#') && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
                const preloadLink = document.createElement('link');
                preloadLink.href = href;
                preloadLink.rel = 'prefetch';
                document.head.appendChild(preloadLink);
                this.dataset.preloaded = true;
            }
        });
    });
});

// Initial performance monitoring
if ('performance' in window && 'PerformanceObserver' in window) {
    // Create performance observer
    const perfObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
            // Log LCP (Largest Contentful Paint) metric
            if (entry.entryType === 'largest-contentful-paint') {
                console.log(`LCP: ${entry.startTime.toFixed(0)}ms`);
            }
            // Log FID (First Input Delay) metric
            if (entry.entryType === 'first-input') {
                console.log(`FID: ${entry.processingStart - entry.startTime}ms`);
            }
            // Log CLS (Cumulative Layout Shift) metric
            if (entry.entryType === 'layout-shift') {
                if (!entry.hadRecentInput) {
                    console.log(`CLS: ${entry.value}`);
                }
            }
        }
    });

    // Register for performance metrics
    perfObserver.observe({entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift']});
}
