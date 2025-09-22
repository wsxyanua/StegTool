// Wire DOMContentLoaded bootstraps formerly in script.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize ImageConverter attempts and status log
    attemptInitialization();

    setTimeout(() => {
        const status = imageConverter ? 'READY' : 'FAILED';
        const color = imageConverter ? 'green' : 'red';
        console.log(`%cImageConverter Status: ${status}`, `color: ${color}; font-weight: bold;`);
        const statusText = document.getElementById('statusText');
        if (statusText && !imageConverter) {
            statusText.textContent = 'Image converter not available - some features may not work';
        }
    }, 2000);

    // Page skeleton then welcome toast
    skeletonLoader.show();
    setTimeout(() => {
        skeletonLoader.hide();
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
            const btn = document.getElementById('themeToggle');
            if (btn) btn.textContent = 'LIGHT';
        }
        setTimeout(() => { showToast('Welcome to Steganography v1.0!', 'success'); }, 500);
    }, 2000);
});


