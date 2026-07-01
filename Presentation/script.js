document.addEventListener('DOMContentLoaded', () => {
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const slideIndicator = document.getElementById('slide-indicator');
    const printModeBtn = document.getElementById('print-mode-btn');
    const container = document.getElementById('presentation-container');
    
    let currentSlideIndex = 0;
    let isPrintPreview = false;

    // 1. Dynamic scale function to fit 1920x1080 workspace to any browser window
    function updateScale() {
        if (isPrintPreview) {
            container.style.transform = 'none';
            container.style.position = 'relative';
            container.style.top = '0';
            container.style.left = '0';
            return;
        }

        const baseWidth = 1920;
        const baseHeight = 1080;
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        // Determine best scale factor
        const scaleX = windowWidth / baseWidth;
        const scaleY = windowHeight / baseHeight;
        const scale = Math.min(scaleX, scaleY) * 0.95; // 5% padding around slide edge

        container.style.position = 'absolute';
        container.style.top = '50%';
        container.style.left = '50%';
        container.style.transform = `translate(-50%, -50%) scale(${scale})`;
    }

    // 2. Navigation logic
    function showSlide(index) {
        if (isPrintPreview) return; // Disable slideshow during print layout inspection

        // Bounds check
        if (index < 0) index = 0;
        if (index >= slides.length) index = slides.length - 1;

        // Update active slide class
        slides.forEach((slide, idx) => {
            if (idx === index) {
                slide.classList.add('active');
            } else {
                slide.classList.remove('active');
            }
        });

        currentSlideIndex = index;
        slideIndicator.textContent = `Slide ${currentSlideIndex + 1} / ${slides.length}`;
    }

    function nextSlide() {
        if (currentSlideIndex < slides.length - 1) {
            showSlide(currentSlideIndex + 1);
        }
    }

    function prevSlide() {
        if (currentSlideIndex > 0) {
            showSlide(currentSlideIndex - 1);
        }
    }

    // Keyboard controls
    document.addEventListener('keydown', (e) => {
        if (isPrintPreview) return;

        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'Enter') {
            nextSlide();
            e.preventDefault();
        } else if (e.key === 'ArrowLeft' || e.key === 'Backspace') {
            prevSlide();
            e.preventDefault();
        }
    });

    // Button controls
    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);

    // 3. Print Mode Preview (for manual QA of margins)
    printModeBtn.addEventListener('click', () => {
        isPrintPreview = !isPrintPreview;
        
        if (isPrintPreview) {
            document.body.style.overflow = 'auto';
            document.body.style.background = '#222';
            container.style.width = '1920px';
            container.style.height = 'auto';
            container.style.transform = 'none';
            container.style.position = 'static';
            container.style.margin = '20px auto';
            
            // Show all slides stacked
            slides.forEach(slide => {
                slide.style.display = 'flex';
                slide.style.opacity = '1';
                slide.style.position = 'relative';
                slide.style.marginBottom = '20px';
            });
            printModeBtn.textContent = "Exit Print Mode Stack";
            printModeBtn.classList.remove('accent-btn');
        } else {
            document.body.style.overflow = 'hidden';
            document.body.style.background = '#050505';
            container.style.width = '1920px';
            container.style.height = '1080px';
            container.style.margin = '0';
            
            // Reset slideshow styles
            slides.forEach((slide, idx) => {
                slide.style.display = '';
                slide.style.opacity = '';
                slide.style.position = '';
                slide.style.marginBottom = '';
            });
            
            showSlide(currentSlideIndex);
            printModeBtn.textContent = "Toggle Slide Stack for Print";
            printModeBtn.classList.add('accent-btn');
            updateScale();
        }
    });

    // Bind listeners
    window.addEventListener('resize', updateScale);
    
    // Initialize
    updateScale();
    showSlide(0);
});
