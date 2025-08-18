// STEGANOGRAPHY v1.0

// Global variables for format conversion
let imageConverter = null;
let needsConversion = false;
let originalFile = null;
let convertedImageData = null;

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

// Start initialization when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    attemptInitialization();

    // Add converter status to page
    setTimeout(() => {
        const status = imageConverter ? 'READY' : 'FAILED';
        const color = imageConverter ? 'green' : 'red';
        console.log(`%cImageConverter Status: ${status}`, `color: ${color}; font-weight: bold;`);

        // Update status bar if available
        const statusText = document.getElementById('statusText');
        if (statusText && !imageConverter) {
            statusText.textContent = 'Image converter not available - some features may not work';
        }
    }, 2000);
});

// Format conversion utilities
class FormatConverter {
    static isSupportedFormat(mimeType) {
        const supportedFormats = ['image/png', 'image/bmp', 'image/tiff'];
        return supportedFormats.includes(mimeType);
    }

    static getFormatName(mimeType) {
        const formatMap = {
            'image/jpeg': 'JPEG',
            'image/jpg': 'JPEG',
            'image/png': 'PNG',
            'image/gif': 'GIF',
            'image/webp': 'WebP',
            'image/svg+xml': 'SVG',
            'image/bmp': 'BMP',
            'image/tiff': 'TIFF'
        };
        return formatMap[mimeType] || 'Unknown';
    }

    static async convertImage(file, targetFormat) {
        if (!imageConverter) {
            // Try to initialize converter one more time
            if (!initializeImageConverter()) {
                throw new Error('ImageConverter not available and failed to initialize');
            }
        }

        if (!file) {
            throw new Error('No file provided for conversion');
        }

        if (!file.type.startsWith('image/')) {
            throw new Error('File is not an image');
        }

        // Validate file size before conversion
        if (file.size > 50 * 1024 * 1024) { // 50MB limit
            throw new Error('File too large for conversion (max 50MB)');
        }

        try {
            console.log(`Converting ${file.name} (${file.type}) to ${targetFormat}`);
            const blob = await imageConverter.convert(file, targetFormat);

            // Validate converted blob
            if (!blob || blob.size === 0) {
                throw new Error('Conversion resulted in empty file');
            }

            // Additional validation
            if (blob.size > 100 * 1024 * 1024) { // 100MB limit for output
                throw new Error('Converted file too large');
            }

            console.log(`Conversion successful: ${blob.size} bytes`);
            return blob;
        } catch (error) {
            console.error('Conversion error:', error);
            throw new Error(`Conversion failed: ${error.message}`);
        }
    }

    static async blobToImageData(blob) {
        return new Promise((resolve, reject) => {
            if (!blob || blob.size === 0) {
                reject(new Error('Invalid blob data'));
                return;
            }

            const img = new Image();

            // Set timeout for image loading
            const timeout = setTimeout(() => {
                reject(new Error('Image loading timeout'));
            }, 10000); // 10 second timeout

            img.onload = function() {
                clearTimeout(timeout);
                try {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');

                    // Validate image dimensions
                    if (img.width <= 0 || img.height <= 0) {
                        reject(new Error('Invalid image dimensions'));
                        return;
                    }

                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);

                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

                    // Validate image data
                    if (!imageData || imageData.data.length === 0) {
                        reject(new Error('Failed to extract image data'));
                        return;
                    }

                    resolve(imageData);
                } catch (error) {
                    reject(new Error(`Canvas processing failed: ${error.message}`));
                }
            };

            img.onerror = () => {
                clearTimeout(timeout);
                reject(new Error('Failed to load converted image'));
            };

            img.src = URL.createObjectURL(blob);
        });
    }

    static validateFileSize(file, maxSizeMB = 50) {
        const maxSizeBytes = maxSizeMB * 1024 * 1024;
        if (file.size > maxSizeBytes) {
            throw new Error(`File too large. Maximum size: ${maxSizeMB}MB`);
        }
        return true;
    }

    static validateImageDimensions(width, height, maxDimension = 8192) {
        if (width > maxDimension || height > maxDimension) {
            throw new Error(`Image dimensions too large. Maximum: ${maxDimension}x${maxDimension}`);
        }
        return true;
    }
}

class SteganographyEngine {
    // LSB Steganography for Images
    static async encodeLSB(imageData, message, password = null) {
        if (password) {
            message = await CryptoEngine.encrypt(message, password);
            message = "ENC:" + message;
        }

        const binaryMessage = message.split('').map(char => 
            char.charCodeAt(0).toString(2).padStart(8, '0')
        ).join('') + '11111110'; // End marker

        if (binaryMessage.length > imageData.data.length) {
            throw new Error(`Message too long. Max: ${Math.floor(imageData.data.length / 8)} chars`);
        }

        const stegoData = new ImageData(
            new Uint8ClampedArray(imageData.data),
            imageData.width,
            imageData.height
        );

        // LSB encoding: modify least significant bit of each pixel channel
        let bitIndex = 0;
        for (let i = 0; i < stegoData.data.length && bitIndex < binaryMessage.length; i += 4) {
            if (bitIndex < binaryMessage.length) {
                const bit = parseInt(binaryMessage[bitIndex]);
                // Modify red channel (R)
                stegoData.data[i] = (stegoData.data[i] & 0xFE) | bit;
                bitIndex++;
            }
            
            if (bitIndex < binaryMessage.length) {
                const bit = parseInt(binaryMessage[bitIndex]);
                // Modify green channel (G)
                stegoData.data[i + 1] = (stegoData.data[i + 1] & 0xFE) | bit;
                bitIndex++;
            }
            
            if (bitIndex < binaryMessage.length) {
                const bit = parseInt(binaryMessage[bitIndex]);
                // Modify blue channel (B)
                stegoData.data[i + 2] = (stegoData.data[i + 2] & 0xFE) | bit;
                bitIndex++;
            }
            
            // Skip alpha channel (A) to preserve transparency
        }

        return stegoData;
    }

    static async decodeLSB(imageData, password = null) {
        let binaryMessage = "";
        
        // Extract LSB from RGB channels (skip alpha)
        for (let i = 0; i < imageData.data.length; i += 4) {
            // Extract from red channel (R)
            binaryMessage += (imageData.data[i] & 1).toString();
            
            // Extract from green channel (G)
            binaryMessage += (imageData.data[i + 1] & 1).toString();
            
            // Extract from blue channel (B)
            binaryMessage += (imageData.data[i + 2] & 1).toString();
            
            // Check for end marker
            if (binaryMessage.endsWith('11111110')) {
                binaryMessage = binaryMessage.slice(0, -8);
                
                let message = "";
                for (let j = 0; j < binaryMessage.length; j += 8) {
                    const byte = binaryMessage.slice(j, j + 8);
                    if (byte.length === 8) {
                        message += String.fromCharCode(parseInt(byte, 2));
                    }
                }
                
                if (message.startsWith("ENC:")) {
                    if (!password) throw new Error("Password required");
                    message = await CryptoEngine.decrypt(message.slice(4), password);
                }
                
                return message;
            }
        }
        
        throw new Error("No hidden message found");
    }

