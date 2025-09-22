// Tiện ích chuyển định dạng (FormatConverter),
// hiển thị/ẩn UI chuyển đổi,
// luồng convert blob→ImageData→preview, 
// cập nhật state sau chuyển đổi. 
// Expose hàm dùng bởi nút “Đổi định dạng”.

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

        if (file.size > 50 * 1024 * 1024) {
            throw new Error('File too large for conversion (max 50MB)');
        }

        try {
            console.log(`Converting ${file.name} (${file.type}) to ${targetFormat}`);
            const blob = await imageConverter.convert(file, targetFormat);
            if (!blob || blob.size === 0) {
                throw new Error('Conversion resulted in empty file');
            }
            if (blob.size > 100 * 1024 * 1024) {
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
            const timeout = setTimeout(() => {
                reject(new Error('Image loading timeout'));
            }, 10000);

            img.onload = function() {
                clearTimeout(timeout);
                try {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    if (img.width <= 0 || img.height <= 0) {
                        reject(new Error('Invalid image dimensions'));
                        return;
                    }
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
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

function showFormatConversion(file) {
    const formatConversion = document.getElementById('formatConversion');
    const originalFormat = document.getElementById('originalFormat');

    if (formatConversion && originalFormat) {
        originalFormat.textContent = FormatConverter.getFormatName(file.type);
        formatConversion.style.display = 'block';

        needsConversion = true;
        convertedImageData = null;

        document.getElementById('encodeButton').disabled = true;

        if (!imageConverter) {
            const convertButton = document.getElementById('convertButton');
            if (convertButton) {
                convertButton.textContent = 'CONVERTER NOT READY';
                convertButton.disabled = true;
                convertButton.style.background = '#666666';
                convertButton.style.color = '#cccccc';
            }

            showToast('Image converter loading... Please wait', 'warning');

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

    if (!imageConverter) {
        console.log('ImageConverter not available, attempting initialization...');
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
        convertButton.disabled = true;
        convertButton.textContent = 'CONVERTING...';
        conversionProgress.style.display = 'block';

        loadingManager.show('CONVERTING IMAGE');
        loadingManager.updateStep(`Converting ${FormatConverter.getFormatName(originalFile.type)} to ${targetFormat}...`);

        FormatConverter.validateFileSize(originalFile, 50);

        loadingManager.updateStep('Processing image data...');
        const convertedBlob = await FormatConverter.convertImage(originalFile, targetFormat);

        loadingManager.updateStep('Extracting pixel data...');
        convertedImageData = await FormatConverter.blobToImageData(convertedBlob);

        FormatConverter.validateImageDimensions(
            convertedImageData.width,
            convertedImageData.height,
            8192
        );

        currentImageData = convertedImageData;
        needsConversion = false;

        hideFormatConversion();

        const preview = document.getElementById('encodePreview');
        const url = URL.createObjectURL(convertedBlob);
        preview.innerHTML = `<img src="${url}" alt="Converted Preview" style="max-width: 100%; max-height: 150px; border: 1px solid var(--border);">`;
        document.getElementById('decodePreview').innerHTML = preview.innerHTML;

        calculateImageCapacity();
        document.getElementById('encodeButton').disabled = false;
        document.getElementById('decodeButton').disabled = false;
        syncFileInputsAndPreviews();

        updateStatus('CONVERSION COMPLETE', `Converted to ${targetFormat} - Ready for steganography`);
        showToast(`Successfully converted to ${targetFormat}`, 'success');

        setTimeout(() => URL.revokeObjectURL(url), 5000);

    } catch (error) {
        console.error('Conversion error:', error);
        showToast(`Conversion failed: ${error.message}`, 'error');
        convertedImageData = null;
        needsConversion = true;
    } finally {
        loadingManager.hide();
        conversionProgress.style.display = 'none';
        convertButton.disabled = false;
        convertButton.textContent = 'CONVERT FORMAT';
    }
}

window.FormatConverter = FormatConverter;
window.showFormatConversion = showFormatConversion;
window.hideFormatConversion = hideFormatConversion;
window.convertImageFormat = convertImageFormat;


