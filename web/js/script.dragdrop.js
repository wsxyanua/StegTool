// Kéo/thả file nâng cao, indicator loại file, validator loại file
// và bind sự kiện cho tab phương pháp.

function initializeDragAndDrop() {
    const dropZones = document.querySelectorAll('.file-input-label');

    dropZones.forEach(dropZone => {
        const fileInput = dropZone.parentElement.querySelector('input[type="file"]');

        const indicator = document.createElement('div');
        indicator.className = 'file-type-indicator';
        indicator.textContent = 'IMG';
        dropZone.appendChild(indicator);

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

                indicator.textContent = getFileTypeLabel(file);
                indicator.style.backgroundColor = isValid ? '#00ff00' : '#ff0000';
            }
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
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
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    fileInput.files = dt.files;

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
        'image/png', 'image/bmp', 'image/tiff', 'image/jpeg', 'image/jpg'
    ];
    return validTypes.includes(file.type) ||
           validTypes.some(type => file.name.toLowerCase().endsWith(type.split('/')[1]));
}

function getFileTypeLabel(file) {
    if (file.type.startsWith('image/')) return 'IMG';
    return 'UNK';
}

document.addEventListener('DOMContentLoaded', function() {
    // method tabs click handlers
    document.querySelectorAll('.method-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                document.querySelectorAll('.method-tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });

    // add drag&drop to labels (basic)
    document.querySelectorAll('.file-input-label').forEach(label => {
        const input = label.querySelector('input[type="file"]');

        label.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
            const items = e.dataTransfer.items;
            let isValid = false;
            for (let item of items) {
                if (item.type.startsWith('image/')) { isValid = true; break; }
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
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    input.files = dt.files;
                    const event = new Event('change', { bubbles: true });
                    input.dispatchEvent(event);
                } else {
                    showToast('Please drop an image file', 'error');
                }
            }
        });
    });

    initializeDragAndDrop();
});

window.initializeDragAndDrop = initializeDragAndDrop;
window.isValidFileType = isValidFileType;
window.getFileTypeLabel = getFileTypeLabel;


