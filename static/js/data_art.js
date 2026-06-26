const dataState = {
    rows: [],
    suggestions: []
};

const dataForm = document.getElementById('dataUploadForm');
const csvFile = document.getElementById('csvFile');
const fileName = document.getElementById('fileName');
const analyzeBtn = document.getElementById('analyzeBtn');
const dataStatus = document.getElementById('dataStatus');
const analysisPanel = document.getElementById('analysisPanel');
const suggestionGrid = document.getElementById('suggestionGrid');
const dataMeta = document.getElementById('dataMeta');
const fileProfile = document.getElementById('fileProfile');
const chartInsight = document.getElementById('chartInsight');
let dataMetaPayload = {};

csvFile.addEventListener('change', () => {
    fileName.textContent = csvFile.files[0] ? csvFile.files[0].name : 'Choose a dataset';
});

dataForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    setDataLoading(true, 'Analyzing structure...');

    try {
        const response = await fetch('/api/analyze-csv', {
            method: 'POST',
            body: new FormData(dataForm)
        });
        const payload = await readJsonResponse(response);

        if (!response.ok || !payload.success) {
            throw new Error(payload.error || 'CSV analysis failed.');
        }

        dataState.rows = payload.data || [];
        dataState.suggestions = payload.suggestions || [];
        dataMetaPayload = payload.meta || {};
        renderMeta(payload.meta || {});
        renderFileProfile(payload.meta || {});
        renderSuggestions();
        analysisPanel.hidden = false;

        if (dataState.suggestions.length) {
            drawChart(0);
            setDataStatus('Analysis complete. Select a visual direction.', false);
            analysisPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            setDataStatus('Analysis complete, but no chart pairings were detected.', false);
        }
    } catch (error) {
        setDataStatus(error.message, true);
    } finally {
        setDataLoading(false);
    }
});

async function readJsonResponse(response) {
    const text = await response.text();
    if (!text) {
        return {};
    }

    try {
        return JSON.parse(text);
    } catch (error) {
        throw new Error('Server returned an unreadable response.');
    }
}

function setDataLoading(isLoading, message = '') {
    analyzeBtn.disabled = isLoading;
    analyzeBtn.textContent = isLoading ? 'Analyzing...' : 'Analyze CSV';
    if (message) {
        setDataStatus(message, false);
    }
}

function setDataStatus(message, isError) {
    dataStatus.textContent = message;
    dataStatus.classList.toggle('error', Boolean(isError));
}

function renderMeta(meta) {
    dataMeta.innerHTML = [
        `${meta.rows || 0} rows`,
        `${(meta.columns || []).length} columns`,
        `${(meta.numeric_cols || []).length} numeric`,
        `${(meta.category_cols || []).length} categories`,
        `${(meta.date_cols || []).length} dates`
    ].map(item => `<span>${item}</span>`).join('');
}

function renderFileProfile(meta) {
    const columnBlocks = [
        ['Numeric', meta.numeric_cols || []],
        ['Categories', meta.category_cols || []],
        ['Dates', meta.date_cols || []]
    ].map(([label, cols]) => `
        <div class="profile-block">
            <strong>${label}</strong>
            <span>${cols.length ? cols.map(escapeHtml).join(', ') : 'None detected'}</span>
        </div>
    `).join('');

    const preview = (meta.preview_rows || []).slice(0, 3).map((row) => {
        const cells = Object.entries(row).slice(0, 4).map(([key, value]) => {
            return `<span><b>${escapeHtml(key)}</b> ${escapeHtml(value ?? 'null')}</span>`;
        }).join('');
        return `<div class="preview-row">${cells}</div>`;
    }).join('');

    fileProfile.innerHTML = `
        <div class="profile-head">
            <div>
                <strong>${escapeHtml(meta.filename || 'Uploaded CSV')}</strong>
                <span>${meta.file_size_kb || 0} KB source file</span>
            </div>
            <div>${meta.rows || 0} records</div>
        </div>
        <div class="profile-grid">${columnBlocks}</div>
        <div class="preview-table">${preview}</div>
    `;
}

function renderSuggestions() {
    suggestionGrid.innerHTML = '';

    dataState.suggestions.forEach((item, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'suggestion-card';
        button.innerHTML = `
            <strong>${item.type}</strong>
            <span>${item.title}</span>
            <small>${axisText(item)}</small>
        `;
        button.addEventListener('click', () => drawChart(index));
        suggestionGrid.appendChild(button);
    });
}

