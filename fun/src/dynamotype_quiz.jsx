import React, { useState, useMemo, useEffect } from "react";

/* ============================================================
   DYNAMOTYPES — an interactive flash-quiz on seizure onset &
   offset bifurcations (Saggio–Jirsa taxonomy).
   Color coding matches the tutorial's figure legend:
     SN   orange  (solid)      SNIC orange (dashed)
     SupH green   (solid)      SubH green  (dashed)
     SH   blue    (solid)      FLC  magenta(solid)
   Quiz traces are drawn NEUTRAL so color never leaks the answer;
   color + dash style are revealed in feedback and study cards.
   ============================================================ */

const C = {
  bg: "#0e1014",
  panel: "#15181f",
  panel2: "#1b1f29",
  line: "#2a2f3a",
  ink: "#e9e2cf",
  inkDim: "#9aa3b2",
  inkFaint: "#5d6675",
  amber: "#e7d2a3",      // neutral oscilloscope trace
  grid: "#202531",
  good: "#7ad19a",
  bad: "#e8748b",
  goodBg: "rgba(122,209,154,0.10)",
  badBg: "rgba(232,116,139,0.10)",
};

const HUE = {
  SN:   "#f49c34",
  SNIC: "#f4b234",
  SupH: "#74bf45",
  SubH: "#3fc197",
  SH:   "#67b3d9",
  FLC:  "#f84495",
};
const DASHED = { SNIC: true, SubH: true };

const ONSET = [
  {
    key: "SN", abbr: "SN", name: "Saddle-Node",
    tell: "DC jump, then steady amplitude & frequency.",
    signal: "The trace jumps to a new baseline (a DC shift) and immediately oscillates at a steady amplitude and steady frequency — no warm-up.",
    flow: "A stable node and a nearby saddle move together, collide, and annihilate. With no equilibria left, trajectories are flung onto a limit cycle.",
  },
  {
    key: "SNIC", abbr: "SNIC", name: "Saddle-Node on Invariant Circle",
    tell: "Frequency speeds up.",
    signal: "Spikes begin far apart and visibly accelerate — the frequency ramps up from near zero.",
    flow: "A stable node and a saddle sitting on a closed periodic orbit drift together and vanish. The orbit survives but is now free of fixed points, so flow circulates around it — infinitely slowly at first, then faster.",
  },
  {
    key: "SupH", abbr: "SupH", name: "Supercritical Hopf",
    tell: "Amplitude grows from zero.",
    signal: "Tiny oscillations appear and grow smoothly in amplitude from zero; the frequency stays put.",
    flow: "A stable spiral loses stability and gives birth to a limit cycle of zero radius, which then grows continuously outward from the fixed point.",
  },
  {
    key: "SubH", abbr: "SubH", name: "Subcritical Hopf",
    tell: "Abrupt full-amplitude switch-on.",
    signal: "Full-blown, large-amplitude oscillations switch on abruptly — no growth, no frequency ramp, no baseline jump.",
    flow: "A small unstable cycle encircling a stable equilibrium contracts onto it and destabilizes it; the state is then thrown out to a pre-existing large-amplitude cycle (hysteresis).",
  },
];

const OFFSET = [
  {
    key: "SNIC", abbr: "SNIC", name: "Saddle-Node on Invariant Circle",
    tell: "Frequency slows, then stops.",
    signal: "Spikes spread further and further apart (frequency decays) and then stop abruptly.",
    flow: "Flow lingers near the 'ghost' of a just-vanished node–saddle pair, taking ever longer to come around, until an infinite-period orbit forms and the state drops to a fixed point.",
  },
  {
    key: "SH", abbr: "SH", name: "Saddle-Homoclinic",
    tell: "Frequency slows (log) ± DC shift.",
    signal: "Frequency slows down (roughly logarithmically) and the baseline may sit shifted, then the voltage snaps back to rest.",
    flow: "The cycle swells until it touches the saddle, forming a loop that departs and returns along the saddle's own stable/unstable directions; the loop's period diverges, then it breaks and oscillation ceases.",
  },
  {
    key: "SupH", abbr: "SupH", name: "Supercritical Hopf",
    tell: "Amplitude shrinks to zero.",
    signal: "Oscillations shrink smoothly in amplitude down to zero while the frequency stays constant.",
    flow: "The stable cycle contracts smoothly toward a re-stabilizing equilibrium; its radius reaches zero and the state rests at the fixed point.",
  },
  {
    key: "FLC", abbr: "FLC", name: "Fold Limit Cycle",
    tell: "Stops dead at full amplitude.",
    signal: "Oscillations stop dead at full amplitude — no slowing and no shrinking beforehand.",
    flow: "A stable and an unstable cycle approach in shape and amplitude, then collide and mutually annihilate, leaving no cycle at all.",
  },
];

const byKey = (arr, k) => arr.find((b) => b.key === k);

/* ---------- deterministic tiny ripple so traces don't jitter ---------- */
const ripple = (u, s) => 0.013 * Math.sin(u * 137.5 + s) + 0.009 * Math.sin(u * 41.3 + s * 2);

/* ---------- waveform generators (return array of y in ~[-1,1]) -------- */
function genOnset(key, N = 620, seed = 1) {
  const on = 0.32, ys = new Array(N);
  for (let i = 0; i < N; i++) {
    const u = i / (N - 1);
    if (u < on) { ys[i] = ripple(u, seed); continue; }
    const v = (u - on) / (1 - on);          // 0..1 inside seizure
    let y = 0;
    if (key === "SN") {
      y = -0.38 + 0.5 * Math.sin(2 * Math.PI * 13 * v);
    } else if (key === "SubH") {
      y = 0.72 * Math.sin(2 * Math.PI * 15 * v);
    } else if (key === "SNIC") {
      const phase = 2 * Math.PI * (3 * v + 16 * v * v); // accelerating
      y = 0.6 * Math.sin(phase);
    } else if (key === "SupH") {
      y = 0.78 * v * Math.sin(2 * Math.PI * 16 * v);     // growing
    }
    ys[i] = y + ripple(u, seed) * 0.6;
  }
  return ys;
}

function genOffset(key, N = 620, seed = 2) {
  const off = 0.68, ys = new Array(N);
  let phase = 0;
  for (let i = 0; i < N; i++) {
    const u = i / (N - 1);
    if (u > off) { ys[i] = ripple(u, seed); continue; }
    const v = u / off;                       // 0..1 inside seizure
    let amp = 0.62, dc = 0, rate;
    if (key === "SupH") { amp = 0.74 * (1 - v); rate = 15; }
    else if (key === "FLC") { amp = 0.7; rate = 15; }
    else if (key === "SNIC") { rate = 22 - 18 * v; amp = 0.6; }       // slows
    else if (key === "SH") { rate = 20 / (1 + 5 * v); amp = 0.56; dc = -0.3; } // log slow + DC
    phase += (2 * Math.PI * rate) / (N * off);
    ys[i] = dc + amp * Math.sin(phase) + ripple(u, seed) * 0.6;
  }
  return ys;
}

