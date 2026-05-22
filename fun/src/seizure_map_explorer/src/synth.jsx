import React, { useState, useMemo, useRef, useEffect } from "react";

/* ============================================================
   SYNTHETIC SEIZURE GENERATOR  (Dynamotypes-for-Dummies, web port — Phase 1)

   Pick an onset bifurcation and an offset bifurcation; the tool integrates the
   corresponding normal-form dynamical systems (RK4) through their bifurcations
   to synthesize a seizure-like signal, then applies clinical-EEG realism:
   pink noise, target rhythmic frequency, and baseline drift. Shows the time
   trace and a synced spectrogram.

   Model fields/descriptors adapted from onset_offset_anim.jsx.
   ============================================================ */

const C = {
  bg: "#0e1014", panel: "#15181f", panel2: "#1b1f29", line: "#2a2f3a",
  ink: "#e9e2cf", inkDim: "#9aa3b2", inkFaint: "#5d6675", trace: "#cfe3ff",
};
const HUE = { SN: "#f49c34", SNIC: "#f4b234", SupH: "#74bf45", SubH: "#3fc197", SH: "#67b3d9", FLC: "#f84495" };

/* ---------- vector fields ---------- */
const fSN = (x, y, p) => {
  const r2 = x * x + y * y, g = 1 / (1 + Math.exp(8 * (x - 1.35)));
  const w = 1.2, c = 0.9, X0 = 2;
  const cx = x - w * y - x * r2, cy = y + w * x - y * r2;
  const rx = y, ry = -c * y - ((x - X0) * (x - X0) - p);
  return [g * cx + (1 - g) * rx, g * cy + (1 - g) * ry];
};
const fSNIC = (x, y, a) => {
  const r = Math.hypot(x, y) || 1e-9, th = Math.atan2(y, x);
  const rd = -2 * (r - 1), thd = a - Math.sin(th);
  return [rd * Math.cos(th) - r * thd * Math.sin(th), rd * Math.sin(th) + r * thd * Math.cos(th)];
};
const fSupH = (x, y, mu) => { const r2 = x * x + y * y; return [mu * x - y - x * r2, mu * y + x - y * r2]; };
const fSubH = (x, y, mu) => { const r2 = x * x + y * y; return [mu * x - y + x * r2 - x * r2 * r2, mu * y + x + y * r2 - y * r2 * r2]; };
const SH_MU2 = 0.326, SH_NU = 0.229, SH_CRIT = 0.033;
const fSH = (x, y, mu1) => [-y, x * x * x - SH_MU2 * x - mu1 - y * (SH_NU + x + x * x)];

/* descriptors: f=field, base ω (rad/model-time, for freq calibration),
   pRest/pOsc = parameter on the rest / oscillating side of the bifurcation,
   init = a state on the oscillating cycle, rest = the resting fixed point.
   sOnset/sOffset map progress in [0,1] across the transition to the parameter. */
const ONSET = {
  SN:   { f: fSN,   w: 1.2, name: "Saddle-Node (DC shift)",
          pRest: 0.30, pOsc: -0.30, init: () => [0, 1], rest: () => [2 + Math.sqrt(0.3), 0] },
  SNIC: { f: fSNIC, w: 1.0, name: "Saddle-Node on Invariant Circle",
          pRest: 0.55, pOsc: 1.30, init: () => [1, 0], rest: () => { const t = Math.asin(0.55); return [Math.cos(t), Math.sin(t)]; } },
  SupH: { f: fSupH, w: 1.0, name: "Supercritical Hopf",
          pRest: -0.30, pOsc: 0.85, init: () => [0.04, 0], rest: () => [0.04, 0] },
  SubH: { f: fSubH, w: 1.0, name: "Subcritical Hopf",
          pRest: -0.12, pOsc: 0.10, init: () => [0.04, 0], rest: () => [0.04, 0] },
};
const OFFSET = {
  SNIC: { f: fSNIC, w: 1.0, name: "Saddle-Node on Invariant Circle",
          pOsc: 1.45, pRest: 0.55, init: () => [1, 0], rest: () => { const t = Math.asin(0.55); return [Math.cos(t), Math.sin(t)]; } },
  SH:   { f: fSH,   w: 0.62, name: "Saddle-Homoclinic",
          pOsc: 0.005, pRest: 0.061, init: () => [-0.51, 0.05], rest: () => [0.646, 0] },
  SupH: { f: fSupH, w: 1.0, name: "Supercritical Hopf",
          pOsc: 0.85, pRest: -0.30, init: () => [Math.sqrt(0.5), 0], rest: () => [0, 0] },
  FLC:  { f: fSubH, w: 1.0, name: "Fold Limit Cycle",
          pOsc: 0.05, pRest: -0.40, init: () => [0.95, 0], rest: () => [0, 0] },
};

