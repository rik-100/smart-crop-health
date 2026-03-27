

const API_BASE = "http://127.0.0.1:5000/api";


let currentFile = null;
let lastResult  = null;


const DISEASE_CATALOG = [
  { class: "Pepper__bell___Bacterial_spot",              crop: "pepper", label: "Bell Pepper Bacterial Spot",     healthy: false },
  { class: "Pepper__bell___healthy",                     crop: "pepper", label: "Bell Pepper Healthy",            healthy: true  },
  { class: "Potato___Early_blight",                      crop: "potato", label: "Potato Early Blight",           healthy: false },
  { class: "Potato___Late_blight",                       crop: "potato", label: "Potato Late Blight",            healthy: false },
  { class: "Potato___healthy",                           crop: "potato", label: "Potato Healthy",                healthy: true  },
  { class: "Tomato_Bacterial_spot",                      crop: "tomato", label: "Tomato Bacterial Spot",         healthy: false },
  { class: "Tomato_Early_blight",                        crop: "tomato", label: "Tomato Early Blight",           healthy: false },
  { class: "Tomato_Late_blight",                         crop: "tomato", label: "Tomato Late Blight",            healthy: false },
  { class: "Tomato_Leaf_Mold",                           crop: "tomato", label: "Tomato Leaf Mold",              healthy: false },
  { class: "Tomato_Septoria_leaf_spot",                  crop: "tomato", label: "Tomato Septoria Leaf Spot",     healthy: false },
  { class: "Tomato_Spider_mites_Two_spotted_spider_mite",crop: "tomato", label: "Tomato Spider Mites",          healthy: false },
  { class: "Tomato__Target_Spot",                        crop: "tomato", label: "Tomato Target Spot",           healthy: false },
  { class: "Tomato__Tomato_YellowLeaf__Curl_Virus",      crop: "tomato", label: "Tomato Yellow Leaf Curl Virus", healthy: false },
  { class: "Tomato__Tomato_mosaic_virus",                crop: "tomato", label: "Tomato Mosaic Virus",           healthy: false },
  { class: "Tomato_healthy",                             crop: "tomato", label: "Tomato Healthy",               healthy: true  }
];

const CROP_ICONS = { pepper: "🌶️", potato: "🥔", tomato: "🍅" };


const uploadZone       = document.getElementById("uploadZone");
const fileInput        = document.getElementById("fileInput");
const browseBtn        = document.getElementById("browseBtn");
const clearBtn         = document.getElementById("clearBtn");
const analyzeBtn       = document.getElementById("analyzeBtn");
const imagePreviewPanel= document.getElementById("imagePreviewPanel");
const previewImg       = document.getElementById("previewImg");
const previewMeta      = document.getElementById("previewMeta");

const emptyState       = document.getElementById("emptyState");
const loadingState     = document.getElementById("loadingState");
const resultsContent   = document.getElementById("resultsContent");

const resetBtn         = document.getElementById("resetBtn");
const downloadBtn      = document.getElementById("downloadBtn");
const diseaseGrid      = document.getElementById("diseaseGrid");
const navbar           = document.getElementById("navbar");
const toast            = document.getElementById("toast");
const toastMsg         = document.getElementById("toastMsg");


window.addEventListener("scroll", () => {
  navbar.classList.toggle("scrolled", window.scrollY > 40);
});


uploadZone.addEventListener("dragover", e => {
  e.preventDefault();
  uploadZone.classList.add("dragover");
});
uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("dragover"));
uploadZone.addEventListener("drop", e => {
  e.preventDefault();
  uploadZone.classList.remove("dragover");
  const f = e.dataTransfer.files[0];
  if (f) handleFile(f);
});
uploadZone.addEventListener("click", () => fileInput.click());
browseBtn.addEventListener("click", e => { e.stopPropagation(); fileInput.click(); });
fileInput.addEventListener("change", () => { if (fileInput.files[0]) handleFile(fileInput.files[0]); });


