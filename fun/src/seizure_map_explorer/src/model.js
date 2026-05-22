/* ============================================================
   Faithful Saggio fast-slow seizure model (ported from
   dynamotypes-for-dummies Piecewise.ipynb).

   A seizure path is a chain of great-circle arcs between waypoints on a
   radius-0.4 sphere. Each arc point's (x,y,z) coordinates are the bifurcation
   parameters (mu2, mu1, nu). We integrate the fast subsystem
       xdot = -y
       ydot = x^3 - mu2*x - mu1 - y*(nu + x + x^2)
   with Euler-Maruyama + pink noise as those parameters move along the path.
   Onset/offset signatures emerge wherever the path crosses a bifurcation
   curve — no hand-stitching.
   ============================================================ */

export const SPHERE_R = 0.4;

function norm3(v) { return Math.hypot(v[0], v[1], v[2]); }
function scale3(v, s) { return [v[0] * s, v[1] * s, v[2] * s]; }
function onSphere(p) { const n = norm3(p) || 1e-9; return scale3(p, SPHERE_R / n); }
function cross3(a, b) { return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]; }
function dot3(a, b) { return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]; }

function rotMat(axis, ang) {
  const [ux, uy, uz] = axis, c = Math.cos(ang), s = Math.sin(ang), t = 1 - c;
  return [
    [t*ux*ux+c,    t*ux*uy-s*uz, t*ux*uz+s*uy],
    [t*ux*uy+s*uz, t*uy*uy+c,    t*uy*uz-s*ux],
    [t*ux*uz-s*uy, t*uy*uz+s*ux, t*uz*uz+c],
  ];
}
function matVec(R, v) {
  return [R[0][0]*v[0]+R[0][1]*v[1]+R[0][2]*v[2],
          R[1][0]*v[0]+R[1][1]*v[1]+R[1][2]*v[2],
          R[2][0]*v[0]+R[2][1]*v[1]+R[2][2]*v[2]];
}

/* great-circle arc between two sphere points; returns array of [mu2,mu1,nu] */
export function arcPath(p1, p2, k, tstep) {
  p1 = onSphere(p1); p2 = onSphere(p2);
  const cosang = Math.max(-1, Math.min(1, dot3(p1, p2) / (SPHERE_R * SPHERE_R)));
  const theta = Math.acos(cosang);
  let axis = cross3(p1, p2);
  const an = norm3(axis);
  if (an < 1e-9) return { pts: [p1.slice()], theta: 0 }; // identical/antipodal
  axis = scale3(axis, 1 / an);
  const num = Math.max(2, Math.floor(theta / k / tstep));
  const pts = new Array(num);
  for (let i = 0; i < num; i++) {
    const ang = (i / (num - 1)) * theta;
    pts[i] = matVec(rotMat(axis, ang), p1);
  }
  return { pts, theta };
}

/* pink-ish noise (Voss-McCartney), returns fn -> sample in ~[-1,1] */
export function makePink(seed) {
  let s = (seed >>> 0) || 1;
  const rnd = () => { s = (1664525 * s + 1013904223) >>> 0; return s / 4294967296; };
  const rows = 16, vals = new Array(rows).fill(0); let key = 0, mx = 1;
  return () => {
    key = (key + 1) & ((1 << rows) - 1);
    for (let i = 0; i < rows; i++) if (key & (1 << i)) { vals[i] = rnd() * 2 - 1; break; }
    let sum = 0; for (let i = 0; i < rows; i++) sum += vals[i];
    mx = Math.max(mx, Math.abs(sum));
    return sum / mx;
  };
}

/* Build the parameter sequence for a chain of waypoints, with an optional
   dwell (stall) at a given waypoint index to lengthen the ictal body. */
export function buildPath(waypoints, k, tstep, dwellIdx, dwellSteps) {
  let mu2 = [], mu1 = [], nu = [];
  const segThetas = [];
  for (let i = 0; i < waypoints.length - 1; i++) {
    const { pts, theta } = arcPath(waypoints[i], waypoints[i + 1], k, tstep);
    segThetas.push(theta);
    for (let j = 0; j < pts.length; j++) { mu2.push(pts[j][0]); mu1.push(pts[j][1]); nu.push(pts[j][2]); }
    if (i === dwellIdx && dwellSteps > 0) {
      const last = pts[pts.length - 1];
      for (let d = 0; d < dwellSteps; d++) { mu2.push(last[0]); mu1.push(last[1]); nu.push(last[2]); }
    }
  }
  return { mu2, mu1, nu, segThetas };
}

