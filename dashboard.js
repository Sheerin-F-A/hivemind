// Dashboard Page Functionality

let sentimentChartInstance = null;

document.addEventListener('DOMContentLoaded', function () {
    // Initial load
    const searchInput = document.querySelector('.topic-search-input');
    const initialQuery = searchInput ? searchInput.value : "Artificial Intelligence";
    fetchAndRenderData(initialQuery, 30);

    // Setup Search Trigger
    const searchBtn = document.querySelector('.analyze-btn');
    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', () => handleSearch(searchInput.value));
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleSearch(searchInput.value);
        });
    }

    // Update time
    updateTime();
    setInterval(updateTime, 1000);

    // Breakdown toggle functionality
    setupBreakdownToggles();

    // Timeline selector
    setupTimelineSelector();
});

async function handleSearch(query) {
    if (!query.trim()) return;
    
    // Show some loading state visually
    const searchBtn = document.querySelector('.analyze-btn');
    const originalText = searchBtn.textContent;
    searchBtn.textContent = "Analyzing...";
    searchBtn.disabled = true;

    try {
        // 1. Ask backend to generate/analyze mock data for the query
        const searchRes = await fetch(`/api/search?query=${encodeURIComponent(query)}`, {
            method: 'POST'
        });
        
        if (!searchRes.ok) {
            const errorData = await searchRes.json().catch(() => ({}));
            const errDetail = errorData.detail || errorData.message || "network connection is unstable";
            alert(errDetail);
            throw new Error(errDetail);
        }

        // 2. Fetch the newly compiled overview and redraw!
        const days = document.getElementById('timelineSelect')?.value || 30;
        await fetchAndRenderData(query, days);
        
        // Update title
        const titleEl = document.querySelector('.dashboard-content h2');
        if (titleEl) titleEl.textContent = `Sentiment Analysis for "${query}"`;
        
    } catch (e) {
        console.error("Search failed:", e);
    } finally {
        searchBtn.textContent = originalText;
        searchBtn.disabled = false;
        
        // Hide the loading modal if it was triggered by the HTML onclick
        const loadingModal = document.getElementById('loadingModal');
        if (loadingModal) {
            loadingModal.classList.remove('show');
        }
    }
}

async function fetchAndRenderData(query, days) {
    try {
        const res = await fetch(`/api/sentiment/overview?query=${encodeURIComponent(query)}&days=${days}`);
        const data = await res.json();
        
        updateDOMCounters(data);
        renderSentimentChart(data.history);
    } catch (e) {
        console.error("Failed to fetch sentiment overview:", e);
    }
}

