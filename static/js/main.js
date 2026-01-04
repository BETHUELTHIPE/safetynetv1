// This file can be used for advanced JavaScript animations and interactions.
// For example, using GreenSock (GSAP) or other animation libraries.
// window.addEventListener('load', () => {
//     gsap.from(".hero h1", {duration: 1, y: -50, opacity: 0, ease: "power2.out"});
//     gsap.from(".hero p", {duration: 1, y: 50, opacity: 0, ease: "power2.out", delay: 0.5});
// });

document.addEventListener('DOMContentLoaded', function() {
    // Back to Top Button functionality
    const backToTopButton = document.getElementById('back-to-top');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) { // Show button after scrolling 300px
            backToTopButton.classList.add('show');
        } else {
            backToTopButton.classList.remove('show');
        }
    });

    backToTopButton.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' }); // Smooth scroll to top
    });
});