/* Integrate the fast subsystem along a parameter sequence (Euler-Maruyama). */
export function integrate(path, opts) {
  const { noise = 0.0, seed = 7, sub = 4, tstep = 0.02 } = opts || {};
  const { mu2, mu1, nu } = path;
  const N = mu2.length;
  const x = new Float64Array(N);
  let X = 0.0, Y = 0.0;
  const pinkX = makePink(seed), pinkY = makePink(seed + 1);
  const ditX = makePink(seed + 555), ditY = makePink(seed + 556);
  const h = tstep / sub;
  const sq = Math.sqrt(h) * noise;
  const DITH = Math.sqrt(h) * 0.006;  // small always-on kick so the state leaves unstable foci
  for (let n = 0; n < N; n++) {
    const m2 = mu2[n], m1 = mu1[n], v = nu[n];
    for (let k = 0; k < sub; k++) {
      const xdot = -Y;
      const ydot = X*X*X - m2*X - m1 - Y*(v + X + X*X);
      X += h * xdot + sq * pinkX() + DITH * ditX();
      Y += h * ydot + sq * pinkY() + DITH * ditY();
      if (!Number.isFinite(X) || Math.abs(X) > 50) { X = 0; Y = 0; }
    }
    x[n] = X;
  }
  return x;
}

/* Clean limit-cycle period (raw samples/cycle) at a fixed parameter point.
   Integrates the fast subsystem with dither to settle onto the cycle, then
   uses normalized autocorrelation on the clean tail. Returns Infinity if the
   point is not oscillating (settles to a fixed point). */
/* Integrate the fast subsystem at a FIXED sphere point and report whether it
   settles onto a limit cycle: { period (raw samples/cycle, or Infinity), amp }.
   `amp` is the settled oscillation amplitude — used to decide if a point is
   genuinely ictal (vigorous limit cycle) vs resting/marginal. */
export function probe(p, opts) {
  const { tstep = 0.02, sub = 4, steps = 2600, seed = 11 } = opts || {};
  const m2 = p[0], m1 = p[1], v = p[2];
  let X = 0.2, Y = 0.0;
  const h = tstep / sub, DITH = Math.sqrt(h) * 0.006;
  const dx = makePink(seed), dy = makePink(seed + 1);
  const x = new Float64Array(steps);
  for (let n = 0; n < steps; n++) {
    for (let k = 0; k < sub; k++) {
      const xdot = -Y, ydot = X*X*X - m2*X - m1 - Y*(v + X + X*X);
      X += h * xdot + DITH * dx(); Y += h * ydot + DITH * dy();
      if (!Number.isFinite(X) || Math.abs(X) > 50) { X = 0.2; Y = 0; }
    }
    x[n] = X;
  }
  // use the settled second half
  const a = steps >> 1, m = steps - a;
  let mean = 0; for (let i = a; i < steps; i++) mean += x[i]; mean /= m;
  let amp = 0; for (let i = a; i < steps; i++) amp = Math.max(amp, Math.abs(x[i] - mean));
  if (amp < 0.05) return { period: Infinity, amp }; // not oscillating
  // period = mean interval between upward zero crossings of (x - mean).
  // Consistent with the zero-crossing frequency metric used downstream.
  let prevUp = -1, sum = 0, cnt = 0;
  for (let i = a + 1; i < steps; i++) {
    if (x[i - 1] - mean < 0 && x[i] - mean >= 0) {
      if (prevUp >= 0) { sum += i - prevUp; cnt++; }
      prevUp = i;
    }
  }
  return { period: cnt < 1 ? Infinity : sum / cnt, amp };
}

export function cyclePeriod(p, opts) { return probe(p, opts).period; }

/* moving-average high-pass (AC-coupled EEG) */
export function highpass(x, win) {
  const n = x.length, out = new Float64Array(n), half = win >> 1;
  // prefix sum for speed
  const pre = new Float64Array(n + 1);
  for (let i = 0; i < n; i++) pre[i + 1] = pre[i] + x[i];
  for (let i = 0; i < n; i++) {
    const lo = Math.max(0, i - half), hi = Math.min(n - 1, i + half);
    const mean = (pre[hi + 1] - pre[lo]) / (hi - lo + 1);
    out[i] = x[i] - mean;
  }
  return out;
}

/* Full pipeline: waypoints -> resampled signal at fs, with realism. */
/* Calm interictal baseline (no seizure): drift + measurement noise, no rhythm. */
export function restBaseline(N, fs, drift, noise, seed) {
  const out = new Float64Array(N);
  if (drift > 0) { const pk = makePink(seed + 99); let d = 0; for (let i = 0; i < N; i++) { d = 0.992 * d + 0.08 * pk(); out[i] = drift * 3 * d; } }
  if (noise > 0) { const pk = makePink(seed + 7); for (let i = 0; i < N; i++) out[i] += noise * 1.5 * pk(); }
  return { sig: out, fs, markers: null };
}

