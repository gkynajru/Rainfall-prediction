let rainfallChart;

// Initialize the chart
function initChart() {
    const ctx = document.getElementById('rainfallChart').getContext('2d');
    rainfallChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'LSTM Predictions',
                    data: [],
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    borderWidth: 2,
                    pointRadius: 3,
                    tension: 0.4
                },
                {
                    label: 'IFS Predictions',
                    data: [],
                    borderColor: '#FF9800',
                    backgroundColor: 'rgba(255, 152, 0, 0.1)',
                    borderWidth: 2,
                    pointRadius: 3,
                    tension: 0.4
                },
                {
                    label: 'Vrain Predictions',
                    data: [],
                    borderColor: '#04FF00',
                    backgroundColor: 'rgba(4, 255, 0, 0.1)',
                    borderWidth: 2,
                    pointRadius: 3,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour',
                        displayFormats: {
                            hour: 'MMM D, HH:mm'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Rainfall (mm)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y.toFixed(2) + ' mm';
                            return label;
                        }
                    }
                },
                legend: {
                    position: 'top'
                }
            }
        }
    });
}

// Update chart with new data
function updateChart(data) {
    if (!data || !data.lstm_predictions || !data.ifs_predictions || !data.vrain_predictions) {
        console.error('Invalid data structure:', data);
        return;
    }

    const lstm = data.lstm_predictions;
    const ifs = data.ifs_predictions;
    const vrain = data.vrain_predictions;

    if (!lstm.timestamps || !lstm.values || !ifs.timestamps || !ifs.values || !vrain.timestamps || !vrain.values) {
        console.error('Missing required data fields:', data);
        return;
    }

    try {
        // Convert timestamps to moment objects
        const labels = lstm.timestamps.map(t => moment(t));
        
        // Create datasets
        const lstmData = lstm.values.map((value, index) => ({
            x: labels[index],
            y: value
        }));
        
        const ifsData = ifs.values.map((value, index) => ({
            x: labels[index],
            y: value
        }));

        const vrainData = vrain.values.map((value, index) => ({
            x: labels[index],
            y: value
        }));

        // Update chart data
        rainfallChart.data.datasets[0].data = lstmData;
        rainfallChart.data.datasets[1].data = ifsData;
        rainfallChart.data.datasets[2].data = vrainData;

        rainfallChart.update();

        // Update metrics
        const lstmAvg = lstm.values.reduce((a, b) => a + b, 0) / lstm.values.length;
        const ifsAvg = ifs.values.reduce((a, b) => a + b, 0) / ifs.values.length;
        const vrainAvg = vrain.values.reduce((a, b) => a + b, 0) / vrain.values.length;
        const maxRainfall = Math.max(...lstm.values, ...ifs.values, ...vrain.values);

        document.getElementById('lstmAvg').textContent = lstmAvg.toFixed(2);
        document.getElementById('ifsAvg').textContent = ifsAvg.toFixed(2);
        document.getElementById('vrainAvg').textContent = vrainAvg.toFixed(2);
        document.getElementById('maxRainfall').textContent = maxRainfall.toFixed(2);
    } catch (error) {
        console.error('Error updating chart:', error);
    }
}

// Fetch data from API
async function fetchData(location) {
    try {
        console.log(`Fetching data for location: ${location}`);  // Debug log
        const response = await fetch(`/api/data?location=${encodeURIComponent(location)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        console.log('Data received:', data);  // Debug log
        
        // Validate data structure
        if (!data.lstm_predictions || !data.ifs_predictions) {
            throw new Error('Invalid data structure received from server');
        }
        
        updateChart(data);
    } catch (error) {
        console.error('Error fetching data:', error);
        alert(`Error fetching data: ${error.message}`);
    }
}

// Update data when button is clicked
function updateData() {
    const location = document.getElementById('locationSelect').value;
    const updateButton = document.getElementById('updateButton');
    
    console.log(`Updating data for location: ${location}`);  // Debug log
    
    // Disable button during update
    updateButton.disabled = true;
    updateButton.textContent = 'Updating...';
    
    // Fetch new data
    fetchData(location)
        .finally(() => {
            // Re-enable button after update
            updateButton.disabled = false;
            updateButton.textContent = 'Update Data';
        });
}

// Initialize chart when page loads
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    
    // Initial data load
    updateData();
    
    // Set up location select change handler
    document.getElementById('locationSelect').addEventListener('change', updateData);
});