    // DCT Steganography - Simplified Frequency Domain Hiding
    static async encodeDCT(imageData, message, password = null) {
        if (password) {
            message = await CryptoEngine.encrypt(message, password);
            message = "ENC:" + message;
        }

        const binaryMessage = message.split('').map(char =>
            char.charCodeAt(0).toString(2).padStart(8, '0')
        ).join('') + '11111110'; // End marker

        const stegoData = new ImageData(
            new Uint8ClampedArray(imageData.data),
            imageData.width,
            imageData.height
        );

        // Simplified DCT: Use LSB on every 4th pixel to simulate frequency domain
        let bitIndex = 0;

        for (let i = 0; i < stegoData.data.length && bitIndex < binaryMessage.length; i += 16) { // Every 4th pixel
            const bit = parseInt(binaryMessage[bitIndex]);

            // Modify blue channel (less noticeable)
            const currentValue = stegoData.data[i + 2];
            stegoData.data[i + 2] = (currentValue & 0xFE) | bit;

            bitIndex++;
        }

        if (bitIndex < binaryMessage.length) {
            throw new Error(`Message too long for DCT. Max: ${Math.floor(stegoData.data.length / 64)} chars`);
        }

        return stegoData;
    }

    static async decodeDCT(imageData, password = null) {
        let binaryMessage = "";

        // Extract from every 4th pixel
        for (let i = 0; i < imageData.data.length; i += 16) {
            const bit = imageData.data[i + 2] & 1;
            binaryMessage += bit.toString();

            // Check for end marker
            if (binaryMessage.endsWith('11111110')) {
                binaryMessage = binaryMessage.slice(0, -8);

                let message = "";
                for (let j = 0; j < binaryMessage.length; j += 8) {
                    const byte = binaryMessage.slice(j, j + 8);
                    if (byte.length === 8) {
                        message += String.fromCharCode(parseInt(byte, 2));
                    }
                }

                if (message.startsWith("ENC:")) {
                    if (!password) {
                        throw new Error("Password required for encrypted message");
                    }
                    return await CryptoEngine.decrypt(message.slice(4), password);
                }

                return message;
            }
        }

        throw new Error("No hidden message found in DCT");
    }

    // DWT Steganography - Simplified Wavelet Domain Hiding
    static async encodeDWT(imageData, message, password = null) {
        if (password) {
            message = await CryptoEngine.encrypt(message, password);
            message = "ENC:" + message;
        }

        const binaryMessage = message.split('').map(char =>
            char.charCodeAt(0).toString(2).padStart(8, '0')
        ).join('') + '11111110'; // End marker

        const stegoData = new ImageData(
            new Uint8ClampedArray(imageData.data),
            imageData.width,
            imageData.height
        );

        // Simplified DWT: Use LSB on every 8th pixel to simulate wavelet domain
        let bitIndex = 0;

        for (let i = 0; i < stegoData.data.length && bitIndex < binaryMessage.length; i += 32) { // Every 8th pixel
            const bit = parseInt(binaryMessage[bitIndex]);

            // Modify green channel (middle frequency simulation)
            const currentValue = stegoData.data[i + 1];
            stegoData.data[i + 1] = (currentValue & 0xFE) | bit;

            bitIndex++;
        }

        if (bitIndex < binaryMessage.length) {
            throw new Error(`Message too long for DWT. Max: ${Math.floor(stegoData.data.length / 128)} chars`);
        }

        return stegoData;
    }

    static async decodeDWT(imageData, password = null) {
        let binaryMessage = "";

        // Extract from every 8th pixel
        for (let i = 0; i < imageData.data.length; i += 32) {
            const bit = imageData.data[i + 1] & 1;
            binaryMessage += bit.toString();

            // Check for end marker
            if (binaryMessage.endsWith('11111110')) {
                binaryMessage = binaryMessage.slice(0, -8);

                let message = "";
                for (let j = 0; j < binaryMessage.length; j += 8) {
                    const byte = binaryMessage.slice(j, j + 8);
                    if (byte.length === 8) {
                        message += String.fromCharCode(parseInt(byte, 2));
                    }
                }

                if (message.startsWith("ENC:")) {
                    if (!password) {
                        throw new Error("Password required for encrypted message");
                    }
                    return await CryptoEngine.decrypt(message.slice(4), password);
                }

                return message;
            }
        }

        throw new Error("No hidden message found in DWT");
    }










}

class CryptoEngine {
    static async encrypt(message, password) {
        const encoder = new TextEncoder();
        const data = encoder.encode(message);
        
        const keyMaterial = await crypto.subtle.importKey(
            'raw',
            encoder.encode(password),
            { name: 'PBKDF2' },
            false,
            ['deriveKey']
        );
        
        const key = await crypto.subtle.deriveKey(
            {
                name: 'PBKDF2',
                salt: encoder.encode('stego-salt-2024'),
                iterations: 100000,
                hash: 'SHA-256'
            },
            keyMaterial,
            { name: 'AES-GCM', length: 256 },
            false,
            ['encrypt']
        );
        
        const iv = crypto.getRandomValues(new Uint8Array(12));
        const encrypted = await crypto.subtle.encrypt(
            { name: 'AES-GCM', iv: iv },
            key,
            data
        );
        
        const combined = new Uint8Array(iv.length + encrypted.byteLength);
        combined.set(iv);
        combined.set(new Uint8Array(encrypted), iv.length);
        
        return btoa(String.fromCharCode(...combined));
    }

    static async decrypt(encryptedMessage, password) {
        try {
            const encoder = new TextEncoder();
            const decoder = new TextDecoder();
            
            const combined = new Uint8Array(
                atob(encryptedMessage).split('').map(char => char.charCodeAt(0))
            );
            
            const iv = combined.slice(0, 12);
            const encrypted = combined.slice(12);
            
            const keyMaterial = await crypto.subtle.importKey(
                'raw',
                encoder.encode(password),
                { name: 'PBKDF2' },
                false,
                ['deriveKey']
            );
            
            const key = await crypto.subtle.deriveKey(
                {
                    name: 'PBKDF2',
                    salt: encoder.encode('stego-salt-2024'),
                    iterations: 100000,
                    hash: 'SHA-256'
                },
                keyMaterial,
                { name: 'AES-GCM', length: 256 },
                false,
                ['decrypt']
            );
            
            const decrypted = await crypto.subtle.decrypt(
                { name: 'AES-GCM', iv: iv },
                key,
                encrypted
            );
            
            return decoder.decode(decrypted);
        } catch (error) {
            throw new Error("Invalid password or corrupted data");
        }
    }
}

