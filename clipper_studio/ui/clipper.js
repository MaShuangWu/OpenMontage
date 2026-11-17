const fileInput = document.getElementById("fileInput");
const uploadStatus = document.getElementById("uploadStatus");
const sourceList = document.getElementById("sourceList");
const sourceCount = document.getElementById("sourceCount");
const preview = document.getElementById("preview");
const playerEmpty = document.getElementById("playerEmpty");
const timelineScrubber = document.getElementById("timelineScrubber");
const currentTime = document.getElementById("currentTime");
const durationLabel = document.getElementById("duration");
const sourceInfo = document.getElementById("sourceInfo");
const startInput = document.getElementById("startTime");
const endInput = document.getElementById("endTime");
const markStartButton = document.getElementById("markStart");
const markEndButton = document.getElementById("markEnd");
const titleInput = document.getElementById("clipTitle");
const addButton = document.getElementById("addClip");
const clipList = document.getElementById("clipList");
const clipCount = document.getElementById("clipCount");
const framingInput = document.getElementById("framing");
const exportAllButton = document.getElementById("exportAll");
const exportStatus = document.getElementById("exportStatus");
const exportsList = document.getElementById("exportsList");

const STORAGE_KEY = "openmontage.clip-studio.v1";
let sources = [];
let activeSource = null;
let clips = [];
let endOfPreview = null;

document.getElementById("importVideoButton").addEventListener("click", () => fileInput.click());
document.getElementById("emptyImportButton").addEventListener("click", () => fileInput.click());

function formatTime(seconds) {
  const value = Number.isFinite(seconds) ? Math.max(0, seconds) : 0;
  const minutes = Math.floor(value / 60);
  const wholeSeconds = Math.floor(value % 60);
  const tenths = Math.floor(value * 10) % 10;
  return `${String(minutes).padStart(2, "0")}:${String(wholeSeconds).padStart(2, "0")}.${tenths}`;
}

function displayDuration(seconds) {
  const value = Number.isFinite(seconds) ? Math.max(0, seconds) : 0;
  const minutes = Math.floor(value / 60);
  const wholeSeconds = Math.floor(value % 60);
  return `${String(minutes).padStart(2, "0")}:${String(wholeSeconds).padStart(2, "0")}`;
}

function setStatus(element, message, kind = "") {
  element.textContent = message;
  element.className = `${element.className.split(" ")[0]}${kind ? ` ${kind}` : ""}`;
}

async function requestJSON(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || `Erreur HTTP ${response.status}`);
  return data;
}

function loadSavedClips() {
  if (!activeSource) return [];
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    const list = saved[activeSource.source_id];
    return Array.isArray(list) ? list : [];
  } catch {
    return [];
  }
}

function saveClips() {
  if (!activeSource) return;
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    saved[activeSource.source_id] = clips;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
  } catch {
    setStatus(exportStatus, "La liste de clips n’a pas pu être enregistrée dans ce navigateur.", "error");
  }
}

function selectSource(source) {
  activeSource = source;
  clips = loadSavedClips();
  preview.src = source.media_url;
  preview.hidden = false;
  playerEmpty.hidden = true;
  sourceInfo.textContent = `${source.filename} · ${source.width} × ${source.height}`;
  durationLabel.textContent = displayDuration(source.duration_seconds);
  endInput.value = Math.min(30, source.duration_seconds).toFixed(1);
  startInput.max = source.duration_seconds;
  endInput.max = source.duration_seconds;
  timelineScrubber.max = source.duration_seconds;
  timelineScrubber.value = "0";
  timelineScrubber.disabled = false;
  timelineScrubber.style.setProperty("--progress", "0%");
  markStartButton.disabled = false;
  markEndButton.disabled = false;
  addButton.disabled = false;
  setStatus(exportStatus, "");
  renderSources();
  renderClips();
  preview.load();
}

