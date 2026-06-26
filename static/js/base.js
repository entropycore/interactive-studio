/* =========================================
   1. THEME TOGGLE LOGIC
   ========================================= */
document.addEventListener('DOMContentLoaded', () => {
    // Apply saved theme on load
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
    }
});

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
}

/* =========================================
   2. MOBILE MENU LOGIC
   ========================================= */
function toggleMobileMenu() {
    const menu = document.getElementById("navMenu");
    if(menu) menu.classList.toggle("active");
}

// Close menu when clicking outside
document.addEventListener("click", function (event) {
    const menu = document.getElementById("navMenu");
    const hamburgerBtn = document.querySelector(".hamburger-btn");
    
    if (menu && hamburgerBtn) {
        if (menu.classList.contains("active") && !menu.contains(event.target) && !hamburgerBtn.contains(event.target)) {
            menu.classList.remove("active");
        }
    }
});

// Close menu when clicking a link
const navLinks = document.querySelectorAll(".nav-menu a");
if(navLinks) {
    navLinks.forEach((link) => {
        link.addEventListener("click", () => {
            const menu = document.getElementById("navMenu");
            if(menu) menu.classList.remove("active");
        });
    });
}

/* =========================================
   3. SEARCH BAR LOGIC
   ========================================= */
function toggleSearch() {
    const searchBox = document.querySelector(".search-box");
    const input = document.getElementById("searchInput");
    
    if (searchBox && input) {
        searchBox.classList.toggle("active");
        if (searchBox.classList.contains("active")) {
            input.focus();
        }
    }
}

// Live Search Fetch
const searchInput = document.getElementById("searchInput");
const resultsList = document.getElementById("searchResults");

if (searchInput && resultsList) {
    searchInput.addEventListener("input", function () {
        const query = this.value;
        if (query.length < 2) {
            resultsList.style.display = "none";
            return;
        }
        fetch(`/search?q=${query}`)
            .then((response) => response.json())
            .then((data) => {
                resultsList.innerHTML = "";
                if (data.length > 0) {
                    resultsList.style.display = "block";
                    data.forEach((item) => {
                        const li = document.createElement("li");
                        li.innerHTML = `<a href="${item.url}">${item.title}</a>`;
                        resultsList.appendChild(li);
                    });
                } else {
                    resultsList.style.display = "none";
                }
            })
            .catch(err => console.error(err));
    });

    // Hide results on outside click
    document.addEventListener("click", function (e) {
        if (!searchInput.contains(e.target) && !resultsList.contains(e.target)) {
            resultsList.style.display = "none";
        }
    });
}

/* =========================================
   4. AI ASSISTANT (HERMES) LOGIC (With Typing Effect )
   ========================================= */
function toggleAI() {
    const wrapper = document.querySelector('.luxury-ai-wrapper');
    const input = document.getElementById('aiInput');
    if (wrapper) {
        wrapper.classList.toggle('open');
        if (wrapper.classList.contains('open') && input) {
            setTimeout(() => input.focus(), 400);
        }
    }
}

function handleAIEnter(e) { 
    if(e.key === "Enter") sendAIMsg(); 
}

function sendAIMsg() {
    const input = document.getElementById("aiInput");
    const body = document.getElementById("aiMessagesBody");
    
    if(!input || !body) return;
    
    const txt = input.value.trim();
    if(!txt) return;
    
    // 1. Show User Message
    addMsg(txt, 'user');
    input.value = "";
    
    // 2. Show Loading Indicator 
    const loadingId = "ai-loading-indicator";
    const loadingDiv = document.createElement("div");
    loadingDiv.id = loadingId;
    loadingDiv.className = "ai-msg bot";
    loadingDiv.innerHTML = "<em>Honar is thinking... ✨</em>";
    loadingDiv.style.opacity = "0.7";
    body.appendChild(loadingDiv);
    body.scrollTop = body.scrollHeight;
    
    // 3. Send to Server
    fetch("/chat", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message: txt })
    })
    .then(res => res.json())
    .then(data => {
        // Remove Loading
        const loader = document.getElementById(loadingId);
        if(loader) loader.remove();

        // 4. Show Bot Response with Animation (Typing Effect)
        addMsg(data.response, 'bot', true); 
    })
    .catch(err => {
        const loader = document.getElementById(loadingId);
        if(loader) loader.remove();
        addMsg("Honar is sleeping... (Connection Error)", 'bot');
    });
}

// wrting effect for bot messages
function addMsg(text, type, animate = false) {
    const body = document.getElementById("aiMessagesBody");
    if(!body) return;
    
    const div = document.createElement("div");
    div.className = `ai-msg ${type}`;
    
    body.appendChild(div);

    if (type === 'bot' && animate) {
        // Typing Animation Logic
        let i = 0;
        const speed = 15; 
        
        function typeWriter() {
            if (i < text.length) {
                
                if (text.charAt(i) === '\n') {
                    div.innerHTML += '<br>';
                } else {
                    div.textContent += text.charAt(i);
                }
                i++;
                body.scrollTop = body.scrollHeight; // Scroll automatic
                setTimeout(typeWriter, speed);
            }
        }
        typeWriter(); // Start Animation
    } else {
        // User message (Direct)
        div.innerText = text;
    }
    
    body.scrollTop = body.scrollHeight;
}

/* =========================================
   5. FOOTER COLLISION FIX (AI Button)
   ========================================= */
window.addEventListener('scroll', function() {
    const btn = document.querySelector('.luxury-ai-wrapper');
    const footer = document.querySelector('.site-footer');
    
    if(!btn || !footer) return;

    const footerRect = footer.getBoundingClientRect();
    const winHeight = window.innerHeight;
    
    if (footerRect.top < winHeight) {
        const liftAmount = winHeight - footerRect.top + 20; 
        btn.style.bottom = `${liftAmount}px`;
    } else {
        btn.style.bottom = '30px';
    }
});