class DigitalSignature {
    static async generateKeypair() {
        const keyPair = await crypto.subtle.generateKey(
            {
                name: 'ECDSA',
                namedCurve: 'P-256'
            },
            true,
            ['sign', 'verify']
        );

        const publicKey = await crypto.subtle.exportKey('spki', keyPair.publicKey);
        const privateKey = await crypto.subtle.exportKey('pkcs8', keyPair.privateKey);

        return {
            publicKey: btoa(String.fromCharCode(...new Uint8Array(publicKey))),
            privateKey: btoa(String.fromCharCode(...new Uint8Array(privateKey)))
        };
    }

    static async signMessage(message, privateKeyStr) {
        try {
            const encoder = new TextEncoder();
            const data = encoder.encode(message);

            const privateKeyBuffer = new Uint8Array(
                atob(privateKeyStr).split('').map(char => char.charCodeAt(0))
            );

            const privateKey = await crypto.subtle.importKey(
                'pkcs8',
                privateKeyBuffer,
                {
                    name: 'ECDSA',
                    namedCurve: 'P-256'
                },
                false,
                ['sign']
            );

            const signature = await crypto.subtle.sign(
                {
                    name: 'ECDSA',
                    hash: 'SHA-256'
                },
                privateKey,
                data
            );

            return btoa(String.fromCharCode(...new Uint8Array(signature)));
        } catch (error) {
            throw new Error("Failed to sign message: " + error.message);
        }
    }

    static async verifySignature(message, signatureStr, publicKeyStr) {
        try {
            const encoder = new TextEncoder();
            const data = encoder.encode(message);

            const signatureBuffer = new Uint8Array(
                atob(signatureStr).split('').map(char => char.charCodeAt(0))
            );

            const publicKeyBuffer = new Uint8Array(
                atob(publicKeyStr).split('').map(char => char.charCodeAt(0))
            );

            const publicKey = await crypto.subtle.importKey(
                'spki',
                publicKeyBuffer,
                {
                    name: 'ECDSA',
                    namedCurve: 'P-256'
                },
                false,
                ['verify']
            );

            const isValid = await crypto.subtle.verify(
                {
                    name: 'ECDSA',
                    hash: 'SHA-256'
                },
                publicKey,
                signatureBuffer,
                data
            );

            return isValid;
        } catch (error) {
            throw new Error("Failed to verify signature: " + error.message);
        }
    }
}

class PasswordStrength {
    static analyze(password) {
        if (!password) return { score: 0, text: "NO PASSWORD", color: "#666666" };

        let score = 0;
        const checks = {
            length: password.length >= 8,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            numbers: /\d/.test(password),
            symbols: /[^A-Za-z0-9]/.test(password),
            longLength: password.length >= 12
        };

        score += checks.length ? 20 : 0;
        score += checks.lowercase ? 15 : 0;
        score += checks.uppercase ? 15 : 0;
        score += checks.numbers ? 15 : 0;
        score += checks.symbols ? 20 : 0;
        score += checks.longLength ? 15 : 0;

        let text, color;
        if (score < 30) {
            text = "WEAK";
            color = "#ff0000";
        } else if (score < 60) {
            text = "MEDIUM";
            color = "#ff8800";
        } else if (score < 80) {
            text = "STRONG";
            color = "#00aa00";
        } else {
            text = "VERY STRONG";
            color = "#00ff00";
        }

        return { score, text, color };
    }
}

// Global variables
let currentFile = null;
let currentFileType = null;
let currentImageData = null;

// UI Functions

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
    } else {
        sidebar.classList.add('open');
        overlay.classList.add('show');
    }
}

// Professional Loading System
class LoadingManager {
    constructor() {
        this.overlay = document.getElementById('loadingOverlay');
        this.text = document.getElementById('loadingText');
        this.progressBar = document.getElementById('loadingProgressBar');
        this.steps = document.getElementById('loadingSteps');
        this.currentStep = 0;
        this.progress = 0;
        this.isActive = false;
    }

    show(operation = 'PROCESSING') {
        if (this.isActive) return;

        this.isActive = true;
        this.currentStep = 0;
        this.progress = 0;

        this.text.textContent = operation;
        this.progressBar.style.width = '0%';
        this.overlay.classList.add('show');

        // Start progress simulation
        this.simulateProgress();
    }

    hide() {
        if (!this.isActive) return;

        this.isActive = false;
        this.overlay.classList.remove('show');
        this.progress = 0;
        this.currentStep = 0;
    }

    updateStep(message) {
        if (!this.isActive) return;
        this.steps.textContent = message;
    }

    updateProgress(percent) {
        if (!this.isActive) return;
        this.progress = Math.min(100, Math.max(0, percent));
        this.progressBar.style.width = this.progress + '%';
    }

    simulateProgress() {
        if (!this.isActive) return;

        const steps = [
            { message: 'Initializing...', duration: 300 },
            { message: 'Loading image data...', duration: 500 },
            { message: 'Analyzing pixels...', duration: 400 },
            { message: 'Processing algorithm...', duration: 600 },
            { message: 'Encoding message...', duration: 500 },
            { message: 'Finalizing...', duration: 300 }
        ];

        let totalDuration = 0;
        let currentProgress = 0;

        steps.forEach((step, index) => {
            setTimeout(() => {
                if (!this.isActive) return;

                this.updateStep(step.message);
                const targetProgress = ((index + 1) / steps.length) * 100;

                // Smooth progress animation
                const progressInterval = setInterval(() => {
                    if (!this.isActive) {
                        clearInterval(progressInterval);
                        return;
                    }

                    currentProgress += 2;
                    if (currentProgress >= targetProgress) {
                        currentProgress = targetProgress;
                        clearInterval(progressInterval);
                    }
                    this.updateProgress(currentProgress);
                }, 20);

            }, totalDuration);

            totalDuration += step.duration;
        });
    }
}

// Initialize loading manager
const loadingManager = new LoadingManager();

// Skeleton Loading Manager
class SkeletonLoader {
    constructor() {
        this.skeletonContainer = document.getElementById('skeletonContainer');
        this.mainContainer = document.getElementById('mainContainer');
    }

    show() {
        if (this.skeletonContainer && this.mainContainer) {
            this.skeletonContainer.style.display = 'block';
            this.mainContainer.style.display = 'none';
        }
    }

    hide() {
        if (this.skeletonContainer && this.mainContainer) {
            this.skeletonContainer.style.display = 'none';
            this.mainContainer.style.display = 'flex';
        }
    }

