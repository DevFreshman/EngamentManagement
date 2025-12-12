// ============================
// API CONFIG
// ============================
const API_BASE = "http://127.0.0.1:8000";


// ============================
// GENERIC FETCH WRAPPER
// ============================
async function callAPI(endpoint, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, options);

        if (!res.ok) {
            console.error(`❌ API Error ${res.status}:`, endpoint);
            return null;
        }

        return await res.json();

    } catch (err) {
        console.error(`❌ API Request Failed: ${endpoint}`, err);
        return null;
    }
}



// ============================
// REALTIME FRAME ANALYSIS
// ============================
async function analyzeFrame(blob) {
    const formData = new FormData();
    formData.append("frame", blob, "frame.jpg");

    return await callAPI("/analyze_frame", {
        method: "POST",
        body: formData
    });
}



// ============================
// SESSION CONTROL (Video/Webcam pipeline cũ)
// ============================
async function startSession(mode = "webcam", videoPath = "") {

    let url = `/start?mode=${encodeURIComponent(mode)}`;
    if (mode === "video") {
        url += `&video_path=${encodeURIComponent(videoPath)}`;
    }

    return await callAPI(url, { method: "GET" });
}


async function stopSession() {
    return await callAPI("/stop", { method: "GET" });
}



// ============================
// REALTIME DASHBOARD SESSION
// ============================
async function rtStartSession() {
    return await callAPI("/rt_start", { method: "GET" });
}

async function rtStopSession() {
    return await callAPI("/rt_stop", { method: "GET" });
}



// ============================
// GET SESSION ANALYTICS
// ============================
async function getAnalytics(sessionId) {
    return await callAPI(`/sessions/${sessionId}/analytics`);
}



// ============================
// GET SESSION CHARTS
// ============================
async function getCharts(sessionId) {
    return await callAPI(`/sessions/${sessionId}/charts`);
}



// ============================
// EXPORT (nếu cần dùng module)
// ============================
// export {
//     analyzeFrame,
//     startSession,
//     stopSession,
//     getAnalytics,
//     getCharts,
//     rtStartSession,
//     rtStopSession
// };