function genFull(onKey, offKey, N = 900, seed = 3) {
  const s0 = 0.15, s1 = 0.85, ys = new Array(N);
  const dc = onKey === "SN" ? -0.34 : 0;
  let phase = 0;
  for (let i = 0; i < N; i++) {
    const u = i / (N - 1);
    if (u < s0 || u > s1) { ys[i] = ripple(u, seed); continue; }
    const v = (u - s0) / (s1 - s0);          // 0..1 inside seizure
    let amp = 0.6, rate = 1;
    if (v < 0.22) {
      const w = v / 0.22;
      if (onKey === "SupH") amp *= w;
      if (onKey === "SNIC") rate *= 0.25 + 0.75 * w;
    }
    if (v > 0.78) {
      const w = (v - 0.78) / 0.22;
      if (offKey === "SupH") amp *= 1 - w;
      if (offKey === "SNIC" || offKey === "SH") rate *= 1 - 0.82 * w;
    }
    phase += (2 * Math.PI * 26 * rate) / (N * (s1 - s0));
    ys[i] = dc + amp * Math.sin(phase) + ripple(u, seed) * 0.55;
  }
  return ys;
}

/* ---------- SVG trace panel ---------- */
function Scope({ ys, color = C.amber, dashed = false, h = 168, label = "x(t)", mini = false }) {
  const W = 640, H = h, mid = H / 2, pad = 10;
  const pts = ys
    .map((y, i) => {
      const x = pad + (i / (ys.length - 1)) * (W - 2 * pad);
      const yy = mid - y * (mid - pad) * 0.92;
      return `${x.toFixed(1)},${yy.toFixed(1)}`;
    })
    .join(" ");
  const vlines = [], hlines = [];
  for (let g = 1; g < 8; g++) vlines.push((W / 8) * g);
  for (let g = 1; g < 4; g++) hlines.push((H / 4) * g);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", display: "block" }} role="img" aria-label="time series trace">
      <rect x="0" y="0" width={W} height={H} fill="#0b0d11" rx="6" />
      {vlines.map((x, i) => <line key={"v" + i} x1={x} y1="0" x2={x} y2={H} stroke={C.grid} strokeWidth="1" />)}
      {hlines.map((y, i) => <line key={"h" + i} x1="0" y1={y} x2={W} y2={y} stroke={C.grid} strokeWidth="1" />)}
      <line x1="0" y1={mid} x2={W} y2={mid} stroke="#2c3340" strokeWidth="1" strokeDasharray="2 4" />
      <polyline
        points={pts} fill="none" stroke={color} strokeWidth="2"
        strokeLinejoin="round" strokeLinecap="round"
        strokeDasharray={dashed ? "7 5" : "0"}
        style={{ filter: `drop-shadow(0 0 5px ${color}55)` }}
      />
      <text x={W - 12} y={H - 10} textAnchor="end" fill={C.inkFaint}
        fontFamily="'IBM Plex Mono', monospace" fontSize="11" letterSpacing="1">{mini ? "" : label}</text>
      {!mini && <text x="12" y="20" fill={C.inkFaint} fontFamily="'IBM Plex Mono', monospace" fontSize="11">t →</text>}
    </svg>
  );
}

/* ---------- color chip ---------- */
function Chip({ k }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6,
      fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: C.inkDim,
    }}>
      <span style={{
        width: 22, height: 0, borderTop: `3px ${DASHED[k] ? "dashed" : "solid"} ${HUE[k]}`,
        borderRadius: 2,
      }} />
    </span>
  );
}

/* ---------- match-mode tile & slot ---------- */
function MatchTile({ wave, selected, revealed, onClick }) {
  const color = revealed ? HUE[wave.key] : C.amber;
  const dashed = revealed ? !!DASHED[wave.key] : false;
  return (
    <div
      draggable={!revealed}
      onDragStart={(e) => e.dataTransfer.setData("text/plain", wave.id)}
      onClick={(e) => { e.stopPropagation(); onClick(); }}
      style={{
        border: `1px solid ${selected && !revealed ? C.ink : C.line}`,
        background: C.panel2, borderRadius: 10, padding: 8,
        cursor: revealed ? "default" : "grab",
        boxShadow: selected && !revealed ? `0 0 0 2px ${C.ink}` : "none",
        transition: "box-shadow .12s ease, border-color .12s ease",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <span style={{
          fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: C.inkDim,
          border: `1px solid ${C.line}`, borderRadius: 6, padding: "0px 7px",
        }}>{wave.badge}</span>
        {revealed && <Chip k={wave.key} />}
        {revealed && <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: C.inkDim }}>{wave.key}</span>}
      </div>
      <Scope ys={wave.ys} color={color} dashed={dashed} h={66} mini />
    </div>
  );
}

function Slot({ labelKey, set, occupant, sel, revealed, onDropWave, onClickSlot, onTileClick }) {
  const b = byKey(set, labelKey);
  let border = C.line, bg = C.panel;
  if (revealed && occupant) {
    const ok = occupant.key === labelKey;
    border = ok ? C.good : C.bad;
    bg = ok ? C.goodBg : C.badBg;
  }
  return (
    <div
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => { e.preventDefault(); onDropWave(e.dataTransfer.getData("text/plain"), labelKey); }}
      onClick={() => onClickSlot(labelKey)}
      style={{ border: `1px solid ${border}`, background: bg, borderRadius: 11, padding: 10, minHeight: 120 }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <Chip k={labelKey} />
        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontWeight: 600, fontSize: 14 }}>{b.abbr}</span>
        <span style={{ color: C.inkDim, fontSize: 12 }}>{b.name}</span>
      </div>
      {occupant ? (
        <MatchTile wave={occupant} selected={sel === occupant.id} revealed={revealed} onClick={() => onTileClick(occupant.id)} />
      ) : (
        <div style={{
          border: `1px dashed ${C.line}`, borderRadius: 9, height: 88,
          display: "flex", alignItems: "center", justifyContent: "center",
          color: C.inkFaint, fontSize: 12.5, fontFamily: "'IBM Plex Mono', monospace",
        }}>{revealed ? "—" : "drop trace"}</div>
      )}
      {revealed && occupant && occupant.key !== labelKey && (
        <div style={{ marginTop: 6, fontSize: 12, color: C.bad, fontFamily: "'IBM Plex Mono', monospace" }}>
          actually {byKey(set, occupant.key).abbr}
        </div>
      )}
    </div>
  );
}

/* ---------- question factory ---------- */
function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
function shuffle(a) {
  const x = a.slice();
  for (let i = x.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1));[x[i], x[j]] = [x[j], x[i]]; }
  return x;
}

