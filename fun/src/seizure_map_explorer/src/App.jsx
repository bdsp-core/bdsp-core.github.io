import React, { useState, useMemo, useRef, useEffect, useCallback } from "react";
import { C, HUE, ONSET, OFFSET, synthesize, TraceCanvas, SpectroCanvas, Slider } from "./synth.jsx";
import { simulate as realSimulate } from "./model.js";
import MAP from "./data/curves.json";
import REG from "./data/regions.json";

/* ============================================================
   SEIZURE DYNAMOTYPE MAP EXPLORER  (Phase 2)
   Interactive 3D view of Saggio's parameter sphere with the real exported
   bifurcation curves. Place an onset and an offset waypoint; the tool finds
   the nearest onset/offset bifurcation curve to each, classifies the
   dynamotype, and synthesizes the seizure with the (validated Phase-1)
   signal engine — shown as trace + spectrogram.
   ============================================================ */

const R = MAP.radius; // 0.4

/* ---- region shading (precomputed dynamical-regime patches from the MATLAB
   tutorial's testmesh.mat, downsampled to a lat/lon label grid) ---- */
const REG_FILL = ["#EBEBEB", "#E4B4D3", "#F8F6B8", "#F8F6B8"]; // rest, seizure, bistable, bistable+LC
// sphere vertices for every grid node (built once); index = i*nLon + j
const REG_GV = (() => {
  const { nLat, nLon } = REG, gv = new Array(nLat * nLon);
  for (let i = 0; i < nLat; i++) {
    const la = (-90 + (180 * i) / (nLat - 1)) * Math.PI / 180, cla = Math.cos(la), sla = Math.sin(la);
    for (let j = 0; j < nLon; j++) {
      const lo = ((360 * j) / (nLon - 1)) * Math.PI / 180;
      gv[i * nLon + j] = [R * cla * Math.cos(lo), R * sla, R * cla * Math.sin(lo)];
    }
  }
  return gv;
})();

/* ---- tiny 3D ---- */
const rotY = (p, a) => { const c = Math.cos(a), s = Math.sin(a); return [c*p[0] + s*p[2], p[1], -s*p[0] + c*p[2]]; };
const rotX = (p, b) => { const c = Math.cos(b), s = Math.sin(b); return [p[0], c*p[1] - s*p[2], s*p[1] + c*p[2]]; };
const fwd = (p, yaw, pitch) => rotX(rotY(p, yaw), pitch);          // model -> view
const inv = (p, yaw, pitch) => rotY(rotX(p, -pitch), -yaw);        // view -> model
const d3 = (a, b) => Math.hypot(a[0]-b[0], a[1]-b[1], a[2]-b[2]);

/* nearest curve (respecting role) to a model-space point -> {label,dyno} */
function classify(point, role) {
  let best = Infinity, hit = null;
  for (const cv of MAP.curves) {
    if (cv.role !== "both" && cv.role !== role) continue;
    for (const q of cv.pts) { const dd = d3(point, q); if (dd < best) { best = dd; hit = cv; } }
  }
  return hit;
}

/* great-circle arc (model space) between two sphere points */
function arc(p1, p2, n = 48) {
  const norm = (v) => { const m = Math.hypot(...v) || 1e-9; return [v[0]/m*R, v[1]/m*R, v[2]/m*R]; };
  p1 = norm(p1); p2 = norm(p2);
  const dot = Math.max(-1, Math.min(1, (p1[0]*p2[0]+p1[1]*p2[1]+p1[2]*p2[2])/(R*R)));
  const th = Math.acos(dot);
  if (th < 1e-4) return [p1, p2];
  const s = Math.sin(th), out = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, a = Math.sin((1-t)*th)/s, b = Math.sin(t*th)/s;
    out.push([a*p1[0]+b*p2[0], a*p1[1]+b*p2[1], a*p1[2]+b*p2[2]]);
  }
  return out;
}

