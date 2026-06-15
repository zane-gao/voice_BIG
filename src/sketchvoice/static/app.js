const canvas = document.getElementById("sketchCanvas");
const ctx = canvas.getContext("2d");
const toolButtons = document.querySelectorAll(".tool-btn[data-tool]");
const clearCanvasBtn = document.getElementById("clearCanvas");
const generateBtn = document.getElementById("generateBtn");
const recordBtn = document.getElementById("recordBtn");
const audioInput = document.getElementById("audioInput");
const audioState = document.getElementById("audioState");
const sampleSelect = document.getElementById("sampleSelect");
const loadSampleBtn = document.getElementById("loadSampleBtn");
const sampleHint = document.getElementById("sampleHint");
const sampleAudioPlayer = document.getElementById("sampleAudioPlayer");
const transcriptInput = document.getElementById("transcriptInput");
const directionInput = document.getElementById("directionInput");
const messageLine = document.getElementById("messageLine");
const healthBadge = document.getElementById("healthBadge");
const mermaidCode = document.getElementById("mermaidCode");
const jsonCode = document.getElementById("jsonCode");
const graphPreview = document.getElementById("graphPreview");
const imageStyleInput = document.getElementById("imageStyleInput");
const finalImageBtn = document.getElementById("finalImageBtn");
const draftStatus = document.getElementById("draftStatus");
const finalStatus = document.getElementById("finalStatus");
const draftMeta = document.getElementById("draftMeta");
const finalMeta = document.getElementById("finalMeta");
const draftImage = document.getElementById("draftImage");
const finalImage = document.getElementById("finalImage");
const narrationProvider = document.getElementById("narrationProvider");
const narrationVoice = document.getElementById("narrationVoice");
const narrationCustomVoiceId = document.getElementById("narrationCustomVoiceId");
const narrationDoubaoVoiceType = document.getElementById("narrationDoubaoVoiceType");
const generateNarrationBtn = document.getElementById("generateNarrationBtn");
const narrationAudio = document.getElementById("narrationAudio");
const narrationCursor = document.getElementById("narrationCursor");
const narrationStatus = document.getElementById("narrationStatus");
const narrationScript = document.getElementById("narrationScript");
const downloadNarrationVideo = document.getElementById("downloadNarrationVideo");

const OFFLINE_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "webp"];
const OFFLINE_MIN_SPIN_SECONDS = 40;
const OFFLINE_MAX_SPIN_SECONDS = 60;
const offlineDelayParam = new URLSearchParams(window.location.search).get("offlineDelayMs");
const parsedOfflineDelayMs = offlineDelayParam === null ? null : Number(offlineDelayParam);
const OFFLINE_DELAY_OVERRIDE_MS = Number.isFinite(parsedOfflineDelayMs) && parsedOfflineDelayMs >= 0 ? parsedOfflineDelayMs : null;
const offlineSeedParam = new URLSearchParams(window.location.search).get("generationSeed");
const OFFLINE_DELAY_SEED = offlineSeedParam || `${Date.now()}-${Math.random()}`;