function makeQuestion(mode, promptPref, prevAnswer, idx) {
  const id = idx + "_" + Math.random().toString(36).slice(2, 7);
  if (mode === "full") {
    const onKey = pick(ONSET).key;
    const offKey = pick(OFFSET).key;
    return { id, full: true, onKey, offKey };
  }
  let cat = mode;
  if (mode === "mixed") cat = Math.random() < 0.5 ? "onset" : "offset";
  const set = cat === "onset" ? ONSET : OFFSET;
  let ans;
  do { ans = pick(set).key; } while (set.length > 1 && ans === prevAnswer);
  let pt = promptPref;
  if (promptPref === "random") pt = pick(["timeseries", "signal", "flow"]);
  return { id, full: false, cat, promptType: pt, answerKey: ans, options: shuffle(set.map((b) => b.key)) };
}

/* ============================================================ */
export default function App() {
  const [screen, setScreen] = useState("home");
  const [mode, setMode] = useState("onset");      // onset | offset | mixed | full
  const [promptPref, setPromptPref] = useState("timeseries"); // timeseries|signal|flow|random
  const [total, setTotal] = useState(10);

  const [queue, setQueue] = useState([]);
  const [qi, setQi] = useState(0);
  const [picked, setPicked] = useState(null);      // for single
  const [pickedOn, setPickedOn] = useState(null);  // for full
  const [pickedOff, setPickedOff] = useState(null);
  const [revealed, setRevealed] = useState(false);
  const [log, setLog] = useState([]);              // {key/cat, correct}

  // match mode
  const [matchCat, setMatchCat] = useState("onset");
  const [matchRounds, setMatchRounds] = useState(3);
  const [matchRound, setMatchRound] = useState(0);
  const [matchData, setMatchData] = useState({ waves: [], labels: [] });
  const [placement, setPlacement] = useState({}); // waveId -> labelKey | null
  const [matchSel, setMatchSel] = useState(null);  // picked-up waveId (tap mode)
  const [matchRevealed, setMatchRevealed] = useState(false);

  const q = queue[qi];

  const wave = useMemo(() => {
    if (!q) return null;
    if (q.full) return genFull(q.onKey, q.offKey, 900, qi + 7);
    if (q.cat === "onset") return genOnset(q.answerKey, 620, qi + 3);
    return genOffset(q.answerKey, 620, qi + 5);
  }, [q, qi]);

  function start() {
    if (mode === "match") { setLog([]); initMatchRound(0); setScreen("match"); return; }
    const arr = [];
    let prev = null;
    for (let i = 0; i < total; i++) {
      const ques = makeQuestion(mode, promptPref, prev, i);
      prev = ques.answerKey || null;
      arr.push(ques);
    }
    setQueue(arr); setQi(0); setPicked(null); setPickedOn(null); setPickedOff(null);
    setRevealed(false); setLog([]); setScreen("quiz");
  }

  function submit() {
    if (q.full) {
      if (!pickedOn || !pickedOff) return;
      const ok = pickedOn === q.onKey && pickedOff === q.offKey;
      setLog((l) => [...l, { full: true, correct: ok, onOk: pickedOn === q.onKey, offOk: pickedOff === q.offKey }]);
    } else {
      if (!picked) return;
      const ok = picked === q.answerKey;
      setLog((l) => [...l, { cat: q.cat, key: q.answerKey, correct: ok }]);
    }
    setRevealed(true);
  }

  function next() {
    if (qi + 1 >= queue.length) { setScreen("result"); return; }
    setQi(qi + 1); setPicked(null); setPickedOn(null); setPickedOff(null); setRevealed(false);
  }

  /* ----- match mode ----- */
  function genMatchRound(cat, r) {
    const set = cat === "onset" ? ONSET : OFFSET;
    const waves = shuffle(set.map((b) => b.key)).map((k, i) => ({
      id: `r${r}_${k}`, key: k, badge: String.fromCharCode(65 + i),
      ys: cat === "onset" ? genOnset(k, 460, r * 9 + i + 1) : genOffset(k, 460, r * 9 + i + 1),
    }));
    const labels = shuffle(set.map((b) => b.key));
    return { waves, labels };
  }
  function initMatchRound(r) {
    setMatchData(genMatchRound(matchCat, r));
    setPlacement({}); setMatchSel(null); setMatchRevealed(false); setMatchRound(r);
  }
  function place(waveId, labelKey) {
    if (matchRevealed || !waveId) return;
    setPlacement((prev) => {
      const np = { ...prev };
      if (labelKey) for (const wid of Object.keys(np)) if (np[wid] === labelKey && wid !== waveId) np[wid] = null;
      np[waveId] = labelKey;
      return np;
    });
    setMatchSel(null);
  }
  function tileClick(id) { if (!matchRevealed) setMatchSel((s) => (s === id ? null : id)); }
  function checkMatch() {
    if (!allPlaced) return;
    setLog((l) => [...l, ...matchData.waves.map((w) => ({ cat: matchCat, key: w.key, correct: placement[w.id] === w.key }))]);
    setMatchRevealed(true);
  }
  function nextMatch() {
    if (matchRound + 1 >= matchRounds) { setScreen("result"); return; }
    initMatchRound(matchRound + 1);
  }

  const score = log.filter((l) => l.correct).length;
  const trayWaves = matchData.waves.filter((w) => !placement[w.id]);
  const allPlaced = matchData.waves.length > 0 && matchData.waves.every((w) => placement[w.id]);

  /* ====================== RENDER ====================== */
  return (
    <div style={{ background: C.bg, minHeight: "100%", color: C.ink, fontFamily: "'IBM Plex Sans', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');
        * { box-sizing: border-box; }
        .dt-btn { transition: all .15s ease; cursor: pointer; }
        .dt-btn:hover { transform: translateY(-1px); }
        .dt-opt:hover { border-color:#3a4150 !important; background:#1e2330 !important; }
        @keyframes dtUp { from { opacity:0; transform: translateY(8px);} to {opacity:1; transform:none;} }
        .dt-fade { animation: dtUp .35s ease both; }
        .dt-seg { transition: all .12s ease; cursor:pointer; }
      `}</style>

      <div style={{ maxWidth: 760, margin: "0 auto", padding: "30px 20px 60px" }}>
        {/* header */}
        <div style={{ display: "flex", alignItems: "baseline", gap: 14, marginBottom: 4, flexWrap: "wrap" }}>
          <h1 style={{
            fontFamily: "'Fraunces', serif", fontWeight: 600, fontSize: 40, margin: 0,
            letterSpacing: "-0.02em", lineHeight: 1,
          }}>Dynamotypes</h1>
          <span style={{
            fontFamily: "'IBM Plex Mono', monospace", fontSize: 12, color: C.inkFaint,
            border: `1px solid ${C.line}`, borderRadius: 20, padding: "3px 10px",
          }}>onset / offset trainer</span>
        </div>
        <p style={{ color: C.inkDim, marginTop: 8, marginBottom: 26, fontSize: 14.5, lineHeight: 1.55 }}>
          Recognize the four onset and four offset bifurcations of the Saggio–Jirsa fast-slow burster
          from their traces, signal signatures, or flow behavior.
        </p>

        {/* ---------------- HOME ---------------- */}
        {screen === "home" && (
          <div className="dt-fade">
            <Card>
              <Label>What to drill</Label>
              <Seg
                value={mode} onChange={setMode}
                opts={[
                  ["onset", "Onset (4)"],
                  ["offset", "Offset (4)"],
                  ["mixed", "Mixed"],
                  ["full", "Full burster ◆"],
                  ["match", "Match ⇄"],
                ]}
              />
              <div style={{ color: C.inkFaint, fontSize: 12.5, marginTop: 10, lineHeight: 1.5 }}>
                {mode === "onset" && "Identify which onset bifurcation starts the seizure: SN, SNIC, SupH, SubH."}
                {mode === "offset" && "Identify which offset bifurcation ends the seizure: SNIC, SH, SupH, FLC."}
                {mode === "mixed" && "Cards drawn at random from both the onset and offset sets."}
                {mode === "full" && "Advanced: a whole burst (rest → seizure → rest). Name both the onset and the offset — i.e. the full dynamotype class."}
                {mode === "match" && "Drag each trace onto its bifurcation label (tap-to-place also works), then check the whole board at once."}
              </div>
            </Card>

            {(mode === "onset" || mode === "offset" || mode === "mixed") && (
              <Card>
                <Label>Prompt style</Label>
                <Seg
                  value={promptPref} onChange={setPromptPref}
                  opts={[
                    ["timeseries", "Time series"],
                    ["signal", "Signal effect"],
                    ["flow", "Flow behavior"],
                    ["random", "Mix it up"],
                  ]}
                />
              </Card>
            )}

            {mode === "match" && (
              <Card>
                <Label>Traces to match</Label>
                <Seg value={matchCat} onChange={setMatchCat}
                  opts={[["onset", "Onset (4)"], ["offset", "Offset (4)"]]} />
              </Card>
            )}

            {mode !== "match" ? (
              <Card>
                <Label>Length</Label>
                <Seg
                  value={String(total)} onChange={(v) => setTotal(Number(v))}
                  opts={[["6", "6"], ["10", "10"], ["16", "16"]]}
                />
              </Card>
            ) : (
              <Card>
                <Label>Rounds</Label>
                <Seg
                  value={String(matchRounds)} onChange={(v) => setMatchRounds(Number(v))}
                  opts={[["1", "1"], ["3", "3"], ["5", "5"]]}
                />
              </Card>
            )}

            <div style={{ display: "flex", gap: 12, marginTop: 22, flexWrap: "wrap" }}>
              <button className="dt-btn" onClick={start} style={{
                background: C.ink, color: C.bg, border: "none", borderRadius: 10,
                padding: "13px 26px", fontSize: 15, fontWeight: 600, fontFamily: "'IBM Plex Sans', sans-serif",
              }}>Start quiz →</button>
              <button className="dt-btn" onClick={() => setScreen("study")} style={{
                background: "transparent", color: C.ink, border: `1px solid ${C.line}`, borderRadius: 10,
                padding: "13px 22px", fontSize: 15, fontWeight: 500, fontFamily: "'IBM Plex Sans', sans-serif",
              }}>Study the 8 cards</button>
            </div>
          </div>
        )}

        {/* ---------------- QUIZ ---------------- */}
        {screen === "quiz" && q && (
          <div className="dt-fade" key={q.id}>
            <Progress qi={qi} total={queue.length} score={score} />

            {/* card */}
            <div style={{
              background: C.panel, border: `1px solid ${C.line}`, borderRadius: 14,
              padding: 18, marginTop: 14,
            }}>
              <div style={{
                fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, letterSpacing: 2,
                color: C.inkFaint, textTransform: "uppercase", marginBottom: 12,
              }}>
                {q.full ? "Full burster — name onset & offset"
                  : (q.cat === "onset" ? "Onset bifurcation" : "Offset bifurcation")
                  + " · " + (q.promptType === "timeseries" ? "from the trace"
                    : q.promptType === "signal" ? "from the signal" : "from the flow")}
              </div>

              {/* prompt body */}
              {(q.full || q.promptType === "timeseries") ? (
                <Scope ys={wave}
                  color={revealed && !q.full ? HUE[q.answerKey] : C.amber}
                  dashed={revealed && !q.full ? !!DASHED[q.answerKey] : false}
                  h={q.full ? 188 : 168}
                  label={q.full ? "x(t)  rest → seizure → rest" : "x(t)"} />
              ) : (
                <div style={{
                  background: C.panel2, borderRadius: 10, padding: "20px 20px",
                  fontSize: 17, lineHeight: 1.6, color: C.ink,
                  fontFamily: q.promptType === "flow" ? "'IBM Plex Sans', sans-serif" : "'IBM Plex Sans', sans-serif",
                }}>
                  {q.promptType === "signal"
                    ? byKey(q.cat === "onset" ? ONSET : OFFSET, q.answerKey).signal
                    : byKey(q.cat === "onset" ? ONSET : OFFSET, q.answerKey).flow}
                </div>
              )}
            </div>

            {/* options */}
            {!q.full ? (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 14 }}>
                {q.options.map((k) => (
                  <Option key={k} k={k}
                    set={q.cat === "onset" ? ONSET : OFFSET}
                    selected={picked === k} revealed={revealed}
                    isAnswer={k === q.answerKey}
                    onClick={() => !revealed && setPicked(k)} />
                ))}
              </div>
            ) : (
              <div style={{ marginTop: 14 }}>
                <SubLabel>Onset</SubLabel>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
                  {ONSET.map((b) => (
                    <Option key={"on" + b.key} k={b.key} set={ONSET}
                      selected={pickedOn === b.key} revealed={revealed}
                      isAnswer={b.key === q.onKey}
                      onClick={() => !revealed && setPickedOn(b.key)} compact />
                  ))}
                </div>
                <SubLabel>Offset</SubLabel>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  {OFFSET.map((b) => (
                    <Option key={"off" + b.key} k={b.key} set={OFFSET}
                      selected={pickedOff === b.key} revealed={revealed}
                      isAnswer={b.key === q.offKey}
                      onClick={() => !revealed && setPickedOff(b.key)} compact />
                  ))}
                </div>
              </div>
            )}

            {/* feedback */}
            {revealed && <Feedback q={q} picked={picked} pickedOn={pickedOn} pickedOff={pickedOff} />}

            {/* action */}
            <div style={{ marginTop: 18, display: "flex", justifyContent: "flex-end" }}>
              {!revealed ? (
                <button className="dt-btn" onClick={submit}
                  disabled={q.full ? !(pickedOn && pickedOff) : !picked}
                  style={{
                    background: (q.full ? (pickedOn && pickedOff) : picked) ? C.ink : C.panel2,
                    color: (q.full ? (pickedOn && pickedOff) : picked) ? C.bg : C.inkFaint,
                    border: "none", borderRadius: 10, padding: "12px 26px", fontSize: 15, fontWeight: 600,
                    fontFamily: "'IBM Plex Sans', sans-serif",
                    cursor: (q.full ? (pickedOn && pickedOff) : picked) ? "pointer" : "default",
                  }}>Check</button>
              ) : (
                <button className="dt-btn" onClick={next} style={{
                  background: C.ink, color: C.bg, border: "none", borderRadius: 10,
                  padding: "12px 26px", fontSize: 15, fontWeight: 600, fontFamily: "'IBM Plex Sans', sans-serif",
                }}>{qi + 1 >= queue.length ? "See results →" : "Next →"}</button>
              )}
            </div>
          </div>
        )}

        {/* ---------------- MATCH ---------------- */}
        {screen === "match" && (
          <div className="dt-fade">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, marginBottom: 8, flexWrap: "wrap" }}>
              <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, letterSpacing: 2, color: C.inkFaint, textTransform: "uppercase" }}>
                Match · {matchCat} · round {matchRound + 1}/{matchRounds}
              </div>
              <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12.5, color: C.inkDim }}>
                {matchRevealed
                  ? `${matchData.waves.filter((w) => placement[w.id] === w.key).length}/4 matched`
                  : `${matchData.waves.filter((w) => placement[w.id]).length}/4 placed`}
              </div>
            </div>
            <p style={{ color: C.inkFaint, fontSize: 12.5, margin: "0 0 14px", lineHeight: 1.5 }}>
              Drag a trace onto the label you think it matches — or tap a trace then tap a slot. Move pieces around freely; check when all four are placed.
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, alignItems: "start" }}>
              {/* tray */}
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => { e.preventDefault(); place(e.dataTransfer.getData("text/plain"), null); }}
                onClick={() => { if (matchSel) place(matchSel, null); }}
                style={{ background: C.panel, border: `1px solid ${C.line}`, borderRadius: 14, padding: 12, minHeight: 220 }}
              >
                <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, letterSpacing: 1.5, color: C.inkFaint, textTransform: "uppercase", marginBottom: 10 }}>Traces</div>
                <div style={{ display: "grid", gap: 10 }}>
                  {trayWaves.length === 0 && (
                    <div style={{ color: C.inkFaint, fontSize: 13, padding: "26px 4px", textAlign: "center" }}>all placed ✓</div>
                  )}
                  {trayWaves.map((w) => (
                    <MatchTile key={w.id} wave={w} selected={matchSel === w.id} revealed={matchRevealed} onClick={() => tileClick(w.id)} />
                  ))}
                </div>
              </div>

              {/* slots */}
              <div style={{ display: "grid", gap: 10 }}>
                {matchData.labels.map((lk) => (
                  <Slot
                    key={lk} labelKey={lk}
                    set={matchCat === "onset" ? ONSET : OFFSET}
                    occupant={matchData.waves.find((w) => placement[w.id] === lk)}
                    sel={matchSel} revealed={matchRevealed}
                    onDropWave={place}
                    onClickSlot={(k) => { if (matchSel) place(matchSel, k); }}
                    onTileClick={tileClick}
                  />
                ))}
              </div>
            </div>

            {matchRevealed && (
              <div className="dt-fade" style={{
                marginTop: 14, background: C.panel2, border: `1px solid ${C.line}`, borderRadius: 12,
                padding: 14, fontSize: 13.5, lineHeight: 1.55, color: C.inkDim,
              }}>
                Traces are now colored by their true type (orange SN, orange-dashed SNIC, green SupH,
                green-dashed SubH, blue SH, magenta FLC). Green slots are correct; red slots note what the
                trace actually was.
              </div>
            )}

            <div style={{ marginTop: 18, display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
              <button className="dt-btn" onClick={() => setScreen("home")} style={ghostBtn}>Quit</button>
              {!matchRevealed ? (
                <button className="dt-btn" onClick={checkMatch} disabled={!allPlaced} style={{
                  ...primaryBtn, background: allPlaced ? C.ink : C.panel2,
                  color: allPlaced ? C.bg : C.inkFaint, cursor: allPlaced ? "pointer" : "default",
                }}>Check matches</button>
              ) : (
                <button className="dt-btn" onClick={nextMatch} style={primaryBtn}>
                  {matchRound + 1 >= matchRounds ? "See results →" : "Next round →"}
                </button>
              )}
            </div>
          </div>
        )}

        {/* ---------------- RESULT ---------------- */}
        {screen === "result" && (
          <div className="dt-fade">
            <Card>
              <div style={{ textAlign: "center", padding: "10px 0 4px" }}>
                <div style={{ fontFamily: "'Fraunces', serif", fontSize: 54, fontWeight: 600, lineHeight: 1 }}>
                  {score}<span style={{ color: C.inkFaint, fontSize: 30 }}>/{log.length}</span>
                </div>
                <div style={{ color: C.inkDim, marginTop: 8, fontSize: 14 }}>
                  {score === log.length ? "Flawless — you can read these in your sleep."
                    : score / log.length >= 0.7 ? "Solid. A couple of signatures to firm up."
                    : "Worth another lap — the study cards will help."}
                </div>
              </div>
            </Card>
            <Breakdown log={log} />
            <div style={{ display: "flex", gap: 12, marginTop: 20, flexWrap: "wrap" }}>
              <button className="dt-btn" onClick={start} style={primaryBtn}>Run it again</button>
              <button className="dt-btn" onClick={() => setScreen("home")} style={ghostBtn}>Change settings</button>
              <button className="dt-btn" onClick={() => setScreen("study")} style={ghostBtn}>Study cards</button>
            </div>
          </div>
        )}

        {/* ---------------- STUDY ---------------- */}
        {screen === "study" && (
          <div className="dt-fade">
            <button className="dt-btn" onClick={() => setScreen("home")} style={{ ...ghostBtn, marginBottom: 18 }}>← Back</button>
            <StudySection title="Onset bifurcations" set={ONSET} role="onset" />
            <StudySection title="Offset bifurcations" set={OFFSET} role="offset" />
            <p style={{ color: C.inkFaint, fontSize: 12.5, lineHeight: 1.5, marginTop: 8 }}>
              Color/line style follows the tutorial's sphere legend: orange = SN, orange-dashed = SNIC,
              green = SupH, green-dashed = SubH, blue = SH, magenta = FLC. The 16 dynamotype classes are
              the 4 onsets × 4 offsets.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

/* ====================== small components ====================== */
const primaryBtn = {
  background: C.ink, color: C.bg, border: "none", borderRadius: 10,
  padding: "13px 26px", fontSize: 15, fontWeight: 600, fontFamily: "'IBM Plex Sans', sans-serif",
};
const ghostBtn = {
  background: "transparent", color: C.ink, border: `1px solid ${C.line}`, borderRadius: 10,
  padding: "13px 22px", fontSize: 15, fontWeight: 500, fontFamily: "'IBM Plex Sans', sans-serif",
};

function Card({ children }) {
  return <div style={{ background: C.panel, border: `1px solid ${C.line}`, borderRadius: 14, padding: 18, marginTop: 14 }}>{children}</div>;
}
function Label({ children }) {
  return <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, letterSpacing: 2, color: C.inkFaint, textTransform: "uppercase", marginBottom: 12 }}>{children}</div>;
}
function SubLabel({ children }) {
  return <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11, letterSpacing: 1.5, color: C.inkFaint, textTransform: "uppercase", marginBottom: 8 }}>{children}</div>;
}

function Seg({ value, onChange, opts }) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
      {opts.map(([v, label]) => {
        const on = value === v;
        return (
          <div key={v} className="dt-seg" onClick={() => onChange(v)} style={{
            padding: "9px 15px", borderRadius: 9, fontSize: 14, fontWeight: 500,
            border: `1px solid ${on ? C.ink : C.line}`,
            background: on ? C.ink : "transparent", color: on ? C.bg : C.inkDim,
          }}>{label}</div>
        );
      })}
    </div>
  );
}

function Progress({ qi, total, score }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
      <div style={{ flex: 1, height: 6, background: C.panel2, borderRadius: 6, overflow: "hidden" }}>
        <div style={{ width: `${(qi / total) * 100}%`, height: "100%", background: C.ink, transition: "width .3s ease" }} />
      </div>
      <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12.5, color: C.inkDim, whiteSpace: "nowrap" }}>
        {qi + 1}/{total} · {score}✓
      </div>
    </div>
  );
}

function Option({ k, set, selected, revealed, isAnswer, onClick, compact }) {
  const b = byKey(set, k);
  let border = C.line, bg = C.panel2, ring = "none";
  if (revealed) {
    if (isAnswer) { border = C.good; bg = C.goodBg; }
    else if (selected) { border = C.bad; bg = C.badBg; }
  } else if (selected) { border = C.ink; bg = "#1e2330"; }
  return (
    <div className={revealed ? "" : "dt-opt"} onClick={onClick} style={{
      border: `1px solid ${border}`, background: bg, borderRadius: 11,
      padding: compact ? "11px 13px" : "14px 16px", cursor: revealed ? "default" : "pointer",
      transition: "all .15s ease", boxShadow: ring,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
        <Chip k={k} />
        <span style={{ fontWeight: 600, fontFamily: "'IBM Plex Mono', monospace", fontSize: 14.5 }}>{b.abbr}</span>
        {revealed && isAnswer && <span style={{ marginLeft: "auto", color: C.good, fontSize: 13 }}>✓</span>}
        {revealed && selected && !isAnswer && <span style={{ marginLeft: "auto", color: C.bad, fontSize: 13 }}>✕</span>}
      </div>
      {!compact && <div style={{ color: C.inkDim, fontSize: 12.5, marginTop: 5, lineHeight: 1.3 }}>{b.name}</div>}
    </div>
  );
}

/* ============================================================
   PHASE-PORTRAIT TRIPTYCH
   For each bifurcation, three schematic state-space pictures in
   REST -> BIFURCATION -> OSCILLATING order. Onsets are shown in
   that order (rest leads to seizure); offsets are shown reversed
   (seizure leads to rest), matching the temporal direction.

   Scene element model (coords in [-1,1], origin at center):
     fps:    fixed points  {x,y,kind}  kind: stable|unstable|saddle|half
     cycles: limit cycles  {x,y,rx,ry,stable,faint}
     spiral: flow spiral    {x,y,r,out}   out=true => outward (unstable)
     ghost:  slow "ghost" of a vanished pair  {x,y}
   ============================================================ */
const PHASE = {
  // ---- onset bifurcations ----
  SN: [
    { fps: [{ x: -0.28, y: 0.05, kind: "stable" }, { x: 0.32, y: 0.05, kind: "saddle" }],
      cycles: [{ x: 0, y: 0, rx: 0.86, ry: 0.66, stable: true, faint: true }] },
    { fps: [{ x: 0.02, y: 0.05, kind: "half" }],
      cycles: [{ x: 0, y: 0, rx: 0.86, ry: 0.66, stable: true, faint: true }] },
    { fps: [], ghost: { x: 0.02, y: 0.05 },
      cycles: [{ x: 0, y: 0, rx: 0.86, ry: 0.66, stable: true }] },
  ],
  SNIC: [
    { cycles: [{ x: 0, y: 0, rx: 0.82, ry: 0.66, stable: true, faint: true }],
      fps: [{ x: -0.50, y: 0.43, kind: "stable" }, { x: 0.50, y: 0.43, kind: "saddle" }] },
    { cycles: [{ x: 0, y: 0, rx: 0.82, ry: 0.66, stable: true, faint: true }],
      fps: [{ x: 0, y: 0.66, kind: "half" }] },
    { cycles: [{ x: 0, y: 0, rx: 0.82, ry: 0.66, stable: true }], ghost: { x: 0, y: 0.66 } },
  ],
  SupH: [
    { fps: [{ x: 0, y: 0, kind: "stable" }], spiral: { x: 0, y: 0, r: 0.78, out: false } },
    { fps: [{ x: 0, y: 0, kind: "half" }], cycles: [{ x: 0, y: 0, rx: 0.10, ry: 0.08, stable: true }] },
    { fps: [{ x: 0, y: 0, kind: "unstable" }], cycles: [{ x: 0, y: 0, rx: 0.82, ry: 0.64, stable: true }] },
  ],
  SubH: [
    { fps: [{ x: 0, y: 0, kind: "stable" }],
      cycles: [{ x: 0, y: 0, rx: 0.40, ry: 0.32, stable: false }, { x: 0, y: 0, rx: 0.86, ry: 0.66, stable: true }] },
    { fps: [{ x: 0, y: 0, kind: "half" }],
      cycles: [{ x: 0, y: 0, rx: 0.86, ry: 0.66, stable: true }] },
    { fps: [{ x: 0, y: 0, kind: "unstable" }],
      cycles: [{ x: 0, y: 0, rx: 0.86, ry: 0.66, stable: true }] },
  ],
  // ---- offset-only bifurcations (also rendered rest->osc here; reversed at display) ----
  SH: [
    { fps: [{ x: 0.55, y: -0.05, kind: "saddle" }, { x: -0.30, y: -0.05, kind: "stable" }] },
    { fps: [{ x: 0.55, y: -0.05, kind: "saddle" }],
      cycles: [{ x: 0.0, y: 0.0, rx: 0.55, ry: 0.6, stable: true, teardrop: true }] },
    { fps: [{ x: 0.55, y: -0.05, kind: "saddle" }],
      cycles: [{ x: -0.05, y: 0.0, rx: 0.62, ry: 0.62, stable: true }] },
  ],
  FLC: [
    { fps: [{ x: 0, y: 0, kind: "stable" }], spiral: { x: 0, y: 0, r: 0.5, out: false } },
    { fps: [{ x: 0, y: 0, kind: "stable" }],
      cycles: [{ x: 0, y: 0, rx: 0.55, ry: 0.44, stable: true }] },
    { fps: [{ x: 0, y: 0, kind: "stable" }],
      cycles: [{ x: 0, y: 0, rx: 0.42, ry: 0.34, stable: false }, { x: 0, y: 0, rx: 0.86, ry: 0.66, stable: true }] },
  ],
};

function spiralPath(cx, cy, R, out, sc, turns = 2.3) {
  const steps = 70, pts = [];
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const theta = turns * 2 * Math.PI * t * (out ? 1 : -1);
    const rad = (out ? t : 1 - t) * R * sc;
    pts.push([cx + rad * Math.cos(theta), cy + rad * Math.sin(theta)]);
  }
  return "M " + pts.map((p) => `${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" L ");
}

function PhasePortrait({ scene, size = 104, accent = "#67b3d9" }) {
  const S = size, pad = 13, sc = (S - 2 * pad) / 2;
  const X = (x) => pad + (x + 1) * sc;
  const Y = (y) => pad + (1 - y) * sc;
  const dim = "#5d6675", line = "#2a2f3a", bg = "#0e1014";
  const els = [];
  els.push(<line key="ax" x1={pad} y1={Y(0)} x2={S - pad} y2={Y(0)} stroke={line} strokeWidth="1" />);
  els.push(<line key="ay" x1={X(0)} y1={pad} x2={X(0)} y2={S - pad} stroke={line} strokeWidth="1" />);

  (scene.cycles || []).forEach((c, i) => {
    if (c.teardrop) {
      // homoclinic loop: a teardrop touching the saddle on the right
      const rx = c.rx * sc, ry = c.ry * sc, cx = X(c.x), cy = Y(c.y);
      const tip = X(0.55);
      els.push(<path key={"td" + i}
        d={`M ${tip} ${cy} C ${cx - rx} ${cy - ry}, ${cx - rx} ${cy + ry}, ${tip} ${cy} Z`}
        fill="none" stroke={accent} strokeWidth="2" />);
    } else {
      els.push(<ellipse key={"c" + i} cx={X(c.x)} cy={Y(c.y)} rx={c.rx * sc} ry={c.ry * sc}
        fill="none" stroke={c.stable ? accent : dim} strokeWidth={c.stable ? 2 : 1.5}
        strokeDasharray={c.stable ? "" : "4 3"} opacity={c.faint ? 0.4 : 1} />);
      // circulation arrowhead near the top of the cycle
      const ax = X(c.x) + c.rx * sc * 0.35, ay = Y(c.y) - c.ry * sc;
      els.push(<path key={"ca" + i} d={`M ${ax - 4} ${ay - 3} L ${ax + 4} ${ay} L ${ax - 4} ${ay + 3}`}
        fill="none" stroke={c.stable ? accent : dim} strokeWidth="1.6" opacity={c.faint ? 0.4 : 1} />);
    }
  });

  if (scene.spiral) {
    const sp = scene.spiral;
    els.push(<path key="sp" d={spiralPath(X(sp.x), Y(sp.y), sp.r, sp.out, sc)}
      fill="none" stroke={sp.out ? dim : accent} strokeWidth="1.6" opacity="0.85" />);
  }

  if (scene.ghost) {
    els.push(<circle key="gh" cx={X(scene.ghost.x)} cy={Y(scene.ghost.y)} r="5"
      fill="none" stroke={dim} strokeWidth="1.4" strokeDasharray="2 2" />);
  }

  (scene.fps || []).forEach((p, i) => {
    const cx = X(p.x), cy = Y(p.y), r = 4.6;
    if (p.kind === "stable") {
      els.push(<circle key={"f" + i} cx={cx} cy={cy} r={r} fill={accent} stroke={accent} strokeWidth="1" />);
    } else if (p.kind === "unstable") {
      els.push(<circle key={"f" + i} cx={cx} cy={cy} r={r} fill={bg} stroke={accent} strokeWidth="1.8" />);
    } else if (p.kind === "half") {
      els.push(<circle key={"f" + i} cx={cx} cy={cy} r={r} fill={bg} stroke={accent} strokeWidth="1.8" />);
      els.push(<path key={"fh" + i} d={`M ${cx} ${cy - r} A ${r} ${r} 0 0 1 ${cx} ${cy + r} Z`} fill={accent} />);
    } else if (p.kind === "saddle") {
      els.push(<circle key={"f" + i} cx={cx} cy={cy} r={r} fill={bg} stroke={dim} strokeWidth="1.6" />);
      els.push(<line key={"sx1" + i} x1={cx - r - 2} y1={cy} x2={cx + r + 2} y2={cy} stroke={dim} strokeWidth="1.2" />);
      els.push(<line key={"sx2" + i} x1={cx} y1={cy - r - 2} x2={cx} y2={cy + r + 2} stroke={dim} strokeWidth="1.2" />);
    }
  });

  return (
    <svg viewBox={`0 0 ${S} ${S}`} width={S} height={S} role="img"
      style={{ background: "#15181f", borderRadius: 8, border: "1px solid #2a2f3a" }}>
      {els}
    </svg>
  );
}

function PhaseSequence({ bkey, role, accent = "#67b3d9" }) {
  const base = PHASE[bkey];
  if (!base) return null;
  // rest -> bifurcation -> oscillating; reverse for offset (oscillating -> rest)
  const order = role === "offset" ? [2, 1, 0] : [0, 1, 2];
  const labels = role === "offset"
    ? ["Oscillating", "At bifurcation", "Resting"]
    : ["Resting", "At bifurcation", "Oscillating"];
  return (
    <div style={{ marginTop: 6, marginBottom: 12 }}>
      <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 11.5, letterSpacing: 1,
        textTransform: "uppercase", color: C.inkFaint, marginBottom: 6 }}>
        State space {role === "offset" ? "(seizure → rest)" : "(rest → seizure)"}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 4, flexWrap: "wrap" }}>
        {order.map((idx, j) => (
          <React.Fragment key={j}>
            <div style={{ textAlign: "center" }}>
              <PhasePortrait scene={base[idx]} accent={accent} />
              <div style={{ fontSize: 10.5, color: C.inkDim, marginTop: 3 }}>{labels[j]}</div>
            </div>
            {j < 2 && <div style={{ color: C.inkFaint, fontSize: 18, padding: "0 1px", marginBottom: 14 }}>→</div>}
          </React.Fragment>
        ))}
      </div>
      <div style={{ fontSize: 10.5, color: C.inkFaint, marginTop: 6, lineHeight: 1.4 }}>
        ● stable&nbsp; ○ unstable&nbsp; ⊕ saddle&nbsp; ◐ merging&nbsp; — stable cycle&nbsp; ┄ unstable cycle
      </div>
    </div>
  );
}

