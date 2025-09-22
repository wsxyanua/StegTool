// Crypto and password strength utilities

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

window.CryptoEngine = CryptoEngine;
window.PasswordStrength = PasswordStrength;


