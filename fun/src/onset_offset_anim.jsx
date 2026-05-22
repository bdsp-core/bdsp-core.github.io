import React, { useRef, useState, useEffect } from "react";

/* ============================================================
   SEIZURE BIFURCATIONS — animated phase portraits + time series
   for the Saggio-Jirsa onsets and offsets.

   ONSET  (4): SN, SNIC, SupH, SubH   — canonical normal forms.
   OFFSET (4): SNIC, SH, SupH, FLC.
     SNIC/SupH = onset normal forms swept the other way.
     FLC = fold of cycles in the subH normal form (mu through -1/4).
     SH  = the REAL Saggio fast subsystem  x'=-y, y'=x^3-mu2 x-mu1-y(nu+x+x^2)
           evaluated at the saddle-homoclinic curve coordinates published
           by the Stacey lab (curves.mat -> SHl): mu2=0.326, nu=0.229,
           homoclinic at mu1~=0.033. Verified: period diverges (log slowing)
           then the cycle hits the saddle and the state drops to the stable
           focus at x~=0.65 (a DC shift).
   Trajectories are precomputed once, so you can watch the sweep play or drag
   the handle to scrub p(t) continuously along t. A flow swarm option seeds
   uniform tracers that follow the field.
   ============================================================ */

const C = {
  bg: "#0e1014", panel: "#15181f", panel2: "#1b1f29", line: "#2a2f3a",
  ink: "#e9e2cf", inkDim: "#9aa3b2", inkFaint: "#5d6675",
  amber: "#e7d2a3", grid: "#1c212c", field: "rgba(150,162,184,0.22)",
  stable: "#7ad19a", saddle: "#e7c34a", unstable: "#e8748b", cycle: "#67b3d9",
  hl: "#fbf3df",
};

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
// real Saggio fast subsystem with mu2, nu fixed at the SHl curve point; param = mu1
const SH_MU2 = 0.326, SH_NU = 0.229, SH_CRIT = 0.033;
const fSH = (x, y, mu1) => [-y, x * x * x - SH_MU2 * x - mu1 - y * (SH_NU + x + x * x)];

// real roots of depressed cubic t^3 + p t + q = 0
function depressedCubic(p, q) {
  const disc = (q * q) / 4 + (p * p * p) / 27, out = [];
  if (disc > 0) {
    const u = Math.cbrt(-q / 2 + Math.sqrt(disc)), v = Math.cbrt(-q / 2 - Math.sqrt(disc));
    out.push(u + v);
  } else {
    const r = Math.sqrt(-(p * p * p) / 27);
    const phi = Math.acos(Math.max(-1, Math.min(1, (-q / 2) / r)));
    const m = 2 * Math.sqrt(-p / 3);
    out.push(m * Math.cos(phi / 3), m * Math.cos((phi + 2 * Math.PI) / 3), m * Math.cos((phi + 4 * Math.PI) / 3));
  }
  return out;
}
function fpsSH(mu1) {
  return depressedCubic(-SH_MU2, -mu1).map((x) => {
    const detJ = 3 * x * x - SH_MU2, tr = -(SH_NU + x + x * x);
    const t = detJ < 0 ? "saddle" : (tr < 0 ? "stable" : "unstable");
    return { x, y: 0, t };
  });
}

const subHCycles = (mu, on) => {
  const d = 1 + 4 * mu, out = [];
  if (mu > -0.25) out.push({ cx: 0, cy: 0, r: Math.sqrt((1 + Math.sqrt(d)) / 2), stable: true, on });
  if (mu > -0.25 && mu < 0) out.push({ cx: 0, cy: 0, r: Math.sqrt(Math.max((1 - Math.sqrt(d)) / 2, 0)), stable: false, on });
  return out;
};