    showSection(sectionSelector) {
        const section = document.querySelector(sectionSelector);
        if (section) {
            section.classList.add('loading-skeleton');

            // Add skeleton elements
            const elements = section.querySelectorAll('input, textarea, button, label');
            elements.forEach(el => {
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    const skeleton = document.createElement('div');
                    skeleton.className = el.tagName === 'TEXTAREA' ? 'skeleton skeleton-textarea' : 'skeleton skeleton-input';
                    el.parentNode.insertBefore(skeleton, el);
                } else if (el.tagName === 'BUTTON') {
                    const skeleton = document.createElement('div');
                    skeleton.className = 'skeleton skeleton-button';
                    el.parentNode.insertBefore(skeleton, el);
                }
            });
        }
    }

    hideSection(sectionSelector) {
        const section = document.querySelector(sectionSelector);
        if (section) {
            section.classList.remove('loading-skeleton');

            // Remove skeleton elements
            const skeletons = section.querySelectorAll('.skeleton');
            skeletons.forEach(skeleton => skeleton.remove());
        }
    }
}

// Initialize skeleton loader
const skeletonLoader = new SkeletonLoader();

// Page Loading with Skeleton
document.addEventListener('DOMContentLoaded', function() {
    // Show skeleton initially
    skeletonLoader.show();

    // Simulate page loading
    setTimeout(() => {
        skeletonLoader.hide();

        // Initialize theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.setAttribute('data-theme', 'dark');
            document.getElementById('themeToggle').textContent = 'LIGHT';
        }

        // Show welcome message
        setTimeout(() => {
            showToast('Welcome to Steganography v1.0!', 'success');
        }, 500);

    }, 2000); // 2 second skeleton loading
});



function showTab(tabName, element) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    document.getElementById(tabName).classList.add('active');
    if (element) {
        element.classList.add('active');
    }

    // Reset file inputs when switching tabs
    resetFileInputs();
}

function resetFileInputs() {
    // Don't clear file inputs and previews - keep them when switching tabs
    // Only clear messages
    document.getElementById('messageText').value = '';
    document.getElementById('resultText').value = '';

    // Update buttons based on current file state
    const hasFile = currentImageData !== null && !needsConversion;
    document.getElementById('encodeButton').disabled = !hasFile;
    document.getElementById('decodeButton').disabled = !hasFile;

    // Hide download button when switching tabs
    const downloadBtn = document.getElementById('encodeDownloadBtn');
    if (downloadBtn) {
        downloadBtn.style.display = 'none';
    }

    // Sync file inputs and previews between tabs
    if (hasFile && currentFile) {
        syncFileInputsAndPreviews();
    }
}

function syncFileInputsAndPreviews() {
    if (!currentImageData) return;

    try {
        // Update capacity info if available
        const capacityInfo = document.getElementById('encodeCapacity');
        if (capacityInfo && currentImageData.width && currentImageData.height) {
            const capacity = Math.floor((currentImageData.width * currentImageData.height * 3) / 8);
            const formatInfo = convertedImageData ? ' (Converted)' : '';
            capacityInfo.innerHTML = `<strong>CAPACITY:</strong> ~${capacity} characters (${currentImageData.width}x${currentImageData.height})${formatInfo}`;
        }

        // Update max chars counter
        const maxCharsElement = document.getElementById('maxChars');
        if (maxCharsElement && currentImageData) {
            const maxChars = Math.floor((currentImageData.data.length) / 8) - 1;
            maxCharsElement.textContent = maxChars.toLocaleString();
        }

        // Update character count display
        const messageText = document.getElementById('messageText');
        const charCount = document.getElementById('charCount');
        if (messageText && charCount) {
            charCount.textContent = messageText.value.length.toLocaleString();
        }

    } catch (error) {
        console.error('Error syncing file previews:', error);
    }
}

// Handle method tab switching and drag & drop
document.addEventListener('DOMContentLoaded', function() {
    // Add click handlers for method tabs
    document.querySelectorAll('.method-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;

                // Update active state
                document.querySelectorAll('.method-tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });

    // Add drag & drop to file input labels
    document.querySelectorAll('.file-input-label').forEach(label => {
        const input = label.querySelector('input[type="file"]');

        label.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');

            // Check if file type is valid
            const items = e.dataTransfer.items;
            let isValid = false;
            for (let item of items) {
                if (item.type.startsWith('image/')) {
                    isValid = true;
                    break;
                }
            }

            this.classList.toggle('drag-valid', isValid);
            this.classList.toggle('drag-invalid', !isValid);
        });

        label.addEventListener('dragleave', function(e) {
            if (!this.contains(e.relatedTarget)) {
                this.classList.remove('drag-over', 'drag-valid', 'drag-invalid');
            }
        });

        label.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over', 'drag-valid', 'drag-invalid');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type.startsWith('image/')) {
                    // Set the file to the input
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    input.files = dt.files;

                    // Trigger change event
                    const event = new Event('change', { bubbles: true });
                    input.dispatchEvent(event);
                } else {
                    showToast('Please drop an image file', 'error');
                }
            }
        });
    });
});

function resetUploadState() {
    // Hide format conversion UI
    hideFormatConversion();

    // Hide download button
    const downloadBtn = document.getElementById('encodeDownloadBtn');
    if (downloadBtn) {
        downloadBtn.style.display = 'none';
        downloadBtn.disabled = true;
    }

    // Clear previous results
    document.getElementById('resultText').value = '';

    // Reset global state
    needsConversion = false;
    convertedImageData = null;
    currentImageData = null;

    // Clear previews
    document.getElementById('encodePreview').innerHTML = '';
    document.getElementById('decodePreview').innerHTML = '';
    document.getElementById('encodeCapacity').innerHTML = '';
}

function updateStatus(text, fileInfo = '') {
    document.getElementById('statusText').textContent = text;
    document.getElementById('fileInfo').textContent = fileInfo;
}