function handleFile(file) {
  const allowed = ["image/jpeg","image/png","image/webp"];
  if (!allowed.includes(file.type)) {
    showToast("Please upload a JPG, PNG, or WEBP image.");
    return;
  }
  if (file.size > 20 * 1024 * 1024) {
    showToast("File size must be under 20MB.");
    return;
  }
  currentFile = file;
  const url = URL.createObjectURL(file);
  previewImg.src = url;
  const sizeKb = (file.size / 1024).toFixed(1);
  previewMeta.textContent = `${file.name} · ${sizeKb} KB`;

  uploadZone.style.display = "none";
  imagePreviewPanel.style.display = "block";
}

clearBtn.addEventListener("click", () => {
  currentFile = null;
  fileInput.value = "";
  previewImg.src = "";
  imagePreviewPanel.style.display = "none";
  uploadZone.style.display = "block";
});


analyzeBtn.addEventListener("click", runAnalysis);

async function runAnalysis() {
  if (!currentFile) { showToast("Please select an image first."); return; }

  
  emptyState.style.display = "none";
  resultsContent.style.display = "none";
  loadingState.style.display = "flex";


  const steps = ["ls1","ls2","ls3","ls4"];
  let stepIdx = 0;
  const stepTimer = setInterval(() => {
    if (stepIdx > 0) {
      const prev = document.getElementById(steps[stepIdx - 1]);
      prev.classList.remove("active");
      prev.classList.add("done");
      prev.querySelector(".ls-dot").textContent = ""; // keep as dot
    }
    if (stepIdx < steps.length) {
      document.getElementById(steps[stepIdx]).classList.add("active");
      stepIdx++;
    } else {
      clearInterval(stepTimer);
    }
  }, 700);

  try {
    const formData = new FormData();
    formData.append("file", currentFile);

    const resp = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      body: formData
    });

    clearInterval(stepTimer);

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.error || "Server error");
    }

    const data = await resp.json();
    if (!data.success) throw new Error(data.error || "Analysis failed");

    lastResult = data;
    displayResults(data);

  } catch (err) {
    clearInterval(stepTimer);
    loadingState.style.display = "none";
    emptyState.style.display = "flex";
    showToast(`Error: ${err.message}`);
  }
}