/* ---------- RK4 ---------- */
function rk4(f, x, y, p, h) {
  const [a1, b1] = f(x, y, p);
  const [a2, b2] = f(x + 0.5 * h * a1, y + 0.5 * h * b1, p);
  const [a3, b3] = f(x + 0.5 * h * a2, y + 0.5 * h * b2, p);
  const [a4, b4] = f(x + h * a3, y + h * b3, p);
  return [x + (h / 6) * (a1 + 2 * a2 + 2 * a3 + a4), y + (h / 6) * (b1 + 2 * b2 + 2 * b3 + b4)];
}

/* ---------- pink noise (Voss-McCartney) ---------- */
function makePink(seed) {
  let s = seed >>> 0;
  const rand = () => { s = (1664525 * s + 1013904223) >>> 0; return s / 4294967296; };
  const rows = 16, vals = new Array(rows).fill(0);
  let runningMax = 0, key = 0;
  return () => {
    key = (key + 1) & ((1 << rows) - 1);
    for (let i = 0; i < rows; i++) if (key & (1 << i)) { vals[i] = rand() * 2 - 1; break; }
    let sum = 0; for (let i = 0; i < rows; i++) sum += vals[i];
    runningMax = Math.max(runningMax, Math.abs(sum)) || 1;
    return sum / Math.max(runningMax, 1e-6);
  };
}

/* ---------- synthesize a seizure ---------- */
function synthesize(onsetKey, offsetKey, opts) {
  const { fs = 200, dur = 16, freq = 12, noise = 0.15, drift = 0.0, seed = 7 } = opts;
  const N = Math.round(fs * dur);
  const on = ONSET[onsetKey], off = OFFSET[offsetKey];

  // segment fractions of total duration
  const fPre = 0.10, fOn = 0.18, fOff = 0.18, fPost = 0.10;
  const iPre = Math.round(N * fPre);
  const iOnEnd = Math.round(N * (fPre + fOn));
  const iOffStart = Math.round(N * (1 - fPost - fOff));
  const iPost = Math.round(N * (1 - fPost));
  const iMid = Math.round((iOnEnd + iOffStart) / 2);

  // model-time step per output sample, calibrated so the cycle lands near `freq`
  const hOf = (w) => (2 * Math.PI * freq) / (w * fs);
  const SUB = 6;

  // tiny deterministic dither so the state escapes unstable equilibria
  // (needed for hard onsets like SubH/SN where rest sits on a now-unstable point)
  const dith = makePink(seed + 4242);
  const DITH = 0.0015;

  const x = new Float32Array(N);
  // ---- onset half: integrate ONSET system rest -> oscillating, up to iMid
  let st = on.rest();
  for (let i = 0; i < iMid; i++) {
    let prog;
    if (i < iPre) prog = 0;
    else if (i < iOnEnd) prog = (i - iPre) / Math.max(1, iOnEnd - iPre);
    else prog = 1;
    const p = on.pRest + (on.pOsc - on.pRest) * smooth(prog);
    const h = hOf(on.w) / SUB;
    for (let k = 0; k < SUB; k++) {
      st = rk4(on.f, st[0], st[1], p, h);
      st = [st[0] + DITH * dith(), st[1] + DITH * dith()];
    }
    x[i] = st[0];
  }
  // ---- offset half: integrate OFFSET system oscillating -> rest, from iMid
  st = off.init();
  for (let i = iMid; i < N; i++) {
    let prog;
    if (i < iOffStart) prog = 0;
    else if (i < iPost) prog = (i - iOffStart) / Math.max(1, iPost - iOffStart);
    else prog = 1;
    const p = off.pOsc + (off.pRest - off.pOsc) * smooth(prog);
    const h = hOf(off.w) / SUB;
    for (let k = 0; k < SUB; k++) {
      st = rk4(off.f, st[0], st[1], p, h);
      st = [st[0] + DITH * dith(), st[1] + DITH * dith()];
    }
    x[i] = st[0];
  }
  // light 3-tap smoothing right at the seam
  for (let j = -2; j <= 2; j++) {
    const idx = iMid + j; if (idx < 1 || idx >= N - 1) continue;
    x[idx] = (x[idx - 1] + x[idx] + x[idx + 1]) / 3;
  }

  // High-pass like an AC-coupled EEG amplifier: subtract a long moving average.
  // Removes resting DC offsets and renders a saddle-node "DC shift" as the
  // decaying onset transient that clinicians actually see.
  const win = Math.max(3, Math.round(fs * 1.2));
  const base = movingAvg(x, win);
  for (let i = 0; i < N; i++) x[i] -= base[i];

  // normalize ictal amplitude to ~1
  let amax = 1e-6;
  for (let i = iPre; i < iPost; i++) amax = Math.max(amax, Math.abs(x[i]));
  for (let i = 0; i < N; i++) x[i] /= amax;

  // baseline drift (added after the high-pass so it stays visible)
  if (drift > 0) {
    const pink = makePink(seed + 99); let d = 0;
    for (let i = 0; i < N; i++) { d = 0.992 * d + 0.08 * pink(); x[i] += drift * 3 * d; }
  }
  // pink measurement noise
  if (noise > 0) {
    const pink = makePink(seed); for (let i = 0; i < N; i++) x[i] += noise * pink();
  }

  return { sig: x, fs, markers: { onset: iPre / N, offset: iPost / N } };
}
const smooth = (t) => t <= 0 ? 0 : t >= 1 ? 1 : t * t * (3 - 2 * t);
function movingAvg(x, win) {
  const n = x.length, out = new Float32Array(n), half = win >> 1;
  let acc = 0;
  for (let i = 0; i < Math.min(win, n); i++) acc += x[i];
  for (let i = 0; i < n; i++) {
    const lo = Math.max(0, i - half), hi = Math.min(n - 1, i + half);
    // simple (recompute-free) windowed mean via prefix would be faster; n is small
    let s = 0; for (let j = lo; j <= hi; j++) s += x[j];
    out[i] = s / (hi - lo + 1);
  }
  return out;
}