function updateProgress(percentage, text = 'PROCESSING') {
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');

    if (progressFill) progressFill.style.width = percentage + '%';
    if (progressText) progressText.textContent = text;
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

async function handleFileUpload(input, type) {
    const file = input.files[0];
    if (!file) return;

    // Reset previous state
    resetUploadState();

    // Show skeleton loading for file section
    const fileSection = type === 'encode' ? '.file-section' : '.decode-file-section';
    skeletonLoader.showSection(fileSection);

    // Show loading for file processing
    loadingManager.show('LOADING FILE');
    loadingManager.updateStep('Reading file data...');

    currentFile = file;
    originalFile = file;
    needsConversion = false;
    convertedImageData = null;

    try {
        // Validate file size first
        FormatConverter.validateFileSize(file, 50);

        if (file.type.startsWith('image/')) {
            currentFileType = 'image';

            // Check if format conversion is needed for encoding
            if (type === 'encode' && !FormatConverter.isSupportedFormat(file.type)) {
                if (imageConverter) {
                    needsConversion = true;
                    showFormatConversion(file);
                    loadingManager.hide();
                    skeletonLoader.hideSection(fileSection);
                    updateStatus('CONVERSION NEEDED', `${file.name} - Convert to supported format`);
                    return;
                } else {
                    // Fallback: try to process anyway and show warning
                    console.warn('Converter not available, attempting to process unsupported format');
                    showToast(`Warning: ${FormatConverter.getFormatName(file.type)} format may not work properly`, 'warning');
                }
            }

            await handleImageUpload(file, type);

            // Sync file inputs between tabs after successful upload
            syncFileInputsAndPreviews();

        } else {
            throw new Error('Unsupported file type');
        }

        loadingManager.updateStep('File loaded successfully!');
        await new Promise(resolve => setTimeout(resolve, 500));
        loadingManager.hide();
        skeletonLoader.hideSection(fileSection);

        updateStatus('FILE LOADED', `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);

    } catch (error) {
        console.error('File upload error:', error);
        loadingManager.hide();
        skeletonLoader.hideSection(fileSection);
        showToast(`Error: ${error.message}`, 'error');

        // Reset state on error
        currentFile = null;
        currentImageData = null;
        originalFile = null;
        needsConversion = false;
        convertedImageData = null;
    }
}

async function handleImageUpload(file, type) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const img = new Image();
        img.onload = function() {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);

            currentImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

            const previewId = type === 'encode' ? 'encodePreview' : 'decodePreview';
            const preview = document.getElementById(previewId);
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;

            if (type === 'encode') {
                calculateImageCapacity();
                document.getElementById('encodeButton').disabled = false;
            } else {
                document.getElementById('decodeButton').disabled = false;
            }
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}





function calculateImageCapacity() {
    if (!currentImageData) return;

    const maxBits = currentImageData.data.length;
    const maxChars = Math.floor(maxBits / 8) - 1;

    document.getElementById('encodeCapacity').innerHTML =
        `CAPACITY: ${maxChars.toLocaleString()} characters (${currentImageData.width}x${currentImageData.height})`;

    document.getElementById('maxChars').textContent = maxChars.toLocaleString();
}





function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;

    if (input.type === 'password') {
        input.type = 'text';
        button.textContent = 'HIDE';
    } else {
        input.type = 'password';
        button.textContent = 'SHOW';
    }
}

// Skeleton Loading Control
function showSkeleton() {
    document.getElementById('skeletonContainer').style.display = 'block';
    document.getElementById('mainContainer').style.display = 'none';
}

function hideSkeleton() {
    const skeletonContainer = document.getElementById('skeletonContainer');
    const mainContainer = document.getElementById('mainContainer');
    
    skeletonContainer.classList.add('fade-out');
    
    setTimeout(() => {
        skeletonContainer.style.display = 'none';
        mainContainer.style.display = 'block';
        mainContainer.style.opacity = '0';
        
        setTimeout(() => {
            mainContainer.style.opacity = '1';
        }, 100);
    }, 750);
}

// Format Conversion Functions
function showFormatConversion(file) {
    const formatConversion = document.getElementById('formatConversion');
    const originalFormat = document.getElementById('originalFormat');

    if (formatConversion && originalFormat) {
        originalFormat.textContent = FormatConverter.getFormatName(file.type);
        formatConversion.style.display = 'block';

        // Reset conversion state
        needsConversion = true;
        convertedImageData = null;

        // Disable encode button until conversion
        document.getElementById('encodeButton').disabled = true;

        // Check converter availability and show warning if needed
        if (!imageConverter) {
            const convertButton = document.getElementById('convertButton');
            if (convertButton) {
                convertButton.textContent = 'CONVERTER NOT READY';
                convertButton.disabled = true;
                convertButton.style.background = '#666666';
                convertButton.style.color = '#cccccc';
            }

            showToast('Image converter loading... Please wait', 'warning');

            // Try to initialize and update UI when ready
            setTimeout(() => {
                if (imageConverter && convertButton) {
                    convertButton.textContent = 'CONVERT FORMAT';
                    convertButton.disabled = false;
                    convertButton.style.background = '';
                    convertButton.style.color = '';
                    showToast('Converter ready!', 'success');
                }
            }, 1000);
        }
    }
}

function hideFormatConversion() {
    const formatConversion = document.getElementById('formatConversion');
    if (formatConversion) {
        formatConversion.style.display = 'none';
    }
}

async function convertImageFormat() {
    if (!originalFile) {
        showToast('No file selected for conversion', 'error');
        return;
    }

    // Try to initialize converter if not available
    if (!imageConverter) {
        console.log('ImageConverter not available, attempting initialization...');

        // Try multiple times with delays
        let attempts = 0;
        const maxAttempts = 3;

        while (attempts < maxAttempts && !imageConverter) {
            attempts++;
            console.log(`Initialization attempt ${attempts}/${maxAttempts}`);

            if (initializeImageConverter()) {
                break;
            }

            if (attempts < maxAttempts) {
                await new Promise(resolve => setTimeout(resolve, 300));
            }
        }

        if (!imageConverter) {
            showToast('Image converter not available. Please refresh the page.', 'error');
            console.error('ImageConverter failed to initialize after multiple attempts');
            return;
        }
    }

    const targetFormat = document.getElementById('targetFormat').value;
    const convertButton = document.getElementById('convertButton');
    const conversionProgress = document.getElementById('conversionProgress');

    try {
        // Show progress
        convertButton.disabled = true;
        convertButton.textContent = 'CONVERTING...';
        conversionProgress.style.display = 'block';

        // Show loading overlay
        loadingManager.show('CONVERTING IMAGE');
        loadingManager.updateStep(`Converting ${FormatConverter.getFormatName(originalFile.type)} to ${targetFormat}...`);

        // Validate file before conversion
        FormatConverter.validateFileSize(originalFile, 50); // 50MB limit

        // Convert image
        loadingManager.updateStep('Processing image data...');
        const convertedBlob = await FormatConverter.convertImage(originalFile, targetFormat);

        // Convert blob to ImageData
        loadingManager.updateStep('Extracting pixel data...');
        convertedImageData = await FormatConverter.blobToImageData(convertedBlob);

        // Validate converted image dimensions
        FormatConverter.validateImageDimensions(
            convertedImageData.width,
            convertedImageData.height,
            8192 // 8K limit
        );

        // Update global state
        currentImageData = convertedImageData;
        needsConversion = false;

        // Hide conversion UI
        hideFormatConversion();

        // Update preview with converted image
        const preview = document.getElementById('encodePreview');
        const url = URL.createObjectURL(convertedBlob);
        preview.innerHTML = `<img src="${url}" alt="Converted Preview" style="max-width: 100%; max-height: 150px; border: 1px solid var(--border);">`;

        // Sync previews to decode tab as well
        document.getElementById('decodePreview').innerHTML = preview.innerHTML;

        // Calculate capacity and enable buttons
        calculateImageCapacity();
        document.getElementById('encodeButton').disabled = false;
        document.getElementById('decodeButton').disabled = false;

        // Sync previews and capacity info
        syncFileInputsAndPreviews();

        // Update status
        updateStatus('CONVERSION COMPLETE', `Converted to ${targetFormat} - Ready for steganography`);
        showToast(`Successfully converted to ${targetFormat}`, 'success');

        // Clean up URL after a delay
        setTimeout(() => URL.revokeObjectURL(url), 5000);

    } catch (error) {
        console.error('Conversion error:', error);
        showToast(`Conversion failed: ${error.message}`, 'error');

        // Reset state on error
        convertedImageData = null;
        needsConversion = true;

    } finally {
        // Hide progress and reset button
        loadingManager.hide();
        conversionProgress.style.display = 'none';
        convertButton.disabled = false;
        convertButton.textContent = 'CONVERT FORMAT';
    }
}

// Fake Loading Control
function showFakeLoading(type) {
    const fakeLoading = document.getElementById(type + 'FakeLoading');
    if (fakeLoading) {
        fakeLoading.style.display = 'block';
    }
}

function hideFakeLoading(type) {
    const fakeLoading = document.getElementById(type + 'FakeLoading');
    if (fakeLoading) {
        fakeLoading.style.display = 'none';
        fakeLoading.classList.remove('fade-out');
    }
}

// Password strength monitoring
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide skeleton after 0.8 second
    setTimeout(() => {
        hideSkeleton();
    }, 800);

    const messageText = document.getElementById('messageText');
    const charCount = document.getElementById('charCount');
    const encodePassword = document.getElementById('encodePassword');

    if (messageText && charCount) {
        messageText.addEventListener('input', function() {
            charCount.textContent = this.value.length.toLocaleString();
        });
    }

    if (encodePassword) {
        encodePassword.addEventListener('input', function() {
            const strength = PasswordStrength.analyze(this.value);
            const strengthBar = document.querySelector('.strength-bar');
            const strengthText = document.querySelector('.strength-text');

            if (strengthBar && strengthText) {
                strengthBar.style.width = strength.score + '%';
                strengthBar.style.backgroundColor = strength.color;
                strengthText.textContent = strength.text;
                strengthText.style.color = strength.color;
            }
        });
    }

    // Initialize advanced drag & drop
    initializeDragAndDrop();
});

// Advanced Drag & Drop Implementation
function initializeDragAndDrop() {
    const dropZones = document.querySelectorAll('.file-input-label');

    dropZones.forEach(dropZone => {
        const fileInput = dropZone.parentElement.querySelector('input[type="file"]');

        // Add file type indicator
        const indicator = document.createElement('div');
        indicator.className = 'file-type-indicator';
        indicator.textContent = 'IMG';
        dropZone.appendChild(indicator);

        // Drag events
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                const isValid = isValidFileType(file);

                dropZone.classList.add('drag-over');
                dropZone.classList.toggle('drag-valid', isValid);
                dropZone.classList.toggle('drag-invalid', !isValid);

                // Update indicator
                indicator.textContent = getFileTypeLabel(file);
                indicator.style.backgroundColor = isValid ? '#00ff00' : '#ff0000';
            }
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();

            // Only remove classes if we're leaving the drop zone entirely
            if (!dropZone.contains(e.relatedTarget)) {
                dropZone.classList.remove('drag-over', 'drag-valid', 'drag-invalid');
                indicator.textContent = 'IMG/AUD';
                indicator.style.backgroundColor = '';
            }
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();

            dropZone.classList.remove('drag-over', 'drag-valid', 'drag-invalid');
            indicator.textContent = 'IMG/AUD';
            indicator.style.backgroundColor = '';

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];

                if (isValidFileType(file)) {
                    // Simulate file input change
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    fileInput.files = dt.files;

                    // Trigger change event
                    const event = new Event('change', { bubbles: true });
                    fileInput.dispatchEvent(event);

                    showToast(`FILE LOADED: ${file.name}`, 'success');
                } else {
                    showToast('UNSUPPORTED FILE TYPE', 'error');
                }
            }
        });
    });
}

function isValidFileType(file) {
    const validTypes = [
        // Images
        'image/png', 'image/bmp', 'image/tiff', 'image/jpeg', 'image/jpg'
    ];

    return validTypes.includes(file.type) ||
           validTypes.some(type => file.name.toLowerCase().endsWith(type.split('/')[1]));
}

function getFileTypeLabel(file) {
    if (file.type.startsWith('image/')) return 'IMG';
    return 'UNK';
}

// Settings Export/Import System
class SettingsManager {
    static async exportSettings() {
        try {
            const settings = {
                version: '1.0',
                timestamp: new Date().toISOString(),
                passwords: {
                    encode: document.getElementById('encodePassword')?.value || '',
                    decode: document.getElementById('decodePassword')?.value || ''
                },
                preferences: {
                    defaultMethod: document.querySelector('input[name="stegoMethod"]:checked')?.value || 'lsb',
                    autoSave: true,
                    showAdvanced: false
                },
                recentFiles: JSON.parse(localStorage.getItem('steganography-recent') || '[]'),
                customSettings: JSON.parse(localStorage.getItem('steganography-custom') || '{}')
            };

            // Encrypt sensitive data
            const masterPassword = prompt('Enter master password to encrypt settings:');
            if (!masterPassword) {
                showToast('EXPORT CANCELLED', 'error');
                return;
            }

            const encryptedSettings = await CryptoEngine.encrypt(JSON.stringify(settings), masterPassword);

            const exportData = {
                app: 'Steganography Re-birth',
                version: '1.0',
                encrypted: true,
                data: encryptedSettings
            };

            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `steganography-settings-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            showToast('SETTINGS EXPORTED SUCCESSFULLY', 'success');
        } catch (error) {
            showToast('EXPORT FAILED: ' + error.message, 'error');
        }
    }

    static async importSettings() {
        try {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';

            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;

                const text = await file.text();
                const importData = JSON.parse(text);

                if (!importData.app || importData.app !== 'Steganography Re-birth') {
                    showToast('INVALID SETTINGS FILE', 'error');
                    return;
                }

                if (importData.encrypted) {
                    const masterPassword = prompt('Enter master password to decrypt settings:');
                    if (!masterPassword) {
                        showToast('IMPORT CANCELLED', 'error');
                        return;
                    }

                    try {
                        const decryptedData = await CryptoEngine.decrypt(importData.data, masterPassword);
                        const settings = JSON.parse(decryptedData);

                        await this.applySettings(settings);
                        showToast('SETTINGS IMPORTED SUCCESSFULLY', 'success');
                    } catch (error) {
                        showToast('WRONG PASSWORD OR CORRUPTED FILE', 'error');
                    }
                } else {
                    await this.applySettings(importData);
                    showToast('SETTINGS IMPORTED SUCCESSFULLY', 'success');
                }
            };

            input.click();
        } catch (error) {
            showToast('IMPORT FAILED: ' + error.message, 'error');
        }
    }

    static async applySettings(settings) {
        // Apply passwords (if user confirms)
        if (settings.passwords) {
            const applyPasswords = confirm('Import saved passwords? (They will overwrite current passwords)');
            if (applyPasswords) {
                if (settings.passwords.encode) {
                    document.getElementById('encodePassword').value = settings.passwords.encode;
                }
                if (settings.passwords.decode) {
                    document.getElementById('decodePassword').value = settings.passwords.decode;
                }
            }
        }

        // Apply method preference
        if (settings.preferences?.defaultMethod) {
            const methodRadio = document.querySelector(`input[name="stegoMethod"][value="${settings.preferences.defaultMethod}"]`);
            if (methodRadio) methodRadio.checked = true;
        }

        // Apply recent files
        if (settings.recentFiles) {
            localStorage.setItem('steganography-recent', JSON.stringify(settings.recentFiles));
        }

        // Apply custom settings
        if (settings.customSettings) {
            localStorage.setItem('steganography-custom', JSON.stringify(settings.customSettings));
        }
    }
}

