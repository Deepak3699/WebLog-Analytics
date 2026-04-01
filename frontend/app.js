async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://127.0.0.1:8000/api/analyze", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    showStats(data);
    drawCharts(data);
}

function showStats(data) {
    if (!data || !data.anomalies) {
        console.error("Invalid API response:", data);
        return;
    }

    document.getElementById("stats").innerHTML = `
        <p>Total Requests: ${data.total_requests}</p>
        <p>Error Rate: ${(data.error_rate * 100).toFixed(2)}%</p>
        <p>Anomalies: ${data.anomalies.count}</p>
    `;
}

function drawCharts(data) {
    // Hour chart
    new Chart(document.getElementById("hourChart"), {
        type: "bar",
        data: {
            labels: Object.keys(data.hour_distribution),
            datasets: [{
                label: "Requests per Hour",
                data: Object.values(data.hour_distribution)
            }]
        }
    });

    // Status chart
    new Chart(document.getElementById("statusChart"), {
        type: "pie",
        data: {
            labels: Object.keys(data.status_distribution),
            datasets: [{
                data: Object.values(data.status_distribution)
            }]
        }
    });
}