function hashSeed(value) {
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function seededRatio(value) {
  const seed = hashSeed(value);
  return (seed % 1000000) / 1000000;
}

function seededGenerationDelayMs(mode, seq) {
  if (OFFLINE_DELAY_OVERRIDE_MS !== null) return OFFLINE_DELAY_OVERRIDE_MS;
  const sampleId = activeSample?.id || "manual";
  const ratio = seededRatio(`${OFFLINE_DELAY_SEED}:${sampleId}:${mode}:${seq}`);
  const span = OFFLINE_MAX_SPIN_SECONDS - OFFLINE_MIN_SPIN_SECONDS + 1;
  return (OFFLINE_MIN_SPIN_SECONDS + Math.floor(ratio * span)) * 1000;
}

const OFFLINE_METHOD_GRAPH = {
  title: "方法图生成演示",
  summary: "根据输入内容生成结构化方法图。",
  nodes: [
    { id: "input", label: "语音和草图输入", kind: "input" },
    { id: "process", label: "结构化建模", kind: "process" },
    { id: "render", label: "图像生成", kind: "process" },
    { id: "final", label: "终稿图和讲解", kind: "output" },
  ],
  edges: [
    { source: "input", target: "process", label: "触发" },
    { source: "process", target: "render", label: "生成" },
    { source: "render", target: "final", label: "展示" },
  ],
};

let activeTool = "pen";
let drawing = false;
let mediaRecorder = null;
let recordedChunks = [];
let recordedAudioBlob = null;
let uploadedAudioFile = null;
let lastResult = null;
let canvasTouched = false;
let draftTimer = null;
let draftRequestSeq = 0;
let finalRequestSeq = 0;
let lastDraftResult = null;
let lastFinalResult = null;
let demoSamples = [];
let sampleAudioBlob = null;
let activeSample = null;
let lastNarration = null;
let narrationAudioUrl = null;
let narrationAnimationFrame = null;

function setMessage(text) {
  messageLine.textContent = text;
}

function setCanvasDefaults() {
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.strokeStyle = "#0f172a";
  ctx.lineWidth = 3;
}

function canvasPoint(event) {
  const rect = canvas.getBoundingClientRect();
  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;
  return {
    x: (event.clientX - rect.left) * scaleX,
    y: (event.clientY - rect.top) * scaleY,
  };
}

function startDrawing(event) {
  drawing = true;
  const point = canvasPoint(event);
  ctx.beginPath();
  ctx.moveTo(point.x, point.y);
  event.preventDefault();
}

function draw(event) {
  if (!drawing) return;
  canvasTouched = true;
  const point = canvasPoint(event);
  if (activeTool === "eraser") {
    ctx.globalCompositeOperation = "destination-out";
    ctx.lineWidth = 18;
  } else {
    ctx.globalCompositeOperation = "source-over";
    ctx.strokeStyle = "#0f172a";
    ctx.lineWidth = 3;
  }
  ctx.lineTo(point.x, point.y);
  ctx.stroke();
  event.preventDefault();
}

function stopDrawing() {
  drawing = false;
  ctx.globalCompositeOperation = "source-over";
  setCanvasDefaults();
  if (canvasTouched) scheduleDraftRender();
}

canvas.addEventListener("pointerdown", startDrawing);
canvas.addEventListener("pointermove", draw);
canvas.addEventListener("pointerup", stopDrawing);
canvas.addEventListener("pointerleave", stopDrawing);
setCanvasDefaults();

toolButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activeTool = button.dataset.tool;
    toolButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
  });
});

clearCanvasBtn.addEventListener("click", () => {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  canvasTouched = false;
  setMessage("画布已清空。");
  scheduleDraftRender();
});

transcriptInput.addEventListener("input", scheduleDraftRender);
directionInput.addEventListener("change", scheduleDraftRender);
imageStyleInput.addEventListener("change", scheduleDraftRender);

audioInput.addEventListener("change", () => {
  uploadedAudioFile = audioInput.files[0] || null;
  recordedAudioBlob = null;
  sampleAudioBlob = null;
  activeSample = null;
  sampleAudioPlayer.removeAttribute("src");
  audioState.textContent = uploadedAudioFile ? `已选择：${uploadedAudioFile.name}` : "未选择音频";
});

recordBtn.addEventListener("click", async () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    recordBtn.textContent = "开始录音";
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) recordedChunks.push(event.data);
    };
    mediaRecorder.onstop = () => {
      recordedAudioBlob = new Blob(recordedChunks, { type: "audio/webm" });
      uploadedAudioFile = null;
      sampleAudioBlob = null;
      activeSample = null;
      audioInput.value = "";
      sampleAudioPlayer.removeAttribute("src");
      stream.getTracks().forEach((track) => track.stop());
      audioState.textContent = `已录音：${Math.round(recordedAudioBlob.size / 1024)} KB`;
      setMessage("录音完成，可以生成方法图。");
    };
    mediaRecorder.start();
    recordBtn.textContent = "停止录音";
    setMessage("正在录音...");
  } catch (error) {
    setMessage(`无法访问麦克风：${error.message}`);
  }
});