/* ---------- FFT (iterative radix-2) + spectrogram ---------- */
function fft(re, im) {
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; }
  }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = -2 * Math.PI / len, wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < n; i += len) {
      let cr = 1, ci = 0;
      for (let k = 0; k < len / 2; k++) {
        const ur = re[i + k], ui = im[i + k];
        const vr = re[i + k + len / 2] * cr - im[i + k + len / 2] * ci;
        const vi = re[i + k + len / 2] * ci + im[i + k + len / 2] * cr;
        re[i + k] = ur + vr; im[i + k] = ui + vi;
        re[i + k + len / 2] = ur - vr; im[i + k + len / 2] = ui - vi;
        const ncr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = ncr;
      }
    }
  }
}
function spectrogram(sig, fs, win = 256, hop = 48) {
  const frames = [];
  const w = new Float32Array(win);
  for (let i = 0; i < win; i++) w[i] = 0.5 * (1 - Math.cos(2 * Math.PI * i / (win - 1))); // Hann
  for (let s = 0; s + win <= sig.length; s += hop) {
    const re = new Float64Array(win), im = new Float64Array(win);
    for (let i = 0; i < win; i++) re[i] = sig[s + i] * w[i];
    fft(re, im);
    const mag = new Float32Array(win / 2);
    for (let k = 0; k < win / 2; k++) mag[k] = Math.hypot(re[k], im[k]);
    frames.push(mag);
  }
  const nyq = fs / 2;
  return { frames, nbins: win / 2, nyq };
}

/* viridis-ish colormap */
function cmap(t) {
  t = Math.max(0, Math.min(1, t));
  const r = Math.round(255 * Math.min(1, Math.max(0, -0.2 + 2.2 * t - 0.7 * t * t)));
  const g = Math.round(255 * Math.min(1, Math.max(0, 0.1 + 0.9 * t)));
  const b = Math.round(255 * Math.min(1, Math.max(0, 0.5 + 0.6 * t - 1.1 * t * t)));
  return `rgb(${r},${g},${b})`;
}