/* ---------- system descriptors ---------- */
const ONSET = {
  SN: {
    abbr: "SN", name: "Saddle-Node", sym: "p", hue: "#f49c34", dash: false, crit: 0,
    tell: "Node & saddle annihilate; the state drops onto a waiting cycle — the baseline jumps (DC shift) and oscillation starts at full, steady amplitude & frequency.",
    f: fSN, view: { x0: -1.7, x1: 2.9, y0: -1.8, y1: 1.8 },
    pOf: (s) => (0.5 - s) * 0.6, osc: (p) => p < 0,
    fps(p) { const a = [{ x: 0, y: 0, t: "unstable" }]; if (p > 0) { const r = Math.sqrt(p); a.push({ x: 2 - r, y: 0, t: "saddle" }, { x: 2 + r, y: 0, t: "stable" }); } return a; },
    cycles: () => [{ cx: 0, cy: 0, r: 1, stable: true, on: true }],
    init: () => [2 + Math.sqrt(0.3), 0], rest: (p) => [2 + Math.sqrt(Math.max(p, 1e-4)), 0],
  },
  SNIC: {
    abbr: "SNIC", name: "Saddle-Node / Invariant Circle", sym: "a", hue: "#f4b234", dash: true, crit: 1,
    tell: "Node & saddle sit ON the circle and annihilate; flow must circulate — the period is infinite at onset then shortens, so spikes accelerate.",
    f: fSNIC, view: { x0: -1.5, x1: 1.5, y0: -1.5, y1: 1.5 },
    pOf: (s) => 1 + (s - 0.5) * 1.1, osc: (p) => p >= 1,
    fps(a) { if (a >= 1) return []; const t1 = Math.asin(a), t2 = Math.PI - Math.asin(a); return [{ x: Math.cos(t1), y: Math.sin(t1), t: "stable" }, { x: Math.cos(t2), y: Math.sin(t2), t: "saddle" }]; },
    cycles: (a) => [{ cx: 0, cy: 0, r: 1, stable: true, on: a >= 1, ring: true }],
    init: () => { const t = Math.asin(0.45); return [Math.cos(t), Math.sin(t)]; },
    rest: (a) => { const t = Math.asin(Math.min(0.999, Math.max(a, -0.999))); return [Math.cos(t), Math.sin(t)]; },
  },
  SupH: {
    abbr: "SupH", name: "Supercritical Hopf", sym: "μ", hue: "#74bf45", dash: false, crit: 0,
    tell: "The resting spiral loses stability and a cycle is born with zero radius, growing smoothly — oscillations swell from nothing.",
    f: fSupH, view: { x0: -1.5, x1: 1.5, y0: -1.5, y1: 1.5 },
    pOf: (s) => (s - 0.5) * 1.0, osc: (p) => p > 0,
    fps: (mu) => [{ x: 0, y: 0, t: mu < 0 ? "stable" : "unstable" }],
    cycles: (mu) => (mu > 0 ? [{ cx: 0, cy: 0, r: Math.sqrt(mu), stable: true, on: true }] : []),
    init: () => [0.04, 0], rest: () => [0.04, 0],
  },
  SubH: {
    abbr: "SubH", name: "Subcritical Hopf", sym: "μ", hue: "#3fc197", dash: true, crit: 0,
    tell: "A small unstable cycle shrinks onto the rest point and destabilizes it; the state is thrown out to a large cycle — abrupt, full-amplitude onset.",
    f: fSubH, view: { x0: -1.6, x1: 1.6, y0: -1.6, y1: 1.6 },
    pOf: (s) => (s - 0.5) * 0.36, osc: (p) => p > 0,
    fps: (mu) => [{ x: 0, y: 0, t: mu < 0 ? "stable" : "unstable" }],
    cycles: (mu) => subHCycles(mu, true),
    init: () => [0.04, 0], rest: () => [0.04, 0],
  },
};

const OFFSET = {
  SNIC: {
    abbr: "SNIC", name: "Saddle-Node / Invariant Circle", sym: "a", hue: "#f4b234", dash: true, crit: 1,
    tell: "Node & saddle reappear on the circle and capture the flow; the period diverges first, so spikes slow down — then stop.",
    f: fSNIC, view: { x0: -1.5, x1: 1.5, y0: -1.5, y1: 1.5 },
    pOf: (s) => 1.45 - s * 0.9, osc: (p) => p >= 1,
    fps(a) { if (a >= 1) return []; const t1 = Math.asin(a), t2 = Math.PI - Math.asin(a); return [{ x: Math.cos(t1), y: Math.sin(t1), t: "stable" }, { x: Math.cos(t2), y: Math.sin(t2), t: "saddle" }]; },
    cycles: (a) => [{ cx: 0, cy: 0, r: 1, stable: true, on: a >= 1, ring: true }],
    init: () => [1, 0], rest: (a) => { const t = Math.asin(Math.min(0.999, Math.max(a, -0.999))); return [Math.cos(t), Math.sin(t)]; },
  },
  SH: {
    abbr: "SH", name: "Saddle-Homoclinic", sym: "μ₁", hue: "#67b3d9", dash: false, crit: SH_CRIT,
    tell: "The cycle swells until it collides with the saddle, forming a homoclinic loop; the period diverges (log slowing), then the state drops to a distant rest point — a DC shift. (Real Saggio fast subsystem at the published SH-curve point.)",
    f: fSH, view: { x0: -0.95, x1: 0.85, y0: -0.5, y1: 0.5 },
    pOf: (s) => 0.005 + s * 0.056, osc: (p) => p < SH_CRIT,
    fps: (mu1) => fpsSH(mu1),
    cycles: () => [],
    init: () => [-0.51, 0.05], rest: () => [0.646, 0],
  },
  SupH: {
    abbr: "SupH", name: "Supercritical Hopf", sym: "μ", hue: "#74bf45", dash: false, crit: 0,
    tell: "The stable cycle shrinks smoothly back into the re-stabilizing focus; amplitude decays to zero at constant frequency, then silence.",
    f: fSupH, view: { x0: -1.5, x1: 1.5, y0: -1.5, y1: 1.5 },
    pOf: (s) => 0.5 - s * 1.0, osc: (p) => p > 0,
    fps: (mu) => [{ x: 0, y: 0, t: mu < 0 ? "stable" : "unstable" }],
    cycles: (mu) => (mu > 0 ? [{ cx: 0, cy: 0, r: Math.sqrt(mu), stable: true, on: true }] : []),
    init: () => [Math.sqrt(0.5), 0], rest: () => [0.0, 0],
  },
  FLC: {
    abbr: "FLC", name: "Fold Limit Cycle", sym: "μ", hue: "#f84495", dash: false, crit: -0.25,
    tell: "The stable cycle meets the shrinking unstable cycle and they annihilate; oscillation stops dead at full amplitude — no slowing, no shrinking beforehand.",
    f: fSubH, view: { x0: -1.6, x1: 1.6, y0: -1.6, y1: 1.6 },
    pOf: (s) => -0.05 - s * 0.4, osc: (p) => p > -0.25,
    fps: (mu) => [{ x: 0, y: 0, t: mu < 0 ? "stable" : "unstable" }],
    cycles: (mu) => subHCycles(mu, mu > -0.25),
    init: () => [0.95, 0], rest: () => [0.0, 0],
  },
};

