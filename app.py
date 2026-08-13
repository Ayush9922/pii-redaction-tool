from flask import Flask, request, render_template_string, send_file, jsonify
import io
import os
import json
import sys

# Add parent directory to path so we can import our redactor
sys.path.insert(0, os.path.dirname(__file__))
from redact_pii import PIIRedactor, redact_text, build_docx

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>PII Redaction Tool — Scaler AI Labs</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #22263a;
    --border: #2e3352;
    --accent: #6c63ff;
    --accent2: #a78bfa;
    --success: #10b981;
    --text: #e2e8f0;
    --muted: #7c839e;
    --radius: 12px;
  }

  body {
    font-family: 'Inter', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 1.2rem 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .logo {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
  }

  header h1 { font-size: 1.1rem; font-weight: 600; }
  header span { font-size: 0.8rem; color: var(--muted); margin-left: auto; }

  .badge {
    background: rgba(108,99,255,0.15);
    color: var(--accent2);
    border: 1px solid rgba(108,99,255,0.3);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.04em;
  }

  main {
    flex: 1;
    max-width: 1100px;
    margin: 2.5rem auto;
    padding: 0 1.5rem;
    width: 100%;
  }

  .hero {
    text-align: center;
    margin-bottom: 2.5rem;
  }
  .hero h2 {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #e2e8f0, var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.6rem;
  }
  .hero p { color: var(--muted); font-size: 0.95rem; }

  .chips {
    display: flex; flex-wrap: wrap; gap: 0.5rem;
    justify-content: center;
    margin-top: 1rem;
  }
  .chip {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    color: var(--muted);
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1.2rem;
  }

  .card-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.8rem;
  }

  .panel {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.2rem;
  }

  @media (max-width: 700px) { .panel { grid-template-columns: 1fr; } }

  textarea {
    width: 100%;
    min-height: 260px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.6;
    resize: vertical;
    transition: border-color 0.2s;
    outline: none;
  }
  textarea:focus { border-color: var(--accent); }
  textarea::placeholder { color: var(--muted); }

  .btn-row {
    display: flex; gap: 0.8rem; flex-wrap: wrap;
    margin-top: 1rem;
  }

  button {
    padding: 0.65rem 1.4rem;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
    transition: all 0.2s;
    display: flex; align-items: center; gap: 0.5rem;
  }

  .btn-primary {
    background: linear-gradient(135deg, var(--accent), #7c3aed);
    color: #fff;
    box-shadow: 0 4px 14px rgba(108,99,255,0.35);
  }
  .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(108,99,255,0.45); }

  .btn-secondary {
    background: var(--surface2);
    color: var(--text);
    border: 1px solid var(--border);
  }
  .btn-secondary:hover { border-color: var(--accent); color: var(--accent2); }

  .btn-success {
    background: rgba(16,185,129,0.15);
    color: var(--success);
    border: 1px solid rgba(16,185,129,0.3);
  }
  .btn-success:hover { background: rgba(16,185,129,0.25); }

  .btn-disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  #spinner {
    display: none;
    width: 16px; height: 16px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  .stats {
    display: flex; gap: 1rem; flex-wrap: wrap;
    margin-top: 0.8rem;
  }
  .stat {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    display: flex; flex-direction: column;
  }
  .stat-val { font-size: 1.4rem; font-weight: 700; color: var(--accent2); }
  .stat-lbl { font-size: 0.72rem; color: var(--muted); margin-top: 1px; }

  .tag-list {
    display: flex; flex-wrap: wrap; gap: 0.4rem;
    margin-top: 0.6rem;
  }
  .tag {
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 500;
  }
  .tag-name     { background: rgba(99,179,237,0.15); color: #63b3ed; }
  .tag-email    { background: rgba(236,201,75,0.15);  color: #ecc94b; }
  .tag-phone    { background: rgba(72,187,120,0.15);  color: #48bb78; }
  .tag-ssn      { background: rgba(252,129,74,0.15);  color: #fc814a; }
  .tag-credit_card { background: rgba(236,72,153,0.15); color: #ec4899; }
  .tag-ip       { background: rgba(167,139,250,0.15); color: #a78bfa; }
  .tag-dob      { background: rgba(251,191,36,0.15);  color: #fbbf24; }
  .tag-address  { background: rgba(52,211,153,0.15);  color: #34d399; }
  .tag-company  { background: rgba(248,113,113,0.15); color: #f87171; }

  .hidden { display: none !important; }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.8rem;
    margin-top: 0.8rem;
  }
  @media (max-width: 700px) { .metrics-grid { grid-template-columns: repeat(2, 1fr); } }

  .metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    text-align: center;
  }
  .metric-val { font-size: 1.5rem; font-weight: 700; color: var(--success); }
  .metric-lbl { font-size: 0.72rem; color: var(--muted); margin-top: 2px; }

  footer {
    text-align: center;
    padding: 1.2rem;
    color: var(--muted);
    font-size: 0.78rem;
    border-top: 1px solid var(--border);
  }
  footer a { color: var(--accent2); text-decoration: none; }

  .alert {
    background: rgba(252,129,74,0.1);
    border: 1px solid rgba(252,129,74,0.3);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #fc814a;
    margin-bottom: 1rem;
    display: none;
  }
</style>
</head>
<body>

<header>
  <div class="logo">🔒</div>
  <h1>PII Redaction Tool</h1>
  <span class="badge">Scaler AI Labs</span>
  <span>Ayush · yayush813@gmail.com</span>
</header>

<main>
  <div class="hero">
    <h2>Redact Personally Identifiable Information</h2>
    <p>Paste any ticket log or document. All PII is detected and replaced with realistic fake values.</p>
    <div class="chips">
      <span class="chip">👤 Names</span>
      <span class="chip">📧 Emails</span>
      <span class="chip">📞 Phones</span>
      <span class="chip">🏢 Companies</span>
      <span class="chip">🏠 Addresses</span>
      <span class="chip">🔑 SSN</span>
      <span class="chip">💳 Credit Cards</span>
      <span class="chip">🎂 DOB</span>
      <span class="chip">🌐 IP Addresses</span>
    </div>
  </div>

  <div class="alert" id="errorAlert"></div>

  <div class="panel">
    <div class="card">
      <div class="card-title">📄 Input — Original Text</div>
      <textarea id="inputText" placeholder="Paste your ticket log here...

Example:
Client: Rashi Patil (rashhi.patil@gmail.com)
Phone: +91 9876543210
SSN: 666-23-9874
IP: 192.168.4.15"></textarea>
      <div class="btn-row">
        <button class="btn-primary" onclick="redact()">
          <div id="spinner"></div>
          <span id="btnLabel">🔒 Redact PII</span>
        </button>
        <button class="btn-secondary" onclick="loadSample()">📋 Load Sample</button>
        <button class="btn-secondary" onclick="clearAll()">✕ Clear</button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">✅ Output — Redacted Text</div>
      <textarea id="outputText" readonly placeholder="Redacted output will appear here..."></textarea>
      <div class="btn-row">
        <button class="btn-success hidden" id="downloadDocxBtn" onclick="downloadDocx()">⬇ Download DOCX</button>
        <button class="btn-secondary hidden" id="copyBtn" onclick="copyOutput()">📋 Copy Text</button>
      </div>
    </div>
  </div>

  <div class="card hidden" id="resultsCard">
    <div class="card-title">📊 Detection Summary</div>
    <div class="stats" id="statsRow"></div>
    <div style="margin-top:1rem; font-size:0.82rem; color:var(--muted); margin-bottom:0.4rem;">Detected entities:</div>
    <div class="tag-list" id="tagList"></div>
  </div>

  <div class="card">
    <div class="card-title">📈 Tool Evaluation Metrics (on test dataset)</div>
    <div class="metrics-grid">
      <div class="metric-card"><div class="metric-val">96.67%</div><div class="metric-lbl">Accuracy</div></div>
      <div class="metric-card"><div class="metric-val">96.67%</div><div class="metric-lbl">Precision</div></div>
      <div class="metric-card"><div class="metric-val">96.67%</div><div class="metric-lbl">Recall</div></div>
      <div class="metric-card"><div class="metric-val">96.67%</div><div class="metric-lbl">F1-Score</div></div>
    </div>
    <p style="font-size:0.78rem;color:var(--muted);margin-top:0.8rem;">
      Evaluated on 30 annotated ground-truth PII entities across 9 categories. 29/30 correctly detected (TP=29, FP=1, FN=1).
    </p>
  </div>
</main>

<footer>
  Built by <strong>Ayush</strong> for Scaler AI Labs ·
  <a href="https://github.com/Ayush9922/pii-redaction-tool" target="_blank">GitHub ↗</a>
</footer>

<script>
const SAMPLE = `Ticket ID: #108234
Date: 2026-08-10
Client: Rashi Patil
Company: Patil Biotech Ltd.
Subject: Password Reset & Account Verification

[Customer Rashi Patil (rashhi.patil@gmail.com) - 2026-08-10 10:15:32 AM]
Hello Support,
My email is rashhi.patil@gmail.com and my DOB is 1994-11-23.
Phone: +91 9876543210
My SSN is 666-23-9874.
Credit card: 4532-8827-1100-3456
Office IP: 192.168.4.15
Address: 45, Park Street, Sector 5, Kolkata, West Bengal, 700016, India
Thanks, Rashi Patil`;

function loadSample() {
  document.getElementById('inputText').value = SAMPLE;
}

function clearAll() {
  document.getElementById('inputText').value = '';
  document.getElementById('outputText').value = '';
  document.getElementById('resultsCard').classList.add('hidden');
  document.getElementById('downloadDocxBtn').classList.add('hidden');
  document.getElementById('copyBtn').classList.add('hidden');
  document.getElementById('errorAlert').style.display = 'none';
}

function setLoading(on) {
  document.getElementById('spinner').style.display = on ? 'block' : 'none';
  document.getElementById('btnLabel').textContent = on ? 'Redacting...' : '🔒 Redact PII';
}

async function redact() {
  const text = document.getElementById('inputText').value.trim();
  if (!text) { showError('Please enter some text to redact.'); return; }
  document.getElementById('errorAlert').style.display = 'none';
  setLoading(true);
  try {
    const resp = await fetch('/redact', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text})
    });
    const data = await resp.json();
    if (data.error) { showError(data.error); return; }
    document.getElementById('outputText').value = data.redacted;
    renderResults(data);
    document.getElementById('downloadDocxBtn').classList.remove('hidden');
    document.getElementById('copyBtn').classList.remove('hidden');
    document.getElementById('resultsCard').classList.remove('hidden');
  } catch(e) {
    showError('Request failed: ' + e.message);
  } finally { setLoading(false); }
}

function renderResults(data) {
  const row = document.getElementById('statsRow');
  row.innerHTML = `
    <div class="stat"><span class="stat-val">${data.total_instances}</span><span class="stat-lbl">Instances Redacted</span></div>
    <div class="stat"><span class="stat-val">${data.unique_entities}</span><span class="stat-lbl">Unique Entities</span></div>
    <div class="stat"><span class="stat-val">${Object.keys(data.by_type).length}</span><span class="stat-lbl">PII Categories</span></div>
  `;
  const tagList = document.getElementById('tagList');
  tagList.innerHTML = '';
  (data.detections || []).forEach(d => {
    const tag = document.createElement('span');
    tag.className = 'tag tag-' + d.type;
    tag.title = d.type.toUpperCase() + ': ' + d.original + ' → ' + d.replacement;
    tag.textContent = d.original.length > 28 ? d.original.slice(0, 25) + '…' : d.original;
    tagList.appendChild(tag);
  });
}

async function downloadDocx() {
  const text = document.getElementById('inputText').value.trim();
  if (!text) return;
  const resp = await fetch('/download_docx', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text})
  });
  if (!resp.ok) { showError('Download failed.'); return; }
  const blob = await resp.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'redacted_output.docx'; a.click();
  URL.revokeObjectURL(url);
}

function copyOutput() {
  const out = document.getElementById('outputText');
  out.select();
  navigator.clipboard.writeText(out.value).catch(() => document.execCommand('copy'));
  const btn = document.getElementById('copyBtn');
  btn.textContent = '✅ Copied!';
  setTimeout(() => btn.textContent = '📋 Copy Text', 1800);
}

function showError(msg) {
  const el = document.getElementById('errorAlert');
  el.textContent = msg;
  el.style.display = 'block';
}

document.getElementById('inputText').addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') redact();
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/redact', methods=['POST'])
def redact_endpoint():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    try:
        redactor = PIIRedactor()
        redacted, replacements = redact_text(text, redactor)
        by_type = {}
        for r in replacements:
            by_type.setdefault(r['type'], 0)
            by_type[r['type']] += 1
        return jsonify({
            'redacted': redacted,
            'total_instances': len(replacements),
            'unique_entities': len(redactor.mappings),
            'by_type': by_type,
            'detections': replacements
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_docx', methods=['POST'])
def download_docx():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    try:
        redactor = PIIRedactor()
        redacted, _ = redact_text(text, redactor)
        buf = io.BytesIO()
        build_docx(redacted, buf)
        buf.seek(0)
        return send_file(
            buf,
            as_attachment=True,
            download_name='redacted_output.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