async function loadSampleList() {
  try {
    const response = await fetch("/api/samples");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    demoSamples = data.samples || [];
    sampleSelect.innerHTML = '<option value="">选择草图 + 语音案例</option>';
    demoSamples.forEach((sample) => {
      const option = document.createElement("option");
      option.value = sample.id;
      option.textContent = `${sample.topic} · ${sample.difficulty}`;
      sampleSelect.appendChild(option);
    });
    sampleHint.textContent = demoSamples.length ? `已载入 ${demoSamples.length} 个演示案例` : "暂无演示案例";
  } catch (error) {
    sampleHint.textContent = "样例列表加载失败";
  }
}

function selectedSample() {
  return demoSamples.find((sample) => sample.id === sampleSelect.value) || null;
}

async function loadImageToCanvas(url) {
  const image = new Image();
  image.crossOrigin = "same-origin";
  await new Promise((resolve, reject) => {
    image.onload = resolve;
    image.onerror = () => reject(new Error("草图图片加载失败"));
    image.src = `${url}?t=${Date.now()}`;
  });
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  const scale = Math.min(canvas.width / image.width, canvas.height / image.height);
  const drawWidth = image.width * scale;
  const drawHeight = image.height * scale;
  const x = (canvas.width - drawWidth) / 2;
  const y = (canvas.height - drawHeight) / 2;
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(image, x, y, drawWidth, drawHeight);
  canvasTouched = true;
}

async function loadSampleAudio(sample) {
  sampleAudioBlob = null;
  sampleAudioPlayer.removeAttribute("src");
  if (!sample.audio_url) {
    audioState.textContent = "样例无音频";
    return;
  }
  const response = await fetch(sample.audio_url);
  if (!response.ok) throw new Error(`音频加载失败：HTTP ${response.status}`);
  sampleAudioBlob = await response.blob();
  sampleAudioPlayer.src = URL.createObjectURL(sampleAudioBlob);
  audioState.textContent = `已载入样例音频：${sample.topic}`;
}

async function loadSelectedSample() {
  const sample = selectedSample();
  if (!sample) {
    setMessage("请先选择一个演示样例。");
    return;
  }
  loadSampleBtn.disabled = true;
  loadSampleBtn.textContent = "载入中...";
  try {
    activeSample = sample;
    uploadedAudioFile = null;
    recordedAudioBlob = null;
    audioInput.value = "";
    transcriptInput.value = sample.transcript || "";
    directionInput.value = sample.direction || "LR";
    resetOfflineOutputs(sample);
    await loadImageToCanvas(sample.sketch_url);
    await loadSampleAudio(sample);
    setMessage(`已载入演示样例：${sample.topic}。可以直接生成方法图。`);
    scheduleDraftRender();
  } catch (error) {
    setMessage(`载入样例失败：${error.message}`);
  } finally {
    loadSampleBtn.disabled = false;
    loadSampleBtn.textContent = "载入样例";
  }
}

loadSampleBtn.addEventListener("click", loadSelectedSample);
sampleSelect.addEventListener("change", () => {
  const sample = selectedSample();
  sampleHint.textContent = sample
    ? `${sample.gold_nodes?.length || 0} 个标准节点 · ${sample.gold_edges?.length || 0} 条边`
    : `${demoSamples.length} 个演示案例可用`;
});

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach((pane) => pane.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById(`${tab.dataset.tab}Pane`).classList.add("active");
  });
});

function offlineImageName(imageKey) {
  return imageKey === "method" ? "method.png / method.jpg / method.jpeg / method.webp" : "final.png / final.jpg / final.jpeg / final.webp";
}

function offlineImageCandidates(imageKey) {
  const sampleId = activeSample?.id;
  const sampleCandidates = sampleId
    ? OFFLINE_IMAGE_EXTENSIONS.map((extension) => `/static/offline/${sampleId}/${imageKey}.${extension}`)
    : [];
  const fallbackCandidates = OFFLINE_IMAGE_EXTENSIONS.map((extension) => `/static/offline/${imageKey}.${extension}`);
  return [...sampleCandidates, ...fallbackCandidates];
}