function updateDOMCounters(data) {
    // 1. Update Score Circle Gauge
    const gaugeText = document.querySelector('#gaugeProgress').nextElementSibling;
    const scoreLabel = document.querySelector('.score-card .score-label');
    const gaugeProgress = document.getElementById('gaugeProgress');
    
    if (gaugeText) gaugeText.textContent = data.overall_score;
    if (scoreLabel) {
        const color = data.overall_label === 'Positive' ? '#4CAF50' : data.overall_label === 'Negative' ? '#FF5252' : '#86868B';
        scoreLabel.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <circle cx="6" cy="6" r="5" fill="${color}" />
            </svg>
            ${data.overall_label}
        `;
        scoreLabel.className = `score-label ${data.overall_label.toLowerCase()}`;
    }
    if (gaugeProgress) {
        const strokeColor = data.overall_label === 'Positive' ? '#4CAF50' : data.overall_label === 'Negative' ? '#FF5252' : '#86868B';
        gaugeProgress.setAttribute('stroke', strokeColor);
    }
    
    // 2. Update Comments Sentiment Card & Content Sentiment Card
    const cards = document.querySelectorAll('.score-card');
    cards.forEach(card => {
        const title = card.querySelector('h3');
        if (!title) return;
        
        let breakdownSource = null;
        if (title.textContent.includes('Comments')) breakdownSource = data.comments_breakdown;
        if (title.textContent.includes('Content')) breakdownSource = data.content_breakdown;
        
        if (breakdownSource) {
            const largeScore = card.querySelector('.large-score');
            
            // Mathematically normalize an exact score 0-100 logic using a base-50 pivot
            // Positive adds points, Negative subtracts points from the baseline
            let cardScore = Math.floor(50 + (breakdownSource.positive * 0.5) - (breakdownSource.negative * 0.5));
            if (largeScore) largeScore.textContent = cardScore;
            
            const cardLabel = card.querySelector('.score-label');
            if (cardLabel) {
                let labelText = 'Neutral';
                let cls = 'neutral';
                let col = '#86868B';
                if (cardScore >= 60) {
                    labelText = 'Positive'; cls = 'positive'; col = '#4CAF50';
                } else if (cardScore <= 40) {
                    labelText = 'Negative'; cls = 'negative'; col = '#FF5252';
                }
                cardLabel.className = `score-label ${cls}`;
                cardLabel.innerHTML = `
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                        <circle cx="6" cy="6" r="5" fill="${col}" />
                    </svg>
                    ${labelText}
                `;
            }
            
            // Update individual breakdown percentages
            const items = card.querySelectorAll('.breakdown-item .percentage');
            if (items.length >= 3) {
                items[0].textContent = breakdownSource.positive + '%';
                items[1].textContent = breakdownSource.neutral + '%';
                items[2].textContent = breakdownSource.negative + '%';
            }
        }
    });
}

function renderSentimentChart(historyData) {
    const ctx = document.getElementById('sentimentChart');
    if (!ctx) return;

    if (sentimentChartInstance) {
        sentimentChartInstance.destroy();
    }

    sentimentChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: historyData.labels,
            datasets: [
                {
                    label: 'Positive',
                    data: historyData.positive,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    borderWidth: 2
                },
                {
                    label: 'Neutral',
                    data: historyData.neutral,
                    borderColor: '#86868B',
                    backgroundColor: 'rgba(134, 134, 139, 0.05)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    borderWidth: 2
                },
                {
                    label: 'Negative',
                    data: historyData.negative,
                    borderColor: '#FF5252',
                    backgroundColor: 'rgba(255, 82, 82, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(29, 29, 31, 0.95)',
                    padding: 12,
                    cornerRadius: 8,
                    titleFont: { size: 12, weight: '600' },
                    bodyFont: { size: 11 },
                    displayColors: true,
                    boxWidth: 8,
                    boxHeight: 8,
                    boxPadding: 4
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#86868B', font: { size: 11 }, maxRotation: 0, autoSkip: true, maxTicksLimit: 8 },
                    border: { display: false }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: '#F5F5F7', drawBorder: false },
                    ticks: { color: '#86868B', font: { size: 11 }, stepSize: 20 },
                    border: { display: false }
                }
            },
            interaction: { mode: 'index', intersect: false }
        }
    });
}

function setupBreakdownToggles() {
    const commentsToggle = document.getElementById('commentsBreakdown');
    const commentsBreakdownList = document.getElementById('commentsBreakdownList');

    const contentToggle = document.getElementById('contentBreakdown');
    const contentBreakdownList = document.getElementById('contentBreakdownList');

    if (commentsToggle) {
        commentsToggle.addEventListener('click', function () {
            const isHidden = commentsBreakdownList.style.display === 'none';
            commentsBreakdownList.style.display = isHidden ? 'flex' : 'none';
            this.innerHTML = isHidden
                ? '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 10L8 6L12 10" stroke="#FF4500" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Hide Breakdown'
                : '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 6L8 10L12 6" stroke="#FF4500" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Show Breakdown';
        });
    }

    if (contentToggle) {
        contentToggle.addEventListener('click', function () {
            const isHidden = contentBreakdownList.style.display === 'none';
            contentBreakdownList.style.display = isHidden ? 'flex' : 'none';
            this.innerHTML = isHidden
                ? '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 10L8 6L12 10" stroke="#FF4500" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Hide Breakdown'
                : '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 6L8 10L12 6" stroke="#FF4500" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Show Breakdown';
        });
    }
}

function setupTimelineSelector() {
    const timelineSelect = document.getElementById('timelineSelect');
    if (timelineSelect) {
        timelineSelect.addEventListener('change', async function () {
            console.log('Timeline changed to:', this.value, 'days');
            const query = document.getElementById('searchInput')?.value.trim() || "";
            await fetchAndRenderData(query, this.value);
        });
    }
}

function updateTime() {
    const timeElements = document.querySelectorAll('.time');
    const dateElements = document.querySelectorAll('.date');
    const now = new Date();

    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });

    const dateString = now.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });

    timeElements.forEach(el => {
        if (el) el.textContent = timeString;
    });

    dateElements.forEach(el => {
        if (el) el.textContent = dateString;
    });
}
