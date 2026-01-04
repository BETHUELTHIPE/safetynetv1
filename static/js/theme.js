// Theme management for SafetyNet Reporting System
document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    const darkIcon = document.querySelector('.dark-icon');
    const lightIcon = document.querySelector('.light-icon');
    const themeText = document.querySelector('.theme-text');
    
    // Check for saved theme preference or use device preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Set initial theme
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (darkIcon) darkIcon.classList.add('d-none');
        if (lightIcon) lightIcon.classList.remove('d-none');
        if (themeText) themeText.textContent = 'Light Mode';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        if (darkIcon) darkIcon.classList.remove('d-none');
        if (lightIcon) lightIcon.classList.add('d-none');
        if (themeText) themeText.textContent = 'Dark Mode';
    }
    
    // Toggle theme when button is clicked
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            // Get current theme
            const currentTheme = document.documentElement.getAttribute('data-theme');
            let newTheme = '';
            
            // Toggle theme
            if (currentTheme === 'light') {
                newTheme = 'dark';
                darkIcon.classList.add('d-none');
                lightIcon.classList.remove('d-none');
                if (themeText) themeText.textContent = 'Light Mode';
            } else {
                newTheme = 'light';
                darkIcon.classList.remove('d-none');
                lightIcon.classList.add('d-none');
                if (themeText) themeText.textContent = 'Dark Mode';
            }
            
            // Apply new theme and save preference
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Dispatch custom event for other scripts that might need to know about theme changes
            document.dispatchEvent(new CustomEvent('themeChanged', { 
                detail: { theme: newTheme } 
            }));
        });
    }
});
