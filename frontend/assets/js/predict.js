// Predict page logic: single-image heatmap + multi-image batch analysis.
// Reuses API_BASE + downloadPdfReport from assets/js/app.js (loaded first).
const API = typeof API_BASE !== 'undefined' ? API_BASE : 'http://127.0.0.1:8000';
const ii = document.getElementById('imageInput');
const pb = document.getElementById('previewBox');
const uz = document.getElementById('uploadZone');
const rc = document.getElementById('resultCard');
let _batchState = null;

function tok() { const t = localStorage.getItem('token'); if (!t) window.location.href = 'login.html'; return t; }
function qc(q) { return q === 'Fresh' ? 'var(--p1)' : q === 'Moderately Fresh' ? 'var(--warn)' : 'var(--danger)'; }
function qb(q) { return q === 'Fresh' ? 'rgba(0,245,160,0.1)' : q === 'Moderately Fresh' ? 'rgba(251,191,36,0.1)' : 'rgba(248,113,113,0.1)'; }
function head(t) { return '<h4 style="font-weight:800;margin-bottom:1rem;background:linear-gradient(135deg,#fff,var(--p1));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">' + t + '</h4>'; }
function row(l, v, c) { if (v == null) return ''; return '<div style="display:flex;justify-content:space-between;font-size:0.8rem;margin:0.3rem 0;"><span>' + l + '</span><span style="color:' + c + ';font-weight:700;">' + (v * 100).toFixed(1) + '%</span></div>'; }

ii.addEventListener('change', () => {
  const fs = Array.from(ii.files);
  if (!fs.length) return;
  uz.style.display = 'none';
  pb.style.display = 'block';
  const r = new FileReader();
  r.onload = e => {
    let h = '<img src="' + e.target.result + '" alt="preview" style="max-height:220px;border-radius:14px;object-fit:contain;box-shadow:0 8px 32px rgba(0,0,0,0.4);"/>';
    h += fs.length > 1
      ? '<p style="color:var(--muted);font-size:0.78rem;margin-top:0.5rem;">' + fs.length + ' images selected - use Batch Analyse below</p>'
      : '<p style="color:var(--muted);font-size:0.78rem;margin-top:0.5rem;">' + fs[0].name + '</p>';
    pb.innerHTML = h;
  };
  r.readAsDataURL(fs[0]);
  rc.innerHTML = head('Prediction Result') + '<p style="color:var(--muted);font-size:0.88rem;">' + (fs.length > 1 ? 'Multiple images selected.' : 'Click Analyse Quality to continue.') + '</p>';
});

function renderError(msg) {
  rc.innerHTML = head('Prediction Result') + '<p style="color:var(--danger);margin-top:0.5rem;">' + msg + '</p>';
}

function _navBar() {
  if (_batchState) return '<div class="d-flex gap-2 mb-3"><button class="btn btn-sm btn-outline-secondary" onclick="backToBatch()"> ← Back to Batch Results</button><button class="btn btn-sm btn-outline-secondary" onclick="resetUpload()"> ↺ Change photo</button></div>';
  return '<div class="mb-3"><button class="btn btn-sm btn-outline-secondary" onclick="resetUpload()"> ↺ Change photo</button></div>';
}
function backToBatch() {
  if (_batchState) { renderBatch(_batchState.data, _batchState.fileMap); }
}

