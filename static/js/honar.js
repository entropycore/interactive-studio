let currentChatId = null;

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainBurger = document.getElementById('main-burger');
    sidebar.classList.toggle('collapsed');
    
    if (sidebar.classList.contains('collapsed')) {
        mainBurger.style.display = 'block';
    } else {
        mainBurger.style.display = 'none';
    }
}

async function handleSendClick() {
    const input = document.getElementById('honar-input');
    const text = input.value.trim();
    if (!text) return;

    const welcomeState = document.getElementById('welcome-state');
    if(welcomeState) welcomeState.style.display = 'none';

    if (!currentChatId) {
        try {
            appendMessage(text, 'user');
            input.value = ''; 

            const res = await fetch('/api/chat/new', { method: 'POST' });
            const chat = await res.json();
            currentChatId = chat.id;
            
            addChatToSidebar(chat.id, text.substring(0, 20) + "...");
            sendMessageToBackend(text);
        } catch (err) {
            console.error("Error creating chat:", err);
        }
    } else {
        appendMessage(text, 'user');
        input.value = '';
        sendMessageToBackend(text);
    }
}

function sendMessageToBackend(text) {
    showTypingIndicator();
    fetch('/api/chat/send', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ chat_id: currentChatId, message: text })
    })
    .then(res => res.json())
    .then(data => {
        removeTypingIndicator();
        appendMessage(data.response, 'bot', true);
        
        const titleEl = document.getElementById(`title-${currentChatId}`);
        if(titleEl && titleEl.innerText === "New Conversation") {
            titleEl.innerText = text.substring(0, 20) + "...";
        }
    })
    .catch(() => {
        removeTypingIndicator();
        appendMessage("Connection Error", 'bot');
    });
}

function loadChat(chatId) {
    if(currentChatId === chatId) return;
    currentChatId = chatId;
    
    const welcomeState = document.getElementById('welcome-state');
    if (welcomeState) welcomeState.style.display = 'none';

    document.querySelectorAll('.chat-item-glass').forEach(el => el.classList.remove('active'));
    const item = document.getElementById(`chat-item-${chatId}`);
    if(item) item.classList.add('active');

    if(window.innerWidth < 768) toggleSidebar();

    fetch(`/api/chat/get/${chatId}`)
    .then(res => res.json())
    .then(chat => {
        const display = document.getElementById('honar-display');
        display.querySelectorAll('.message-row').forEach(row => row.remove());
        chat.messages.forEach(msg => appendMessage(msg.text, msg.sender));
        display.scrollTop = display.scrollHeight;
    });
}

function appendMessage(text, sender, animate = false) {
    const display = document.getElementById('honar-display');
    const row = document.createElement('div');
    row.className = `message-row ${sender}`;
    const bubble = document.createElement('div');
    bubble.className = `bubble ${sender}`;
    row.appendChild(bubble);
    display.appendChild(row);

    if (sender === 'bot' && animate) {
        let i = 0; const speed = 10;
        function typeWriter() {
            if (i < text.length) {
                if (text.charAt(i) === '\n') bubble.innerHTML += '<br>';
                else bubble.textContent += text.charAt(i);
                i++;
                display.scrollTop = display.scrollHeight;
                setTimeout(typeWriter, speed);
            }
        }
        typeWriter();
    } else {
        bubble.innerText = text;
    }
    display.scrollTop = display.scrollHeight;
}

function toggleMenu(e, chatId) {
    e.stopPropagation();
    document.querySelectorAll('.glass-dropdown').forEach(el => el.classList.remove('show'));
    const menu = document.getElementById(`menu-${chatId}`);
    if(menu) menu.classList.toggle('show');
}

document.addEventListener('click', () => {
    document.querySelectorAll('.glass-dropdown').forEach(el => el.classList.remove('show'));
});