function mimeTypeFromPath(path, fallback = "image/png") {
  const normalized = path.toLowerCase();
  if (normalized.endsWith(".jpg") || normalized.endsWith(".jpeg")) return "image/jpeg";
  if (normalized.endsWith(".webp")) return "image/webp";
  if (normalized.endsWith(".png")) return "image/png";
  return fallback;
}

function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const dataUrl = String(reader.result || "");
      resolve(dataUrl.includes(",") ? dataUrl.split(",")[1] : dataUrl);
    };
    reader.onerror = () => reject(new Error("图片读取失败"));
    reader.readAsDataURL(blob);
  });
}

async function loadOfflineImageResult(mode, imageKey) {
  const candidates = offlineImageCandidates(imageKey);
  for (const url of candidates) {
    const response = await fetch(`${url}?t=${Date.now()}`, { cache: "no-store" });
    if (response.ok) {
      const blob = await response.blob();
      return {
        mode,
        image_b64: await blobToBase64(blob),
        mime_type: blob.type || mimeTypeFromPath(url),
        provider: "offline",
        model: url.replace("/static/offline/", ""),
        cached: false,
        timings_ms: { total: "--" },
        warnings: [],
        source_url: url,
      };
    }
  }
  const samplePrefix = activeSample?.id ? `${activeSample.id}/` : "";
  throw new Error(`生成资源未就绪，请检查 ${samplePrefix}${offlineImageName(imageKey)}`);
}

function ensureOfflineMethodResult() {
  const transcript = transcriptInput.value.trim() || activeSample?.transcript || "演示：使用语音和草图生成方法图。";
  const graph = graphFromSample(activeSample);
  lastResult = {
    transcript,
    mermaid: mermaidFromGraph(graph, directionInput.value || activeSample?.direction || "LR"),
    graph,
    timings_ms: { asr: "--", graph: "--", total: "--" },
  };
  transcriptInput.value = transcript;
  mermaidCode.textContent = lastResult.mermaid;
  jsonCode.textContent = JSON.stringify(lastResult.graph, null, 2);
  document.getElementById("asrTime").textContent = lastResult.timings_ms.asr;
  document.getElementById("graphTime").textContent = lastResult.timings_ms.graph;
  document.getElementById("totalTime").textContent = lastResult.timings_ms.total;
}

function showOfflineGraphPreview(result) {
  const imageSrc = `data:${result.mime_type};base64,${result.image_b64}`;
  graphPreview.innerHTML = "";
  const image = document.createElement("img");
  image.src = imageSrc;
  image.alt = "方法图";
  image.style.width = "100%";
  image.style.maxWidth = "760px";
  image.style.maxHeight = "520px";
  image.style.objectFit = "contain";
  graphPreview.appendChild(image);
}

function graphFromSample(sample) {
  if (!sample) return OFFLINE_METHOD_GRAPH;
  const nodes = (sample.gold_nodes || []).map((label, index) => ({
    id: `n${index + 1}`,
    label,
    kind: index === 0 ? "input" : index === (sample.gold_nodes || []).length - 1 ? "output" : "process",
  }));
  const nodeIdByLabel = new Map(nodes.map((node) => [node.label, node.id]));
  const edges = (sample.gold_edges || [])
    .map(([source, target]) => ({
      source: nodeIdByLabel.get(source) || source,
      target: nodeIdByLabel.get(target) || target,
      label: "",
    }))
    .filter((edge) => edge.source && edge.target);
  return {
    title: sample.topic || sample.id || "方法图生成演示",
    summary: sample.transcript || "样例方法图。",
    nodes,
    edges,
  };
}