// Global functions for HTML onclick
function exportSettings() {
    SettingsManager.exportSettings();
}

function importSettings() {
    SettingsManager.importSettings();
}

// Main encode/decode functions
async function encodeMessage() {
    if (!currentFile) {
        showToast('SELECT A FILE FIRST', 'error');
        return;
    }

    const message = document.getElementById('messageText').value.trim();
    if (!message) {
        showToast('ENTER A MESSAGE', 'error');
        return;
    }

    const password = document.getElementById('encodePassword').value.trim() || null;
    const method = document.querySelector('input[name="stegoMethod"]:checked').value;

    try {
        // Reset download button
        const downloadBtn = document.getElementById('encodeDownloadBtn');
        if (downloadBtn) {
            downloadBtn.style.display = 'none';
            downloadBtn.disabled = true;
        }
        
        // Show professional loading
        loadingManager.show('ENCODING MESSAGE');

        // Add processing dots to button
        const encodeBtn = document.getElementById('encodeButton');
        const originalText = encodeBtn.textContent;
        encodeBtn.textContent = 'PROCESSING';
        encodeBtn.classList.add('processing-dots');
        encodeBtn.disabled = true;

        // Simulate processing time with realistic steps
        await new Promise(resolve => setTimeout(resolve, 2500));

        // Restore button
        encodeBtn.textContent = originalText;
        encodeBtn.classList.remove('processing-dots');
        encodeBtn.disabled = false;

        loadingManager.hide();
        
        document.getElementById('encodeProgress').style.display = 'block';
        updateProgress(10, 'PREPARING');

        await new Promise(resolve => setTimeout(resolve, 100));

        let result;
        updateProgress(50, 'ENCODING');

        if (currentFileType === 'image') {
            // Use converted image data if available, otherwise use original
            const imageDataToUse = convertedImageData || currentImageData;

            if (!imageDataToUse) {
                throw new Error('No valid image data available. Please convert format first if needed.');
            }

            // Validate image data integrity
            if (!imageDataToUse.data || imageDataToUse.data.length === 0) {
                throw new Error('Image data is corrupted or empty');
            }

            if (imageDataToUse.width <= 0 || imageDataToUse.height <= 0) {
                throw new Error('Invalid image dimensions');
            }

            // Check if image data size matches expected size
            const expectedSize = imageDataToUse.width * imageDataToUse.height * 4;
            if (imageDataToUse.data.length !== expectedSize) {
                throw new Error(`Image data size mismatch. Expected: ${expectedSize}, Got: ${imageDataToUse.data.length}`);
            }

            // Debug logging
            console.log(`Encoding with method: ${method}`);
            console.log(`Image data dimensions: ${imageDataToUse.width}x${imageDataToUse.height}`);
            console.log(`Message length: ${message.length} characters`);
            console.log(`Image data length: ${imageDataToUse.data.length} pixels`);
            console.log(`Using converted data: ${!!convertedImageData}`);
            
            switch (method) {
                case 'lsb':
                    console.log('Using LSB method...');
                    result = await SteganographyEngine.encodeLSB(imageDataToUse, message, password);
                    break;
                case 'dct':
                    console.log('Using DCT method...');
                    result = await SteganographyEngine.encodeDCT(imageDataToUse, message, password);
                    break;
                case 'dwt':
                    console.log('Using DWT method...');
                    result = await SteganographyEngine.encodeDWT(imageDataToUse, message, password);
                    break;
                default:
                    throw new Error(`Unknown method: ${method}`);
            }
            
            console.log('Encoding completed successfully');
            console.log(`Result dimensions: ${result.width}x${result.height}`);
        }

        updateProgress(80, 'CREATING FILE');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = result.width;
        canvas.height = result.height;
        ctx.putImageData(result, 0, 0);

        updateProgress(100, 'DONE');

        // Create blob and store for manual download
        const targetFormat = needsConversion ? document.getElementById('targetFormat').value : 'PNG';
        const mimeType = targetFormat === 'PNG' ? 'image/png' : 
                        targetFormat === 'BMP' ? 'image/bmp' : 'image/tiff';
        
        canvas.toBlob(function(blob) {
            window.encodedImageBlob = blob;
            
            // Update filename based on converted format
            let filename = 'hidden_message';
            if (needsConversion && convertedImageData) {
                filename += '.' + imageConverter.getFileExtension(targetFormat).toLowerCase();
            } else {
                filename += '.png';
            }
            window.encodedImageName = filename;
            
            showToast('MESSAGE HIDDEN SUCCESSFULLY - CLICK DOWNLOAD', 'success');
            
            // Show download button
            const downloadBtn = document.getElementById('encodeDownloadBtn');
            if (downloadBtn) {
                downloadBtn.style.display = 'inline-block';
                downloadBtn.disabled = false;
            }
        }, mimeType);

    } catch (error) {
        showToast('ERROR: ' + error.message, 'error');
    } finally {
        setTimeout(() => {
            document.getElementById('encodeProgress').style.display = 'none';
            updateProgress(0);
        }, 1000);
    }
}