/* ---------- canvases ---------- */
function TraceCanvas({ sig, fs, markers }) {
  const ref = useRef(null);
  useEffect(() => {
    const cv = ref.current; if (!cv) return;
    const dpr = window.devicePixelRatio || 1;
    const W = cv.clientWidth, H = 150;
    cv.width = W * dpr; cv.height = H * dpr;
    const g = cv.getContext("2d"); g.scale(dpr, dpr);
    g.fillStyle = C.panel; g.fillRect(0, 0, W, H);
    // ictal shading
    if (markers) {
      g.fillStyle = "rgba(103,179,217,0.07)";
      g.fillRect(markers.onset * W, 0, (markers.offset - markers.onset) * W, H);
    }
    // midline
    g.strokeStyle = C.line; g.lineWidth = 1; g.beginPath(); g.moveTo(0, H / 2); g.lineTo(W, H / 2); g.stroke();
    // trace
    g.strokeStyle = C.trace; g.lineWidth = 1; g.beginPath();
    const n = sig.length;
    for (let i = 0; i < n; i++) {
      const px = (i / (n - 1)) * W, py = H / 2 - sig[i] * (H * 0.36);
      i === 0 ? g.moveTo(px, py) : g.lineTo(px, py);
    }
    g.stroke();
    // onset/offset markers
    if (markers) {
      g.strokeStyle = "#e8748b"; g.setLineDash([4, 3]);
      [markers.onset, markers.offset].forEach((m) => { g.beginPath(); g.moveTo(m * W, 0); g.lineTo(m * W, H); g.stroke(); });
      g.setLineDash([]);
    }
  });
  return <canvas ref={ref} style={{ width: "100%", height: 150, display: "block", borderRadius: 8 }} />;
}

function SpectroCanvas({ sig, fs }) {
  const ref = useRef(null);
  useEffect(() => {
    const cv = ref.current; if (!cv) return;
    const { frames, nbins, nyq } = spectrogram(sig, fs);
    const dpr = window.devicePixelRatio || 1;
    const W = cv.clientWidth, H = 150;
    cv.width = W * dpr; cv.height = H * dpr;
    const g = cv.getContext("2d"); g.scale(dpr, dpr);
    g.fillStyle = C.panel; g.fillRect(0, 0, W, H);
    if (!frames.length) return;
    // display only 0..40 Hz
    const fMax = 40, kMax = Math.min(nbins - 1, Math.round((fMax / nyq) * nbins));
    let mx = 1e-9; frames.forEach((f) => { for (let k = 0; k <= kMax; k++) mx = Math.max(mx, f[k]); });
    const fw = W / frames.length;
    for (let t = 0; t < frames.length; t++) {
      for (let k = 0; k <= kMax; k++) {
        const db = 20 * Math.log10((frames[t][k] + 1e-9) / mx); // -inf..0
        const v = Math.max(0, Math.min(1, (db + 45) / 45));
        g.fillStyle = cmap(v);
        const y = H - (k / kMax) * H;
        g.fillRect(t * fw, y - H / kMax, fw + 1, H / kMax + 1);
      }
    }
    // freq gridlines
    g.fillStyle = C.inkDim; g.font = "10px system-ui";
    [10, 20, 30].forEach((f) => { const y = H - (f / fMax) * H; g.fillText(f + " Hz", 3, y - 1); });
  });
  return <canvas ref={ref} style={{ width: "100%", height: 150, display: "block", borderRadius: 8 }} />;
}

/* ---------- UI bits ---------- */
function Slider({ label, value, min, max, step, onChange, fmt }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, color: C.inkDim, marginBottom: 4 }}>
        <span>{label}</span><span style={{ fontFamily: "monospace", color: C.ink }}>{fmt ? fmt(value) : value}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{ width: "100%", accentColor: "#67b3d9" }} />
    </div>
  );
}
function Picker({ label, value, opts, hues, onChange }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ fontSize: 13, color: C.inkDim, marginBottom: 6 }}>{label}</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {opts.map((k) => (
          <button key={k} onClick={() => onChange(k)}
            style={{
              padding: "6px 10px", borderRadius: 8, cursor: "pointer",
              border: `1.5px solid ${value === k ? hues[k] : C.line}`,
              background: value === k ? hues[k] + "22" : C.panel2,
              color: value === k ? C.ink : C.inkDim, fontFamily: "monospace", fontSize: 13,
            }}>{k}</button>
        ))}
      </div>
    </div>
  );
}