function displayResults(data) {
  const { prediction, severity, images, recommendation } = data;


  const isHealthy = prediction.is_healthy;
  const diseaseIcon = document.getElementById("diseaseIconWrap");
  const cropType = prediction.class.toLowerCase().includes("tomato") ? "🍅"
    : prediction.class.toLowerCase().includes("potato") ? "🥔"
    : "🌶️";

  diseaseIcon.textContent = isHealthy ? "✅" : "🔬";
  document.getElementById("diseaseBadge").textContent = isHealthy ? "Healthy Plant" : "Disease Detected";
  document.getElementById("diseaseBadge").className = `disease-badge ${isHealthy ? "healthy" : "diseased"}`;
  document.getElementById("diseaseName").textContent = prediction.label;
  document.getElementById("diseaseDesc").textContent = recommendation.description;

  const confFill = document.getElementById("confidenceFill");
  confFill.style.width = "0%";
  document.getElementById("confValue").textContent = `${prediction.confidence.toFixed(1)}%`;
  setTimeout(() => { confFill.style.width = `${prediction.confidence}%`; }, 100);

  
  const sevLevel = document.getElementById("sevLevel");
  sevLevel.textContent = isHealthy ? "None" : severity.level;
  sevLevel.style.color = isHealthy ? "var(--green-400)" : severity.color;
  document.getElementById("sevPercent").textContent = isHealthy
    ? "No infected area detected"
    : `${severity.percentage.toFixed(1)}% infected area`;

  const sevInfoEl = document.getElementById("sevInfo");
  const sevInfoMap = {
    "Mild":     { text: "Early stage — act quickly", cls: "sev-mild"    },
    "Moderate": { text: "Significant spread — treat now", cls: "sev-mod" },
    "Severe":   { text: "Critical — immediate action!", cls: "sev-sev"   }
  };
  if (isHealthy) {
    sevInfoEl.textContent = "Plant is in great shape!";
    sevInfoEl.style.background = "rgba(34,197,94,0.1)";
    sevInfoEl.style.color = "var(--green-400)";
  } else {
    const info = sevInfoMap[severity.level] || {};
    sevInfoEl.textContent = info.text || severity.level;
    sevInfoEl.style.background = severity.level === "Severe" ? "rgba(239,68,68,0.12)"
      : severity.level === "Moderate" ? "rgba(251,191,36,0.12)"
      : "rgba(34,197,94,0.12)";
    sevInfoEl.style.color = severity.color;
  }

  
  const pct = isHealthy ? 0 : Math.min(severity.percentage, 100);
  const gaugeArc  = document.getElementById("gaugeArc");
  const gaugeText = document.getElementById("gaugeText");
  const arcLength = 157;
  setTimeout(() => {
    gaugeArc.style.strokeDashoffset = arcLength - (arcLength * pct / 100);
    gaugeText.textContent = `${pct.toFixed(0)}%`;
  }, 100);

  
  const topPredsEl = document.getElementById("topPreds");
  topPredsEl.innerHTML = prediction.top5.map((p, i) => `
    <div class="tp-item">
      <span class="tp-name" title="${p.class}">${truncate(p.class, 22)}</span>
      <div class="tp-bar-wrap">
        <div class="tp-bar-fill" style="width:0%" data-w="${p.confidence}"></div>
      </div>
      <span class="tp-pct">${p.confidence.toFixed(1)}%</span>
    </div>
  `).join("");

  setTimeout(() => {
    topPredsEl.querySelectorAll(".tp-bar-fill").forEach(el => {
      el.style.width = `${el.dataset.w}%`;
    });
  }, 150);


  document.getElementById("originalImg").src = `data:image/jpeg;base64,${images.original}`;
  document.getElementById("gradcamImg").src  = `data:image/jpeg;base64,${images.gradcam}`;

  // YOLOv8 Detections
  const yoloCard = document.getElementById("yoloCard");
  if (images.yolo) {
    yoloCard.style.display = "block";
    document.getElementById("yoloImg").src  = `data:image/jpeg;base64,${images.yolo}`;
    document.getElementById("yoloCountBadge").textContent = `${data.detections.length} Objects`;
    
    if (data.detections && data.detections.length > 0) {
      document.getElementById("yoloDetections").innerHTML = data.detections.map(
        d => `<div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border);padding:4px 0;">
                <span style="color:var(--text-2);font-weight:600;text-transform:capitalize;">${d.class}</span>
                <span style="color:var(--green-400);">${d.confidence.toFixed(1)}%</span>
              </div>`
      ).join("");
    } else {
      document.getElementById("yoloDetections").innerHTML = `<div style="text-align:center;padding:8px 0;">No objects detected.</div>`;
    }
  } else {
    yoloCard.style.display = "none";
  }

  
  const urgencyBadge = document.getElementById("urgencyBadge");
  urgencyBadge.textContent = recommendation.urgency.toUpperCase();
  urgencyBadge.className = `urgency-badge urgency-${recommendation.urgency}`;

  renderList("immediateList", recommendation.immediate_actions);
  renderList("treatmentList", recommendation.treatments);
  renderList("preventionList", recommendation.prevention);
  document.getElementById("fertText").textContent = recommendation.fertilizer;

  loadingState.style.display = "none";
  resultsContent.style.display = "block";


  setTimeout(() => {
    document.getElementById("resultsPanel").scrollIntoView({ behavior: "smooth", block: "start" });
  }, 200);
}

function renderList(id, items) {
  document.getElementById(id).innerHTML = items.map(item => `<li>${item}</li>`).join("");
}
function truncate(str, n) { return str.length > n ? str.slice(0, n) + "…" : str; }

