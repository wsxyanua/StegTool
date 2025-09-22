// Quản lý overlay loading chuyên nghiệp (LoadingManager) và skeleton UI (SkeletonLoader)
// hàm show/hide skeleton và bind ra window.

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

const loadingManager = new LoadingManager();
window.loadingManager = loadingManager;

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

            const skeletons = section.querySelectorAll('.skeleton');
            skeletons.forEach(skeleton => skeleton.remove());
        }
    }
}

const skeletonLoader = new SkeletonLoader();
window.skeletonLoader = skeletonLoader;

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

window.showSkeleton = showSkeleton;
window.hideSkeleton = hideSkeleton;