function mermaidFromGraph(graph, direction = "LR") {
  const lines = [`flowchart ${direction}`];
  graph.nodes.forEach((node) => {
    lines.push(`  ${node.id}[${node.label}]`);
  });
  graph.edges.forEach((edge) => {
    lines.push(edge.label ? `  ${edge.source} -->|${edge.label}| ${edge.target}` : `  ${edge.source} --> ${edge.target}`);
  });
  return lines.join("\n");
}

function resetOfflineOutputs(sample) {
  window.clearTimeout(draftTimer);
  draftRequestSeq += 1;
  finalRequestSeq += 1;
  lastResult = null;
  lastDraftResult = null;
  lastFinalResult = null;
  mermaidCode.textContent = "等待生成...";
  jsonCode.textContent = "等待生成...";
  graphPreview.textContent = "等待图形预览";
  draftImage.removeAttribute("src");
  finalImage.removeAttribute("src");
  draftImage.closest(".image-frame").classList.remove("has-image");
  finalImage.closest(".image-frame").classList.remove("has-image");
  draftStatus.textContent = sample ? "点击按钮生成" : "等待输入";
  finalStatus.textContent = "点击按钮生成";
  draftMeta.textContent = "Seedream 5.0 lite";
  finalMeta.textContent = "GPT Image";
  clearNarrationState("等待终稿图");
}

function wait(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

async function spinOfflineGeneration(mode, seq, delayMs) {
  const isDraft = mode === "draft";
  const label = isDraft ? "方法图" : "终稿图";
  const status = isDraft ? draftStatus : finalStatus;
  if (isDraft && seq !== draftRequestSeq) return false;
  if (!isDraft && seq !== finalRequestSeq) return false;
  status.textContent = `生成${label}中...`;
  setMessage(`正在生成${label}...`);
  await wait(delayMs);
  if (isDraft && seq !== draftRequestSeq) return false;
  if (!isDraft && seq !== finalRequestSeq) return false;
  return true;
}

function activateTab(tabName) {
  const tab = document.querySelector(`.tab[data-tab="${tabName}"]`);
  if (tab) tab.click();
}

generateBtn.addEventListener("click", async () => {
  generateBtn.disabled = true;
  generateBtn.textContent = "生成中...";
  try {
    await renderImage("draft");
  } catch (error) {
    setMessage(`生成失败：${error.message}`);
  } finally {
    generateBtn.disabled = false;
    generateBtn.textContent = "生成方法图";
  }
});

function hasImageSignal() {
  return Boolean(canvasTouched || transcriptInput.value.trim() || lastResult);
}

function scheduleDraftRender(delay = null) {
  window.clearTimeout(draftTimer);
  if (!hasImageSignal()) {
    draftStatus.textContent = "等待输入";
    return;
  }
  draftStatus.textContent = lastDraftResult ? "已生成，可重新生成" : "点击按钮生成";
}

async function renderImage(mode) {
  const isDraft = mode === "draft";
  const seq = isDraft ? ++draftRequestSeq : ++finalRequestSeq;
  const delayMs = seededGenerationDelayMs(mode, seq);
  if (isDraft) {
    window.clearTimeout(draftTimer);
    draftStatus.textContent = "生成方法图中...";
  } else {
    finalImageBtn.disabled = true;
    finalStatus.textContent = "生成终稿图中...";
  }

  try {
    if (!await spinOfflineGeneration(mode, seq, delayMs)) return;
    if (!lastResult) ensureOfflineMethodResult();
    const imageKey = isDraft ? "method" : "final";
    const result = await loadOfflineImageResult(mode, imageKey);
    if (isDraft && seq !== draftRequestSeq) return;
    if (!isDraft && seq !== finalRequestSeq) return;
    if (isDraft) showOfflineGraphPreview(result);
    updateImageResult(result);
    setMessage(isDraft ? "方法图已生成。" : "终稿图已生成。");
  } catch (error) {
    if (isDraft) {
      draftStatus.textContent = `方法图加载失败：${error.message}`;
    } else {
      finalStatus.textContent = `终稿图加载失败：${error.message}`;
    }
  } finally {
    if (!isDraft) finalImageBtn.disabled = false;
  }
}

function updateImageResult(result) {
  const isDraft = result.mode === "draft";
  const image = isDraft ? draftImage : finalImage;
  const status = isDraft ? draftStatus : finalStatus;
  const meta = isDraft ? draftMeta : finalMeta;
  const frame = image.closest(".image-frame");
  image.src = `data:${result.mime_type};base64,${result.image_b64}`;
  frame.classList.add("has-image");
  const usedMock = String(result.provider || "").includes("mock");
  const stateText = usedMock ? "回退 Mock" : result.cached ? "缓存命中" : "完成";
  const modelText = isDraft ? "Seedream 5.0 lite" : "GPT Image";
  status.textContent = `${stateText} · ${result.timings_ms.total ?? "--"} ms`;
  meta.textContent = modelText;
  if (isDraft) {
    lastDraftResult = result;
  } else {
    lastFinalResult = result;
    clearNarrationState("终稿图已更新，可生成语音讲解。");
  }
}

function b64ToBlob(base64, mimeType) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return new Blob([bytes], { type: mimeType });
}