const PHASES = {
  onset: { dict: ONSET, keys: ["SN", "SNIC", "SupH", "SubH"], mark: "onset" },
  offset: { dict: OFFSET, keys: ["SNIC", "SH", "SupH", "FLC"], mark: "offset" },
};

const rk4 = (f, x, y, p, h) => {
  const [a1, b1] = f(x, y, p);
  const [a2, b2] = f(x + h / 2 * a1, y + h / 2 * b1, p);
  const [a3, b3] = f(x + h / 2 * a2, y + h / 2 * b2, p);
  const [a4, b4] = f(x + h * a3, y + h * b3, p);
  return [x + h / 6 * (a1 + 2 * a2 + 2 * a3 + a4), y + h / 6 * (b1 + 2 * b2 + 2 * b3 + b4)];
};

const N = 900, STEPS = 22, H = 0.02, NOISE = 0.0022, TRAIL = 90;

function precompute(dict, keys) {
  const out = {};
  for (const k of keys) {
    const sys = dict[k];
    let [x, y] = sys.init();
    const xs = new Float64Array(N), ys = new Float64Array(N);
    let mark = -1, prevP = sys.pOf(0);
    for (let i = 0; i < N; i++) {
      xs[i] = x; ys[i] = y;
      const s = i / (N - 1), p = sys.pOf(s);
      if (i > 1 && mark < 0 && (prevP - sys.crit) * (p - sys.crit) <= 0) mark = i;
      prevP = p;
      for (let st = 0; st < STEPS; st++) {
        let [nx, ny] = rk4(sys.f, x, y, p, H);
        nx += (Math.random() - 0.5) * NOISE; ny += (Math.random() - 0.5) * NOISE;
        if (!isFinite(nx) || Math.hypot(nx, ny) > 60) { const r = sys.rest(p); nx = r[0]; ny = r[1]; }
        x = nx; y = ny;
      }
    }
    out[k] = { xs, ys, mark };
  }
  return out;
}

/* ---------- tracer swarm ---------- */
const BATCH_COLORS = ["#6fb1e0", "#e0883f", "#7ad19a", "#c98ad6", "#e0c44a"];
const SWARM_LIFE = 80, SWARM_STAGGER = 14, SWARM_COUNT = 220;
function seedUniform(sys, n = SWARM_COUNT) {
  const v = sys.view, pts = [];
  for (let i = 0; i < n; i++) pts.push([v.x0 + Math.random() * (v.x1 - v.x0), v.y0 + Math.random() * (v.y1 - v.y0)]);
  return pts;
}