/* sliding standard-deviation envelope (O(N) via prefix sums) */
function envelopeStd(x, win) {
  const n = x.length, env = new Float64Array(n), half = win >> 1;
  const p1 = new Float64Array(n + 1), p2 = new Float64Array(n + 1);
  for (let i = 0; i < n; i++) { p1[i + 1] = p1[i] + x[i]; p2[i + 1] = p2[i] + x[i] * x[i]; }
  for (let i = 0; i < n; i++) {
    const lo = Math.max(0, i - half), hi = Math.min(n - 1, i + half), m = hi - lo + 1;
    const mean = (p1[hi + 1] - p1[lo]) / m, ms = (p2[hi + 1] - p2[lo]) / m;
    env[i] = Math.sqrt(Math.max(0, ms - mean * mean));
  }
  return env;
}

/* mean interval (raw samples) between upward zero crossings of (x-mean) over a
   window centred at `c`. Returns 0 if too few crossings. */
function measurePeriod(x, c, halfwin) {
  const lo = Math.max(0, c - halfwin), hi = Math.min(x.length - 1, c + halfwin);
  let mean = 0; for (let i = lo; i <= hi; i++) mean += x[i]; mean /= (hi - lo + 1);
  let prevUp = -1, sum = 0, cnt = 0;
  for (let i = lo + 1; i <= hi; i++) {
    if (x[i - 1] - mean < 0 && x[i] - mean >= 0) { if (prevUp >= 0) { sum += i - prevUp; cnt++; } prevUp = i; }
  }
  return cnt < 1 ? 0 : sum / cnt;
}

const SEIZ_STD = 0.3;   // envelope std threshold separating ictal limit cycle from rest+dither
const DEF_PRAW = 289;   // fallback raw samples/cycle (validated ictal period)

