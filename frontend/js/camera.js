// =========================
// CAMERA + REALTIME ANALYSIS
// =========================

const video = document.getElementById("video");
const overlay = document.getElementById("overlay");
const ctx = overlay.getContext("2d");

let stream = null;
let running = false;
let intervalId = null;
let isProcessing = false; // tránh call /analyze_frame chồng nhau


// Đồng bộ kích thước canvas với video (để vẽ box không lệch)
function resizeOverlayToVideo() {
    const vw = video.videoWidth;
    const vh = video.videoHeight;
    if (!vw || !vh) return;

    overlay.width = vw;
    overlay.height = vh;
}


// =========================
// START CAMERA
// =========================
async function startCamera() {
    try {
        // báo backend bắt đầu 1 session realtime (mở file CSV)
        await rtStartSession();

        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        running = true;

        // Khi metadata sẵn sàng thì sync size canvas
        video.onloadedmetadata = () => {
            video.play();
            resizeOverlayToVideo();
        };

        // chạy mỗi 600ms (quá nhanh sẽ lag)
        intervalId = setInterval(captureFrame, 600);
    } catch (err) {
        console.error("Cannot start camera:", err);
    }
}


// =========================
// STOP CAMERA
// =========================
async function stopCamera() {
    running = false;

    if (intervalId) clearInterval(intervalId);

    if (stream) {
        stream.getTracks().forEach((t) => t.stop());
        stream = null;
    }

    ctx.clearRect(0, 0, overlay.width, overlay.height);

    // reset dashboard
    updateGauge(0);
    document.getElementById("currentEngagement").textContent = "0.00";
    document.getElementById("currentFaces").textContent = "0";

    // báo backend đóng session realtime + sinh report từ CSV
    const summary = await rtStopSession();
    console.log("Realtime session summary:", summary);
}


// =========================
// CAPTURE FRAME + SEND TO BACKEND
// =========================
async function captureFrame() {
    if (!running) return;
    if (isProcessing) return; // frame trước còn đang xử lý
    if (video.videoWidth === 0 || video.videoHeight === 0) return;

    isProcessing = true;

    const temp = document.createElement("canvas");
    temp.width = video.videoWidth;
    temp.height = video.videoHeight;

    const tctx = temp.getContext("2d");
    tctx.drawImage(video, 0, 0);

    temp.toBlob(
        async (blob) => {
            try {
                const data = await analyzeFrame(blob);

                // vẽ khung
                drawOverlay(data);

                const engSpan = document.getElementById("currentEngagement");
                const facesSpan = document.getElementById("currentFaces");

                // KHÔNG có mặt nào
                if (!data || !data.faces || data.faces.length === 0) {
                    engSpan.textContent = "0.00";
                    facesSpan.textContent = "0";
                    updateGauge(0);
                    return;
                }

                const faces = data.faces;
                const n = faces.length;

                // ===== 1. Tính engagement trung bình =====
                let sumEng = 0;
                faces.forEach((f) => {
                    sumEng += f.engagement || 0;
                });
                const avgEng = sumEng / n;

                // ===== 2. Tính probs (emotion) trung bình =====
                const aggProbs = {};
                faces.forEach((f) => {
                    const probs = f.probs || {};
                    for (const emo in probs) {
                        if (!aggProbs[emo]) aggProbs[emo] = 0;
                        aggProbs[emo] += probs[emo] / n;
                    }
                });

                // ===== 3. Cập nhật số lên dashboard trước =====
                engSpan.textContent = avgEng.toFixed(2);
                facesSpan.textContent = String(n);

                // ===== 4. Rồi mới cập nhật chart (nếu chart có lỗi thì số vẫn đúng) =====
                try {
                    updateGauge(avgEng);
                    updateLineChart(avgEng);
                    updateRadar(aggProbs);
                    updateHeatmap({ probs: aggProbs });
                } catch (e) {
                    console.error("Chart update error:", e);
                }
            } finally {
                isProcessing = false;
            }
        },
        "image/jpeg",
        0.6 // nén mạnh hơn chút để gửi nhanh hơn
    );
}


// =========================
// DRAW OVERLAY BOUNDING BOX
// =========================
function drawOverlay(data) {
    ctx.clearRect(0, 0, overlay.width, overlay.height);

    if (!data || !data.faces) return;

    ctx.lineWidth = 2;
    ctx.font = "16px Arial";

    data.faces.forEach((face) => {
        const { id, x, y, w, h, emotion, engagement } = face;

        // Bounding box
        ctx.strokeStyle = "lime";
        ctx.strokeRect(x, y, w, h);

        // Label
        const label = `ID${id} - ${emotion} (${engagement.toFixed(2)})`;
        const textWidth = ctx.measureText(label).width;

        let textX = x;
        let textY = y - 8;

        // nếu label bị tràn lên trên thì vẽ xuống dưới khung
        if (textY < 18) {
            textY = y + h + 18;
        }

        ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
        ctx.fillRect(textX - 4, textY - 16, textWidth + 8, 18);

        ctx.fillStyle = "#00FF00";
        ctx.fillText(label, textX, textY);
    });
}


// =========================
// BUTTON EVENTS
// =========================
document.getElementById("startBtn").onclick = startCamera;
document.getElementById("stopBtn").onclick = stopCamera;