function renderPrediction(d) {
    let heat = '', stats = '';
    if (d.analysis_image) heat = '<p style="font-size:0.85rem;color:var(--muted);margin:0.8rem 0 0.4rem;">Spoilage heatmap (red = rot, green boxes = damage regions)</p><img src="' + d.analysis_image + '" alt="heatmap" style="width:100%;border-radius:14px;border:1px solid rgba(255,255,255,0.1);"/>';
    if (d.analysis_stats) {
      const s = d.analysis_stats;
      stats = head('Detection basis')
        + row('Brown / rot ratio', s.brown_ratio, 'var(--danger)')
        + row('Dark / decay ratio', s.dark_ratio, '#fbbf24')
        + row('Yellow (degraded)', s.yellow_ratio, 'var(--warn)')
        + row('Rotten pixel coverage', s.rotten_pixel_ratio, 'var(--danger)');
    }
    const c = qc(d.quality);
    rc.innerHTML = _navBar() + head('Prediction Result')
      + '<div style="background:' + qb(d.quality) + ';border:1px solid ' + c + ';border-radius:14px;padding:1rem 1.2rem;margin-bottom:1rem;"><div style="font-size:1.8rem;font-weight:900;color:' + c + ';">' + d.quality + '</div></div>'
      + '<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0.3rem;">Confidence</p><div class="progress-bar-custom"><div class="progress-fill" style="width:' + d.confidence + '%;"></div></div><div style="text-align:right;font-size:0.82rem;color:' + c + ';font-weight:700;margin-bottom:1rem;">' + d.confidence + '%</div>'
      + heat + stats
      + '<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0.3rem;">Recommendation</p><p style="font-size:0.88rem;line-height:1.6;">' + d.recommendation + '</p>'
      + '<div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:14px;padding:1rem;margin-bottom:0.5rem;"><div style="display:flex;justify-content:space-between;"><span style="color:var(--muted);font-size:0.82rem;">Storage Life</span><span style="font-size:1.1rem;font-weight:700;color:var(--p1);">' + d.storage_days + ' days</span></div><div style="display:flex;justify-content:space-between;margin-top:0.4rem;"><span style="color:var(--muted);font-size:0.82rem;">Storage Temperature</span><span style="font-size:0.95rem;font-weight:600;">' + d.storage_temperature + '</span></div></div>'
      + '<div class="d-flex gap-2 mt-3"><button class="btn-primary-custom" style="font-size:0.82rem;padding:0.55rem 1.1rem;" onclick="downloadPdfReport(' + d.id + ', this)">📄 Download PDF</button><a class="btn-outline-custom" style="font-size:0.82rem;padding:0.55rem 1.1rem;" href="history.html">View History</a></div>';
}

// Click any batch thumbnail to re-run the detailed single-image analysis on it.
rc.addEventListener('click', async e => {
  const img = e.target.closest('[data-image-url]');
  if (!img) return;
  const url = img.getAttribute('data-image-url');
  const filename = img.getAttribute('data-filename') || 'batch-image.jpg';
  const t = tok();
  rc.innerHTML = '<div class="d-flex align-items-center gap-2" style="color:var(--p1);"><div class="spinner" style="border-top-color:var(--p1);border-color:rgba(0,245,160,0.2);"></div><span style="font-weight:600;">Analysing image...</span></div>';
  try {
    const blob = await (await fetch(url)).blob();
    const fd = new FormData(); fd.append('file', blob, filename);
    const res = await fetch(API + '/predict', { method: 'POST', headers: { Authorization: 'Bearer ' + t }, body: fd });
    const d = await res.json();
    if (!res.ok) throw new Error(d.detail || 'Prediction failed');
    renderPrediction(d);
  } catch (err) {
    renderError(err.message);
  }
});
// SINGLE image: show WHERE the rotten/spoiled regions are detected (heatmap).
document.getElementById('predictBtn').addEventListener('click', async () => {
  const f = ii.files[0];
  if (!f) return alert('Please choose an image first.');
  _batchState = null;
  const t = tok();
  const fd = new FormData(); fd.append('file', f);
  rc.innerHTML = '<div class="d-flex align-items-center gap-2" style="color:var(--p1);"><div class="spinner" style="border-top-color:var(--p1);border-color:rgba(0,245,160,0.2);"></div><span style="font-weight:600;">Analysing image...</span></div>';
  try {
    const res = await fetch(API + '/predict', { method: 'POST', headers: { Authorization: 'Bearer ' + t }, body: fd });
    const d = await res.json();
    if (!res.ok) throw new Error(d.detail || 'Prediction failed');
    renderPrediction(d);
  } catch (e) { renderError(e.message); }
});

