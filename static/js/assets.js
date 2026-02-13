document.addEventListener('DOMContentLoaded', function() {
    
    // =========================================
    // 1. FILTERING SYSTEM (Renaissance, Classic...)
    // =========================================
    const filterBtns = document.querySelectorAll('.filter-chip');
    const items = document.querySelectorAll('.grid-item');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;

            items.forEach(item => {
                // Show/Hide logic
                if (filter === 'all' || item.dataset.movement === filter) {
                    item.style.display = 'block';
                    // Trigger reflow for Masonry if used, or just CSS grid
                    item.style.opacity = '0';
                    setTimeout(() => item.style.opacity = '1', 50);
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    // =========================================
    // 2. FAST ADD BUTTON (Hover Buttons) 
    // =========================================
    document.querySelectorAll('.add-fast-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation(); 
            
            const filename = this.dataset.filename;
            const icon = this.querySelector('i');
            const originalTooltip = this.getAttribute('data-tooltip');

            // Animation (Loading)
            icon.className = "ph ph-spinner ph-spin";

            fetch('/api/add-to-gallery', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({filename: filename})
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    // Success State
                    icon.className = "ph ph-check";
                    this.classList.add('added');
                    this.setAttribute('data-tooltip', 'Saved!');
                    
                    // Reset after 2 seconds (Optional)
                    setTimeout(() => {
                        this.setAttribute('data-tooltip', 'Saved'); 
                    }, 2000);
                }
            })
            .catch(err => {
                console.error(err);
                icon.className = "ph ph-warning"; // Error icon
            });
        });
    });
});

// =========================================
// 3. OPEN MODAL LOGIC (Global Function)
// =========================================
function openArtModal(card) {
    // 1. Grab data from HTML attributes
    const file = card.dataset.file;
    const title = card.dataset.title;
    const artist = card.dataset.artist;
    const year = card.dataset.year;
    const museum = card.dataset.museum;
    // Try to find movement from parent grid item
    const movement = card.parentElement.dataset.movement || 'Art';

    // 2. Populate Modal Elements
    const imgPath = '/static/wallpapers/' + file;
    document.getElementById('modalImg').src = imgPath;
    document.getElementById('modalTitle').innerText = title;
    document.getElementById('modalArtist').innerText = artist;
    document.getElementById('modalYear').innerText = year;
    document.getElementById('modalMuseum').innerText = museum;
    document.getElementById('modalMovement').innerText = movement;

    // 3. Update Download Link
    document.getElementById('downloadLink').href = imgPath;

    // 4. Update "Add to Gallery" Button inside Modal
    const addBtn = document.getElementById('addToGalleryBtn');
    addBtn.innerHTML = '<i class="ph ph-plus-circle"></i> Add to Gallery'; // Reset text
    addBtn.classList.remove('btn-success'); // Reset color
    
    // Add Click Event to Modal Button
    addBtn.onclick = function() {
        const icon = this.querySelector('i');
        icon.className = "ph ph-spinner ph-spin"; // Loading
        
        fetch('/api/add-to-gallery', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filename: file})
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                addBtn.innerHTML = '<i class="ph ph-check"></i> Saved to Gallery';
                addBtn.classList.add('btn-success'); // Green color
            }
        });
    };

    // 5. Show Modal (Using Bootstrap 5 API)
    var myModal = new bootstrap.Modal(document.getElementById('artDetailModal'));
    myModal.show();
}