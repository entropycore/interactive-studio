document.querySelectorAll('.tool-choice').forEach((button) => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.tool-choice').forEach(item => item.classList.remove('active'));
        document.querySelectorAll('.tool-panel').forEach(panel => panel.classList.remove('active'));
        button.classList.add('active');
        document.getElementById(button.dataset.panel).classList.add('active');
    });
});

bindFileName('imageFile', 'imageFileName', 'Choose image');
bindFileName('audioFile', 'audioFileName', 'Choose audio');

bindMediaForm({
    formId: 'imageForm',
    endpoint: '/api/media/image',
    statusId: 'imageStatus',
    resultId: 'imageResult',
    loadingText: 'Rendering image effect...',
    render: (payload) => `
        <div>
            <img src="${payload.url}" alt="Edited artwork">
            <a class="download-link" href="${payload.url}" download>Download Image</a>
        </div>
    `
});

bindMediaForm({
    formId: 'audioForm',
    endpoint: '/api/media/audio',
    statusId: 'audioStatus',
    resultId: 'audioResult',
    loadingText: 'Processing voice texture...',
    render: (payload) => `
        <div class="audio-output">
            <audio controls src="${payload.url}"></audio>
            <a class="download-link" href="${payload.url}" download>Download Audio</a>
        </div>
    `
});

function bindMediaForm(config) {
    const form = document.getElementById(config.formId);
    const status = document.getElementById(config.statusId);
    const result = document.getElementById(config.resultId);
    const button = form.querySelector('button[type="submit"]');
    const defaultButtonText = button.textContent;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        setStatus(status, config.loadingText, false);
        button.disabled = true;
        button.textContent = 'Working...';

        try {
            const response = await fetch(config.endpoint, {
                method: 'POST',
                body: new FormData(form)
            });
            const payload = await readJsonResponse(response);

            if (!response.ok || !payload.success) {
                throw new Error(payload.error || 'Processing failed.');
            }

            result.innerHTML = config.render(payload);
            setStatus(status, 'Ready.', false);
        } catch (error) {
            setStatus(status, error.message, true);
        } finally {
            button.disabled = false;
            button.textContent = defaultButtonText;
        }
    });
}

async function readJsonResponse(response) {
    const text = await response.text();
    if (!text) return {};

    try {
        return JSON.parse(text);
    } catch (error) {
        throw new Error('Server returned an unreadable response.');
    }
}

function setStatus(element, message, isError) {
    element.textContent = message;
    element.classList.toggle('error', Boolean(isError));
}

function bindFileName(inputId, labelId, fallback) {
    const input = document.getElementById(inputId);
    const label = document.getElementById(labelId);
    if (!input || !label) return;

    input.addEventListener('change', () => {
        label.textContent = input.files[0] ? input.files[0].name : fallback;
    });
}
