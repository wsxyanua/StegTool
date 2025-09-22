// Digital signature helpers

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

window.DigitalSignature = DigitalSignature;