// MULTIPLE images: detect all at once, grouped by Fresh / Moderately Fresh / Rotten.
document.getElementById('batchBtn').addEventListener('click', async () => {
  const fs = ii.files;
  if (!fs || fs.length < 2) return alert('Select 2 or more images to batch-analyse.');
  const t = tok();
  const fd = new FormData();
  const fileMap = {};
  for (let i = 0; i < fs.length; i++) { fd.append('files', fs[i]); fileMap[fs[i].name] = URL.createObjectURL(fs[i]); }
  rc.innerHTML = '<div class="d-flex align-items-center gap-2" style="color:var(--p1);"><div class="spinner" style="border-top-color:var(--p1);border-color:rgba(0,245,160,0.2);"></div><span style="font-weight:600;">Analysing ' + fs.length + ' images...</span></div>';
  try {
    const res = await fetch(API + '/predict-batch', { method: 'POST', headers: { Authorization: 'Bearer ' + t }, body: fd });
    const d = await res.json();
    if (!res.ok) throw new Error(d.detail || 'Batch prediction failed');
    renderBatch(d, fileMap);
    _batchState = { data: d, fileMap: fileMap };
  } catch (e) { rc.innerHTML = head('Batch Result') + '<p style="color:var(--danger);margin-top:0.5rem;">' + e.message + '</p>'; }
});

function renderBatch(d, fileMap) {
  const order = ['Fresh', 'Moderately Fresh', 'Rotten'];
  const results = d.results || [];
  const byQ = { 'Fresh': [], 'Moderately Fresh': [], 'Rotten': [] };
  results.forEach(r => { (byQ[r.quality] || (byQ[r.quality] = [])).push(r); });

  let h = head('Batch Prediction Results');
  // Summary bar: e.g. 30 Fresh / 40 Moderate / 30 Rotten
  h += '<div style="display:flex;gap:0.6rem;flex-wrap:wrap;margin-bottom:1.5rem;">';
  order.forEach(q => {
    const cnt = (d.summary && d.summary[q] != null) ? d.summary[q] : byQ[q].length;
    h += '<div style="background:' + qb(q) + ';border:1px solid ' + qc(q) + ';border-radius:14px;padding:0.5rem 1rem;min-width:110px;text-align:center;">'
       + '<div style="font-size:0.72rem;color:var(--muted);">' + q + '</div>'
       + '<div style="font-size:1.3rem;font-weight:900;color:' + qc(q) + ';">' + cnt + '</div></div>';
  });
  h += '</div>';

  // Master "Download All" -> one ZIP with every heatmap PNG + a report.json.
  h += '<div class="d-flex gap-2 mb-3" style="align-items:center;justify-content:space-between;flex-wrap:wrap;">'
    + '<button class="btn btn-success big-dl" style="padding:0.55rem 1.1rem;font-size:0.95rem;font-weight:600;" onclick="downloadAllBatch()">📥 Download All Batch Analysis</button>'
    + '<span style="color:var(--muted);font-size:0.82rem;">' + results.length + ' images - click any thumbnail for full detail</span>'
    + '</div>';

  // Images are SEPARATED into their own section per quality (Fresh / Moderate / Rotten).
  let any = false;
  order.forEach(q => {
    const group = byQ[q] || [];
    if (!group.length) return;
    any = true;
    h += '<div style="margin-bottom:1.7rem;">';
    h += '<div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.7rem;">'
       + '<span style="font-size:1.05rem;font-weight:800;color:' + qc(q) + ';">' + q + ' - ' + group.length + '</span>'
       + '<span style="flex:1;height:2px;background:rgba(255,255,255,0.08);"></span></div>';
    h += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:0.8rem;">';
    group.forEach(r => {
      const rot = r.analysis_stats ? (r.analysis_stats.rotten_pixel_ratio * 100).toFixed(1) : '0.0';
      const thumb = r.image_url ? API + r.image_url : ((fileMap && fileMap[r.filename]) || '');
      const hm = (r.analysis_image || '').startsWith('data:')
        ? r.analysis_image
        : (r.analysis_image ? API + r.analysis_image : null);
      const img = thumb
        ? '<img src="' + thumb + '" alt="' + (r.filename || '') + '" style="width:100%;height:110px;object-fit-cover;border-radius:10px;border:1px solid rgba(255,255,255,0.12);"/>'
        : '<div style="width:100%;height:110px;border:2px dashed rgba(255,255,255,0.12);border-radius:10px;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:0.72rem;">no thumbnail</div>';
      h += '<div' + (thumb ? ' data-image-url="' + thumb + '" data-filename="' + (r.filename || 'batch-image.jpg') + '" title="Click for detailed analysis"' : '') + ' style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:0.55rem;box-sizing:border-box;cursor:pointer;">'
         + img
        + (hm ? '<img src="' + hm + '" alt="heatmap" style="position:absolute;bottom:4px;right:4px;width:48px;height:48px;object-fit-cover;border-radius:8px;border:2px solid rgba(0,245,160,0.6);box-shadow:0 0 6px rgba(0,0,0,0.7);background:#000;"/>' : '')
         + '<div style="margin-top:0.45rem;">'
         + '<div style="font-weight:700;color:' + qc(q) + ';">' + r.quality + '</div>'
         + '<div style="font-size:0.82rem;color:var(--muted);">' + r.confidence + '% confidence</div>'
         + '<div style="font-size:0.72rem;color:' + (parseFloat(rot) > 0 ? 'var(--danger)' : 'var(--muted)') + ';">' + rot + '% rot</div>'
         + '</div></div>';
    });
    h += '</div></div>';
  });
  if (!any) h += '<p style="color:var(--muted);font-size:0.88rem;">No valid images were processed.</p>';
  rc.innerHTML = '<div class="d-flex gap-2 mb-3"><button class="btn btn-sm btn-outline-secondary" onclick="resetUpload()"> ↺ Change selection</button></div>' + h;
}