function SphereMap({ onsetPt, offsetPt, placing, onPlace, showRegions }) {
  const ref = useRef(null);
  const rot = useRef({ yaw: 0.6, pitch: -0.35 });
  const drag = useRef(null);
  const [, force] = useState(0);

  const draw = useCallback(() => {
    const cv = ref.current; if (!cv) return;
    const dpr = window.devicePixelRatio || 1;
    const W = cv.clientWidth, H = 420;
    cv.width = W*dpr; cv.height = H*dpr;
    const g = cv.getContext("2d"); g.scale(dpr, dpr);
    g.fillStyle = "#0b0d12"; g.fillRect(0,0,W,H);
    const cx = W/2, cy = H/2, scale = (Math.min(W,H)/2 - 26) / R;
    const { yaw, pitch } = rot.current;
    const P = (p) => { const v = fwd(p, yaw, pitch); return [cx + scale*v[0], cy - scale*v[1], v[2]]; };
    // sphere disc
    g.beginPath(); g.arc(cx, cy, scale*R, 0, 2*Math.PI);
    g.fillStyle = "#12151d"; g.fill(); g.strokeStyle = "#222732"; g.lineWidth = 1; g.stroke();
    // dynamical-regime region shading (front-facing patches, batched by color)
    if (showRegions) {
      const { nLat, nLon, grid } = REG;
      const sp = REG_GV.map(P);                       // project all grid nodes
      const groups = { "#EBEBEB": [], "#E4B4D3": [], "#F8F6B8": [] };
      for (let i = 0; i < nLat - 1; i++) {
        const row = grid[i];
        for (let j = 0; j < nLon - 1; j++) {
          const a = sp[i*nLon+j], b = sp[i*nLon+j+1], c = sp[(i+1)*nLon+j+1], dd = sp[(i+1)*nLon+j];
          if (a[2] + b[2] + c[2] + dd[2] <= 0) continue;   // back-facing
          groups[REG_FILL[+row[j]]].push(a, b, c, dd);
        }
      }
      g.globalAlpha = 0.5;
      for (const col in groups) {
        const q = groups[col]; if (!q.length) continue;
        g.fillStyle = col; g.beginPath();
        for (let k = 0; k < q.length; k += 4) {
          g.moveTo(q[k][0], q[k][1]); g.lineTo(q[k+1][0], q[k+1][1]);
          g.lineTo(q[k+2][0], q[k+2][1]); g.lineTo(q[k+3][0], q[k+3][1]); g.closePath();
        }
        g.fill();
      }
      g.globalAlpha = 1;
    }
    // graticule (faint)
    g.strokeStyle = "rgba(120,130,150,0.10)"; g.lineWidth = 1;
    for (let lat=-60; lat<=60; lat+=30){ g.beginPath(); for(let lo=0;lo<=360;lo+=8){const la=lat*Math.PI/180,l=lo*Math.PI/180;const pt=[R*Math.cos(la)*Math.cos(l),R*Math.sin(la),R*Math.cos(la)*Math.sin(l)];const s=P(pt);lo===0?g.moveTo(s[0],s[1]):g.lineTo(s[0],s[1]);} g.stroke(); }
    // curves (back dim, front bright)
    for (const pass of [0,1]) {
      for (const cvr of MAP.curves) {
        g.strokeStyle = HUE[cvr.dyno] || "#999"; g.lineWidth = pass ? 2.4 : 1;
        g.globalAlpha = pass ? 1 : 0.18;
        g.beginPath(); let started=false;
        for (const q of cvr.pts) { const s=P(q); const front=s[2]>=0; if((pass===1)!==front){started=false;continue;} started?g.lineTo(s[0],s[1]):(g.moveTo(s[0],s[1]),started=true); }
        g.stroke();
      }
    }
    g.globalAlpha = 1;
    // arc path
    if (onsetPt && offsetPt) {
      const pts = arc(onsetPt, offsetPt);
      g.strokeStyle = "rgba(233,226,207,0.8)"; g.lineWidth = 2; g.setLineDash([5,4]); g.beginPath();
      pts.forEach((q,i)=>{const s=P(q); i?g.lineTo(s[0],s[1]):g.moveTo(s[0],s[1]);}); g.stroke(); g.setLineDash([]);
    }
    // markers
    const marker = (pt, color, txt) => { if(!pt)return; const s=P(pt); const front=s[2]>=0;
      g.globalAlpha=front?1:0.4; g.fillStyle=color; g.beginPath(); g.arc(s[0],s[1],7,0,2*Math.PI); g.fill();
      g.strokeStyle="#0b0d12"; g.lineWidth=2; g.stroke();
      g.fillStyle=C.ink; g.font="bold 11px system-ui"; g.fillText(txt, s[0]+10, s[1]-8); g.globalAlpha=1; };
    marker(onsetPt, "#e8748b", "onset");
    marker(offsetPt, "#67b3d9", "offset");
  }, [onsetPt, offsetPt, showRegions]);

  useEffect(draw);

  const onDown = (e) => { const r = ref.current.getBoundingClientRect(); drag.current = { x:e.clientX, y:e.clientY, moved:0, sx:e.clientX-r.left, sy:e.clientY-r.top }; };
  const onMove = (e) => { if(!drag.current)return; const dx=e.clientX-drag.current.x, dy=e.clientY-drag.current.y; drag.current.moved+=Math.abs(dx)+Math.abs(dy); rot.current.yaw+=dx*0.01; rot.current.pitch=Math.max(-1.4,Math.min(1.4,rot.current.pitch+dy*0.01)); drag.current.x=e.clientX; drag.current.y=e.clientY; draw(); };
  const onUp = (e) => {
    if (drag.current && drag.current.moved < 4) { // a click: place a marker
      const cv = ref.current, r = cv.getBoundingClientRect();
      const W = cv.clientWidth, H = 420, cx=W/2, cy=H/2, scale=(Math.min(W,H)/2-26)/R;
      const sx=(e.clientX-r.left-cx)/scale, sy=-(e.clientY-r.top-cy)/scale;
      const rr = sx*sx+sy*sy;
      if (rr <= R*R) {
        const sz = Math.sqrt(R*R-rr);
        const model = inv([sx,sy,sz], rot.current.yaw, rot.current.pitch);
        onPlace(model);
      }
    }
    drag.current = null;
  };
  return <canvas ref={ref}
    onMouseDown={onDown} onMouseMove={onMove} onMouseUp={onUp} onMouseLeave={()=>{drag.current=null;}}
    style={{ width:"100%", height:420, display:"block", borderRadius:12, cursor: placing?"crosshair":"grab", touchAction:"none" }} />;
}

