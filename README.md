# Reddit Hive Mind - Frontend

## 📱 Pixel-Perfect UI Recreation

This is an exact recreation of the Figma designs for Reddit Hive Mind. The frontend is built with vanilla HTML, CSS, and JavaScript with mobile-first responsive design.

## 🎨 Design Features

- **Login Page** - Clean OAuth2-ready login interface
- **Sentiment Dashboard** - Overview with gauge charts and timeline
- **Personal Analysis** - Trend tracking with Chart.js visualization
- **Recommendations** - Subreddit suggestions based on sentiment
- **Fully Responsive** - Mobile-first design that scales beautifully

## 📁 File Structure

```
reddit-hive-mind-frontend/
├── index.html              # Login page
├── dashboard.html          # Sentiment analysis dashboard
├── personal.html           # Personal trends page
├── recommendations.html    # Subreddit recommendations
├── styles/
│   └── main.css           # Complete stylesheet (mobile-first)
└── scripts/
    ├── login.js           # Login functionality
    ├── dashboard.js       # Dashboard with Chart.js
    ├── personal.js        # Personal page with trending chart
    └── recommendations.js # Recommendations logic
```

## 🚀 Quick Start

### Option 1: Open Directly
Simply open `index.html` in a modern web browser.

### Setup the Environment Wait List

> [!IMPORTANT]
> **Environment Variables:** Before starting the application, you must fill out the `.env` file! We auto-generate a `.env` from `.env.example` when you boot the backend. You need to assign your **Reddit Client ID** and **Reddit Client Secret** inside the `.env` file to enable Reddit OAuth! Ensure your Reddit app callback matches `http://localhost:8080/api/auth/callback`.

### 1. Start the Backend API (FastAPI)
The backend runs on FastAPI and acts as the secure middleman to fetch and store sentiment data. Run this in a terminal at the root directory:
```bash
chmod +x run.sh
./run.sh
```
This automatically initiates a virtual environment (`venv`), installs `requirements.txt`, processes the NLTK databases, and boots the backend server on `http://localhost:8080`.

### 2. Start the Frontend Application (UI)
In a *separate* terminal, run the static server from the root `hivemind` directory to serve the frontend:
```bash
python3 -m http.server 8000
```

Then navigate to `http://localhost:8000` via your web browser. Click the **Log In with Reddit** button to test the authenticated connection with the backend.

## 🎯 Demo Credentials

For testing the login flow:
- **Username:** `demo` or `test`
- **Password:** (any)

This will redirect you to the dashboard. In production, this would integrate with Reddit OAuth2.

## 📊 Dependencies

The only external dependency is **Chart.js** for data visualization, loaded via CDN in the HTML files:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

No build process, no npm install, no webpack - just pure vanilla web technologies.

## 🎨 Design System

### Colors
- **Reddit Orange:** `#FF4500`
- **Positive Green:** `#4CAF50`
- **Neutral Gray:** `#86868B`
- **Negative Red:** `#FF5252`
- **Background:** `#F5F5F7`
- **Text Primary:** `#1D1D1F`

### Typography
System fonts for optimal performance:
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
```

### Components
- **Cards:** 20px border-radius, soft shadows
- **Buttons:** 12px border-radius, 150ms transitions
- **Inputs:** 12px border-radius, 1.5px borders
- **Charts:** Smooth curves with Chart.js tension: 0.4

## 📱 Responsive Breakpoints

- **Desktop:** > 1200px (3-column grid)
- **Tablet:** 968px - 1200px (2-column grid)
- **Mobile:** < 968px (Single column, sidebar hidden)
- **Small Mobile:** < 640px (Compact header)

## 🔧 Customization

### Changing Colors
Edit CSS variables in `styles/main.css`:
```css
:root {
    --reddit-orange: #FF4500;
    --positive-green: #4CAF50;
    /* ... */
}
```

### Modifying Charts
Edit chart configuration in `scripts/dashboard.js` and `scripts/personal.js`:
```javascript
const chart = new Chart(ctx, {
    type: 'line',
    data: { /* ... */ },
    options: { /* ... */ }
});
```

## 🔌 Backend Integration

To connect with your FastAPI backend:

1. **Update API endpoints** in JavaScript files
2. **Replace demo login** with actual OAuth2 flow in `login.js`
3. **Fetch real data** instead of generated sample data
4. **Add authentication** headers to API calls

Example API integration:
```javascript
// In dashboard.js
async function fetchSentimentData() {
    const response = await fetch('/api/sentiment?days=30', {
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    });
    const data = await response.json();
    updateChart(data);
}
```

## ✨ Features Implemented

- ✅ Login page with error states
- ✅ Loading animations
- ✅ Sentiment gauge charts
- ✅ Interactive timeline charts (Chart.js)
- ✅ Breakdown toggles
- ✅ Timeline selector (7/30/90/365 days)
- ✅ Trend indicators with icons
- ✅ Subreddit recommendation cards
- ✅ Join/unjoin button states
- ✅ External link buttons
- ✅ Live time/date display
- ✅ Smooth transitions and hover states
- ✅ Mobile-responsive sidebar
- ✅ Accessible form inputs
- ✅ Password visibility toggle

## 🎯 Next Steps for Integration

1. **Set up FastAPI backend** following the technical spec
2. **Implement Reddit OAuth2** authentication flow
3. **Create API endpoints** for data fetching
4. **Connect frontend** to real API calls
5. **Add data persistence** with SQLite/JSON
6. **Implement VADER** sentiment analysis
7. **Build sync engine** for incremental updates
8. **Add spam filtering** logic

## 📝 Notes

- All SVG icons are inline for performance
- Charts use generated sample data (replace with API calls)
- CSS is mobile-first with progressive enhancement
- No JavaScript frameworks - pure vanilla for maximum compatibility
- Designed for modern browsers (Chrome, Firefox, Safari, Edge)

## 🐛 Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support  
- Safari: ✅ Full support
- Mobile browsers: ✅ Optimized

## 📄 License

This frontend is part of the Reddit Hive Mind project.

---

**Built with ❤️ using vanilla web technologies**