// ─── RESET ───────────────────────────────────
resetBtn.addEventListener("click", () => {
  currentFile = null;
  lastResult = null;
  fileInput.value = "";
  previewImg.src = "";
  imagePreviewPanel.style.display = "none";
  uploadZone.style.display = "block";
  resultsContent.style.display = "none";
  emptyState.style.display = "flex";
  document.getElementById("yoloCard").style.display = "none";
  // Reset loading step states
  ["ls1","ls2","ls3","ls4"].forEach(id => {
    const el = document.getElementById(id);
    el.classList.remove("active","done");
  });
  document.getElementById("analyzer").scrollIntoView({ behavior: "smooth" });
});

// ─── DOWNLOAD REPORT ─────────────────────────
downloadBtn.addEventListener("click", () => {
  if (!lastResult) return;
  const d = lastResult;
  const rec = d.recommendation;

  const clean = (str) => typeof str === 'string' 
      ? str.replace(/\u2014/g, '&mdash;').replace(/\u2013/g, '&ndash;') 
      : str;

  const label = clean(d.prediction.label);
  const statusCls = d.prediction.is_healthy ? 'healthy' : 'diseased';
  const statusText = d.prediction.is_healthy ? 'Healthy Plant' : 'Disease Detected';
  const severityLevel = d.prediction.is_healthy ? 'None' : d.severity.level;
  const infectionArea = d.prediction.is_healthy ? '0%' : d.severity.percentage.toFixed(2) + '%';
  const confidence = d.prediction.confidence.toFixed(2) + '%';

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>CropSense AI Report - ${label}</title>
<style>
  :root {
    --primary: #16a34a;
    --primary-light: #dcfce7;
    --primary-dark: #15803d;
    --danger: #dc2626;
    --danger-light: #fee2e2;
    --bg: #f8fafc;
    --card: #ffffff;
    --text-main: #1e293b;
    --text-muted: #64748b;
    --border: #e2e8f0;
  }
  body {
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    background-color: var(--bg);
    color: var(--text-main);
    line-height: 1.6;
    margin: 0;
    padding: 40px 20px;
  }
  .report-container {
    max-width: 850px;
    margin: 0 auto;
    background: var(--card);
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    overflow: hidden;
  }
  .header {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    padding: 40px;
    text-align: center;
  }
  .header h1 {
    margin: 0;
    font-size: 2.2em;
    letter-spacing: -0.5px;
  }
  .header p {
    margin: 10px 0 0 0;
    opacity: 0.9;
    font-size: 0.95em;
  }
  .content {
    padding: 40px;
  }
  .badge {
    display: inline-flex;
    align-items: center;
    padding: 6px 14px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 0.85em;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .healthy { background: var(--primary-light); color: var(--primary-dark); }
  .diseased { background: var(--danger-light); color: var(--danger); }
  
  .grid-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }
  .stat-card {
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
  }
  .stat-card .label {
    display: block;
    color: var(--text-muted);
    font-size: 0.85em;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .stat-card .val {
    display: block;
    font-size: 1.25em;
    font-weight: 700;
    color: var(--text-main);
  }
  
  .section {
    margin-top: 35px;
  }
  .section h2 {
    color: var(--text-main);
    font-size: 1.4em;
    border-bottom: 2px solid var(--primary-light);
    padding-bottom: 10px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .description-box {
    background: #f1f5f9;
    border-left: 4px solid var(--primary);
    padding: 16px 20px;
    border-radius: 0 8px 8px 0;
    font-size: 1.05em;
    margin-bottom: 20px;
  }
  
  ul.action-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  ul.action-list li {
    position: relative;
    padding-left: 28px;
    margin-bottom: 12px;
  }
  ul.action-list li::before {
    content: "→";
    position: absolute;
    left: 0;
    top: 0;
    color: var(--primary);
    font-weight: bold;
  }
  
  .footer {
    text-align: center;
    margin-top: 50px;
    padding-top: 25px;
    border-top: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 0.85em;
  }
</style>
</head>
<body>
<div class="report-container">
  <div class="header">
    <h1>🌿 CropSense AI Report</h1>
    <p>Generated: ${new Date().toLocaleString()}</p>
  </div>
  
  <div class="content">
    <div class="grid-stats">
      <div class="stat-card">
        <span class="label">Crop / Disease</span>
        <span class="val">${label}</span>
      </div>
      <div class="stat-card">
        <span class="label">Status</span>
        <span class="badge ${statusCls}">${statusText}</span>
      </div>
      <div class="stat-card">
        <span class="label">Confidence</span>
        <span class="val">${confidence}</span>
      </div>
      <div class="stat-card">
        <span class="label">Infection Area</span>
        <span class="val">${infectionArea}</span>
        <span style="display:block;font-size:0.8em;color:var(--text-muted);margin-top:4px;">Severity: ${severityLevel}</span>
      </div>
    </div>

    <div class="description-box">
      ${clean(rec.description)}
    </div>

    <div class="section">
      <h2>⚡ Immediate Actions</h2>
      <ul class="action-list">
        ${rec.immediate_actions.map(a => `<li>${clean(a)}</li>`).join("")}
      </ul>
    </div>

    <div class="section">
      <h2>💊 Treatments</h2>
      <ul class="action-list">
        ${rec.treatments.map(t => `<li>${clean(t)}</li>`).join("")}
      </ul>
    </div>

    <div class="section">
      <h2>🛡️ Prevention</h2>
      <ul class="action-list">
        ${rec.prevention.map(p => `<li>${clean(p)}</li>`).join("")}
      </ul>
    </div>

    <div class="section">
      <h2>🌱 Fertilizer Advice</h2>
      <p style="margin-left: 10px;">${clean(rec.fertilizer)}</p>
    </div>

    <div class="footer">
      <strong>CropSense AI</strong> &mdash; Ensemble Models &mdash; Smart Crop Health Detection System
    </div>
  </div>
</div>
</body>
</html>`;

  const blob = new Blob(["\uFEFF", html], { type: "text/html;charset=utf-8" });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href = url;
  a.download = `cropsense-report-${Date.now()}.html`;
  a.click();
  URL.revokeObjectURL(url);
});


function renderDiseaseGrid(filter = "all") {
  const items = filter === "all"
    ? DISEASE_CATALOG
    : DISEASE_CATALOG.filter(d => d.crop === filter);

  diseaseGrid.innerHTML = items.map((d, i) => `
    <div class="disease-item glass-card" style="animation-delay:${i * 0.04}s">
      <div class="di-crop">${CROP_ICONS[d.crop]} ${d.crop}</div>
      <div class="di-name">${d.label}</div>
      <span class="di-status ${d.healthy ? 'healthy':'disease'}">${d.healthy ? '✓ Healthy' : '⚠ Disease'}</span>
    </div>
  `).join("");
}

document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    renderDiseaseGrid(btn.dataset.crop);
  });
});

// ─── CHECK API STATUS ────────────────────────
async function checkApiStatus() {
  const navStatus = document.getElementById("navStatus");
  try {
    const r = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(5000) });
    if (!r.ok) throw new Error();
    const data = await r.json();
    navStatus.innerHTML = `<div class="status-dot"></div><span>Model Online (${data.classes} classes)</span>`;
    navStatus.style.color = "var(--green-400)";
  } catch {
    navStatus.innerHTML = `<div class="status-dot" style="background:var(--red-400);animation:none"></div><span style="color:var(--red-400)">Model Offline</span>`;
  }
}

// ─── TOAST ───────────────────────────────────
let toastTimer = null;
function showToast(msg) {
  toastMsg.textContent = msg;
  toast.style.display = "flex";
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.style.display = "none"; }, 4000);
}

// ─── SMOOTH SCROLL NAV ───────────────────────
document.querySelectorAll("a[href^='#']").forEach(a => {
  a.addEventListener("click", e => {
    const target = document.querySelector(a.getAttribute("href"));
    if (target) { e.preventDefault(); target.scrollIntoView({ behavior: "smooth" }); }
  });
});

// ─── INIT ────────────────────────────────────
renderDiseaseGrid();
checkApiStatus();
setInterval(checkApiStatus, 30000); // Re-check every 30s