function clearNarrationState(statusText = "等待终稿图") {
  if (narrationAudioUrl) URL.revokeObjectURL(narrationAudioUrl);
  window.cancelAnimationFrame(narrationAnimationFrame);
  lastNarration = null;
  narrationAudioUrl = null;
  narrationAnimationFrame = null;
  narrationAudio.pause();
  narrationAudio.removeAttribute("src");
  narrationAudio.load();
  narrationCursor.classList.remove("active", "focus");
  narrationStatus.textContent = statusText;
  narrationScript.textContent = "";
}

function narrationSegmentAt(currentTime, duration) {
  const segments = lastNarration?.segments || [];
  if (!segments.length) return null;
  const safeDuration = Number.isFinite(duration) && duration > 0 ? duration : Math.max(1, segments.length * 2.5);
  const ratio = Math.min(1, Math.max(0, currentTime / safeDuration));
  const weights = segments.map((segment) => Math.max(4, segment.text.length));
  const totalWeight = weights.reduce((sum, value) => sum + value, 0);
  let cursor = ratio * totalWeight;
  for (let index = 0; index < segments.length; index += 1) {
    cursor -= weights[index];
    if (cursor <= 0) return segments[index];
  }
  return segments[segments.length - 1];
}

function updateNarrationCursor() {
  const segment = narrationSegmentAt(narrationAudio.currentTime || 0, narrationAudio.duration || 0);
  if (!segment || !finalImage.complete || !finalImage.clientWidth || !finalImage.clientHeight) return;
  const left = finalImage.offsetLeft + segment.x * finalImage.clientWidth;
  const top = finalImage.offsetTop + segment.y * finalImage.clientHeight;
  narrationCursor.style.left = `${left}px`;
  narrationCursor.style.top = `${top}px`;
  narrationCursor.classList.toggle("focus", segment.emphasis === "focus");
  narrationCursor.classList.add("active");
  narrationStatus.textContent = segment.target_label ? `讲解中：${segment.target_label}` : "讲解中";
}

function startNarrationCursorLoop() {
  window.cancelAnimationFrame(narrationAnimationFrame);
  const tick = () => {
    updateNarrationCursor();
    if (!narrationAudio.paused && !narrationAudio.ended) {
      narrationAnimationFrame = window.requestAnimationFrame(tick);
    }
  };
  tick();
}