// 👇 النافذة المخصصة اللي غتعوض Default Alert (Logic) 👇
function openModal(title, text, type) {
    return new Promise((resolve) => {
        const modal = document.getElementById('honarModal');
        const input = document.getElementById('modal-input');
        
        document.getElementById('modal-title').innerText = title;
        document.getElementById('modal-text').innerText = text;

        if (type === 'prompt') {
            input.style.display = 'block';
            input.value = '';
            setTimeout(() => input.focus(), 100);
        } else {
            input.style.display = 'none';
        }

        modal.style.display = 'flex';

        document.getElementById('modal-btn-ok').onclick = () => {
            modal.style.display = 'none';
            resolve(type === 'prompt' ? input.value : true);
        };
        
        document.getElementById('modal-btn-cancel').onclick = () => {
            modal.style.display = 'none';
            resolve(null);
        };
    });
}


async function deleteChat(e, chatId) {
    e.stopPropagation();
    document.getElementById(`menu-${chatId}`).classList.remove('show');

    
    const confirmed = await openModal("Delete Chat", "Are you sure you want to delete this conversation?", "confirm");
    
    if (confirmed) {
        fetch('/api/chat/delete', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ chat_id: chatId })
        }).then(() => {
            document.getElementById(`chat-item-${chatId}`).remove();
            if(currentChatId === chatId) location.reload();
        });
    }
}


async function renameChat(e, chatId) {
    e.stopPropagation();
    document.getElementById(`menu-${chatId}`).classList.remove('show');

    
    const newTitle = await openModal("Rename Chat", "Please enter a new name for this chat:", "prompt");
    
    if(newTitle && newTitle.trim() !== "") {
        document.getElementById(`title-${chatId}`).innerText = newTitle;
    }
}

function startNewChatUI() {
    currentChatId = null;
    const display = document.getElementById('honar-display');
    display.querySelectorAll('.message-row').forEach(row => row.remove());
    const welcomeState = document.getElementById('welcome-state');
    if (welcomeState) welcomeState.style.display = 'flex';
    document.querySelectorAll('.chat-item-glass').forEach(el => el.classList.remove('active'));
    
    const sidebar = document.getElementById('sidebar');
    if (sidebar && sidebar.classList.contains('collapsed')) {
        toggleSidebar();
    }
}

function addChatToSidebar(id, title) {
    const chatList = document.querySelector('.chat-list-glass');
    document.querySelectorAll('.chat-item-glass').forEach(el => el.classList.remove('active'));

    const template = document.getElementById('chat-item-template');
    const clone = template.content.cloneNode(true);

    const newChatDiv = clone.querySelector('.chat-item-glass');
    newChatDiv.id = `chat-item-${id}`;
    newChatDiv.classList.add('active');
    newChatDiv.setAttribute('onclick', `loadChat('${id}')`);

    const titleSpan = clone.querySelector('.chat-title-text');
    titleSpan.id = `title-${id}`;
    titleSpan.textContent = title;

    const optionsDiv = clone.querySelector('.chat-options');
    optionsDiv.setAttribute('onclick', `toggleMenu(event, '${id}')`);

    const dropdownDiv = clone.querySelector('.glass-dropdown');
    dropdownDiv.id = `menu-${id}`;

    const renameBtn = clone.querySelector('.action-rename');
    renameBtn.setAttribute('onclick', `renameChat(event, '${id}')`);

    const deleteBtn = clone.querySelector('.action-delete');
    deleteBtn.setAttribute('onclick', `deleteChat(event, '${id}')`);

    chatList.prepend(clone);
}

function showTypingIndicator() {
    const display = document.getElementById('honar-display');
    const row = document.createElement('div');
    row.id = 'typing-row'; row.className = 'message-row bot';
    row.innerHTML = `<div class="bubble bot" style="font-style:italic; opacity:0.7;">Honar is thinking...</div>`;
    display.appendChild(row);
    display.scrollTop = display.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById('typing-row');
    if(el) el.remove();
}

document.getElementById('honar-input').addEventListener('keypress', function(e) {
    if(e.key === 'Enter') {
        e.preventDefault(); 
        handleSendClick();
    }
});

window.onload = () => document.getElementById('honar-input').focus();