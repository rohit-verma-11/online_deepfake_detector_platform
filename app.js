// AUDIO ENGINE (WOW FACTOR)
const AudioFX = {
    ctx: new (window.AudioContext || window.webkitAudioContext)(),
    play(freq, type, dur) {
        const osc = this.ctx.createOscillator();
        const g = this.ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        g.gain.setValueAtTime(0.1, this.ctx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + dur);
        osc.connect(g); g.connect(this.ctx.destination);
        osc.start(); osc.stop(this.ctx.currentTime + dur);
    },
    click() { this.play(800, 'square', 0.05); },
    success() { 
        this.play(500, 'sine', 0.1); 
        setTimeout(() => this.play(1000, 'sine', 0.1), 100); 
    }
};

// MATRIX BG
const canvas = document.getElementById('matrix-bg');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth; canvas.height = window.innerHeight;
const drops = Array(Math.floor(canvas.width / 20)).fill(1);
function drawMatrix() {
    ctx.fillStyle = "rgba(2, 6, 23, 0.1)"; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#00f3ff"; ctx.font = "12px monospace";
    drops.forEach((y, i) => {
        ctx.fillText(Math.random() > 0.5 ? "1" : "0", i * 20, y * 20);
        if (y * 20 > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
    });
}
setInterval(drawMatrix, 50);

// MOTION GRAPH
const gCanvas = document.getElementById('motion-graph');
const gCtx = gCanvas.getContext('2d');
let points = Array(100).fill(50);
function drawGraph() {
    gCtx.clearRect(0, 0, gCanvas.width, gCanvas.height);
    gCtx.strokeStyle = '#00f3ff'; gCtx.lineWidth = 1;
    gCtx.beginPath();
    points.forEach((p, i) => {
        const x = (i / 100) * gCanvas.width;
        const y = gCanvas.height - (p / 100 * gCanvas.height);
        i === 0 ? gCtx.moveTo(x, y) : gCtx.lineTo(x, y);
    });
    gCtx.stroke();
    points.push(Math.random() * 40 + 30); points.shift();
    requestAnimationFrame(drawGraph);
}
drawGraph();

// APP LOGIC
const addLog = (msg) => {
    const p = document.createElement('p');
    p.innerHTML = `> [${new Date().toLocaleTimeString()}] ${msg}`;
    document.getElementById('log-feed').prepend(p);
};

document.getElementById('drop-zone').onclick = () => document.getElementById('video-input').click();

document.getElementById('video-input').onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    AudioFX.click();
    resetHUD();
    addLog(`INJECTING: ${file.name.toUpperCase()}`);

    const formData = new FormData();
    formData.append('video_file', file);
    
    try {
        const res = await fetch('http:/127.0.0.1:8000/api/detect/', { method: 'POST', body: formData });
        const data = await res.json();
        pollStatus(data.task_id);
    } catch (e) { addLog("UPLINK FAILED"); }
};

function resetHUD() {
    document.getElementById('idle-display').classList.add('hidden');
    document.getElementById('results-display').classList.remove('hidden');
    document.getElementById('scan-bar').classList.remove('hidden');
    document.getElementById('verdict').innerText = "ANALYZING";
    document.getElementById('verdict').className = "text-6xl font-black italic tracking-tighter mt-2 text-cyan-600 animate-pulse";
    const ring = document.getElementById('progress-ring');
    const offset = 377 - (377 * (0 / 100));
    ring.style.strokeDashoffset = offset;
    document.querySelector('#confidence-val span:last-child').innerText = `0%`;
}

async function pollStatus(id) {
    const interval = setInterval(async () => {
        const res = await fetch(`http:/127.0.0.1:8000/api/detect/${id}/`);
        const data = await res.json();
        if (data.status === 'COMPLETED') {
            clearInterval(interval);
            renderResults(data);
        }
    }, 2000);
}

function renderResults(data) {
    AudioFX.success();
    document.getElementById('scan-bar').classList.add('hidden');
    
    const verdict = document.getElementById('verdict');
    verdict.innerText = data.is_fake ? "FORGERY_DETECTED" : "SOURCE_AUTHENTIC";
    verdict.className = `text-6xl font-black italic tracking-tighter mt-2 ${data.is_fake ? 'text-red-600' : 'text-green-500'}`;
    
    document.getElementById('content-type').innerText = data.content_type.toUpperCase();
    
    // Progress Ring
    const ring = document.getElementById('progress-ring');
    const offset = 377 - (377 * (data.confidence_score / 100));
    ring.style.strokeDashoffset = offset;
    document.querySelector('#confidence-val span:last-child').innerText = `${data.confidence_score}%`;

    // Typewriter
    const reason = document.getElementById('reasoning');
    reason.innerText = "";
    let i = 0;
    const type = () => {
        if (i < data.reasoning.length) {
            reason.innerHTML += data.reasoning.charAt(i);
            i++; setTimeout(type, 20);
        }
    };
    type();
}