async function generateNarration() {
  if (!lastFinalResult) {
    setMessage("请先生成终稿图。");
    return;
  }
  generateNarrationBtn.disabled = true;
  generateNarrationBtn.textContent = "生成中...";
  narrationStatus.textContent = "正在生成讲解...";
  try {
    const imageBlob = b64ToBlob(lastFinalResult.image_b64, lastFinalResult.mime_type);
    const form = new FormData();
    const extension = lastFinalResult.mime_type.includes("png") ? "png" : "jpg";
    form.append("image", imageBlob, `final.${extension}`);
    form.append("provider", narrationProvider.value);
    form.append("voice", narrationVoice.value);
    form.append("custom_voice_id", narrationCustomVoiceId.value.trim());
    form.append("doubao_voice_type", narrationDoubaoVoiceType.value.trim());
    form.append("graph_json", lastResult?.graph ? JSON.stringify(lastResult.graph) : jsonCode.textContent || "");
    form.append("mermaid", lastResult?.mermaid || mermaidCode.textContent || "");
    form.append("transcript", transcriptInput.value);

    const response = await fetch("/api/narrate-image", { method: "POST", body: form });
    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || `HTTP ${response.status}`);
    }
    clearNarrationState("讲解已生成。");
    lastNarration = await response.json();
    const audioBlob = b64ToBlob(lastNarration.audio_b64, lastNarration.mime_type);
    narrationAudioUrl = URL.createObjectURL(audioBlob);
    narrationAudio.src = narrationAudioUrl;
    narrationScript.textContent = lastNarration.script;
    updateNarrationCursor();
    setMessage(`语音讲解已生成：${lastNarration.provider} · ${lastNarration.model}`);
  } catch (error) {
    narrationStatus.textContent = `讲解失败：${error.message}`;
    setMessage(`讲解失败：${error.message}`);
  } finally {
    generateNarrationBtn.disabled = false;
    generateNarrationBtn.textContent = "生成讲解";
  }
}

finalImageBtn.addEventListener("click", () => renderImage("final"));

function downloadText(filename, text, type = "text/plain") {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

document.getElementById("downloadMermaid").addEventListener("click", () => {
  if (!lastResult) return setMessage("请先生成结果。");
  downloadText("method_graph.mmd", lastResult.mermaid);
});

document.getElementById("downloadJson").addEventListener("click", () => {
  if (!lastResult) return setMessage("请先生成结果。");
  downloadText("method_graph.json", JSON.stringify(lastResult.graph, null, 2), "application/json");
});

document.getElementById("downloadSvg").addEventListener("click", () => {
  const svg = graphPreview.querySelector("svg");
  if (!svg) return setMessage("当前没有可下载的 SVG。");
  downloadText("method_graph.svg", svg.outerHTML, "image/svg+xml");
});

function downloadImageResult(result, filename) {
  if (!result) return setMessage("请先生成对应图片。");
  const binary = atob(result.image_b64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  const blob = new Blob([bytes], { type: result.mime_type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function imageExtension(result, fallback = "png") {
  if (!result?.mime_type) return fallback;
  if (result.mime_type.includes("jpeg") || result.mime_type.includes("jpg")) return "jpg";
  if (result.mime_type.includes("webp")) return "webp";
  if (result.mime_type.includes("png")) return "png";
  return fallback;
}

document.getElementById("downloadDraftImage").addEventListener("click", () => {
  downloadImageResult(lastDraftResult, `method_image.${imageExtension(lastDraftResult, "png")}`);
});

document.getElementById("downloadFinalImage").addEventListener("click", () => {
  downloadImageResult(lastFinalResult, `final_method_image.${imageExtension(lastFinalResult, "png")}`);
});

function loadImageFromDataUrl(src) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("终稿图加载失败"));
    image.src = src;
  });
}

function drawNarrationFrame(context, recordImage, segment, width, height) {
  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, width, height);
  const scale = Math.min(width / recordImage.width, height / recordImage.height);
  const drawWidth = recordImage.width * scale;
  const drawHeight = recordImage.height * scale;
  const offsetX = (width - drawWidth) / 2;
  const offsetY = (height - drawHeight) / 2;
  context.drawImage(recordImage, offsetX, offsetY, drawWidth, drawHeight);

  if (!segment) return;
  const x = offsetX + segment.x * drawWidth;
  const y = offsetY + segment.y * drawHeight;
  context.beginPath();
  context.arc(x, y, segment.emphasis === "focus" ? 16 : 13, 0, Math.PI * 2);
  context.fillStyle = "rgba(239, 68, 68, 0.18)";
  context.fill();
  context.beginPath();
  context.arc(x, y, 7, 0, Math.PI * 2);
  context.fillStyle = "#ef4444";
  context.fill();
  context.lineWidth = 3;
  context.strokeStyle = "#ffffff";
  context.stroke();
}

