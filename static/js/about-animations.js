// Advanced animations for the About Us page

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations when DOM is fully loaded
    initializeAdvancedAnimations();
});

function initializeAdvancedAnimations() {
    // Setup scroll-triggered animations
    setupScrollAnimations();
    
    // Setup parallax effects
    setupParallaxEffects();
    
    // Setup particle background for hero
    setupParticleBackground();
    
    // Setup interactive elements
    setupInteractiveElements();
    
    // Setup counter animations for stats
    setupCounterAnimations();
    
    // Setup 3D card effects
    setup3DCardEffects();
}

// Scroll-triggered animations with IntersectionObserver API
function setupScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-fade-in, .animate-slide-up, .animate-slide-in-left, .animate-slide-in-right, .animate-scale-in');
    
    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Add class to trigger CSS animations
                entry.target.classList.add('animated');
                
                // For elements with sequence children, animate them in sequence
                if (entry.target.classList.contains('sequence-parent')) {
                    animateChildrenInSequence(entry.target);
                }
                
                scrollObserver.unobserve(entry.target);
            }
        });
    }, { 
        threshold: 0.2,
        rootMargin: '0px 0px -100px 0px'
    });
    
    animatedElements.forEach(element => {
        scrollObserver.observe(element);
    });
}

// Animate children elements in sequence
function animateChildrenInSequence(parent) {
    const children = parent.querySelectorAll('.sequence-child');
    children.forEach((child, index) => {
        setTimeout(() => {
            child.classList.add('animated');
        }, 150 * index);
    });
}

// Parallax scrolling effects
function setupParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.parallax');
    
    window.addEventListener('scroll', () => {
        const scrollPosition = window.pageYOffset;
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            const offset = scrollPosition * speed;
            element.style.transform = `translateY(${offset}px)`;
        });
    });
}

// Create particle background effect for hero section
function setupParticleBackground() {
    const heroSection = document.querySelector('.about-hero');
    if (!heroSection) return;
    
    // Create canvas element for particles
    const canvas = document.createElement('canvas');
    canvas.classList.add('particle-canvas');
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '0';
    
    // Insert canvas as first child of hero section
    heroSection.insertBefore(canvas, heroSection.firstChild);
    
    // Initialize particles
    initializeParticles(canvas);
}

// Initialize particle animation
function initializeParticles(canvas) {
    const ctx = canvas.getContext('2d');
    let particles = [];
    
    // Resize canvas to match parent dimensions
    function resizeCanvas() {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
    }
    
    // Create particles
    function createParticles() {
        particles = [];
        const particleCount = Math.floor(canvas.width * canvas.height / 10000);
        
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 2 + 1,
                color: 'rgba(255, 255, 255, ' + (Math.random() * 0.2 + 0.1) + ')',
                speedX: Math.random() * 0.5 - 0.25,
                speedY: Math.random() * 0.5 - 0.25
            });
        }
    }
    
    // Draw particles
    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            ctx.fillStyle = particle.color;
            ctx.fill();
            
            // Update particle position
            particle.x += particle.speedX;
            particle.y += particle.speedY;
            
            // Wrap particles around screen edges
            if (particle.x < 0) particle.x = canvas.width;
            if (particle.x > canvas.width) particle.x = 0;
            if (particle.y < 0) particle.y = canvas.height;
            if (particle.y > canvas.height) particle.y = 0;
        });
        
        // Draw connections between nearby particles
        drawConnections();
        
        requestAnimationFrame(drawParticles);
    }
    
    // Draw connections between close particles
    function drawConnections() {
        const maxDistance = 100;
        
        particles.forEach((particle1, i) => {
            for (let j = i + 1; j < particles.length; j++) {
                const particle2 = particles[j];
                const dx = particle1.x - particle2.x;
                const dy = particle1.y - particle2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < maxDistance) {
                    ctx.beginPath();
                    ctx.strokeStyle = 'rgba(255, 255, 255, ' + (0.2 - distance / maxDistance * 0.2) + ')';
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particle1.x, particle1.y);
                    ctx.lineTo(particle2.x, particle2.y);
                    ctx.stroke();
                }
            }
        });
    }
    
    // Initialize canvas and start animation
    resizeCanvas();
    createParticles();
    drawParticles();
    
    // Handle window resize
    window.addEventListener('resize', () => {
        resizeCanvas();
        createParticles();
    });
}

