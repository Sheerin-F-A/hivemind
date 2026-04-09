import re

with open('recommendations.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the specific block
start = text.find('<div class="subreddit-list">')
end = text.find('</div>\n        </div>\n    </main>')

if start != -1 and end != -1:
    new_html = """<div class="subreddit-list" id="rec-feed">
                    <div style="text-align: center; color: #86868B; margin-top: 20px;">Computing Recommendations from Vault History...</div>
                </div>
            </div>
        </div>
    </main>

    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            const feed = document.getElementById('rec-feed');
            try {
                const res = await fetch('/api/sentiment/overview?days=30');
                const data = await res.json();
                
                if (data.recent_vault && data.recent_vault.length > 0) {
                    const subStats = {};
                    data.recent_vault.forEach(c => {
                        let sub = c.subreddit;
                        if (sub === "unknown" || sub === "user_profile") return;
                        if (!subStats[sub]) subStats[sub] = { count: 0, pos: 0 };
                        subStats[sub].count++;
                        if (c.sentiment_label === 'positive') subStats[sub].pos++;
                    });
                    
                    const sortedSubs = Object.keys(subStats)
                        .filter(sub => subStats[sub].pos > 0)
                        .sort((a, b) => (subStats[b].pos/subStats[b].count) - (subStats[a].pos/subStats[a].count));

                    feed.innerHTML = "";
                    if (sortedSubs.length === 0) {
                        feed.innerHTML = "<div style='color:#86868B;'>Your NLTK History doesn't have enough positive subreddits to recommend new clusters. Search for more!</div>";
                        return;
                    }

                    sortedSubs.forEach((sub, i) => {
                        const match = Math.floor((subStats[sub].pos / subStats[sub].count) * 100);
                        feed.innerHTML += `
                        <div class="subreddit-card">
                            <div class="subreddit-rank">${i + 1}</div>
                            <div class="subreddit-content">
                                <div class="subreddit-header">
                                    <h4>r/${sub}</h4>
                                    <span class="member-count">Analyzed Cluster</span>
                                </div>
                                <p class="subreddit-desc">Organic Subreddit extracted dynamically based on positive Vault analytics.</p>
                                <div class="match-reason">Matches your high positivity (${match}%) in historic threads.</div>
                            </div>
                            <div class="subreddit-match">
                                <div class="match-score">${match}%</div>
                                <div class="match-label">match</div>
                            </div>
                            <div class="subreddit-actions">
                                <button class="btn-external" onclick="window.open('https://reddit.com/r/${sub}', '_blank')">
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M12 4L4 12M12 4H6M12 4V10" stroke="#86868B" stroke-width="2" stroke-linecap="round"/>
                                    </svg>
                                </button>
                            </div>
                        </div>`;
                    });
                } else {
                    feed.innerHTML = '<div class="readonly-notice">No history found to analyze. Search first!</div>';
                }
            } catch(e) { console.error(e); }
        });
    </script>"""
    
    text = text[:start] + new_html + text[end + len('</div>\n        </div>\n    </main>'):]
    with open('recommendations.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Patched correctly.")
else:
    print("Could not find blocks.")
