// Personal Analysis Page Functionality

document.addEventListener('DOMContentLoaded', function () {
    // Initialize Chart
    initPersonalChart();

    // Update time
    updateTime();
    setInterval(updateTime, 1000);
});

async function initPersonalChart() {
    const ctx = document.getElementById('personalChart');
    if (!ctx) return;

    try {
        const res = await fetch('/api/sentiment/overview?days=30');
        const data = await res.json();
        
        let labels = data.history ? data.history.labels : [];
        let sentimentData = data.history ? data.history.positive : [];
        
        if (!labels || labels.length === 0) {
            labels = generateDateLabels(7);
            sentimentData = [0,0,0,0,0,0,0];
        }

        // Fill Personal Overvall Gauge dynamically as well!
        const gaugeVal = document.getElementById('personalGaugeProgress');
        const scoreText = document.querySelector('.gauge-container-small text');
        if (gaugeVal && data.overall_score !== undefined) {
             const dashoffset = 408 - (408 * data.overall_score) / 100;
             gaugeVal.setAttribute('stroke-dashoffset', dashoffset);
             scoreText.textContent = data.overall_score;
        }
        
        // Populate Trends from recent_vault dynamically
        populateDynamicTrends(data.recent_vault);

        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Sentiment Score',
                        data: sentimentData,
                        borderColor: '#FF4500',
                        backgroundColor: 'rgba(255, 69, 0, 0.05)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 3,
                        pointBackgroundColor: '#FF4500',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
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
                        displayColors: false,
                        callbacks: {
                            label: function (context) { return 'Score: ' + context.parsed.y; }
                        }
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
                        min: 0,
                        max: 100,
                        grid: { color: '#F5F5F7', drawBorder: false },
                        ticks: { color: '#86868B', font: { size: 11 }, stepSize: 20 },
                        border: { display: false }
                    }
                },
                interaction: { mode: 'index', intersect: false }
            }
        });
    } catch (e) {
        console.error("Personal Chart Error:", e);
    }
}

function populateDynamicTrends(vault) {
    const list = document.querySelector('.trends-list');
    if (!list || !vault) return;
    
    list.innerHTML = "";
    if (vault.length === 0) {
        list.innerHTML = "<div style='color:#86868B'>No trends observed yet. Explore threads first!</div>";
        return;
    }
    
    vault.slice(0, 5).forEach(c => {
         let iconCol = '#86868B'; let cls = 'neutral';
         if (c.sentiment_label === 'positive') { iconCol = '#4CAF50'; cls = 'positive'; }
         if (c.sentiment_label === 'negative') { iconCol = '#FF5252'; cls = 'negative'; }
         
         const scoreStr = c.sentiment_score ? Math.round(c.sentiment_score * 100) : 0;
         
         list.innerHTML += `
             <div class="trend-item">
                <div class="trend-icon ${cls}">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <circle cx="8" cy="8" r="6" stroke="${iconCol}" stroke-width="2"/>
                    </svg>
                </div>
                <div class="trend-content">
                    <div class="trend-title">${c.title} (r/${c.subreddit})</div>
                    <div class="trend-desc">${c.body.substring(0, 60)}...</div>
                </div>
                <div class="trend-stats">
                    <span class="trend-percent ${cls}">${scoreStr > 0 ? '+':''}${scoreStr}%</span>
                    <span class="trend-label">${c.sentiment_label}</span>
                </div>
             </div>
         `;
    });
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

function generateDateLabels(days) {
    const labels = [];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const today = new Date();

    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        labels.push(`${months[date.getMonth()]} ${date.getDate()}`);
    }

    return labels;
}