async function decodeMessage() {
    if (!currentFile) {
        showToast('SELECT A FILE FIRST', 'error');
        return;
    }

    const password = document.getElementById('decodePassword').value.trim() || null;
    const method = document.querySelector('input[name="decodeMethod"]:checked').value;

    try {
        // Show professional loading
        loadingManager.show('EXTRACTING MESSAGE');

        // Add processing dots to button
        const decodeBtn = document.getElementById('decodeButton');
        const originalText = decodeBtn.textContent;
        decodeBtn.textContent = 'PROCESSING';
        decodeBtn.classList.add('processing-dots');
        decodeBtn.disabled = true;

        // Simulate processing time with realistic steps
        await new Promise(resolve => setTimeout(resolve, 2500));

        // Restore button
        decodeBtn.textContent = originalText;
        decodeBtn.classList.remove('processing-dots');
        decodeBtn.disabled = false;

        loadingManager.hide();
        
        document.getElementById('decodeProgress').style.display = 'block';
        updateProgress(10, 'PREPARING');

        await new Promise(resolve => setTimeout(resolve, 100));

        let message;
        updateProgress(50, 'EXTRACTING');

        if (currentFileType === 'image') {
            // Validate image data before decoding
            if (!currentImageData) {
                throw new Error('No image data available for decoding');
            }

            if (!currentImageData.data || currentImageData.data.length === 0) {
                throw new Error('Image data is corrupted or empty');
            }

            if (currentImageData.width <= 0 || currentImageData.height <= 0) {
                throw new Error('Invalid image dimensions');
            }

            // Debug logging
            console.log(`Decoding with method: ${method}`);
            console.log(`Image data dimensions: ${currentImageData.width}x${currentImageData.height}`);
            console.log(`Image data length: ${currentImageData.data.length} pixels`);

            switch (method) {
                case 'lsb':
                    message = await SteganographyEngine.decodeLSB(currentImageData, password);
                    break;
                case 'dct':
                    message = await SteganographyEngine.decodeDCT(currentImageData, password);
                    break;
                case 'dwt':
                    message = await SteganographyEngine.decodeDWT(currentImageData, password);
                    break;
                default:
                    throw new Error(`Unknown decoding method: ${method}`);
            }
        }

        updateProgress(100, 'DONE');

        document.getElementById('resultText').value = message;
        showToast('MESSAGE EXTRACTED', 'success');

    } catch (error) {
        showToast('ERROR: ' + error.message, 'error');
        document.getElementById('resultText').value = '';
    } finally {
        setTimeout(() => {
            document.getElementById('decodeProgress').style.display = 'none';
            updateProgress(0);
        }, 1000);
    }
}