export default function App() {
  // defaults: an onset (SN) and offset (FLC) point whose arc crosses the
  // seizure core, so the tool opens on a clean SN -> FLC seizure.
  const [onsetPt, setOnsetPt] = useState([0.2864, -0.059, 0.273]);
  const [offsetPt, setOffsetPt] = useState([-0.1721, -0.1011, -0.3467]);
  const [placing, setPlacing] = useState("onset");
  const [freq, setFreq] = useState(10);
  const [noise, setNoise] = useState(0.12);
  const [drift, setDrift] = useState(0.05);
  const [seed, setSeed] = useState(7);
  const [engine, setEngine] = useState("real"); // "real" | "normal"
  const [showRegions, setShowRegions] = useState(true);

  const onCurve = classify(onsetPt, "onset");
  const offCurve = classify(offsetPt, "offset");
  // map to valid dynamotype keys for each role
  const onsetKey = ONSET[onCurve?.dyno] ? onCurve.dyno : "SNIC";
  const offsetKey = OFFSET[offCurve?.dyno] ? offCurve.dyno : "SH";

  // The real fast-slow model integrated continuously along the onset->offset arc.
  // It self-detects whether the path actually produces a sustained seizure
  // (markers === null means it stayed at rest); this is the source of truth.
  const realOut = useMemo(
    () => realSimulate([onsetPt, offsetPt], { fs:200, dur:16, freq, noise, drift, seed }),
    [onsetPt, offsetPt, freq, noise, drift, seed]
  );
  const hasSeizure = realOut.markers != null;

  const out = useMemo(() => {
    if (engine === "real") return realOut;
    // normal-form engine: same rest/seizure verdict, but idealized per-dynamotype waveform
    if (!hasSeizure) return realSimulate([onsetPt, offsetPt], { fs:200, dur:16, freq, noise, drift, seed, quiescent:true });
    return synthesize(onsetKey, offsetKey, { fs:200, dur:16, freq, noise, drift, seed });
  }, [engine, realOut, hasSeizure, onsetKey, offsetKey, onsetPt, offsetPt, freq, noise, drift, seed]);

  const place = (model) => { placing === "onset" ? setOnsetPt(model) : setOffsetPt(model); };

  return (
    <div style={{ fontFamily:"system-ui,-apple-system,sans-serif", color:C.ink, background:C.bg, minHeight:"100vh", padding:"22px 18px" }}>
      <div style={{ maxWidth:1060, margin:"0 auto" }}>
        <h1 style={{ fontSize:22, margin:"0 0 4px" }}>Seizure dynamotype map explorer</h1>
        <p style={{ color:C.inkDim, fontSize:14, margin:"0 0 18px", maxWidth:760 }}>
          This is Saggio's parameter <b style={{color:C.ink}}>sphere</b>, shaded by dynamical regime, with the real bifurcation
          curves. Drag to rotate. Pick <span style={{color:"#e8748b"}}>onset</span> or <span style={{color:"#67b3d9"}}>offset</span> below,
          then click the sphere to place that waypoint. The model rests unless the dashed path runs through the
          <span style={{color:"#c98bb0"}}> seizure</span> region — route it through the pink to trigger a seizure; the bifurcation
          curves it crosses set the dynamotype.
        </p>
        <div style={{ display:"grid", gridTemplateColumns:"460px 1fr", gap:22, alignItems:"start" }}>
          <div>
            <div style={{ display:"flex", gap:8, marginBottom:8 }}>
              {["onset","offset"].map(role=>(
                <button key={role} onClick={()=>setPlacing(role)}
                  style={{ flex:1, padding:"8px 0", borderRadius:8, cursor:"pointer", fontSize:13,
                    border:`1.5px solid ${placing===role ? (role==="onset"?"#e8748b":"#67b3d9") : C.line}`,
                    background: placing===role ? (role==="onset"?"#e8748b22":"#67b3d922") : C.panel2,
                    color: placing===role ? C.ink : C.inkDim }}>
                  Place {role}
                </button>
              ))}
            </div>
            <SphereMap onsetPt={onsetPt} offsetPt={offsetPt} placing={placing} onPlace={place} showRegions={showRegions} />
            <label style={{ display:"flex", alignItems:"center", gap:7, marginTop:8, fontSize:12, color:C.inkDim, cursor:"pointer" }}>
              <input type="checkbox" checked={showRegions} onChange={e=>setShowRegions(e.target.checked)} style={{accentColor:"#cdb87a"}} />
              Shade dynamical regimes
            </label>
            {showRegions && (
              <div style={{ display:"flex", flexWrap:"wrap", gap:12, marginTop:6, fontSize:11.5, color:C.inkDim }}>
                {[["#EBEBEB","Active rest"],["#E4B4D3","Seizure"],["#F8F6B8","Bistable"]].map(([col,lab])=>(
                  <span key={lab} style={{display:"inline-flex",alignItems:"center",gap:5}}>
                    <span style={{width:13,height:13,borderRadius:3,background:col,display:"inline-block",opacity:0.7}} /> {lab}
                  </span>))}
              </div>
            )}
            <div style={{ display:"flex", flexWrap:"wrap", gap:10, marginTop:8, fontSize:11.5, color:C.inkDim }}>
              {MAP.curves.map(c=>(<span key={c.label} style={{display:"inline-flex",alignItems:"center",gap:5}}>
                <span style={{width:14,height:3,background:HUE[c.dyno],display:"inline-block"}} /> {c.label} ({c.role})
              </span>))}
            </div>
          </div>

          <div>
            <div style={{ background:C.panel, border:`1px solid ${C.line}`, borderRadius:12, padding:"12px 16px", marginBottom:14 }}>
              <div style={{ fontSize:12, color:C.inkFaint, textTransform:"uppercase", letterSpacing:1 }}>Detected dynamotype</div>
              {hasSeizure ? (<>
                <div style={{ fontSize:16, margin:"4px 0 2px" }}>
                  <span style={{color:"#e8748b"}}>{onsetKey}</span> onset → <span style={{color:"#67b3d9"}}>{offsetKey}</span> offset
                </div>
                <div style={{ fontSize:12.5, color:C.inkDim }}>{ONSET[onsetKey].name} / {OFFSET[offsetKey].name}</div>
              </>) : (<>
                <div style={{ fontSize:16, margin:"4px 0 2px", color:"#cdb87a" }}>No seizure</div>
                <div style={{ fontSize:12.5, color:C.inkDim }}>
                  The path stays in the resting region. Move a waypoint so the dashed arc crosses a bifurcation
                  curve into the <span style={{color:"#c98bb0"}}>seizure</span> region.
                </div>
              </>)}
            </div>
            <div style={{ background:C.panel, border:`1px solid ${C.line}`, borderRadius:12, padding:"12px 16px", marginBottom:14 }}>
              <div style={{ fontSize:12, color:C.inkFaint, textTransform:"uppercase", letterSpacing:1, marginBottom:8 }}>Signal engine</div>
              <div style={{ display:"flex", gap:8 }}>
                {[["real","Real model","integrates Saggio's fast-slow system along the arc"],
                  ["normal","Normal-form","fast analytic approximation per dynamotype"]].map(([key,label,desc])=>(
                  <button key={key} onClick={()=>setEngine(key)} title={desc}
                    style={{ flex:1, padding:"8px 0", borderRadius:8, cursor:"pointer", fontSize:13,
                      border:`1.5px solid ${engine===key ? "#cdb87a" : C.line}`,
                      background: engine===key ? "#cdb87a22" : C.panel2,
                      color: engine===key ? C.ink : C.inkDim }}>
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ background:C.panel, border:`1px solid ${C.line}`, borderRadius:12, padding:"6px 16px 14px", marginBottom:14 }}>
              <Slider label="Rhythmic frequency" value={freq} min={2} max={25} step={0.5} onChange={setFreq} fmt={(v)=>v.toFixed(1)+" Hz"} />
              <Slider label="Pink noise" value={noise} min={0} max={0.5} step={0.01} onChange={setNoise} fmt={(v)=>v.toFixed(2)} />
              <Slider label="Baseline drift" value={drift} min={0} max={0.3} step={0.01} onChange={setDrift} fmt={(v)=>v.toFixed(2)} />
              <button onClick={()=>setSeed(s=>s+1)} style={{ width:"100%", marginTop:2, padding:"8px 0", borderRadius:8, cursor:"pointer", border:`1px solid ${C.line}`, background:C.panel2, color:C.ink, fontSize:13 }}>↻ New noise seed</button>
            </div>
            <div style={{ fontSize:12.5, color:C.inkDim, marginBottom:4 }}>Simulated EEG</div>
            <TraceCanvas sig={out.sig} fs={out.fs} markers={out.markers} />
            <div style={{ fontSize:12.5, color:C.inkDim, margin:"14px 0 4px" }}>Spectrogram (0–40 Hz)</div>
            <SpectroCanvas sig={out.sig} fs={out.fs} />
            <p style={{ color:C.inkFaint, fontSize:11.5, marginTop:10, lineHeight:1.5 }}>
              The map geometry is the real exported Saggio bifurcation set, and the dynamotype is read off from which
              curves the path crosses. With <b style={{color:C.inkDim}}>Real model</b> the EEG comes from numerically
              integrating Saggio's actual fast-slow system along the great-circle arc through your waypoints;
              <b style={{color:C.inkDim}}> Normal-form</b> uses the faster analytic per-dynamotype approximation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