function preferredWebMMimeType() {
  if (!window.MediaRecorder) return "";
  return (
    ["video/webm;codecs=vp9,opus", "video/webm;codecs=vp8,opus", "video/webm"].find((type) =>
      MediaRecorder.isTypeSupported(type)
    ) || ""
  );
}

async function recordNarrationVideo() {
  if (!lastFinalResult || !lastNarration || !narrationAudio.src) {
    setMessage("请先生成终稿图和语音讲解。");
    return;
  }
  if (!window.MediaRecorder) {
    setMessage("当前浏览器不支持 MediaRecorder，无法下载 WebM。");
    return;
  }

  const recordCanvas = document.createElement("canvas");
  recordCanvas.width = 1280;
  recordCanvas.height = 720;
  const context = recordCanvas.getContext("2d");
  if (!context || !recordCanvas.captureStream) {
    setMessage("当前浏览器不支持 canvas.captureStream，无法下载 WebM。");
    return;
  }
  const captureAudioStream = narrationAudio.captureStream || narrationAudio.mozCaptureStream;
  if (!captureAudioStream) {
    setMessage("当前浏览器不支持音频 captureStream，无法合成带声音的 WebM。");
    return;
  }

  downloadNarrationVideo.disabled = true;
  downloadNarrationVideo.textContent = "录制中...";
  setMessage("正在录制讲解 WebM...");
  try {
    const recordImage = await loadImageFromDataUrl(`data:${lastFinalResult.mime_type};base64,${lastFinalResult.image_b64}`);
    const canvasStream = recordCanvas.captureStream(30);
    const audioStream = captureAudioStream.call(narrationAudio);
    const stream = new MediaStream([...canvasStream.getVideoTracks(), ...audioStream.getAudioTracks()]);
    const mimeType = preferredWebMMimeType();
    const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
    const chunks = [];
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunks.push(event.data);
    };

    const stopped = new Promise((resolve) => {
      recorder.onstop = resolve;
    });
    const ended = new Promise((resolve) => {
      narrationAudio.addEventListener("ended", resolve, { once: true });
    });

    let recording = true;
    const paint = () => {
      const segment = narrationSegmentAt(narrationAudio.currentTime || 0, narrationAudio.duration || 0);
      drawNarrationFrame(context, recordImage, segment, recordCanvas.width, recordCanvas.height);
      if (recording) window.requestAnimationFrame(paint);
    };

    narrationAudio.currentTime = 0;
    recorder.start();
    paint();
    await narrationAudio.play();
    await ended;
    recording = false;
    recorder.stop();
    await stopped;
    stream.getTracks().forEach((track) => track.stop());

    const blob = new Blob(chunks, { type: recorder.mimeType || "video/webm" });
    if (!blob.size) throw new Error("录制结果为空");
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "final_method_narration.webm";
    anchor.click();
    URL.revokeObjectURL(url);
    setMessage("讲解 WebM 已生成。");
  } catch (error) {
    setMessage(`WebM 录制失败：${error.message}`);
  } finally {
    downloadNarrationVideo.disabled = false;
    downloadNarrationVideo.textContent = "下载 WebM";
  }
}

generateNarrationBtn.addEventListener("click", generateNarration);
narrationAudio.addEventListener("timeupdate", updateNarrationCursor);
narrationAudio.addEventListener("play", startNarrationCursorLoop);
narrationAudio.addEventListener("pause", () => window.cancelAnimationFrame(narrationAnimationFrame));
narrationAudio.addEventListener("ended", () => {
  updateNarrationCursor();
  narrationStatus.textContent = "讲解播放完成";
});
downloadNarrationVideo.addEventListener("click", recordNarrationVideo);

healthBadge.textContent = "生成服务就绪";
draftMeta.textContent = "Seedream 5.0 lite";
finalMeta.textContent = "GPT Image";

loadSampleList();
