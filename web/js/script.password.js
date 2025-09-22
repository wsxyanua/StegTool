// Lắng nghe input mật khẩu để cập nhật thanh độ mạnh; auto ẩn skeleton sớm khi DOM ready.

document.addEventListener('DOMContentLoaded', function() {
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
});


