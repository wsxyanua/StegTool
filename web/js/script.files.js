// File handling, upload, encode/decode, settings, downloads

function resetUploadState() {
    hideFormatConversion();

    const downloadBtn = document.getElementById('encodeDownloadBtn');
    if (downloadBtn) {
        downloadBtn.style.display = 'none';
        downloadBtn.disabled = true;
    }

    document.getElementById('resultText').value = '';

    needsConversion = false;
    convertedImageData = null;
    currentImageData = null;

    document.getElementById('encodePreview').innerHTML = '';
    document.getElementById('decodePreview').innerHTML = '';
    document.getElementById('encodeCapacity').innerHTML = '';
}

async function handleFileUpload(input, type) {
    const file = input.files[0];
    if (!file) return;

    resetUploadState();

    const fileSection = type === 'encode' ? '.file-section' : '.decode-file-section';
    skeletonLoader.showSection(fileSection);

    loadingManager.show('LOADING FILE');
    loadingManager.updateStep('Reading file data...');

    currentFile = file;
    originalFile = file;
    needsConversion = false;
    convertedImageData = null;

    try {
        FormatConverter.validateFileSize(file, 50);

        if (file.type.startsWith('image/')) {
            currentFileType = 'image';

            if (type === 'encode' && !FormatConverter.isSupportedFormat(file.type)) {
                if (imageConverter) {
                    needsConversion = true;
                    showFormatConversion(file);
                    loadingManager.hide();
                    skeletonLoader.hideSection(fileSection);
                    updateStatus('CONVERSION NEEDED', `${file.name} - Convert to supported format`);
                    return;
                } else {
                    console.warn('Converter not available, attempting to process unsupported format');
                    showToast(`Warning: ${FormatConverter.getFormatName(file.type)} format may not work properly`, 'warning');
                }
            }

            await handleImageUpload(file, type);
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
        const downloadBtn = document.getElementById('encodeDownloadBtn');
        if (downloadBtn) {
            downloadBtn.style.display = 'none';
            downloadBtn.disabled = true;
        }
        
        loadingManager.show('ENCODING MESSAGE');

        const encodeBtn = document.getElementById('encodeButton');
        const originalText = encodeBtn.textContent;
        encodeBtn.textContent = 'PROCESSING';
        encodeBtn.classList.add('processing-dots');
        encodeBtn.disabled = true;

        await new Promise(resolve => setTimeout(resolve, 2500));

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
            const imageDataToUse = convertedImageData || currentImageData;
            if (!imageDataToUse) {
                throw new Error('No valid image data available. Please convert format first if needed.');
            }
            if (!imageDataToUse.data || imageDataToUse.data.length === 0) {
                throw new Error('Image data is corrupted or empty');
            }
            if (imageDataToUse.width <= 0 || imageDataToUse.height <= 0) {
                throw new Error('Invalid image dimensions');
            }
            const expectedSize = imageDataToUse.width * imageDataToUse.height * 4;
            if (imageDataToUse.data.length !== expectedSize) {
                throw new Error(`Image data size mismatch. Expected: ${expectedSize}, Got: ${imageDataToUse.data.length}`);
            }

            switch (method) {
                case 'lsb':
                    result = await SteganographyEngine.encodeLSB(imageDataToUse, message, password);
                    break;
                case 'dct':
                    result = await SteganographyEngine.encodeDCT(imageDataToUse, message, password);
                    break;
                case 'dwt':
                    result = await SteganographyEngine.encodeDWT(imageDataToUse, message, password);
                    break;
                default:
                    throw new Error(`Unknown method: ${method}`);
            }
        }

        updateProgress(80, 'CREATING FILE');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = result.width;
        canvas.height = result.height;
        ctx.putImageData(result, 0, 0);

        updateProgress(100, 'DONE');

        const targetFormat = needsConversion ? document.getElementById('targetFormat').value : 'PNG';
        const mimeType = targetFormat === 'PNG' ? 'image/png' : 
                        targetFormat === 'BMP' ? 'image/bmp' : 'image/tiff';
        
        canvas.toBlob(function(blob) {
            window.encodedImageBlob = blob;
            let filename = 'hidden_message';
            if (needsConversion && convertedImageData) {
                filename += '.' + imageConverter.getFileExtension(targetFormat).toLowerCase();
            } else {
                filename += '.png';
            }
            window.encodedImageName = filename;
            showToast('MESSAGE HIDDEN SUCCESSFULLY - CLICK DOWNLOAD', 'success');
            const downloadBtn2 = document.getElementById('encodeDownloadBtn');
            if (downloadBtn2) {
                downloadBtn2.style.display = 'inline-block';
                downloadBtn2.disabled = false;
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
        loadingManager.show('EXTRACTING MESSAGE');
        const decodeBtn = document.getElementById('decodeButton');
        const originalText = decodeBtn.textContent;
        decodeBtn.textContent = 'PROCESSING';
        decodeBtn.classList.add('processing-dots');
        decodeBtn.disabled = true;
        await new Promise(resolve => setTimeout(resolve, 2500));
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
            if (!currentImageData) {
                throw new Error('No image data available for decoding');
            }
            if (!currentImageData.data || currentImageData.data.length === 0) {
                throw new Error('Image data is corrupted or empty');
            }
            if (currentImageData.width <= 0 || currentImageData.height <= 0) {
                throw new Error('Invalid image dimensions');
            }

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
    showToast('AUTO-VERIFY NOT IMPLEMENTED YET', 'warning');
}

function downloadEncodedImage() {
    if (window.encodedImageBlob) {
        const url = URL.createObjectURL(window.encodedImageBlob);
        const a = document.createElement('a');
        a.href = url;
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

            const masterPassword = prompt('Enter master password to encrypt settings:');
            if (!masterPassword) {
                showToast('EXPORT CANCELLED', 'error');
                return;
            }

            const encryptedSettings = await CryptoEngine.encrypt(JSON.stringify(settings), masterPassword);
            const exportData = { app: 'Steganography Re-birth', version: '1.0', encrypted: true, data: encryptedSettings };

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
        if (settings.preferences?.defaultMethod) {
            const methodRadio = document.querySelector(`input[name="stegoMethod"][value="${settings.preferences.defaultMethod}"]`);
            if (methodRadio) methodRadio.checked = true;
        }
        if (settings.recentFiles) {
            localStorage.setItem('steganography-recent', JSON.stringify(settings.recentFiles));
        }
        if (settings.customSettings) {
            localStorage.setItem('steganography-custom', JSON.stringify(settings.customSettings));
        }
    }
}

function exportSettings() { SettingsManager.exportSettings(); }
function importSettings() { SettingsManager.importSettings(); }

window.resetUploadState = resetUploadState;
window.handleFileUpload = handleFileUpload;
window.handleImageUpload = handleImageUpload;
window.showFakeLoading = showFakeLoading;
window.hideFakeLoading = hideFakeLoading;
window.encodeMessage = encodeMessage;
window.decodeMessage = decodeMessage;
window.generateKeypair = generateKeypair;
window.signMessage = signMessage;
window.verifySignatureManual = verifySignatureManual;
window.verifySignature = verifySignature;
window.downloadEncodedImage = downloadEncodedImage;
window.copyToClipboard = copyToClipboard;
window.downloadText = downloadText;
window.SettingsManager = SettingsManager;
window.exportSettings = exportSettings;
window.importSettings = importSettings;


