document.addEventListener("DOMContentLoaded", function() {
    // 1. Intersection Observer for Scroll Animation
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
            } else {
                entry.target.classList.remove('show');
            }
        });
    }, { threshold: 0.1, rootMargin: "0px 0px -50px 0px" });

    // 2. Select Elements to Animate
    const hiddenElements = document.querySelectorAll('.hidden-left, .hidden-right');
    hiddenElements.forEach((el) => observer.observe(el));
});