function drawChart(index) {
    const config = dataState.suggestions[index];
    if (!config) return;
    const isDark = document.body.classList.contains('dark-mode');
    const textColor = isDark ? '#f7f4ff' : '#12131a';
    const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(15, 23, 42, 0.08)';

    document.querySelectorAll('.suggestion-card').forEach((card, cardIndex) => {
        card.classList.toggle('active', cardIndex === index);
    });

    const layout = {
        title: { text: config.title, font: { size: 20 } },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(255,255,255,0.22)',
        font: { family: 'Segoe UI, sans-serif', color: textColor },
        margin: { t: 70, r: 28, b: 78, l: 78 },
        xaxis: {
            title: { text: getXAxisLabel(config), standoff: 14 },
            gridcolor: gridColor,
            zerolinecolor: gridColor
        },
        yaxis: {
            title: { text: getYAxisLabel(config), standoff: 14 },
            gridcolor: gridColor,
            zerolinecolor: gridColor
        }
    };

    const trace = buildTrace(config);
    renderChartInsight(config);
    Plotly.newPlot('chartDisplay', [trace], layout, {
        responsive: true,
        displayModeBar: false
    });
}

function buildTrace(config) {
    if (config.type === 'bar') {
        return {
            type: 'bar',
            x: dataState.rows.map(row => row[config.x]),
            y: dataState.rows.map(row => row[config.y]),
            marker: { color: '#00d8ff' },
            hovertemplate: `${config.x}: %{x}<br>${config.y}: %{y}<extra></extra>`
        };
    }

    if (config.type === 'line' || config.type === 'area') {
        return {
            type: 'scatter',
            mode: 'lines+markers',
            fill: config.type === 'area' ? 'tozeroy' : 'none',
            x: dataState.rows.map(row => row[config.x]),
            y: dataState.rows.map(row => row[config.y]),
            line: { color: '#fb7185', width: 3, shape: 'spline' },
            marker: { size: 7, color: '#10131a' },
            hovertemplate: `${config.x}: %{x}<br>${config.y}: %{y}<extra></extra>`
        };
    }

    if (config.type === 'pie') {
        return {
            type: 'pie',
            labels: dataState.rows.map(row => row[config.labels]),
            values: dataState.rows.map(row => row[config.values]),
            marker: { colors: ['#00d8ff', '#fb7185', '#111827', '#94a3b8', '#22c55e'] },
            hovertemplate: `${config.labels}: %{label}<br>${config.values}: %{value}<extra></extra>`
        };
    }

    return {
        type: 'scatter',
        mode: 'markers',
        x: dataState.rows.map(row => row[config.x]),
        y: dataState.rows.map(row => row[config.y]),
        marker: {
            size: 12,
            color: dataState.rows.map(row => row[config.y]),
            colorscale: 'Viridis',
            opacity: 0.82
        },
        hovertemplate: `${config.x}: %{x}<br>${config.y}: %{y}<extra></extra>`
    };
}

function renderChartInsight(config) {
    chartInsight.innerHTML = `
        <div>
            <strong>Chart type</strong>
            <span>${escapeHtml(config.type)}</span>
        </div>
        <div>
            <strong>X axis</strong>
            <span>${escapeHtml(getXAxisLabel(config))}</span>
        </div>
        <div>
            <strong>Y axis / value</strong>
            <span>${escapeHtml(getYAxisLabel(config))}</span>
        </div>
        <p>${escapeHtml(chartPurpose(config))}</p>
    `;
}

function axisText(config) {
    return `X: ${getXAxisLabel(config)} / Y: ${getYAxisLabel(config)}`;
}

function getXAxisLabel(config) {
    return config.x || config.labels || 'Category';
}

function getYAxisLabel(config) {
    return config.y || config.values || 'Value';
}

function chartPurpose(config) {
    if (config.type === 'bar') return 'Best for comparing a numeric measure across categories.';
    if (config.type === 'line') return 'Best for showing how a numeric measure evolves over time.';
    if (config.type === 'pie') return 'Best for showing each category as part of the whole.';
    return 'Best for reading correlation between two numeric columns.';
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
