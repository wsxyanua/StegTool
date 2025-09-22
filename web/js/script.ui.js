// UI helpers, tabs, status, toast

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

    resetFileInputs();
}

function resetFileInputs() {
    document.getElementById('messageText').value = '';
    document.getElementById('resultText').value = '';

    const hasFile = currentImageData !== null && !needsConversion;
    document.getElementById('encodeButton').disabled = !hasFile;
    document.getElementById('decodeButton').disabled = !hasFile;

    const downloadBtn = document.getElementById('encodeDownloadBtn');
    if (downloadBtn) {
        downloadBtn.style.display = 'none';
    }

    if (hasFile && currentFile) {
        syncFileInputsAndPreviews();
    }
}

function syncFileInputsAndPreviews() {
    if (!currentImageData) return;

    try {
        const capacityInfo = document.getElementById('encodeCapacity');
        if (capacityInfo && currentImageData.width && currentImageData.height) {
            const capacity = Math.floor((currentImageData.width * currentImageData.height * 3) / 8);
            const formatInfo = convertedImageData ? ' (Converted)' : '';
            capacityInfo.innerHTML = `<strong>CAPACITY:</strong> ~${capacity} characters (${currentImageData.width}x${currentImageData.height})${formatInfo}`;
        }

        const maxCharsElement = document.getElementById('maxChars');
        if (maxCharsElement && currentImageData) {
            const maxChars = Math.floor((currentImageData.data.length) / 8) - 1;
            maxCharsElement.textContent = maxChars.toLocaleString();
        }

        const messageText = document.getElementById('messageText');
        const charCount = document.getElementById('charCount');
        if (messageText && charCount) {
            charCount.textContent = messageText.value.length.toLocaleString();
        }

    } catch (error) {
        console.error('Error syncing file previews:', error);
    }
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

function calculateImageCapacity() {
    if (!currentImageData) return;

    const maxBits = currentImageData.data.length;
    const maxChars = Math.floor(maxBits / 8) - 1;

    document.getElementById('encodeCapacity').innerHTML =
        `CAPACITY: ${maxChars.toLocaleString()} characters (${currentImageData.width}x${currentImageData.height})`;

    document.getElementById('maxChars').textContent = maxChars.toLocaleString();
}

window.toggleSidebar = toggleSidebar;
window.showTab = showTab;
window.resetFileInputs = resetFileInputs;
window.syncFileInputsAndPreviews = syncFileInputsAndPreviews;
window.updateStatus = updateStatus;
window.updateProgress = updateProgress;
window.showToast = showToast;
window.togglePasswordVisibility = togglePasswordVisibility;
window.calculateImageCapacity = calculateImageCapacity;