// Setup interactive elements with hover effects
function setupInteractiveElements() {
    const missionCards = document.querySelectorAll('.mission-icon');
    
    missionCards.forEach(card => {
        card.addEventListener('mousemove', handleMissionCardHover);
        card.addEventListener('mouseleave', resetMissionCard);
    });
    
    // Add mouse tracking to partnership section
    const partnershipSection = document.querySelector('.partnership-card');
    if (partnershipSection) {
        partnershipSection.addEventListener('mousemove', handlePartnershipHover);
        partnershipSection.addEventListener('mouseleave', resetPartnershipSection);
    }
}

// Handle hover effects for mission cards with 3D transform
function handleMissionCardHover(e) {
    const card = this;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const angleY = (x - centerX) / 10;
    const angleX = (centerY - y) / 10;
    
    card.style.transform = `perspective(800px) rotateX(${angleX}deg) rotateY(${angleY}deg) scale(1.05)`;
    card.style.boxShadow = `0 5px 15px rgba(0, 0, 0, 0.2), ${angleY * 0.5}px ${angleX * -0.5}px 10px rgba(0, 0, 0, 0.1)`;
}

// Reset mission card style when not hovering
function resetMissionCard() {
    this.style.transform = 'perspective(800px) rotateX(0) rotateY(0) scale(1)';
    this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.1)';
}

// Handle hover effect for partnership section
function handlePartnershipHover(e) {
    const section = this;
    const rect = section.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Calculate percentage position
    const percentX = x / rect.width;
    const percentY = y / rect.height;
    
    // Apply subtle gradient overlay based on mouse position
    section.style.backgroundImage = `
        linear-gradient(
            ${135 + percentX * 30}deg, 
            rgba(255, 255, 255, 0.9) 0%, 
            rgba(240, 240, 250, 0.9) 100%
        )
    `;
    
    // Add subtle shadow effect
    section.style.boxShadow = `
        0 10px 30px rgba(0, 0, 0, 0.1),
        ${(percentX - 0.5) * 20}px ${(percentY - 0.5) * 20}px 40px rgba(0, 0, 0, 0.05)
    `;
    
    // Move visual elements based on mouse position
    const visual = section.querySelector('.partnership-visual');
    if (visual) {
        visual.style.transform = `translateX(${(percentX - 0.5) * 10}px) translateY(${(percentY - 0.5) * 10}px)`;
    }
}

// Reset partnership section styles
function resetPartnershipSection() {
    this.style.backgroundImage = 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(240, 240, 250, 0.9) 100%)';
    this.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.1)';
    
    const visual = this.querySelector('.partnership-visual');
    if (visual) {
        visual.style.transform = 'translateX(0) translateY(0)';
    }
}

// Set up 3D card effects
function setup3DCardEffects() {
    const cards = document.querySelectorAll('.contact-card, .stat-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const angleY = (x - centerX) / 20;
            const angleX = (centerY - y) / 20;
            
            card.style.transform = `perspective(1000px) rotateX(${angleX}deg) rotateY(${angleY}deg) scale3d(1.02, 1.02, 1.02)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        });
    });
}

// Set up counter animations
function setupCounterAnimations() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    statNumbers.forEach(stat => {
        observer.observe(stat);
    });
}

// Animate counter from 0 to target number
function animateCounter(element) {
    const targetValue = parseInt(element.textContent);
    let currentValue = 0;
    const duration = 2000; // 2 seconds
    const stepTime = 16; // ~60fps
    const totalSteps = duration / stepTime;
    const stepValue = targetValue / totalSteps;
    
    // Check if the string contains a plus sign
    const hasPlus = element.textContent.includes('+');
    
    function step() {
        currentValue += stepValue;
        if (currentValue < targetValue) {
            element.textContent = hasPlus ? 
                Math.floor(currentValue) + '+' : 
                Math.floor(currentValue);
            requestAnimationFrame(step);
        } else {
            element.textContent = hasPlus ? 
                targetValue + '+' : 
                targetValue;
        }
    }
    
    requestAnimationFrame(step);
}
