/**
 * Image Converter Module - Convert images to PNG/BMP/TIFF
 * Supports: JPG, JPEG, PNG, GIF, WebP, SVG → PNG/BMP/TIFF
 * Usage: const converter = new ImageConverter(); const blob = await converter.convert(file, 'PNG');
 */

class ImageConverter {
    constructor() {
        this.supportedInputFormats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'];
        this.supportedOutputFormats = ['PNG', 'BMP', 'TIFF'];
    }

    /**
     * Convert image file to specified format
     * @param {File} file - Input image file
     * @param {string} outputFormat - 'PNG', 'BMP', or 'TIFF'
     * @param {Object} options - Conversion options
     * @returns {Promise<Blob>} - Converted image blob
     */
    async convert(file, outputFormat = 'PNG', options = {}) {
        try {
            // Validate input
            this._validateInput(file, outputFormat);

            // Load image to canvas
            const canvas = await this._loadImageToCanvas(file);
            
            // Convert based on output format
            switch (outputFormat.toUpperCase()) {
                case 'PNG':
                    return await this._convertToPNG(canvas, options);
                case 'BMP':
                    return await this._convertToBMP(canvas);
                case 'TIFF':
                    return await this._convertToTIFF(canvas);
                default:
                    throw new Error(`Unsupported output format: ${outputFormat}`);
            }
        } catch (error) {
            throw new Error(`Conversion failed: ${error.message}`);
        }
    }

    /**
     * Validate input file and output format
     */
    _validateInput(file, outputFormat) {
        if (!file || !(file instanceof File)) {
            throw new Error('Invalid file input');
        }

        if (!this.supportedInputFormats.includes(file.type)) {
            throw new Error(`Unsupported input format: ${file.type}. Supported: ${this.supportedInputFormats.join(', ')}`);
        }

        if (!this.supportedOutputFormats.includes(outputFormat.toUpperCase())) {
            throw new Error(`Unsupported output format: ${outputFormat}. Supported: ${this.supportedOutputFormats.join(', ')}`);
        }
    }

    /**
     * Load image file to canvas
     */
    async _loadImageToCanvas(file) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            img.onload = () => {
                try {
                    // Set canvas dimensions to match image
                    canvas.width = img.naturalWidth || img.width;
                    canvas.height = img.naturalHeight || img.height;

                    // Draw image to canvas
                    ctx.drawImage(img, 0, 0);

                    // Clean up object URL
                    URL.revokeObjectURL(img.src);

                    resolve(canvas);
                } catch (error) {
                    URL.revokeObjectURL(img.src);
                    reject(new Error(`Canvas processing failed: ${error.message}`));
                }
            };

            img.onerror = () => {
                URL.revokeObjectURL(img.src);
                reject(new Error('Failed to load image'));
            };