/* ============================================================ */
export default function App() {
  const [phase, setPhase] = useState("onset");
  const [view, setView] = useState("all");
  const [playing, setPlaying] = useState(true);
  const [speed, setSpeed] = useState(1);
  const [swarm, setSwarm] = useState(false);

  const canvases = useRef({});
  const traj = useRef({});            // phase -> trajectories
  const prog = useRef(0);
  const playRef = useRef(true);
  const dsRef = useRef(0.0012);
  const dragRef = useRef(false);
  const swarmRef = useRef(false);
  const swarmState = useRef({});
  const barRef = useRef(null);
  const knobRef = useRef(null);
  const trackRef = useRef(null);
  const phaseRef = useRef("onset");
  const activeRef = useRef(PHASES.onset.keys);

  useEffect(() => { playRef.current = playing; }, [playing]);
  useEffect(() => { dsRef.current = 0.0012 * speed; }, [speed]);
  useEffect(() => { swarmRef.current = swarm; }, [swarm]);

  const dict = PHASES[phase].dict, keys = PHASES[phase].keys, markName = PHASES[phase].mark;

  // reset view to "all" when switching phase (keys differ)
  useEffect(() => { setView("all"); }, [phase]);

  useEffect(() => {
    phaseRef.current = phase;
    if (!traj.current[phase]) traj.current[phase] = precompute(dict, keys);
    activeRef.current = view === "all" ? keys : [view];
    swarmState.current = {};
    for (const k of keys) swarmState.current[k] = { particles: [], flow: 0, nextBatch: 0, lastBirth: -1e9 };
    let raf;
    const loop = () => {
      if (playRef.current && !dragRef.current && prog.current < 1) prog.current = Math.min(1, prog.current + dsRef.current);
      const idx = Math.round(prog.current * (N - 1));
      const TJ = traj.current[phaseRef.current];

      if (swarmRef.current) {
        const advancing = playRef.current && !dragRef.current;
        const spd = dsRef.current / 0.0012;
        for (const k of activeRef.current) {
          const sw = swarmState.current[k], sys = dict[k], p = sys.pOf(idx / (N - 1));
          if (advancing) {
            sw.flow += spd;
            if (sw.flow - sw.lastBirth >= SWARM_STAGGER) {
              const col = BATCH_COLORS[sw.nextBatch % BATCH_COLORS.length];
              for (const [sx, sy] of seedUniform(sys)) sw.particles.push({ x: sx, y: sy, age: 0, col });
              sw.nextBatch++; sw.lastBirth = sw.flow;
            }
            const h = 0.02 * spd; const next = [];
            for (const pt of sw.particles) {
              let { x, y } = pt;
              for (let s = 0; s < 5; s++) { const [nx, ny] = rk4(sys.f, x, y, p, h); x = nx; y = ny; }
              pt.x = x; pt.y = y; pt.age += spd;
              if (pt.age < SWARM_LIFE && isFinite(x) && Math.hypot(x, y) < 60) next.push(pt);
            }
            sw.particles = next;
          }
        }
      }

      for (const k of activeRef.current) {
        drawPhase(canvases.current[k + "-ph"], dict[k], TJ[k], idx, view !== "all", swarmRef.current ? swarmState.current[k] : null);
        drawTS(canvases.current[k + "-ts"], dict[k], TJ[k], idx, view !== "all", markName);
      }
      if (barRef.current) barRef.current.style.width = (prog.current * 100).toFixed(2) + "%";
      if (knobRef.current) knobRef.current.style.left = (prog.current * 100).toFixed(2) + "%";
      if (prog.current >= 1 && playRef.current) { playRef.current = false; setPlaying(false); }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
  }, [view, phase]);

  const restart = () => { prog.current = 0; playRef.current = true; setPlaying(true); };
  const togglePlay = () => { if (prog.current >= 1) prog.current = 0; setPlaying((p) => !p); };
  const posFromEvent = (e) => { const r = trackRef.current.getBoundingClientRect(); return Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)); };
  const onDown = (e) => { dragRef.current = true; try { e.currentTarget.setPointerCapture(e.pointerId); } catch (_) {} playRef.current = false; setPlaying(false); prog.current = posFromEvent(e); };
  const onMove = (e) => { if (dragRef.current) prog.current = posFromEvent(e); };
  const onUp = () => { dragRef.current = false; };
  const burst = () => {
    const sw0 = swarmState.current; if (!sw0) return;
    for (const k of keys) { const sw = sw0[k]; if (!sw) continue; const col = BATCH_COLORS[sw.nextBatch % BATCH_COLORS.length]; for (const [sx, sy] of seedUniform(dict[k], 420)) sw.particles.push({ x: sx, y: sy, age: 0, col }); sw.nextBatch++; }
    if (!swarmRef.current) setSwarm(true);
  };

  const panels = view === "all" ? keys : [view];

  return (
    <div style={{ background: C.bg, minHeight: "100%", color: C.ink, fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
        * { box-sizing: border-box; }
        .oa-btn{transition:all .14s ease;cursor:pointer}
        .oa-btn:hover{transform:translateY(-1px)}
        .oa-tab{transition:all .12s ease;cursor:pointer}
        canvas{width:100%;height:auto;display:block;border-radius:8px}
      `}</style>

      <div style={{ maxWidth: 980, margin: "0 auto", padding: "28px 18px 56px" }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
          <h1 style={{ fontFamily: "'Fraunces', serif", fontWeight: 600, fontSize: 34, margin: 0, letterSpacing: "-0.02em" }}>
            Seizure bifurcations
          </h1>
          <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: C.inkFaint, border: `1px solid ${C.line}`, borderRadius: 20, padding: "3px 10px" }}>
            phase portrait + time series
          </span>
        </div>
        <p style={{ color: C.inkDim, fontSize: 14, lineHeight: 1.55, margin: "8px 0 16px" }}>
          Watch the sweep play, or grab the handle and drag to scrub the state p(t) = (x(t), y(t)) continuously along t.
          The bright marker is p(t); its dashed drop-line shows the x-coordinate on the voltage axis — the value at the
          leading edge of x(t). Each panel bifurcates at the midpoint of the sweep (the trace's {markName} line).
        </p>

        {/* phase toggle */}
        <div style={{ display: "inline-flex", gap: 0, marginBottom: 14, border: `1px solid ${C.line}`, borderRadius: 10, overflow: "hidden" }}>
          {[["onset", "Onset (seizure starts)"], ["offset", "Offset (seizure ends)"]].map(([v, lab]) => {
            const on = phase === v;
            return (
              <div key={v} className="oa-tab" onClick={() => setPhase(v)} style={{
                padding: "9px 16px", fontSize: 14, fontWeight: 600,
                background: on ? C.ink : "transparent", color: on ? C.bg : C.inkDim,
              }}>{lab}</div>
            );
          })}
        </div>

        {/* sub-tabs */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12 }}>
          {[["all", "All four"], ...keys.map((k) => [k, dict[k].abbr])].map(([v, lab]) => {
            const on = view === v, hue = v === "all" ? C.ink : dict[v].hue;
            return (
              <div key={v} className="oa-tab" onClick={() => setView(v)} style={{
                padding: "8px 14px", borderRadius: 9, fontSize: 14, fontWeight: 500,
                fontFamily: v === "all" ? "'IBM Plex Sans',sans-serif" : "'IBM Plex Mono',monospace",
                border: `1px solid ${on ? hue : C.line}`, background: on ? hue : "transparent", color: on ? C.bg : C.inkDim,
              }}>{lab}</div>
            );
          })}
        </div>

        {/* controls */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6, flexWrap: "wrap" }}>
          <button className="oa-btn" onClick={togglePlay} style={ctrlBtn}>{playing ? "❚❚ Pause" : "▶ Play"}</button>
          <button className="oa-btn" onClick={restart} style={ghostBtn}>↺ Restart</button>
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            {[[0.1, "0.1×"], [0.25, "0.25×"], [0.5, "0.5×"], [1, "1×"], [2, "2×"]].map(([v, l]) => (
              <div key={l} className="oa-tab" onClick={() => setSpeed(v)} style={{
                padding: "6px 11px", borderRadius: 7, fontSize: 12.5, fontFamily: "'IBM Plex Mono',monospace",
                border: `1px solid ${speed === v ? C.ink : C.line}`, background: speed === v ? C.ink : "transparent",
                color: speed === v ? C.bg : C.inkDim, cursor: "pointer",
              }}>{l}</div>
            ))}
          </div>
          <div style={{ flex: 1, minWidth: 200 }}>
            <div ref={trackRef} onPointerDown={onDown} onPointerMove={onMove} onPointerUp={onUp} onPointerLeave={onUp}
              style={{ position: "relative", height: 26, display: "flex", alignItems: "center", cursor: "pointer", touchAction: "none" }}>
              <div style={{ position: "relative", width: "100%", height: 6, background: C.panel2, borderRadius: 6 }}>
                <div style={{ position: "absolute", left: "50%", top: -5, width: 1, height: 16, background: C.inkFaint }} />
                <div ref={barRef} style={{ height: "100%", width: "0%", background: C.amber, borderRadius: 6 }} />
                <div ref={knobRef} style={{ position: "absolute", left: "0%", top: "50%", width: 16, height: 16, marginLeft: -8, marginTop: -8, borderRadius: "50%", background: C.hl, border: `2px solid ${C.bg}`, boxShadow: "0 0 7px rgba(251,243,223,0.7)" }} />
              </div>
            </div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
          <button className="oa-btn" onClick={() => setSwarm((s) => !s)} style={{ ...(swarm ? ctrlBtn : ghostBtn), display: "inline-flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 13 }}>✦</span>{swarm ? "Flow swarm: on" : "Flow swarm: off"}
          </button>
          <button className="oa-btn" onClick={burst} style={{ ...ghostBtn, display: "inline-flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 13 }}>⦿</span>Release sheet
          </button>
          <span style={{ fontFamily: "'IBM Plex Mono',monospace", fontSize: 11.5, color: C.inkFaint, lineHeight: 1.4 }}>
            {swarm ? "uniform-random points fill the square each birth; bright = freshly seeded, dim = settled onto an attractor" : "show many tracer points flowing along the field, not just p(t)"}
          </span>
          <span style={{ flex: 1 }} />
          <span style={{ fontFamily: "'IBM Plex Mono',monospace", fontSize: 11, color: C.inkFaint }}>drag the ◍ handle to move p(t) · midline = {markName}</span>
        </div>

        {/* panels */}
        <div style={{ display: "grid", gridTemplateColumns: view === "all" ? "1fr 1fr" : "1fr", gap: 14 }}>
          {panels.map((k) => {
            const sys = dict[k];
            return (
              <div key={k} style={{ background: C.panel, border: `1px solid ${C.line}`, borderRadius: 14, padding: 14 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 9, marginBottom: 10 }}>
                  <span style={{ width: 22, borderTop: `3px ${sys.dash ? "dashed" : "solid"} ${sys.hue}`, borderRadius: 2 }} />
                  <span style={{ fontFamily: "'IBM Plex Mono',monospace", fontWeight: 600, fontSize: 15 }}>{sys.abbr}</span>
                  <span style={{ color: C.inkDim, fontSize: 13 }}>{sys.name}</span>
                </div>
                <canvas ref={(el) => (canvases.current[k + "-ph"] = el)} width={view === "all" ? 380 : 640} height={view === "all" ? 300 : 460} />
                <div style={{ height: 8 }} />
                <canvas ref={(el) => (canvases.current[k + "-ts"] = el)} width={view === "all" ? 380 : 640} height={view === "all" ? 110 : 150} />
                <p style={{ color: C.inkDim, fontSize: 12.5, lineHeight: 1.5, margin: "10px 0 0" }}>{sys.tell}</p>
              </div>
            );
          })}
        </div>

        {/* legend */}
        <div style={{ display: "flex", gap: 18, flexWrap: "wrap", marginTop: 16, fontFamily: "'IBM Plex Mono',monospace", fontSize: 12, color: C.inkDim }}>
          <Leg c={C.stable} label="stable fixed pt" fill />
          <Leg c={C.saddle} label="saddle" cross />
          <Leg c={C.unstable} label="unstable fixed pt" />
          <Leg c={C.cycle} label="stable limit cycle" line />
          <Leg c={C.unstable} label="unstable cycle" dash />
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><span style={{ width: 16, borderTop: `2px solid ${C.amber}` }} /> trajectory</span>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}><span style={{ width: 10, height: 10, borderRadius: 10, border: `2px solid ${C.hl}`, display: "inline-block" }} /> p(t) = (x, y)</span>
        </div>
        <p style={{ color: C.inkFaint, fontSize: 12, lineHeight: 1.5, marginTop: 12 }}>
          Onset SN/SNIC/SupH/SubH and offset SNIC/SupH/FLC are canonical normal forms (FLC is the fold of cycles in the
          subcritical-Hopf form). The offset <b style={{ color: C.inkDim }}>Saddle-Homoclinic</b> panel integrates the real
          Saggio–Jirsa cubic fast subsystem at the published SH bifurcation-curve coordinates (Stacey lab
          “Dynamotypes-for-Dummies” <span style={{ fontFamily: "'IBM Plex Mono',monospace" }}>curves.mat → SHl</span>):
          μ₂=0.326, ν=0.229, homoclinic at μ₁≈0.033. Select a single tab for the vector field and labeled equilibria.
        </p>
      </div>
    </div>
  );
}

const ctrlBtn = { background: C.ink, color: C.bg, border: "none", borderRadius: 9, padding: "9px 18px", fontSize: 14, fontWeight: 600, fontFamily: "'IBM Plex Sans',sans-serif" };
const ghostBtn = { background: "transparent", color: C.ink, border: `1px solid ${C.line}`, borderRadius: 9, padding: "9px 16px", fontSize: 14, fontWeight: 500, fontFamily: "'IBM Plex Sans',sans-serif" };

function Leg({ c, label, fill, cross, line, dash }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      {line || dash ? <span style={{ width: 16, borderTop: `2px ${dash ? "dashed" : "solid"} ${c}` }} />
        : cross ? <span style={{ color: c, fontWeight: 700, fontSize: 13, lineHeight: 1 }}>×</span>
        : <span style={{ width: 9, height: 9, borderRadius: 9, border: `2px solid ${c}`, background: fill ? c : "transparent" }} />}
      {label}
    </span>
  );
}

/* ---------- drawing ---------- */
function tf(cv, sys, pad) {
  const W = cv.width, Ht = cv.height, v = sys.view;
  const s = Math.min((W - 2 * pad) / (v.x1 - v.x0), (Ht - 2 * pad) / (v.y1 - v.y0));
  const ox = pad + ((W - 2 * pad) - s * (v.x1 - v.x0)) / 2;
  const oy = pad + ((Ht - 2 * pad) - s * (v.y1 - v.y0)) / 2;
  return { X: (x) => ox + (x - v.x0) * s, Y: (y) => Ht - (oy + (y - v.y0) * s), s };
}

function drawPhase(cv, sys, tj, idx, big, sw) {
  if (!cv || !tj) return;
  const ctx = cv.getContext("2d"), W = cv.width, H = cv.height;
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#0b0d11"; roundRect(ctx, 0, 0, W, H, 8); ctx.fill();
  const T = tf(cv, sys, 14);
  const p = sys.pOf(idx / (N - 1)), seiz = sys.osc(p);
  const x = tj.xs[idx], y = tj.ys[idx];

  ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
  for (let gx = Math.ceil(sys.view.x0); gx <= sys.view.x1; gx++) { ctx.beginPath(); ctx.moveTo(T.X(gx), T.Y(sys.view.y0)); ctx.lineTo(T.X(gx), T.Y(sys.view.y1)); ctx.stroke(); }
  for (let gy = Math.ceil(sys.view.y0); gy <= sys.view.y1; gy++) { ctx.beginPath(); ctx.moveTo(T.X(sys.view.x0), T.Y(gy)); ctx.lineTo(T.X(sys.view.x1), T.Y(gy)); ctx.stroke(); }

  if (big) {
    const nx = 17, ny = 13; ctx.strokeStyle = C.field; ctx.fillStyle = C.field; ctx.lineWidth = 1;
    for (let i = 0; i <= nx; i++) for (let j = 0; j <= ny; j++) {
      const wx = sys.view.x0 + (i / nx) * (sys.view.x1 - sys.view.x0), wy = sys.view.y0 + (j / ny) * (sys.view.y1 - sys.view.y0);
      let [u, w] = sys.f(wx, wy, p); const m = Math.hypot(u, w) || 1e-9; const L = 9; u = u / m * L; w = w / m * L;
      const x0 = T.X(wx), y0 = T.Y(wy), x1 = x0 + u, y1 = y0 - w;
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke();
      const ang = Math.atan2(y0 - y1, x1 - x0);
      ctx.beginPath(); ctx.moveTo(x1, y1);
      ctx.lineTo(x1 - 3 * Math.cos(ang - 0.5), y1 + 3 * Math.sin(ang - 0.5));
      ctx.lineTo(x1 - 3 * Math.cos(ang + 0.5), y1 + 3 * Math.sin(ang + 0.5));
      ctx.closePath(); ctx.fill();
    }
  }

  for (const cyc of sys.cycles(p)) {
    if (!cyc.on || cyc.r < 1e-3) continue;
    ctx.beginPath(); ctx.ellipse(T.X(cyc.cx), T.Y(cyc.cy), cyc.r * T.s, cyc.r * T.s, 0, 0, Math.PI * 2);
    if (cyc.ring && !seiz) { ctx.setLineDash([3, 4]); ctx.strokeStyle = "rgba(103,179,217,0.5)"; ctx.lineWidth = 1.5; }
    else if (cyc.stable) { ctx.setLineDash([]); ctx.strokeStyle = C.cycle; ctx.lineWidth = 2.4; ctx.shadowColor = C.cycle; ctx.shadowBlur = 6; }
    else { ctx.setLineDash([4, 4]); ctx.strokeStyle = C.unstable; ctx.lineWidth = 1.6; }
    ctx.stroke(); ctx.setLineDash([]); ctx.shadowBlur = 0;
  }

  if (sw && sw.particles.length) {
    for (const pt of sw.particles) {
      const fin = Math.min(1, pt.age / 4), fout = pt.age > SWARM_LIFE - 18 ? Math.max(0, (SWARM_LIFE - pt.age) / 18) : 1, fade = fin * fout;
      if (fade <= 0) continue;
      const youth = Math.max(0, 1 - pt.age / 40);
      ctx.globalAlpha = (0.32 + 0.58 * youth) * fade; ctx.fillStyle = pt.col;
      ctx.beginPath(); ctx.arc(T.X(pt.x), T.Y(pt.y), (big ? 1.7 : 1.3) + (big ? 1.6 : 1.2) * youth, 0, 7); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  const lo = Math.max(0, idx - TRAIL);
  for (let i = lo + 1; i <= idx; i++) {
    const a = (i - lo) / TRAIL; ctx.strokeStyle = `rgba(231,210,163,${(a * 0.85).toFixed(3)})`; ctx.lineWidth = 1 + a * 1.6;
    ctx.beginPath(); ctx.moveTo(T.X(tj.xs[i - 1]), T.Y(tj.ys[i - 1])); ctx.lineTo(T.X(tj.xs[i]), T.Y(tj.ys[i])); ctx.stroke();
  }

  for (const fp of sys.fps(p)) {
    const fx = T.X(fp.x), fy = T.Y(fp.y);
    if (fp.t === "stable") { ctx.fillStyle = C.stable; ctx.beginPath(); ctx.arc(fx, fy, big ? 6 : 4.5, 0, 7); ctx.fill(); ctx.strokeStyle = "#0b0d11"; ctx.lineWidth = 1.5; ctx.stroke(); }
    else if (fp.t === "unstable") { ctx.strokeStyle = C.unstable; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(fx, fy, big ? 6 : 4.5, 0, 7); ctx.stroke(); }
    else { ctx.strokeStyle = C.saddle; ctx.lineWidth = 2; const d = big ? 5 : 4; ctx.beginPath(); ctx.moveTo(fx - d, fy - d); ctx.lineTo(fx + d, fy + d); ctx.moveTo(fx - d, fy + d); ctx.lineTo(fx + d, fy - d); ctx.stroke(); }
  }

  const px = T.X(x), py = T.Y(y), railY = T.Y(sys.view.y0);
  ctx.strokeStyle = "rgba(251,243,223,0.22)"; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(T.X(sys.view.x0), railY); ctx.lineTo(T.X(sys.view.x1), railY); ctx.stroke();
  ctx.fillStyle = "rgba(251,243,223,0.45)"; ctx.font = `${big ? 11 : 9}px 'IBM Plex Mono',monospace`; ctx.textAlign = "right";
  ctx.fillText("x = voltage", T.X(sys.view.x1) - 2, railY - 4);
  ctx.strokeStyle = "rgba(251,243,223,0.4)"; ctx.setLineDash([3, 3]); ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px, railY); ctx.stroke(); ctx.setLineDash([]);
  ctx.fillStyle = C.hl; ctx.beginPath(); ctx.moveTo(px, railY - 7); ctx.lineTo(px - 4, railY); ctx.lineTo(px + 4, railY); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.arc(px, py, big ? 7 : 5.5, 0, 7); ctx.strokeStyle = C.hl; ctx.lineWidth = 2; ctx.stroke();
  ctx.fillStyle = C.hl; ctx.shadowColor = C.hl; ctx.shadowBlur = 10; ctx.beginPath(); ctx.arc(px, py, big ? 3 : 2.4, 0, 7); ctx.fill(); ctx.shadowBlur = 0;
  ctx.fillStyle = C.hl; ctx.font = `${big ? 13 : 10}px 'IBM Plex Mono',monospace`; ctx.textAlign = "left";
  ctx.fillText("p(t)", px + (big ? 10 : 7), py - (big ? 7 : 5));

  ctx.fillStyle = seiz ? sys.hue : C.inkDim; ctx.font = `${big ? 14 : 12}px 'IBM Plex Mono', monospace`; ctx.textAlign = "left";
  ctx.fillText(`${sys.sym} = ${(p >= 0 ? "+" : "") + p.toFixed(3)}`, 12, big ? 24 : 20);
  ctx.fillStyle = C.inkFaint; ctx.fillText(seiz ? "oscillating" : "resting", 12, big ? 44 : 36);
}

function drawTS(cv, sys, tj, idx, big, markName) {
  if (!cv || !tj) return;
  const ctx = cv.getContext("2d"), W = cv.width, H = cv.height, pad = 10;
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#0b0d11"; roundRect(ctx, 0, 0, W, H, 8); ctx.fill();
  const v = sys.view, mapY = (xx) => H - pad - ((xx - v.x0) / (v.x1 - v.x0)) * (H - 2 * pad);
  ctx.strokeStyle = "#222838"; ctx.setLineDash([2, 4]); ctx.beginPath(); ctx.moveTo(pad, mapY(0)); ctx.lineTo(W - pad, mapY(0)); ctx.stroke(); ctx.setLineDash([]);

  const WIN = big ? 640 : 380, plotW = W - 2 * pad, lo = Math.max(0, idx - WIN + 1), xAt = (i) => pad + ((i - lo) / (WIN - 1)) * plotW;
  if (tj.mark >= lo && tj.mark <= idx) {
    const mx = xAt(tj.mark);
    ctx.strokeStyle = "rgba(231,210,163,0.55)"; ctx.setLineDash([3, 3]); ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(mx, pad); ctx.lineTo(mx, H - pad); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle = "rgba(231,210,163,0.8)"; ctx.font = "10px 'IBM Plex Mono',monospace"; ctx.textAlign = "left"; ctx.fillText(markName, Math.min(mx + 3, W - 44), pad + 9);
  }
  if (idx > lo) {
    ctx.strokeStyle = C.amber; ctx.lineWidth = big ? 1.6 : 1.3; ctx.beginPath();
    for (let i = lo; i <= idx; i++) { const X = xAt(i), Y = mapY(tj.xs[i]); i === lo ? ctx.moveTo(X, Y) : ctx.lineTo(X, Y); }
    ctx.stroke();
    const cx = xAt(idx), cy = mapY(tj.xs[idx]);
    ctx.strokeStyle = "rgba(251,243,223,0.3)"; ctx.setLineDash([3, 3]); ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(pad, cy); ctx.lineTo(cx, cy); ctx.stroke(); ctx.setLineDash([]);
    ctx.beginPath(); ctx.arc(cx, cy, big ? 4.5 : 3.5, 0, 7); ctx.strokeStyle = C.hl; ctx.lineWidth = 1.6; ctx.stroke();
    ctx.fillStyle = C.hl; ctx.beginPath(); ctx.arc(cx, cy, big ? 2 : 1.6, 0, 7); ctx.fill();
  }
  ctx.fillStyle = C.inkFaint; ctx.font = "11px 'IBM Plex Mono',monospace"; ctx.textAlign = "left"; ctx.fillText("x(t)", 12, 16);
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
}
