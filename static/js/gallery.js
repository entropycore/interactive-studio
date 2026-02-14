/* =========================================
   1. FILTER LOGIC
   ========================================= */
function filterGallery(category, btn) {
    // Update Active Button
    document.querySelectorAll('.dock-item').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const items = document.querySelectorAll('.gallery-item');
    const emptyMsg = document.getElementById('empty-message');
    let hasVisible = false;

    items.forEach(item => {
        if (category === 'all' || item.classList.contains('category-' + category)) {
            item.style.display = 'block';
            // Animation Reset
            item.style.opacity = '0'; 
            item.style.transform = 'translateY(20px)';
            setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, 50);
            hasVisible = true;
        } else {
            item.style.display = 'none';
        }
    });

    if (hasVisible) emptyMsg.classList.add('d-none');
    else emptyMsg.classList.remove('d-none');
}

/* =========================================
   2. DELETE LOGIC
   ========================================= */
function deleteImage(filename, btnElement) {
    event.stopPropagation(); // Stop Lightbox
    
    if (!confirm("Are you sure you want to delete this art? 🗑️")) return;

    fetch('/delete_image', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ filename: filename })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const card = btnElement.closest('.gallery-item');
            card.style.transform = "scale(0)";
            setTimeout(() => card.remove(), 300);
        } else {
            alert("Error: " + data.error);
        }
    });
}

/* =========================================
   3. LIGHTBOX LOGIC
   ========================================= */
let currentImages = [];
let currentIndex = 0;
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightbox-img');

function openLightbox(clickedSrc) {
    // Collect ONLY visible images (respects current filter)
    const visibleItems = Array.from(document.querySelectorAll('.gallery-item')).filter(item => item.style.display !== 'none');
    const images = visibleItems.map(item => item.querySelector('img'));
    
    currentImages = images.map(img => img.src);
    currentIndex = currentImages.indexOf(clickedSrc);
    
    // Safety check
    if (currentIndex === -1) currentIndex = 0;
    
    updateLightboxImage();
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden'; // Stop scrolling
}

function closeLightbox() {
    lightbox.classList.remove('active');
    document.body.style.overflow = 'auto'; // Resume scrolling
}

function changeImage(direction) {
    if (currentImages.length <= 1) return;
    currentIndex += direction;
    
    // Loop
    if (currentIndex >= currentImages.length) currentIndex = 0;
    if (currentIndex < 0) currentIndex = currentImages.length - 1;
    
    updateLightboxImage();
}

function updateLightboxImage() {
    lightboxImg.style.opacity = 0;
    lightboxImg.style.transform = "scale(0.95)";
    
    setTimeout(() => {
        lightboxImg.src = currentImages[currentIndex];
        lightboxImg.style.opacity = 1;
        lightboxImg.style.transform = "scale(1)";
    }, 150);
}

// Keyboard Events
document.addEventListener('keydown', function(e) {
    if (!lightbox.classList.contains('active')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowRight') changeImage(1);
    if (e.key === 'ArrowLeft') changeImage(-1);
});