function renderSources() {
  sourceList.replaceChildren();
  sourceCount.textContent = String(sources.length);
  for (const source of sources) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `source-item${activeSource?.source_id === source.source_id ? " active" : ""}`;
    const name = document.createElement("b");
    name.textContent = source.filename;
    const meta = document.createElement("span");
    meta.textContent = `${displayDuration(source.duration_seconds)} · ${source.width} × ${source.height}`;
    button.append(name, meta);
    button.addEventListener("click", () => selectSource(source));
    sourceList.append(button);
  }
}

function renderClips() {
  clipList.replaceChildren();
  clipCount.textContent = `${clips.length} ${clips.length === 1 ? "CLIP" : "CLIPS"}`;
  exportAllButton.disabled = !clips.length;
  if (!clips.length) {
    const empty = document.createElement("div");
    empty.className = "empty-list";
    const icon = document.createElement("span");
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = "✂";
    const title = document.createElement("b");
    title.textContent = "Aucun clip pour le moment";
    const hint = document.createElement("small");
    hint.textContent = "Marquez un début et une fin, puis ajoutez le passage à votre liste.";
    empty.append(icon, title, hint);
    clipList.append(empty);
    return;
  }

  clips.forEach((clip, index) => {
    const row = document.createElement("article");
    row.className = "clip-row";
    const number = document.createElement("span");
    number.className = "clip-number";
    number.textContent = String(index + 1).padStart(2, "0");
    const details = document.createElement("div");
    details.className = "clip-details";
    const title = document.createElement("b");
    title.textContent = clip.title;
    const times = document.createElement("span");
    times.textContent = `${formatTime(clip.start_seconds)} — ${formatTime(clip.end_seconds)} · ${formatTime(clip.end_seconds - clip.start_seconds)}`;
    details.append(title, times);
    const actions = document.createElement("div");
    actions.className = "clip-row-actions";
    const previewButton = document.createElement("button");
    previewButton.type = "button";
    previewButton.className = "quiet-button";
    previewButton.textContent = "Prévisualiser";
    previewButton.addEventListener("click", () => {
      startInput.value = clip.start_seconds.toFixed(1);
      endInput.value = clip.end_seconds.toFixed(1);
      titleInput.value = clip.title;
      preview.currentTime = clip.start_seconds;
      endOfPreview = clip.end_seconds;
      preview.play();
    });
    const removeButton = document.createElement("button");
    removeButton.type = "button";
    removeButton.className = "remove-button";
    removeButton.setAttribute("aria-label", `Supprimer ${clip.title}`);
    removeButton.textContent = "×";
    removeButton.addEventListener("click", () => {
      clips = clips.filter((item) => item.id !== clip.id);
      saveClips();
      renderClips();
    });
    actions.append(previewButton, removeButton);
    row.append(number, details, actions);
    clipList.append(row);
  });
}

function renderExports(exports) {
  exportsList.replaceChildren();
  document.getElementById("exportCount").textContent = `${exports.length} ${exports.length === 1 ? "FICHIER" : "FICHIERS"}`;
  if (!exports.length) {
    const empty = document.createElement("p");
    empty.className = "empty-exports";
    empty.textContent = "Vos exports apparaîtront ici.";
    exportsList.append(empty);
    return;
  }
  for (const item of exports.slice(0, 8)) {
    const card = document.createElement("article");
    card.className = "export-card";
    const video = document.createElement("video");
    video.src = item.media_url;
    video.controls = true;
    video.playsInline = true;
    video.preload = "metadata";
    const heading = document.createElement("b");
    heading.textContent = item.title;
    const details = document.createElement("span");
    details.textContent = `${formatTime(item.start_seconds)} — ${formatTime(item.end_seconds)} · ${item.framing === "portrait" ? "9:16" : "format source"}`;
    const download = document.createElement("a");
    download.className = "download-link";
    download.href = item.download_url;
    download.textContent = "Télécharger le MP4 ↓";
    card.append(video, heading, details, download);
    exportsList.append(card);
  }
}

async function refreshExports() {
  const items = await requestJSON("/api/clipper/exports");
  renderExports(items);
}