export function simulate(waypoints, opts) {
  const {
    fs = 200, dur = 16, k = 0.02, tstep = 0.02, freq = 10,
    noise = 0.04, drift = 0.05, seed = 7, quiescent = false,
  } = opts || {};

  const N = Math.round(fs * dur);
  if (quiescent) return restBaseline(N, fs, drift, noise, seed);

  // The seizure is HYSTERETIC: away from the ictal core the limit cycle
  // coexists with a stable rest state, so the system only oscillates if it
  // arrives already on the cycle. We therefore integrate CONTINUOUSLY along the
  // arc (carrying state) instead of probing points in isolation.
  const onset = onSphere(waypoints[0]);
  const offset = onSphere(waypoints[waypoints.length - 1]);
  const arc = arcPath(onset, offset, k, tstep).pts;     // [mu2,mu1,nu] ...
  const Aarc = arc.length;
  const settleN = 1200;                                 // burn-in to relax onto rest at onset

  // ---- structural pass: settle at onset, traverse the arc with only the tiny
  //      dither (no user noise) so the envelope is clean. ----
  const s2 = [], s1 = [], sv = [];
  for (let d = 0; d < settleN; d++) { s2.push(onset[0]); s1.push(onset[1]); sv.push(onset[2]); }
  for (let j = 0; j < Aarc; j++) { s2.push(arc[j][0]); s1.push(arc[j][1]); sv.push(arc[j][2]); }
  const xs = integrate({ mu2: s2, mu1: s1, nu: sv }, { noise: 0, seed, tstep });
  const senv = envelopeStd(xs, 400);
  let peak = 0, peakIdx = 0;
  for (let j = 0; j < Aarc; j++) { const e = senv[settleN + j]; if (e > peak) { peak = e; peakIdx = j; } }
  if (peak < SEIZ_STD) return restBaseline(N, fs, drift, noise, seed); // arc never enters a sustained seizure

  // Natural cycle period at the ictal core. Measure it where the PARAMETERS ARE
  // FIXED: carry the state onto the limit cycle along the arc up to the core,
  // then hold params there and time the cycle. This makes the period (and hence
  // the frequency calibration) independent of the sweep speed k.
  const pCore = arc[peakIdx];
  const m2 = [], m1 = [], mv = [], DWELLM = 5000;
  for (let d = 0; d < settleN; d++) { m2.push(onset[0]); m1.push(onset[1]); mv.push(onset[2]); }
  for (let j = 0; j <= peakIdx; j++) { m2.push(arc[j][0]); m1.push(arc[j][1]); mv.push(arc[j][2]); }
  for (let d = 0; d < DWELLM; d++) { m2.push(pCore[0]); m1.push(pCore[1]); mv.push(pCore[2]); }
  const xm = integrate({ mu2: m2, mu1: m1, nu: mv }, { noise: 0, seed, tstep });
  let pRaw = measurePeriod(xm, xm.length - (DWELLM >> 1), (DWELLM >> 1) - 50);
  if (!(pRaw > 0)) pRaw = DEF_PRAW;

  // ---- production pass: re-integrate with a dwell at the ictal core to give
  //      the seizure a realistic duration, plus rest pads, then resample. ----
  const occupancy = 0.72;                               // fraction of the window the event fills
  const ratio = (pRaw * freq) / fs;
  const Mtarget = occupancy * N * ratio;
  const padN = Math.max(600, Math.round(0.13 * Mtarget));
  let dwellN = Math.round(Mtarget - Aarc - 2 * padN);
  dwellN = Math.max(Math.round(3 * pRaw), Math.min(260000, dwellN));

  const mu2 = [], mu1 = [], nu = [];
  const push = (p, m) => { for (let d = 0; d < m; d++) { mu2.push(p[0]); mu1.push(p[1]); nu.push(p[2]); } };
  push(onset, settleN);                                 // discarded burn-in
  push(onset, padN);                                    // preictal rest
  for (let j = 0; j <= peakIdx; j++) { mu2.push(arc[j][0]); mu1.push(arc[j][1]); nu.push(arc[j][2]); }
  push(arc[peakIdx], dwellN);                           // ictal dwell at the core
  for (let j = peakIdx + 1; j < Aarc; j++) { mu2.push(arc[j][0]); mu1.push(arc[j][1]); nu.push(arc[j][2]); }
  push(offset, padN);                                   // postictal rest

  let raw = integrate({ mu2, mu1, nu }, { noise, seed, tstep });
  raw = Array.prototype.slice.call(raw.subarray(settleN));
  const M0 = raw.length;

  // Frequency resample: map the cycle period pRaw -> fs/freq samples/cycle.
  // ratio (raw samples per output sample) was computed above; L = signal at `freq` Hz.
  const L = Math.max(2, Math.round(M0 / ratio));
  const res = new Float64Array(L);
  for (let i = 0; i < L; i++) {
    const u = (i / (L - 1)) * (M0 - 1), a = Math.floor(u), bb = Math.min(M0 - 1, a + 1), f = u - a;
    res[i] = raw[a] * (1 - f) + raw[bb] * f;
  }
  if (opts && opts._dbg) console.error(`[dbg] pRaw=${pRaw.toFixed(0)} M0=${M0} cyc=${(M0/pRaw).toFixed(0)} L=${L} N=${N}`);

  // place into the N=fs*dur window: crop center if longer, pad rest if shorter
  const sig = new Float64Array(N);
  if (L >= N) { const o = Math.floor((L - N) / 2); for (let i = 0; i < N; i++) sig[i] = res[o + i]; }
  else { const o = Math.floor((N - L) / 2);
    for (let i = 0; i < o; i++) sig[i] = res[0];
    for (let i = 0; i < L; i++) sig[o + i] = res[i];
    for (let i = o + L; i < N; i++) sig[i] = res[L - 1]; }

  // high-pass (AC coupling) + normalize ictal amplitude to ~1
  const hp = highpass(sig, Math.max(3, Math.round(fs * 1.2)));
  let amax = 1e-9; for (let i = 0; i < N; i++) amax = Math.max(amax, Math.abs(hp[i]));
  for (let i = 0; i < N; i++) hp[i] /= amax;

  // onset/offset from the CLEAN envelope (before drift/noise, which would
  // otherwise inflate the resting baseline and break detection)
  const env = new Float64Array(N), ew = Math.max(3, Math.round(fs * 0.25));
  { const pre = new Float64Array(N + 1);
    for (let i = 0; i < N; i++) pre[i + 1] = pre[i] + hp[i] * hp[i];
    for (let i = 0; i < N; i++) { const lo = Math.max(0, i - ew), hi = Math.min(N - 1, i + ew); env[i] = Math.sqrt((pre[hi + 1] - pre[lo]) / (hi - lo + 1)); } }
  let emax = 1e-9; for (let i = 0; i < N; i++) emax = Math.max(emax, env[i]);
  const thr = 0.35 * emax;
  let on = 0, off = N - 1;
  for (let i = 0; i < N; i++) { if (env[i] > thr) { on = i; break; } }
  for (let i = N - 1; i >= 0; i--) { if (env[i] > thr) { off = i; break; } }

  // now add baseline drift + pink measurement noise (cosmetic realism)
  if (drift > 0) { const pk = makePink(seed + 99); let d = 0; for (let i = 0; i < N; i++) { d = 0.992 * d + 0.08 * pk(); hp[i] += drift * 3 * d; } }
  if (noise > 0) { const pk = makePink(seed + 7); for (let i = 0; i < N; i++) hp[i] += noise * 1.5 * pk(); }

  return { sig: hp, fs, markers: { onset: on / N, offset: off / N } };
}