// Digital signature functions
async function generateKeypair() {
    try {
        loadingManager.show('GENERATING KEYPAIR');
        loadingManager.updateStep('Creating cryptographic keys...');

        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 2500));

        loadingManager.hide();

        updateStatus('GENERATING KEYPAIR');
        const keypair = await DigitalSignature.generateKeypair();

        document.getElementById('keypairResult').innerHTML = `
            <strong>PUBLIC KEY:</strong><br>
            ${keypair.publicKey}<br><br>
            <strong>PRIVATE KEY:</strong><br>
            ${keypair.privateKey}
        `;

        showToast('KEYPAIR GENERATED', 'success');
        updateStatus('READY');
    } catch (error) {
        showToast('ERROR: ' + error.message, 'error');
    }
}

async function signMessage() {
    const message = document.getElementById('signMessage').value.trim();
    const privateKey = document.getElementById('privateKey').value.trim();

    if (!message || !privateKey) {
        showToast('ENTER MESSAGE AND PRIVATE KEY', 'error');
        return;
    }

    try {
        loadingManager.show('SIGNING MESSAGE');
        loadingManager.updateStep('Creating digital signature...');

        await new Promise(resolve => setTimeout(resolve, 1500));
        loadingManager.hide();

        updateStatus('SIGNING MESSAGE');
        const signature = await DigitalSignature.signMessage(message, privateKey);

        document.getElementById('signatureResult').innerHTML = `
            <strong>SIGNATURE:</strong><br>
            ${signature}
        `;

        showToast('MESSAGE SIGNED', 'success');
        updateStatus('READY');
    } catch (error) {
        showToast('ERROR: ' + error.message, 'error');
    }
}

async function verifySignatureManual() {
    const message = document.getElementById('verifyMessage').value.trim();
    const signature = document.getElementById('signature').value.trim();
    const publicKey = document.getElementById('publicKey').value.trim();

    if (!message || !signature || !publicKey) {
        showToast('ENTER ALL FIELDS', 'error');
        return;
    }

    try {
        loadingManager.show('VERIFYING SIGNATURE');
        loadingManager.updateStep('Checking signature validity...');

        await new Promise(resolve => setTimeout(resolve, 1500));
        loadingManager.hide();

        updateStatus('VERIFYING SIGNATURE');
        const isValid = await DigitalSignature.verifySignature(message, signature, publicKey);

        document.getElementById('verifyResult').innerHTML = `
            <strong>VERIFICATION:</strong><br>
            ${isValid ? 'VALID SIGNATURE' : 'INVALID SIGNATURE'}
        `;

        document.getElementById('verifyResult').style.color = isValid ? '#00ff00' : '#ff0000';

        showToast(isValid ? 'SIGNATURE VALID' : 'SIGNATURE INVALID', isValid ? 'success' : 'error');
        updateStatus('READY');
    } catch (error) {
        showToast('ERROR: ' + error.message, 'error');
    }
}

async function verifySignature() {
    // Auto-verify signature from extracted message
    showToast('AUTO-VERIFY NOT IMPLEMENTED YET', 'warning');
}

// Download functions
function downloadEncodedImage() {
    if (window.encodedImageBlob) {
        const url = URL.createObjectURL(window.encodedImageBlob);
        const a = document.createElement('a');
        a.href = url;
        
        // Use converted format for filename if available
        let filename = 'hidden_message';
        if (needsConversion && convertedImageData) {
            const targetFormat = document.getElementById('targetFormat').value;
            filename += '.' + imageConverter.getFileExtension(targetFormat).toLowerCase();
        } else {
            filename += '.png';
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('IMAGE DOWNLOADED SUCCESSFULLY', 'success');
    } else {
        showToast('NO ENCODED IMAGE TO DOWNLOAD', 'error');
    }
}

// Utility functions
async function copyToClipboard() {
    const text = document.getElementById('resultText').value;
    if (!text) {
        showToast('NO MESSAGE TO COPY', 'error');
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        showToast('COPIED TO CLIPBOARD', 'success');
    } catch (error) {
        showToast('COPY FAILED', 'error');
    }
}

function downloadText() {
    const text = document.getElementById('resultText').value;
    if (!text) {
        showToast('NO MESSAGE TO DOWNLOAD', 'error');
        return;
    }

    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'extracted_message.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('MESSAGE DOWNLOADED', 'success');
}