function Feedback({ q, picked, pickedOn, pickedOff }) {
  if (q.full) {
    const on = byKey(ONSET, q.onKey), off = byKey(OFFSET, q.offKey);
    const onOk = pickedOn === q.onKey, offOk = pickedOff === q.offKey;
    return (
      <div className="dt-fade" style={fbBox(onOk && offOk)}>
        <div style={fbHead(onOk && offOk)}>
          {onOk && offOk ? "Correct dynamotype" : "Not quite"} — {on.abbr}/{off.abbr}
        </div>
        <FbRow ok={onOk} title={`Onset · ${on.abbr} (${on.name})`} body={on.signal} k={q.onKey} />
        <PhaseSequence bkey={q.onKey} role="onset" accent={HUE[q.onKey]} />
        <FbRow ok={offOk} title={`Offset · ${off.abbr} (${off.name})`} body={off.signal} k={q.offKey} />
        <PhaseSequence bkey={q.offKey} role="offset" accent={HUE[q.offKey]} />
      </div>
    );
  }
  const set = q.cat === "onset" ? ONSET : OFFSET;
  const b = byKey(set, q.answerKey);
  const ok = picked === q.answerKey;
  return (
    <div className="dt-fade" style={fbBox(ok)}>
      <div style={fbHead(ok)}>
        {ok ? "Correct" : "Not quite"} — it's {b.abbr}
        {!ok && picked ? `, not ${byKey(set, picked).abbr}` : ""}
        <span style={{ marginLeft: 8 }}><Chip k={q.answerKey} /></span>
      </div>
      <div style={{ fontWeight: 600, fontSize: 14.5, marginBottom: 4 }}>{b.name}</div>
      <p style={{ margin: "0 0 10px", fontSize: 14, lineHeight: 1.55, color: C.ink }}><b style={{ color: C.inkDim }}>Signal:</b> {b.signal}</p>
      <p style={{ margin: "0 0 10px", fontSize: 14, lineHeight: 1.55, color: C.ink }}><b style={{ color: C.inkDim }}>Flow:</b> {b.flow}</p>
      <PhaseSequence bkey={q.answerKey} role={q.cat} accent={HUE[q.answerKey]} />
      <div style={{
        fontFamily: "'IBM Plex Mono', monospace", fontSize: 12.5, color: C.inkDim,
        borderLeft: `2px solid ${HUE[q.answerKey]}`, paddingLeft: 10,
      }}>tell → {b.tell}</div>
    </div>
  );
}
function FbRow({ ok, title, body, k }) {
  return (
    <div style={{ marginTop: 10 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 600, fontSize: 14, color: ok ? C.good : C.bad }}>
        <Chip k={k} />{ok ? "✓" : "✕"} {title}
      </div>
      <p style={{ margin: "3px 0 0", fontSize: 13.5, lineHeight: 1.5, color: C.ink }}>{body}</p>
    </div>
  );
}
const fbBox = (ok) => ({
  marginTop: 14, background: ok ? C.goodBg : C.badBg,
  border: `1px solid ${ok ? "rgba(122,209,154,0.35)" : "rgba(232,116,139,0.35)"}`,
  borderRadius: 12, padding: 16,
});
const fbHead = (ok) => ({
  display: "flex", alignItems: "center", flexWrap: "wrap",
  fontFamily: "'IBM Plex Mono', monospace", fontSize: 13, letterSpacing: 1,
  textTransform: "uppercase", color: ok ? C.good : C.bad, marginBottom: 10,
});