fileInput.addEventListener("change", async () => {
  const file = fileInput.files?.[0];
  if (!file) return;
  setStatus(uploadStatus, `Import de « ${file.name} »…`);
  fileInput.disabled = true;
  try {
    const source = await requestJSON(`/api/clipper/sources?filename=${encodeURIComponent(file.name)}`, {
      method: "POST",
      headers: { "Content-Type": file.type || "application/octet-stream" },
      body: file,
    });
    sources = [source, ...sources.filter((item) => item.source_id !== source.source_id)];
    selectSource(source);
    setStatus(uploadStatus, "Vidéo importée et prête à découper.", "success");
  } catch (error) {
    setStatus(uploadStatus, error.message, "error");
  } finally {
    fileInput.disabled = false;
    fileInput.value = "";
  }
});

markStartButton.addEventListener("click", () => {
  startInput.value = preview.currentTime.toFixed(1);
});
markEndButton.addEventListener("click", () => {
  endInput.value = preview.currentTime.toFixed(1);
});
preview.addEventListener("timeupdate", () => {
  currentTime.textContent = formatTime(preview.currentTime);
  timelineScrubber.value = String(preview.currentTime);
  const progress = preview.duration ? (preview.currentTime / preview.duration) * 100 : 0;
  timelineScrubber.style.setProperty("--progress", `${progress}%`);
  if (endOfPreview !== null && preview.currentTime >= endOfPreview) {
    preview.pause();
    endOfPreview = null;
  }
});
preview.addEventListener("loadedmetadata", () => {
  durationLabel.textContent = displayDuration(preview.duration);
  timelineScrubber.max = preview.duration;
});
timelineScrubber.addEventListener("input", () => {
  const time = Number(timelineScrubber.value);
  preview.currentTime = time;
  currentTime.textContent = formatTime(time);
  const progress = preview.duration ? (time / preview.duration) * 100 : 0;
  timelineScrubber.style.setProperty("--progress", `${progress}%`);
});

addButton.addEventListener("click", () => {
  if (!activeSource) return;
  const start = Number(startInput.value);
  const end = Number(endInput.value);
  if (!Number.isFinite(start) || !Number.isFinite(end) || start < 0 || end <= start || end > activeSource.duration_seconds) {
    setStatus(exportStatus, "Vérifiez les temps : la fin doit être après le début et dans la durée de la vidéo.", "error");
    return;
  }
  const title = titleInput.value.trim() || `Clip ${clips.length + 1}`;
  clips.push({ id: crypto.randomUUID(), title, start_seconds: start, end_seconds: end });
  titleInput.value = "";
  saveClips();
  renderClips();
  setStatus(exportStatus, "Passage ajouté. Vous pouvez encore le prévisualiser avant l’export.", "success");
});

async function exportClip(clip) {
  if (!activeSource) throw new Error("Sélectionnez une vidéo source.");
  return requestJSON("/api/clipper/exports", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      source_id: activeSource.source_id,
      start_seconds: clip.start_seconds,
      end_seconds: clip.end_seconds,
      title: clip.title,
      framing: framingInput.value,
    }),
  });
}

async function exportAll() {
  if (!clips.length || !activeSource) return;
  exportAllButton.disabled = true;
  const exported = [];
  try {
    for (let index = 0; index < clips.length; index += 1) {
      const clip = clips[index];
      setStatus(exportStatus, `Export ${index + 1}/${clips.length} · « ${clip.title} »…`);
      exported.push(await exportClip(clip));
    }
    await refreshExports();
    setStatus(exportStatus, `${exported.length} clip(s) exporté(s) en MP4 sur ce disque.`, "success");
  } catch (error) {
    await refreshExports();
    setStatus(exportStatus, `Export interrompu : ${error.message}`, "error");
  } finally {
    exportAllButton.disabled = false;
  }
}

exportAllButton.addEventListener("click", exportAll);

async function init() {
  try {
    sources = await requestJSON("/api/clipper/sources");
    renderSources();
    if (sources.length) selectSource(sources[0]);
    await refreshExports();
  } catch (error) {
    setStatus(uploadStatus, error.message, "error");
  }
}

init();
