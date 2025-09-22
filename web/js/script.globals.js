// Global state and ImageConverter bootstrap

// STEGANOGRAPHY v1.0

// Global variables for format conversion
let imageConverter = null;
let needsConversion = false;
let originalFile = null;
let convertedImageData = null;

// Global variables
let currentFile = null;
let currentFileType = null;
let currentImageData = null;

// Initialize ImageConverter when page loads
function initializeImageConverter() {
    try {
        if (typeof ImageConverter !== 'undefined') {
            imageConverter = new ImageConverter();
            console.log('ImageConverter initialized successfully');
            console.log('Supported input formats:', imageConverter.getSupportedInputFormats());
            console.log('Supported output formats:', imageConverter.getSupportedOutputFormats());
            return true;
        } else {
            console.warn('ImageConverter class not found');
            return false;
        }
    } catch (error) {
        console.error('Error initializing ImageConverter:', error);
        return false;
    }
}

// Multiple initialization attempts with progressive delays
let initAttempts = 0;
const maxAttempts = 5;

function attemptInitialization() {
    initAttempts++;
    console.log(`ImageConverter initialization attempt ${initAttempts}/${maxAttempts}`);

    if (initializeImageConverter()) {
        console.log('ImageConverter ready!');

        // Update any pending conversion UIs
        const convertButtons = document.querySelectorAll('#convertButton');
        convertButtons.forEach(btn => {
            if (btn.textContent === 'CONVERTER NOT READY') {
                btn.textContent = 'CONVERT FORMAT';
                btn.disabled = false;
                btn.style.background = '';
                btn.style.color = '';
            }
        });

        return;
    }

    if (initAttempts < maxAttempts) {
        const delay = initAttempts * 200; // Progressive delay: 200ms, 400ms, 600ms, etc.
        console.log(`Retrying in ${delay}ms...`);
        setTimeout(attemptInitialization, delay);
    } else {
        console.error('Failed to initialize ImageConverter after all attempts');
        // Don't show error toast immediately - wait for user interaction
    }
}

// Expose needed globals
window.initializeImageConverter = initializeImageConverter;
window.attemptInitialization = attemptInitialization;
window.imageConverter = imageConverter;
window.needsConversion = needsConversion;
window.originalFile = originalFile;
window.convertedImageData = convertedImageData;
window.currentFile = currentFile;
window.currentFileType = currentFileType;
window.currentImageData = currentImageData;