function Breakdown({ log }) {
  const tally = {};
  log.forEach((l) => {
    if (l.full) {
      add(tally, "Full burster", l.correct);
    } else {
      add(tally, (l.cat === "onset" ? "Onset · " : "Offset · ") + l.key, l.correct);
    }
  });
  const rows = Object.entries(tally);
  if (!rows.length) return null;
  return (
    <Card>
      <Label>By item</Label>
      {rows.map(([name, v]) => (
        <div key={name} style={{ display: "flex", alignItems: "center", gap: 12, padding: "6px 0" }}>
          <div style={{ flex: 1, fontFamily: "'IBM Plex Mono', monospace", fontSize: 13, color: C.inkDim }}>{name}</div>
          <div style={{ width: 120, height: 6, background: C.panel2, borderRadius: 6, overflow: "hidden" }}>
            <div style={{ width: `${(v.c / v.n) * 100}%`, height: "100%", background: v.c === v.n ? C.good : v.c === 0 ? C.bad : C.amber }} />
          </div>
          <div style={{ width: 36, textAlign: "right", fontFamily: "'IBM Plex Mono', monospace", fontSize: 12.5, color: C.inkDim }}>{v.c}/{v.n}</div>
        </div>
      ))}
    </Card>
  );
}
function add(t, key, ok) { if (!t[key]) t[key] = { c: 0, n: 0 }; t[key].n++; if (ok) t[key].c++; }

function StudySection({ title, set, role }) {
  return (
    <div style={{ marginBottom: 22 }}>
      <h2 style={{ fontFamily: "'Fraunces', serif", fontWeight: 600, fontSize: 22, margin: "6px 0 14px" }}>{title}</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 14 }}>
        {set.map((b, i) => {
          const ys = role === "onset" ? genOnset(b.key, 620, i + 11) : genOffset(b.key, 620, i + 21);
          return (
            <div key={b.key} style={{ background: C.panel, border: `1px solid ${C.line}`, borderRadius: 14, padding: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                <Chip k={b.key} />
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontWeight: 600, fontSize: 16 }}>{b.abbr}</span>
                <span style={{ color: C.inkDim, fontSize: 14 }}>{b.name}</span>
              </div>
              <Scope ys={ys} color={HUE[b.key]} dashed={!!DASHED[b.key]} h={132} />
              <p style={{ margin: "12px 0 8px", fontSize: 13.5, lineHeight: 1.55, color: C.ink }}>{b.signal}</p>
              <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: 12.5, color: C.inkDim, borderLeft: `2px solid ${HUE[b.key]}`, paddingLeft: 10 }}>
                tell → {b.tell}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