            // Create object URL and load image
            img.src = URL.createObjectURL(file);
        });
    }

    /**
     * Convert canvas to PNG
     */
    async _convertToPNG(canvas, options = {}) {
        const quality = options.quality || 1.0; // PNG doesn't use quality, but kept for consistency
        
        return new Promise((resolve) => {
            canvas.toBlob((blob) => {
                resolve(blob);
            }, 'image/png');
        });
    }

    /**
     * Convert canvas to BMP
     */
    async _convertToBMP(canvas) {
        // Get image data
        const ctx = canvas.getContext('2d');
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        
        // Create BMP buffer
        const bmpBuffer = this._createBMPBuffer(imageData, canvas.width, canvas.height);
        
        return new Blob([bmpBuffer], { type: 'image/bmp' });
    }

    /**
     * Convert canvas to TIFF (basic uncompressed)
     */
    async _convertToTIFF(canvas) {
        // Get image data
        const ctx = canvas.getContext('2d');
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        
        // Create TIFF buffer
        const tiffBuffer = this._createTIFFBuffer(imageData, canvas.width, canvas.height);
        
        return new Blob([tiffBuffer], { type: 'image/tiff' });
    }

    /**
     * Create BMP buffer from image data
     */
    _createBMPBuffer(imageData, width, height) {
        const pixelArraySize = width * height * 4;
        const headerSize = 54;
        const fileSize = headerSize + pixelArraySize;

        const buffer = new ArrayBuffer(fileSize);
        const view = new DataView(buffer);
        const pixels = new Uint8Array(buffer, headerSize);

        // BMP Header
        view.setUint16(0, 0x4D42, false); // BM
        view.setUint32(2, fileSize, true); // File size
        view.setUint32(6, 0, true); // Reserved
        view.setUint32(10, headerSize, true); // Offset to pixel data

        // DIB Header
        view.setUint32(14, 40, true); // DIB header size
        view.setInt32(18, width, true); // Width
        view.setInt32(22, -height, true); // Height (negative for top-down)
        view.setUint16(26, 1, true); // Planes
        view.setUint16(28, 32, true); // Bits per pixel
        view.setUint32(30, 0, true); // Compression
        view.setUint32(34, pixelArraySize, true); // Image size
        view.setInt32(38, 2835, true); // X pixels per meter
        view.setInt32(42, 2835, true); // Y pixels per meter
        view.setUint32(46, 0, true); // Colors used
        view.setUint32(50, 0, true); // Important colors

        // Pixel data (BGRA)
        const data = imageData.data;
        for (let i = 0; i < data.length; i += 4) {
            pixels[i] = data[i + 2]; // B
            pixels[i + 1] = data[i + 1]; // G
            pixels[i + 2] = data[i]; // R
            pixels[i + 3] = data[i + 3]; // A
        }

        return buffer;
    }

    /**
     * Create basic TIFF buffer from image data
     */
    _createTIFFBuffer(imageData, width, height) {
        const pixelData = imageData.data;
        const headerSize = 8 + 12 * 11 + 4; // TIFF header + 11 IFD entries + next IFD offset
        const bufferSize = headerSize + pixelData.length;

        const buffer = new ArrayBuffer(bufferSize);
        const view = new DataView(buffer);
        const pixels = new Uint8Array(buffer, headerSize);

        let offset = 0;

        // TIFF Header
        view.setUint16(offset, 0x4949, false); // Little endian
        offset += 2;
        view.setUint16(offset, 42, true); // TIFF magic
        offset += 2;
        view.setUint32(offset, 8, true); // Offset to first IFD
        offset += 4;

        // IFD (Image File Directory)
        view.setUint16(offset, 11, true); // Number of entries
        offset += 2;

        // IFD Entries
        this._writeTIFFEntry(view, offset, 256, 4, 1, width); offset += 12; // ImageWidth
        this._writeTIFFEntry(view, offset, 257, 4, 1, height); offset += 12; // ImageLength
        this._writeTIFFEntry(view, offset, 258, 3, 4, headerSize - 8); offset += 12; // BitsPerSample (8,8,8,8)
        this._writeTIFFEntry(view, offset, 259, 3, 1, 1); offset += 12; // Compression (none)
        this._writeTIFFEntry(view, offset, 262, 3, 1, 2); offset += 12; // PhotometricInterpretation (RGB)
        this._writeTIFFEntry(view, offset, 273, 4, 1, headerSize); offset += 12; // StripOffsets
        this._writeTIFFEntry(view, offset, 277, 3, 1, 4); offset += 12; // SamplesPerPixel
        this._writeTIFFEntry(view, offset, 278, 4, 1, height); offset += 12; // RowsPerStrip
        this._writeTIFFEntry(view, offset, 279, 4, 1, pixelData.length); offset += 12; // StripByteCounts
        this._writeTIFFEntry(view, offset, 282, 5, 1, headerSize - 4); offset += 12; // XResolution
        this._writeTIFFEntry(view, offset, 283, 5, 1, headerSize - 4); offset += 12; // YResolution

        // Next IFD offset (0 = no more IFDs)
        view.setUint32(offset, 0, true);

        // Copy pixel data (RGBA)
        pixels.set(pixelData);

        return buffer;
    }

    /**
     * Write TIFF IFD entry
     */
    _writeTIFFEntry(view, offset, tag, type, count, value) {
        view.setUint16(offset, tag, true);
        view.setUint16(offset + 2, type, true);
        view.setUint32(offset + 4, count, true);
        view.setUint32(offset + 8, value, true);
    }

    /**
     * Get supported input formats
     */
    getSupportedInputFormats() {
        return [...this.supportedInputFormats];
    }

    /**
     * Get supported output formats
     */
    getSupportedOutputFormats() {
        return [...this.supportedOutputFormats];
    }

    /**
     * Check if input format is supported
     */
    isInputFormatSupported(mimeType) {
        return this.supportedInputFormats.includes(mimeType);
    }

    /**
     * Get file extension for output format
     */
    getFileExtension(format) {
        const extensions = {
            'PNG': 'png',
            'BMP': 'bmp', 
            'TIFF': 'tiff'
        };
        return extensions[format.toUpperCase()] || 'png';
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ImageConverter;
} else {
    window.ImageConverter = ImageConverter;
}