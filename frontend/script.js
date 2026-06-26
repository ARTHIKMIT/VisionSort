const API_BASE_URL = '/api';

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('image-upload');
const previewImage = document.getElementById('preview-image');
const uploadPrompt = document.getElementById('upload-prompt');
const predictedClassEl = document.getElementById('predicted-class');
const confidenceBar = document.getElementById('confidence-bar');
const confidenceTextEl = document.getElementById('confidence-text');
const faultBanner = document.getElementById('fault-banner');
const totalItemsEl = document.getElementById('total-items');
const avgConfidenceEl = document.getElementById('avg-confidence');
const liveFeedEl = document.getElementById('live-feed');

// Chart instance
let statsChart;

// Initialize the dashboard
function init() {
    setupDragAndDrop();
    initChart();
    updateDashboard();
    
    // Poll stats and feed every 5 seconds
    setInterval(updateDashboard, 5000);
}

// Drag and drop event listeners
function setupDragAndDrop() {
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--accent-blue)';
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = 'var(--border-color)';
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border-color)';
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

// Handle file upload & prediction
async function handleFileUpload(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please upload an image file.');
        return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewImage.style.display = 'block';
        uploadPrompt.style.display = 'none';
    };
    reader.readAsDataURL(file);

    // Set UI to processing
    predictedClassEl.textContent = 'ANALYZING...';
    predictedClassEl.style.color = 'white';
    confidenceBar.style.width = '0%';
    confidenceTextEl.textContent = '--%';
    faultBanner.classList.add('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Prediction failed');

        const data = await response.json();
        displayResult(data);
        updateDashboard(); // Update stats immediately
    } catch (error) {
        console.error('Error:', error);
        predictedClassEl.textContent = 'ERROR';
        predictedClassEl.style.color = 'var(--accent-red)';
    }
}

// Display prediction result on UI
function displayResult(data) {
    const className = data.predicted_class;
    const confidence = (data.confidence_score * 100).toFixed(1);
    
    predictedClassEl.textContent = className;
    confidenceBar.style.width = `${confidence}%`;
    confidenceTextEl.textContent = `${confidence}%`;

    // Determine fault condition (< 60% confidence)
    if (confidence < 60) {
        faultBanner.classList.remove('hidden');
        predictedClassEl.style.color = 'var(--accent-red)';
    } else {
        faultBanner.classList.add('hidden');
        predictedClassEl.style.color = 'var(--accent-green)';
    }
}

// Update charts and feed
async function updateDashboard() {
    try {
        const [statsRes, feedRes] = await Promise.all([
            fetch(`${API_BASE_URL}/stats`),
            fetch(`${API_BASE_URL}/recent`)
        ]);

        if (statsRes.ok) {
            const stats = await statsRes.json();
            updateStats(stats);
        }

        if (feedRes.ok) {
            const feed = await feedRes.json();
            updateFeed(feed.recent);
        }
    } catch (error) {
        console.error("Error updating dashboard:", error);
    }
}

function updateStats(stats) {
    totalItemsEl.textContent = stats.total_processed;
    avgConfidenceEl.textContent = `${(stats.average_confidence * 100).toFixed(1)}%`;

    // Update Chart
    const labels = Object.keys(stats.class_counts);
    const data = Object.values(stats.class_counts);

    statsChart.data.labels = labels;
    statsChart.data.datasets[0].data = data;
    statsChart.update();
}

function updateFeed(recentItems) {
    liveFeedEl.innerHTML = '';
    
    recentItems.forEach(item => {
        const date = new Date(item.timestamp);
        const timeStr = date.toLocaleTimeString();
        const confPercent = (item.confidence_score * 100).toFixed(1);
        
        let confClass = 'high-conf';
        if (item.confidence_score < 0.6) confClass = 'low-conf';

        const itemEl = document.createElement('div');
        itemEl.className = `feed-item ${confClass}`;
        itemEl.innerHTML = `
            <div class="feed-time">${timeStr}</div>
            <div class="feed-details">
                <span>${item.predicted_class.toUpperCase()}</span>
                <span>${confPercent}%</span>
            </div>
        `;
        liveFeedEl.appendChild(itemEl);
    });
}

function initChart() {
    const ctx = document.getElementById('statsChart').getContext('2d');
    
    // Chart.js global defaults for dark theme
    Chart.defaults.color = '#888';
    Chart.defaults.font.family = "'Share Tech Mono', monospace";
    
    statsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Items Segregated',
                data: [],
                backgroundColor: '#00f0ff',
                borderColor: '#00f0ff',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#333' }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            },
            animation: { duration: 500 }
        }
    });
}

// Start app
window.onload = init;
