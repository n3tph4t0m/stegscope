const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("file");
const pick = document.getElementById("pick");
const meta = document.getElementById("meta");
const metaName = document.getElementById("meta-name");
const metaSize = document.getElementById("meta-size");
const statusEl = document.getElementById("status");
const errorEl = document.getElementById("error");
const results = document.getElementById("results");

const LABELS = {
  ok: "ok",
  empty: "vide",
  skipped: "ignoré",
  unavailable: "indisponible",
  timeout: "timeout",
};

function humanSize(bytes) {
  const units = ["o", "Ko", "Mo"];
  let value = bytes;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit += 1;
  }
  return `${value.toFixed(value < 10 && unit > 0 ? 1 : 0)} ${units[unit]}`;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function card(entry) {
  const tone = entry.status === "ok" ? "text-emerald-400"
    : entry.status === "unavailable" ? "text-amber-400"
    : entry.status === "timeout" ? "text-red-400"
    : "text-slate-500";
  const highlights = (entry.highlights || []).length
    ? `<div class="mt-3 flex flex-wrap gap-2">${entry.highlights
        .map((h) => `<span class="rounded bg-emerald-500/10 px-2 py-0.5 text-xs text-emerald-300">${escapeHtml(h)}</span>`)
        .join("")}</div>`
    : "";
  const timing = entry.duration ? `<span class="ml-2 text-slate-600">${entry.duration}s</span>` : "";

  return `
    <article class="rounded-xl border border-slate-800 bg-slate-900/50 p-5">
      <div class="flex items-baseline justify-between">
        <h2 class="text-sm font-semibold text-slate-200">${escapeHtml(entry.label)}</h2>
        <span class="text-xs ${tone}">${LABELS[entry.status] || entry.status}${timing}</span>
      </div>
      <p class="mt-1 text-xs text-slate-500">${escapeHtml(entry.description)}</p>
      ${highlights}
      <pre class="mt-3 max-h-80 overflow-auto rounded-lg bg-slate-950 p-4 text-xs leading-relaxed text-slate-300 whitespace-pre-wrap">${escapeHtml(entry.output || "")}</pre>
    </article>`;
}

async function analyze(file) {
  errorEl.classList.add("hidden");
  results.innerHTML = "";
  metaName.textContent = file.name;
  metaSize.textContent = humanSize(file.size);
  meta.classList.remove("hidden");
  meta.classList.add("flex");
  statusEl.classList.remove("hidden");

  const body = new FormData();
  body.append("image", file);

  try {
    const res = await fetch("/api/analyze", { method: "POST", body });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Erreur serveur.");
    metaSize.textContent = humanSize(data.size);
    results.innerHTML = data.report.map(card).join("");
  } catch (err) {
    errorEl.textContent = err.message;
    errorEl.classList.remove("hidden");
  } finally {
    statusEl.classList.add("hidden");
  }
}

pick.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => {
  if (fileInput.files.length) analyze(fileInput.files[0]);
});

["dragover", "dragenter"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("border-emerald-500/60");
  })
);
["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("border-emerald-500/60");
  })
);
dropzone.addEventListener("drop", (e) => {
  if (e.dataTransfer.files.length) analyze(e.dataTransfer.files[0]);
});