function resetUpload() {
  _batchState = null;
  ii.value = '';
  pb.style.display = 'none';
  pb.innerHTML = '';
  uz.style.display = 'flex';
  rc.innerHTML = head('Prediction Result') + '<p style="color:var(--muted);font-size:0.88rem;">Your analysis will appear here after uploading an image.</p>';
}

function logout() {
  localStorage.removeItem('token');
  window.location.href = 'login.html';
}

// ---------------------------------------------------------------------------
// Download ALL batch results as one ZIP: every per-image heatmap PNG plus a
// report.json summarising quality / confidence / stats for each image.
function downloadAllBatch() {
  if (!_batchState || !_batchState.data) return alert('No batch results available. Run a batch analysis first.');
  var results = (_batchState.data.results || []).filter(function (r) { return r.analysis_image; });
  if (!results.length) return alert('No heatmaps available for download.');
  if (typeof JSZip === 'undefined') return alert('ZIP library not loaded.');
  var t = localStorage.getItem('token') || '';
  var zip = new JSZip();
  var folder = zip.folder('batch_analysis');
  folder.file('report.json', JSON.stringify({
    summary: _batchState.data.summary || {},
    generated_at: new Date().toISOString(),
    items: results.map(function (r) { return { filename: r.filename, quality: r.quality, confidence: r.confidence, storage_days: r.storage_days, storage_temperature: r.storage_temperature, analysis_stats: r.analysis_stats }; }),
  }, null, 2));
  results.forEach(function (r, i) {
    var url = (r.analysis_image || '').startsWith('data:')
      ? r.analysis_image
      : (API + r.analysis_image);
    var name = (r.filename ? r.filename.replace(/\.[^.]+$/, '') : ('image_' + (i + 1))) + '_heatmap.png';
    if (url.startsWith('data:image/png;base64,')) {
      folder.file(name, atob(url.split(',', 1)[1]));
    } else {
      folder.file(name, fetch(url, { headers: { Authorization: 'Bearer ' + t } }).then(function (resp) { return resp.arrayBuffer(); }));
    }
  });
  zip.generateAsync({ type: 'blob' }).then(function (content) {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(content);
    a.download = 'batch_analysis.zip';
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  }).catch(function (e) { console.error(e); alert('Failed to build batch download: ' + (e && e.message)); });
}

