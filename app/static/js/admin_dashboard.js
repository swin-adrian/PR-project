// Global variables to keep track of chart instances
let topCountriesChartInstance = null;
let ageChartInstance = null;
let testChartInstance = null;

// Function to fetch and render all charts on page load
async function fetchAndRenderCharts() {
    try {
        // Fetch data
        const topCountriesData = await fetchTopCountriesData();
        const usersByAgeData = await fetchUsersByAgeData();
        const usersByTestData = await fetchUsersByTestData();

        // Log the fetched data
        console.log("Top Countries Data:", topCountriesData);
        console.log("Users by Age Data:", usersByAgeData);
        console.log("Users by Test Data:", usersByTestData);

        // Render charts with a small delay to ensure proper rendering
        setTimeout(() => {
            renderTopCountriesChart(topCountriesData);
            renderUsersByAgeChart(usersByAgeData);
            renderUsersByTestChart(usersByTestData);
        }, 100);
    } catch (error) {
        console.error('Error fetching or rendering data:', error);
    }
}

// Fetch Top 5 Countries Data
async function fetchTopCountriesData() {
    try {
        const response = await fetch('/admin/api/top-countries');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching Top Countries data:', error);
        return []; // Return empty array on error to prevent further issues
    }
}

// Fetch Users by Age Data
async function fetchUsersByAgeData() {
    try {
        const response = await fetch('/admin/api/users-by-age');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching Users by Age data:', error);
        return []; // Return empty array on error to prevent further issues
    }
}

// Fetch Users by Test Data
async function fetchUsersByTestData() {
    try {
        const response = await fetch('/admin/api/users-by-test');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching Users by Test data:', error);
        return []; // Return empty array on error to prevent further issues
    }
}

// Render Top 5 Countries Chart
function renderTopCountriesChart(data) {
    console.log("Rendering Top Countries Chart with data:", data);
    if (topCountriesChartInstance) {
        console.log("Destroying Top Countries Chart");
        topCountriesChartInstance.destroy();
    }

    const labels = data.map(item => item._id || 'Unknown Country');
    const values = data.map(item => item.count || 0);

    const ctx = document.getElementById('topCountriesChart').getContext('2d');
    topCountriesChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Users',
                data: values,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Render Users by Age Chart
function renderUsersByAgeChart(data) {
    console.log("Rendering Users by Age Chart with data:", data);
    if (ageChartInstance) {
        console.log("Destroying Age Chart");
        ageChartInstance.destroy();
    }

    const labels = data.map(item => item._id || 'Unknown Age');
    const values = data.map(item => item.count || 0);

    const ctx = document.getElementById('ageChart').getContext('2d');
    ageChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Users by Age',
                data: values,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Render Users by English Test Chart as a Pie Chart
function renderUsersByTestChart(data) {
    console.log("Rendering Users by Test Chart with data:", data);
    if (testChartInstance) {
        console.log("Destroying Test Chart");
        testChartInstance.destroy();
    }

    const labels = data.map(item => item._id || 'Unknown Test');
    const values = data.map(item => item.count || 0);

    const ctx = document.getElementById('testChart').getContext('2d');
    testChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Users by English Test',
                data: values,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            maintainAspectRatio: false,
            responsive: true
        }
    });
}

// Call the function to fetch and render all charts on page load
fetchAndRenderCharts(); // This should be placed after the function definition
