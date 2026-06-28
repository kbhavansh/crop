class CropAIApp {
    constructor() {
        this.predictionHistory = [];
        this.chart = null;
        this.initTabs();
        this.initForms();
    }

    // ----------------------
    // Tab Switching
    // ----------------------
    initTabs() {
        const tabs = document.querySelectorAll(".nav-tab");
        tabs.forEach(tab => {
            tab.addEventListener("click", () => {
                tabs.forEach(t => t.classList.remove("active"));
                document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

                tab.classList.add("active");
                const target = tab.getAttribute("data-tab");
                document.getElementById(target + "-tab").classList.add("active");
            });
        });
    }

    // ----------------------
    // Form Initialization
    // ----------------------
    initForms() {
        document.getElementById("predictForm")?.addEventListener("submit", (e) => {
            e.preventDefault();
            this.handlePrediction();
        });

        document.getElementById("dosageForm")?.addEventListener("submit", (e) => {
            e.preventDefault();
            this.calculateDosage();
        });
    }

    // ----------------------
    // Handle Prediction
    // ----------------------
    async handlePrediction() {
        const inputs = {
            soil_moisture: parseFloat(document.getElementById("soilMoisture").value),
            soil_temp: parseFloat(document.getElementById("soilTemp").value),
            air_temp: parseFloat(document.getElementById("airTemp").value),
            air_humidity: parseFloat(document.getElementById("airHumidity").value),
            soil_salinity: parseFloat(document.getElementById("soilSalinity").value),
            ndvi: parseFloat(document.getElementById("ndvi").value)
        };

        try {
            const response = await fetch("http://127.0.0.1:5001/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(inputs)
            });
            const result = await response.json();

            if (result.error) {
                alert("Error: " + result.error);
                return;
            }

            this.displayHomepagePrediction(result);
            this.savePrediction(inputs, result);
            this.updateChart();
            this.displayPesticides(result);
            this.updateGauge(result.infection_level);
            this.updateConfidence(result.confidence);
        } catch (error) {
            alert("Server Error: " + error.message);
        }
    }

    // ----------------------
    // Display latest prediction on homepage
    // ----------------------
    displayHomepagePrediction(result) {
        const resultContainer = document.getElementById("result");
        resultContainer.innerHTML = `
            <div class="homepage-prediction">
                <p><strong>Infection Level:</strong> ${result.infection_level}</p>
                <p><strong>Risk Level:</strong> ${result.risk_level}</p>
                <p><strong>Confidence:</strong> ${result.confidence.toFixed(2)}%</p>
            </div>
        `;
    }

    // ----------------------
    // Update Gauge
    // ----------------------
    updateGauge(infectionLevel) {
        const needle = document.getElementById("gauge-needle");
        const value = document.getElementById("gauge-value");
        if (needle && value) {
            const angle = -90 + (infectionLevel / 10) * 180; // Assuming gauge scale 0-10
            needle.style.transform = `translateX(-50%) rotate(${angle}deg)`;
            value.textContent = infectionLevel;
        }
    }

    // ----------------------
    // Update Confidence Bar
    // ----------------------
    updateConfidence(confidence) {
        const fill = document.getElementById("confidence-fill");
        const text = document.getElementById("confidence-text");
        if (fill && text) {
            fill.style.width = `${confidence}%`;
            text.textContent = `Confidence: ${confidence.toFixed(2)}%`;
        }
    }

    // ----------------------
    // Save & Update History
    // ----------------------
    savePrediction(inputs, result) {
        const entry = {
            timestamp: new Date().toLocaleString(),
            inputs,
            result
        };
        this.predictionHistory.unshift(entry);
        if (this.predictionHistory.length > 50) this.predictionHistory.pop(); // store last 50
        this.updateHistoryTable();
    }

    updateHistoryTable() {
        const tbody = document.querySelector("#historyTable tbody");
        tbody.innerHTML = "";
        this.predictionHistory.forEach(p => {
            const row = `
                <tr>
                    <td>${p.timestamp}</td>
                    <td style="text-align:center;">${p.result.infection_level}</td>
                    <td style="text-align:center;">${p.result.risk_level}</td>
                    <td style="text-align:center;">${p.result.confidence.toFixed(2)}%</td>
                </tr>
            `;
            tbody.innerHTML += row;
        });
    }

    // ----------------------
    // Update Chart
    // ----------------------
    updateChart() {
        const ctx = document.getElementById("trendChart").getContext("2d");
        if (this.chart) this.chart.destroy();

        this.chart = new Chart(ctx, {
            type: "line",
            data: {
                labels: this.predictionHistory.map(p => p.timestamp).reverse(),
                datasets: [{
                    label: "Infection Level",
                    data: this.predictionHistory.map(p => p.result.infection_level).reverse(),
                    borderColor: "blue",
                    fill: false
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true, max: 10 }
                }
            }
        });
    }

    // ----------------------
    // Display Pesticides
    // ----------------------
    displayPesticides(result) {
        const container = document.getElementById("pesticideRecommendations");
        container.innerHTML = `
            <p><strong>Recommended Pesticides:</strong></p>
            <ul>
                ${result.recommended_pesticides.map(p => `<li>${p}</li>`).join("")}
            </ul>
        `;
    }

    // ----------------------
    // Dosage Calculation
    // ----------------------
    calculateDosage() {
        const acres = parseFloat(document.getElementById("acreInput").value);
        if (isNaN(acres) || acres <= 0) {
            alert("Please enter a valid land size in acres.");
            return;
        }

        const dosageRates = {
            "Neem Oil": "500 ml",
            "Sulfur Dust": "2 kg",
            "Copper Fungicide": "1.5 kg",
            "Potassium Bicarbonate": "1 kg",
            "Mancozeb": "2.5 kg"
        };

        const recommendations = this.predictionHistory[0]?.result.recommended_pesticides || [];

        let tableHTML = `
            <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%; text-align:center;">
                <tr style="background-color:#f2f2f2;">
                    <th>Pesticide</th>
                    <th>Dosage per Acre</th>
                    <th>Total for ${acres} acres</th>
                </tr>
        `;

        recommendations.forEach(pesticide => {
            let perAcre = dosageRates[pesticide] || "N/A";
            let total = "N/A";

            if (perAcre.includes("ml")) {
                let value = parseFloat(perAcre.replace("ml", ""));
                total = (value * acres) + " ml";
            } else if (perAcre.includes("kg")) {
                let value = parseFloat(perAcre.replace("kg", ""));
                total = (value * acres) + " kg";
            }

            tableHTML += `<tr>
                <td>${pesticide}</td>
                <td>${perAcre}</td>
                <td>${total}</td>
            </tr>`;
        });

        tableHTML += "</table>";
        document.getElementById("dosageResult").innerHTML = tableHTML;
    }
}

// ----------------------
// Initialize App
// ----------------------
document.addEventListener("DOMContentLoaded", () => new CropAIApp());
