// Steganography engines

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

        let bitIndex = 0;
        for (let i = 0; i < stegoData.data.length && bitIndex < binaryMessage.length; i += 4) {
            if (bitIndex < binaryMessage.length) {
                const bit = parseInt(binaryMessage[bitIndex]);
                stegoData.data[i] = (stegoData.data[i] & 0xFE) | bit;
                bitIndex++;
            }
            if (bitIndex < binaryMessage.length) {
                const bit = parseInt(binaryMessage[bitIndex]);
                stegoData.data[i + 1] = (stegoData.data[i + 1] & 0xFE) | bit;
                bitIndex++;
            }
            if (bitIndex < binaryMessage.length) {
                const bit = parseInt(binaryMessage[bitIndex]);
                stegoData.data[i + 2] = (stegoData.data[i + 2] & 0xFE) | bit;
                bitIndex++;
            }
        }

        return stegoData;
    }

    static async decodeLSB(imageData, password = null) {
        let binaryMessage = "";
        
        for (let i = 0; i < imageData.data.length; i += 4) {
            binaryMessage += (imageData.data[i] & 1).toString();
            binaryMessage += (imageData.data[i + 1] & 1).toString();
            binaryMessage += (imageData.data[i + 2] & 1).toString();
            
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
        ).join('') + '11111110';

        const stegoData = new ImageData(
            new Uint8ClampedArray(imageData.data),
            imageData.width,
            imageData.height
        );

        let bitIndex = 0;
        for (let i = 0; i < stegoData.data.length && bitIndex < binaryMessage.length; i += 16) {
            const bit = parseInt(binaryMessage[bitIndex]);
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
        for (let i = 0; i < imageData.data.length; i += 16) {
            const bit = imageData.data[i + 2] & 1;
            binaryMessage += bit.toString();
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
        ).join('') + '11111110';

        const stegoData = new ImageData(
            new Uint8ClampedArray(imageData.data),
            imageData.width,
            imageData.height
        );

        let bitIndex = 0;
        for (let i = 0; i < stegoData.data.length && bitIndex < binaryMessage.length; i += 32) {
            const bit = parseInt(binaryMessage[bitIndex]);
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
        for (let i = 0; i < imageData.data.length; i += 32) {
            const bit = imageData.data[i + 1] & 1;
            binaryMessage += bit.toString();
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

window.SteganographyEngine = SteganographyEngine;


