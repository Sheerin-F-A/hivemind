// Recommendations Page Functionality

document.addEventListener('DOMContentLoaded', function () {
    // Update time
    updateTime();
    setInterval(updateTime, 1000);

    // Setup join button functionality
    setupJoinButtons();

    // Setup external link buttons
    setupExternalButtons();
});

function setupJoinButtons() {
    const joinButtons = document.querySelectorAll('.btn-join');

    joinButtons.forEach(button => {
        button.addEventListener('click', function () {
            const card = this.closest('.subreddit-card');
            const subredditName = card.querySelector('h4').textContent;

            // Change button state
            if (this.classList.contains('joined')) {
                this.classList.remove('joined');
                this.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M8 3V13M3 8H13" stroke="white" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    Join
                `;
            } else {
                this.classList.add('joined');
                this.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M3 8L6 11L13 4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Joined
                `;
                this.style.background = '#4CAF50';

                // In production, this would make an API call to join the subreddit
                console.log('Joined:', subredditName);
            }
        });
    });
}

function setupExternalButtons() {
    const externalButtons = document.querySelectorAll('.btn-external');

    externalButtons.forEach(button => {
        button.addEventListener('click', function () {
            const card = this.closest('.subreddit-card');
            const subredditName = card.querySelector('h4').textContent;
            const subredditPath = subredditName.replace('r/', '');

            // Open subreddit in new tab
            window.open(`https://www.reddit.com/${subredditName}`, '_blank');
        });
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
