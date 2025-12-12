// =====================
//  COMMON CONSTANTS
// =====================
const EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"];


// =====================
//  GAUGE CHART
// =====================
const gaugeCtx = document.getElementById("gaugeChart").getContext("2d");

let gaugeChart = new Chart(gaugeCtx, {
    type: "doughnut",
    data: {
        labels: ["Engagement"],
        datasets: [
            {
                data: [0.0, 1.0],
                backgroundColor: ["#22c55e", "#111827"],
                borderWidth: 0
            }
        ]
    },
    options: {
        responsive: true,
        animation: false,          // không animate để cập nhật tức thì
        rotation: -90,
        circumference: 180,
        cutout: "75%",
        plugins: {
            legend: { display: false },
            tooltip: { enabled: false }
        }
    }
});

function updateGauge(value) {
    value = Math.min(1, Math.max(0, value));
    gaugeChart.data.datasets[0].data = [value, 1 - value];
    gaugeChart.update();
}


// =====================
//  LINE CHART
// =====================
const lineCtx = document.getElementById("lineChart").getContext("2d");

let engagementData = [];
let timeLabels = [];

let lineChart = new Chart(lineCtx, {
    type: "line",
    data: {
        labels: timeLabels,
        datasets: [
            {
                label: "Engagement",
                data: engagementData,
                borderColor: "#22c55e",
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 0,
                fill: true,
                backgroundColor: "rgba(34, 197, 94, 0.08)"
            }
        ]
    },
    options: {
        responsive: true,
        animation: false,          // tắt animation
        plugins: {
            legend: { display: false },
            tooltip: {
                mode: "index",
                intersect: false
            }
        },
        scales: {
            x: {
                ticks: { color: "#9ca3af", maxRotation: 0, autoSkip: true },
                grid: { color: "rgba(31, 41, 55, 0.5)" }
            },
            y: {
                min: 0,
                max: 1,
                ticks: { color: "#9ca3af", stepSize: 0.2 },
                grid: { color: "rgba(31, 41, 55, 0.5)" }
            }
        }
    }
});

function updateLineChart(value) {
    const timestamp = new Date().toLocaleTimeString();

    timeLabels.push(timestamp);
    engagementData.push(value);

    // giữ tối đa 30 điểm
    if (timeLabels.length > 30) {
        timeLabels.shift();
        engagementData.shift();
    }

    lineChart.update();
}


// =====================
//  RADAR CHART (Emotion Overview)
// =====================
const radarCtx = document.getElementById("radarChart").getContext("2d");

let radarChart = new Chart(radarCtx, {
    type: "radar",
    data: {
        labels: EMOTION_LABELS,
        datasets: [
            {
                label: "Average Emotion",
                data: [0, 0, 0, 0, 0, 0, 0],
                backgroundColor: "rgba(45, 212, 191, 0.20)",  // fill mềm
                borderColor: "#22c55e",
                borderWidth: 2,
                pointBackgroundColor: "#22c55e",
                pointBorderColor: "#022c22",
                pointRadius: 3,
                pointHoverRadius: 4
            }
        ]
    },
    options: {
        responsive: true,
        animation: false,          // tắt animation
        plugins: {
            legend: { display: false },
            tooltip: { enabled: true }
        },
        scales: {
            r: {
                beginAtZero: true,
                min: 0,
                max: 1,
                ticks: {
                    display: false,      // ẩn mớ số 0.1..1.0 ở giữa cho đỡ rối
                    stepSize: 0.1
                },
                grid: {
                    color: "rgba(148, 163, 184, 0.25)"  // vòng tròn mờ
                },
                angleLines: {
                    color: "rgba(148, 163, 184, 0.25)"
                },
                pointLabels: {
                    color: "#e5e7eb",
                    font: {
                        size: 11,
                        family: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                    }
                }
            }
        }
    }
});

// probs: { angry: 0.2, ... }
function updateRadar(probs) {
    const data = EMOTION_LABELS.map((emo) =>
        probs && probs[emo] ? probs[emo] : 0
    );
    radarChart.data.datasets[0].data = data;
    radarChart.update();
}


// =====================
//  HEATMAP (Emotion trend – optional)
// =====================
const heatCtx = document.getElementById("heatmapChart").getContext("2d");

// mỗi phần tử = {x: timeIndex, y: emotionIndex, v: value}
let heatData = [];
let heatTimeIndex = 0;

let heatmapChart = new Chart(heatCtx, {
    type: "matrix",
    data: {
        datasets: [
            {
                label: "Emotion Heatmap",
                data: heatData,
                width: (ctx) => {
                    const chartArea = ctx.chart.chartArea || {};
                    const width = chartArea.right - chartArea.left;
                    return Math.max(width / 30, 6); // tối đa ~30 cột
                },
                height: (ctx) => {
                    const chartArea = ctx.chart.chartArea || {};
                    const height = chartArea.bottom - chartArea.top;
                    return Math.max(height / EMOTION_LABELS.length, 12);
                },
                backgroundColor: (ctx) => {
                    const v = ctx.raw.v || 0;
                    const alpha = 0.15 + v * 0.85;
                    return `rgba(34, 197, 94, ${alpha})`;
                },
                borderWidth: 0
            }
        ]
    },
    options: {
        responsive: true,
        animation: false,          // tắt animation
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    title: (items) => {
                        const i = items[0].raw.y;
                        return EMOTION_LABELS[i];
                    },
                    label: (item) => {
                        return "Intensity: " + item.raw.v.toFixed(2);
                    }
                }
            }
        },
        scales: {
            x: {
                display: false
            },
            y: {
                type: "category",
                labels: EMOTION_LABELS,
                ticks: { color: "#9ca3af" },
                grid: { display: false }
            }
        }
    }
});

// payload: { probs: {angry:.., ...} }
function updateHeatmap(payload) {
    if (!payload || !payload.probs) return;

    const probs = payload.probs;
    EMOTION_LABELS.forEach((emo, idx) => {
        const v = probs[emo] || 0;
        heatData.push({ x: heatTimeIndex, y: idx, v });
    });

    // giữ tối đa ~30 time steps
    const maxCols = 30;
    if (heatTimeIndex > maxCols) {
        heatData = heatData.filter((d) => d.x >= heatTimeIndex - maxCols);
    }

    heatTimeIndex++;
    heatmapChart.data.datasets[0].data = heatData;
    heatmapChart.update();
}