function PhaseOneApp() {
  const [onset, setOnset] = useState("SNIC");
  const [offset, setOffset] = useState("SH");
  const [freq, setFreq] = useState(10);
  const [noise, setNoise] = useState(0.12);
  const [drift, setDrift] = useState(0.06);
  const [dur, setDur] = useState(16);
  const [seed, setSeed] = useState(7);

  const out = useMemo(
    () => synthesize(onset, offset, { fs: 200, dur, freq, noise, drift, seed }),
    [onset, offset, freq, noise, drift, dur, seed]
  );

  return (
    <div style={{ fontFamily: "system-ui, -apple-system, sans-serif", color: C.ink, background: C.bg, minHeight: "100vh", padding: "24px 18px" }}>
      <div style={{ maxWidth: 1000, margin: "0 auto" }}>
        <h1 style={{ fontSize: 22, margin: "0 0 4px" }}>Synthetic seizure generator</h1>
        <p style={{ color: C.inkDim, fontSize: 14, margin: "0 0 20px", maxWidth: 720 }}>
          Choose an <b style={{ color: C.ink }}>onset</b> and <b style={{ color: C.ink }}>offset</b> bifurcation. The tool integrates the
          corresponding dynamical systems through their bifurcations and adds clinical-EEG realism (pink noise,
          rhythmic frequency, baseline drift). Onset shapes how the rhythm begins; offset shapes how it ends.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 22, alignItems: "start" }}>
          <div style={{ background: C.panel, border: `1px solid ${C.line}`, borderRadius: 12, padding: 16 }}>
            <Picker label="Onset bifurcation" value={onset} opts={Object.keys(ONSET)} hues={HUE} onChange={setOnset} />
            <Picker label="Offset bifurcation" value={offset} opts={Object.keys(OFFSET)} hues={HUE} onChange={setOffset} />
            <div style={{ height: 1, background: C.line, margin: "10px 0 16px" }} />
            <Slider label="Rhythmic frequency" value={freq} min={2} max={25} step={0.5} onChange={setFreq} fmt={(v) => v.toFixed(1) + " Hz"} />
            <Slider label="Pink noise" value={noise} min={0} max={0.5} step={0.01} onChange={setNoise} fmt={(v) => v.toFixed(2)} />
            <Slider label="Baseline drift" value={drift} min={0} max={0.3} step={0.01} onChange={setDrift} fmt={(v) => v.toFixed(2)} />
            <Slider label="Duration" value={dur} min={8} max={30} step={1} onChange={setDur} fmt={(v) => v + " s"} />
            <button onClick={() => setSeed((s) => s + 1)}
              style={{ width: "100%", marginTop: 4, padding: "9px 0", borderRadius: 8, cursor: "pointer", border: `1px solid ${C.line}`, background: C.panel2, color: C.ink, fontSize: 13 }}>
              ↻ New noise seed
            </button>
          </div>

          <div>
            <div style={{ fontSize: 12, color: C.inkFaint, textTransform: "uppercase", letterSpacing: 1, marginBottom: 6 }}>
              {onset} onset → {offset} offset · {ONSET[onset].name} / {OFFSET[offset].name}
            </div>
            <div style={{ fontSize: 12.5, color: C.inkDim, marginBottom: 4 }}>Simulated EEG (x(t))</div>
            <TraceCanvas sig={out.sig} fs={out.fs} markers={out.markers} />
            <div style={{ fontSize: 12.5, color: C.inkDim, margin: "16px 0 4px" }}>Spectrogram (0–40 Hz)</div>
            <SpectroCanvas sig={out.sig} fs={out.fs} />
            <p style={{ color: C.inkFaint, fontSize: 11.5, marginTop: 10, lineHeight: 1.5 }}>
              Watch the spectrogram for the onset/offset signatures: SNIC ramps frequency up at onset / down at offset;
              SupH ramps amplitude at constant frequency; SH slows logarithmically before stopping; SN/SubH/FLC start or
              stop abruptly. Red dashed lines mark seizure onset and offset. <i>Phase-1 prototype — model fields are
              schematic normal forms, not the full Saggio sphere path.</i>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export { C, HUE, ONSET, OFFSET, synthesize, TraceCanvas, SpectroCanvas, Slider, Picker };
