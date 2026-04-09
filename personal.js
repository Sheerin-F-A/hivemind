// Personal Analysis Page Functionality

document.addEventListener('DOMContentLoaded', function () {
    // Initialize Chart
    initPersonalChart();

    // Update time
    updateTime();
    setInterval(updateTime, 1000);
});

function initPersonalChart() {
    const ctx = document.getElementById('personalChart');
    if (!ctx) return;

    // Sample data showing upward trend
    const labels = generateDateLabels(60);
    const sentimentData = generateTrendingData(60, 55, 75);

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
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(29, 29, 31, 0.95)',
                    padding: 12,
                    cornerRadius: 8,
                    titleFont: {
                        size: 12,
                        weight: '600'
                    },
                    bodyFont: {
                        size: 11
                    },
                    displayColors: false,
                    callbacks: {
                        label: function (context) {
                            return 'Score: ' + context.parsed.y;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#86868B',
                        font: {
                            size: 11
                        },
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 8
                    },
                    border: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: false,
                    min: 40,
                    max: 80,
                    grid: {
                        color: '#F5F5F7',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#86868B',
                        font: {
                            size: 11
                        },
                        stepSize: 10
                    },
                    border: {
                        display: false
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
}

function generateDateLabels(days) {
    const labels = [];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const today = new Date();

    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);

        if (i === days - 1 || i % 15 === 0) {
            labels.push(`${months[date.getMonth()]} ${date.getDate()}`);
        } else {
            labels.push('');
        }
    }

    return labels;
}

function generateTrendingData(count, min, max) {
    const data = [];
    const trend = (max - min) / count; // Upward trend

    for (let i = 0; i < count; i++) {
        const baseValue = min + (trend * i);
        const variance = (Math.random() - 0.5) * 8; // Add some variance
        const value = baseValue + variance;
        data.push(Math.round(Math.max(min, Math.min(max, value))));
    }

    return data;
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
