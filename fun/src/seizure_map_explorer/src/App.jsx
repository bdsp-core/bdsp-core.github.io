import React, { useState, useMemo, useRef, useEffect, useCallback } from "react";
import { C, HUE, ONSET, OFFSET, synthesize, TraceCanvas, SpectroCanvas, Slider } from "./synth.jsx";
import { simulate as realSimulate } from "./model.js";
import MAP from "./data/curves.json";
import REG from "./data/regions.json";
import PRESETS from "./data/presets.json";

/* ============================================================
   SEIZURE DYNAMOTYPE MAP EXPLORER  (Phase 2)
   Interactive 3D view of Saggio's parameter sphere with the real exported
   bifurcation curves. Place an onset and an offset waypoint; the tool finds
   the nearest onset/offset bifurcation curve to each, classifies the
   dynamotype, and synthesizes the seizure with the (validated Phase-1)
   signal engine — shown as trace + spectrogram.
   ============================================================ */

const R = MAP.radius; // 0.4

/* ---- region shading (dynamical-regime label grid from the MATLAB tutorial's
   testmesh.mat). Rendered per screen-pixel for smooth boundaries. ---- */
const REG_FILL = ["#EBEBEB", "#E4B4D3", "#F8F6B8", "#F8F6B8"]; // rest, seizure, bistable, bistable+LC
const SPHERE_BASE = [18, 21, 29]; // #12151d, the unshaded sphere disc colour
// region colours pre-blended over the disc base at 50% (opaque RGB triplets)
const REG_RGB = REG_FILL.map((hex) => {
  const r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
  return [Math.round(0.5 * SPHERE_BASE[0] + 0.5 * r),
          Math.round(0.5 * SPHERE_BASE[1] + 0.5 * g),
          Math.round(0.5 * SPHERE_BASE[2] + 0.5 * b)];
});
// region grid rows kept as strings; charCodeAt - 48 gives the region index
const REG_ROWS = REG.grid, REG_NLAT = REG.nLat, REG_NLON = REG.nLon;

/* ---- tiny 3D ---- */
const rotY = (p, a) => { const c = Math.cos(a), s = Math.sin(a); return [c*p[0] + s*p[2], p[1], -s*p[0] + c*p[2]]; };
const rotX = (p, b) => { const c = Math.cos(b), s = Math.sin(b); return [p[0], c*p[1] - s*p[2], s*p[1] + c*p[2]]; };
const fwd = (p, yaw, pitch) => rotX(rotY(p, yaw), pitch);          // model -> view
const inv = (p, yaw, pitch) => rotY(rotX(p, -pitch), -yaw);        // view -> model
const d3 = (a, b) => Math.hypot(a[0]-b[0], a[1]-b[1], a[2]-b[2]);

const minDistToCurve = (point, cv) => {
  let m = Infinity;
  for (const q of cv.pts) { const dd = d3(point, q); if (dd < m) m = dd; }
  return m;
};

/* Classify a waypoint by the nearest bifurcation curve (respecting role).
   SNIC and subcritical-Hopf are special points embedded in the larger
   saddle-node (SN) football and Hopf curve, so for ONSET we upgrade an SN/SupH
   hit to SNIC/SubH when the point is within a small band of those arcs. */
const SPECIAL_TOL = 0.03;
function classify(point, role) {
  let best = Infinity, hit = null;
  for (const cv of MAP.curves) {
    if (cv.role !== "both" && cv.role !== role) continue;
    const dm = minDistToCurve(point, cv);
    if (dm < best) { best = dm; hit = cv; }
  }
  if (hit && role === "onset" && (hit.dyno === "SN" || hit.dyno === "SupH")) {
    for (const dyno of ["SNIC", "SubH"]) {
      const cv = MAP.curves.find((c) => c.dyno === dyno);
      if (cv && minDistToCurve(point, cv) < SPECIAL_TOL) return cv;
    }
  }
  return hit;
}

/* ---- path geometry: turn control points into a dense sweep polyline ----
   The number of points sets the sweep speed, so density scales with 1/(k·tstep).
   Three path types (matching the DfD tutorial):
     arc       2 pts  great-circle geodesic
     circle    3 pts  small circle through onset, via, offset
     piecewise 4 pts  geodesic segments onset -> via1 -> via2 -> offset       */
const onR = (v) => { const m = Math.hypot(v[0],v[1],v[2]) || 1e-9; return [v[0]/m*R, v[1]/m*R, v[2]/m*R]; };
const dot3 = (a,b) => a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
const cross3 = (a,b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
const TSTEP = 0.02;
const segN = (ang, k) => Math.max(2, Math.round(ang / (k * TSTEP)));

/* great-circle arc A->B, density set by k */
function geoArc(A, B, k) {
  A = onR(A); B = onR(B);
  const th = Math.acos(Math.max(-1, Math.min(1, dot3(A,B)/(R*R))));
  if (th < 1e-4) return [A.slice()];
  const s = Math.sin(th), n = segN(th, k), out = [];
  for (let i = 0; i <= n; i++) {
    const t = i/n, a = Math.sin((1-t)*th)/s, b = Math.sin(t*th)/s;
    out.push([a*A[0]+b*B[0], a*A[1]+b*B[1], a*A[2]+b*B[2]]);
  }
  return out;
}

/* small circle through 3 sphere points; arc from A through V to B */
function circleArc(A, V, B, k) {
  A = onR(A); V = onR(V); B = onR(B);
  let nrm = cross3([V[0]-A[0],V[1]-A[1],V[2]-A[2]], [B[0]-A[0],B[1]-A[1],B[2]-A[2]]);
  const nl = Math.hypot(...nrm);
  if (nl < 1e-7) return geoArc(A, B, k);          // collinear -> geodesic
  nrm = [nrm[0]/nl, nrm[1]/nl, nrm[2]/nl];
  const d = dot3(nrm, A);                          // signed origin->plane distance
  const C = [nrm[0]*d, nrm[1]*d, nrm[2]*d];        // circle centre
  const r = Math.sqrt(Math.max(1e-9, R*R - d*d));
  let E = [A[0]-C[0], A[1]-C[1], A[2]-C[2]]; const el = Math.hypot(...E); E = [E[0]/el,E[1]/el,E[2]/el];
  const F = cross3(nrm, E);                         // unit (n ⟂ E, both unit)
  const ang = (p) => { const q=[p[0]-C[0],p[1]-C[1],p[2]-C[2]]; return Math.atan2(dot3(q,F), dot3(q,E)); };
  const TAU = 2*Math.PI, wrap = (x) => { x %= TAU; return x < 0 ? x + TAU : x; };
  const aV = wrap(ang(V)), aB = wrap(ang(B));       // aA = 0 (E points to A)
  let dir, total;
  if (aV <= aB) { dir = 1; total = aB; } else { dir = -1; total = TAU - aB; } // arc through V
  const n = segN(total, k), out = [];
  for (let i = 0; i <= n; i++) {
    const th = dir * total * i / n, c = Math.cos(th), s = Math.sin(th);
    out.push([C[0]+r*(c*E[0]+s*F[0]), C[1]+r*(c*E[1]+s*F[1]), C[2]+r*(c*E[2]+s*F[2])]);
  }
  return out;
}

/* dense polyline for the chosen path type from its control points */
function genPath(type, pts, k) {
  if (type === "circle" && pts.length >= 3) return circleArc(pts[0], pts[1], pts[2], k);
  if (type === "piecewise" && pts.length >= 4) {
    let out = [];
    for (let i = 0; i < pts.length - 1; i++) { const seg = geoArc(pts[i], pts[i+1], k); out = out.concat(i ? seg.slice(1) : seg); }
    return out;
  }
  return geoArc(pts[0], pts[pts.length - 1], k);     // arc (or fallback)
}

const PATH_NPTS = { arc: 2, circle: 3, piecewise: 4 };

/* point at fraction f along the great circle A->B (for seeding via points) */
function slerpPt(A, B, f) {
  A = onR(A); B = onR(B);
  const th = Math.acos(Math.max(-1, Math.min(1, dot3(A,B)/(R*R))));
  if (th < 1e-4) return A.slice();
  const s = Math.sin(th), a = Math.sin((1-f)*th)/s, b = Math.sin(f*th)/s;
  return [a*A[0]+b*B[0], a*A[1]+b*B[1], a*A[2]+b*B[2]];
}

const ptColor = (i, n) => (i === 0 ? "#e8748b" : i === n - 1 ? "#67b3d9" : "#cdb87a");
const ptLabel = (i, n) => (i === 0 ? "onset" : i === n - 1 ? "offset" : (n === 4 ? `via ${i}` : "via"));

function SphereMap({ pts, path, selected, onPlace, onDragPoint, showRegions, opaque }) {
  const ref = useRef(null);
  const off = useRef(null); // offscreen buffer for the per-pixel region layer
  const regKey = useRef(null); // cache key (rotation/size) for that buffer
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
    const rad = scale * R;
    // sphere disc: smooth per-pixel dynamical-regime shading, or a plain fill
    if (showRegions) {
      let oc = off.current;
      if (!oc) oc = off.current = document.createElement("canvas");
      if (oc.width !== W || oc.height !== H) { oc.width = W; oc.height = H; }
      // the region layer only depends on rotation + size; recompute just when
      // those change (so dragging handles, which don't rotate, stays cheap).
      const key = `${yaw.toFixed(4)},${pitch.toFixed(4)},${W},${H}`;
      if (regKey.current !== key) { regKey.current = key;
      const og = oc.getContext("2d");
      const img = og.createImageData(W, H), data = img.data;
      // view -> model rotation: rotX(-pitch) then rotY(-yaw)
      const ca = Math.cos(pitch), sa = -Math.sin(pitch);
      const cb = Math.cos(yaw),   sb = -Math.sin(yaw);
      const R2 = R * R, invScale = 1 / scale, TAU = 2 * Math.PI, HALFPI = Math.PI / 2;
      const yLo = Math.max(0, (cy - rad) | 0), yHi = Math.min(H, Math.ceil(cy + rad));
      const xLo = Math.max(0, (cx - rad) | 0), xHi = Math.min(W, Math.ceil(cx + rad));
      for (let py = yLo; py < yHi; py++) {
        const sy = -(py - cy) * invScale, base = py * W;
        for (let px = xLo; px < xHi; px++) {
          const sx = (px - cx) * invScale, rr = sx * sx + sy * sy;
          if (rr > R2) continue;                       // outside disc -> transparent
          const sz = Math.sqrt(R2 - rr);
          const z1 = sa * sy + ca * sz;                // rotX(-pitch)
          const ym = ca * sy - sa * sz;
          const xm = cb * sx + sb * z1, zm = -sb * sx + cb * z1; // rotY(-yaw)
          let t = ym / R; t = t > 1 ? 1 : t < -1 ? -1 : t;
          const i = (((Math.asin(t) + HALFPI) / Math.PI) * (REG_NLAT - 1) + 0.5) | 0;
          let lon = Math.atan2(zm, xm); if (lon < 0) lon += TAU;
          const j = ((lon / TAU) * (REG_NLON - 1) + 0.5) | 0;
          const c = REG_RGB[REG_ROWS[i].charCodeAt(j) - 48];
          const o = (base + px) * 4;
          data[o] = c[0]; data[o + 1] = c[1]; data[o + 2] = c[2]; data[o + 3] = 255;
        }
      }
      og.putImageData(img, 0, 0);
      }
      g.drawImage(oc, 0, 0, W, H);                      // upscaled to device px (smooths edges)
      g.beginPath(); g.arc(cx, cy, rad, 0, 2 * Math.PI); g.strokeStyle = "#222732"; g.lineWidth = 1; g.stroke();
    } else {
      g.beginPath(); g.arc(cx, cy, rad, 0, 2 * Math.PI);
      g.fillStyle = "#12151d"; g.fill(); g.strokeStyle = "#222732"; g.lineWidth = 1; g.stroke();
    }
    // graticule (faint). When opaque, draw only the front-facing half.
    g.strokeStyle = "rgba(120,130,150,0.10)"; g.lineWidth = 1;
    for (let lat=-60; lat<=60; lat+=30){ g.beginPath(); let st=false; for(let lo=0;lo<=360;lo+=8){const la=lat*Math.PI/180,l=lo*Math.PI/180;const pt=[R*Math.cos(la)*Math.cos(l),R*Math.sin(la),R*Math.cos(la)*Math.sin(l)];const s=P(pt); if(opaque&&s[2]<0){st=false;continue;} st?g.lineTo(s[0],s[1]):(g.moveTo(s[0],s[1]),st=true);} g.stroke(); }
    // curves: front bright; back dim only when see-through. Some dashed (subcritical).
    for (const pass of (opaque ? [1] : [0,1])) {
      for (const cvr of MAP.curves) {
        g.strokeStyle = HUE[cvr.dyno] || "#999"; g.lineWidth = pass ? 2.4 : 1;
        g.globalAlpha = pass ? 1 : 0.18;
        g.setLineDash(cvr.dash ? [6,4] : []);
        g.beginPath(); let started=false;
        for (const q of cvr.pts) { const s=P(q); const front=s[2]>=0; if((pass===1)!==front){started=false;continue;} started?g.lineTo(s[0],s[1]):(g.moveTo(s[0],s[1]),started=true); }
        g.stroke();
      }
    }
    g.setLineDash([]); g.globalAlpha = 1;
    // the seizure path (dashed). When opaque, hide the part behind the sphere.
    if (path && path.length) {
      g.strokeStyle = "rgba(233,226,207,0.85)"; g.lineWidth = 2; g.setLineDash([5,4]); g.beginPath(); let st=false;
      path.forEach((q)=>{const s=P(q); if(opaque&&s[2]<0){st=false;return;} st?g.lineTo(s[0],s[1]):(g.moveTo(s[0],s[1]),st=true);}); g.stroke(); g.setLineDash([]);
    }
    // control-point handles (onset / via / offset). Opaque -> occlude the back.
    const n = pts.length;
    pts.forEach((pt, i) => {
      const s = P(pt), front = s[2] >= 0;
      if (opaque && !front) return;
      g.globalAlpha = front ? 1 : 0.4;
      if (i === selected) { g.beginPath(); g.arc(s[0], s[1], 10, 0, 2*Math.PI); g.strokeStyle = "#e9e2cf"; g.lineWidth = 2; g.stroke(); }
      g.fillStyle = ptColor(i, n); g.beginPath(); g.arc(s[0], s[1], 7, 0, 2*Math.PI); g.fill();
      g.strokeStyle = "#0b0d12"; g.lineWidth = 2; g.stroke();
      g.fillStyle = C.ink; g.font = "bold 11px system-ui"; g.fillText(ptLabel(i, n), s[0]+11, s[1]-8); g.globalAlpha = 1;
    });
  }, [pts, path, selected, showRegions, opaque]);

  useEffect(draw);

  // screen geometry + view->model unprojection shared by the handlers
  const geom = () => { const cv = ref.current, r = cv.getBoundingClientRect(); const W = cv.clientWidth, H = 420; return { r, W, H, cx: W/2, cy: H/2, scale: (Math.min(W,H)/2-26)/R }; };
  const toModel = (e) => { const { r, cx, cy, scale } = geom();
    const sx=(e.clientX-r.left-cx)/scale, sy=-(e.clientY-r.top-cy)/scale, rr=sx*sx+sy*sy;
    if (rr > R*R) return null;
    return inv([sx, sy, Math.sqrt(R*R-rr)], rot.current.yaw, rot.current.pitch); };
  // index of a control-point handle under the cursor (front-facing), or -1
  const hitHandle = (e) => { const { r, cx, cy, scale } = geom(), mx=e.clientX-r.left, my=e.clientY-r.top;
    for (let i = 0; i < pts.length; i++) { const v = fwd(pts[i], rot.current.yaw, rot.current.pitch);
      if (opaque && v[2] < 0) continue;
      const px = cx + scale*v[0], py = cy - scale*v[1];
      if (Math.hypot(mx-px, my-py) <= 11) return i; }
    return -1; };

  const onDown = (e) => { const hit = hitHandle(e); drag.current = { x:e.clientX, y:e.clientY, moved:0, point: hit }; };
  const onMove = (e) => { if(!drag.current)return;
    const dx=e.clientX-drag.current.x, dy=e.clientY-drag.current.y; drag.current.moved+=Math.abs(dx)+Math.abs(dy);
    if (drag.current.point >= 0) { const m = toModel(e); if (m) onDragPoint(drag.current.point, m); }
    else { rot.current.yaw+=dx*0.01; rot.current.pitch=Math.max(-1.4,Math.min(1.4,rot.current.pitch+dy*0.01)); draw(); }
    drag.current.x=e.clientX; drag.current.y=e.clientY; };
  const onUp = (e) => {
    if (drag.current && drag.current.moved < 4 && drag.current.point < 0) { // a click on empty sphere: place the selected point
      const m = toModel(e); if (m) onPlace(m);
    }
    drag.current = null;
  };
  return <canvas ref={ref}
    onMouseDown={onDown} onMouseMove={onMove} onMouseUp={onUp} onMouseLeave={()=>{drag.current=null;}}
    style={{ width:"100%", height:420, display:"block", borderRadius:12, cursor:"crosshair", touchAction:"none" }} />;
}

export default function App() {
  // path: control points (onset = first, offset = last, middle = via points).
  // Default opens on a clean SupH -> FLC arc (smooth onset/offset ramps).
  const [pathType, setPathType] = useState("arc"); // "arc" | "circle" | "piecewise"
  const [pts, setPts] = useState([[-0.242, -0.200, 0.247], [0.152, 0.039, -0.368]]);
  const [selected, setSelected] = useState(0);
  const [freq, setFreq] = useState(10);
  const [noise, setNoise] = useState(0.12);
  const [drift, setDrift] = useState(0.05);
  const [k, setK] = useState(0.02); // slow-sweep speed (kappa): higher = faster, sharper transitions
  const [seed, setSeed] = useState(7);
  const [engine, setEngine] = useState("real"); // "real" | "normal"
  const [showRegions, setShowRegions] = useState(true);
  const [opaque, setOpaque] = useState(true); // hide back-hemisphere curves/markers

  const onsetPt = pts[0], offsetPt = pts[pts.length - 1];
  const onCurve = classify(onsetPt, "onset");
  const offCurve = classify(offsetPt, "offset");
  // map to valid dynamotype keys for each role
  const onsetKey = ONSET[onCurve?.dyno] ? onCurve.dyno : "SNIC";
  const offsetKey = OFFSET[offCurve?.dyno] ? offCurve.dyno : "SH";

  // dense sweep polyline for the chosen path type (k sets the sweep speed)
  const pathPoly = useMemo(() => genPath(pathType, pts, k), [pathType, pts, k]);

  // The real fast-slow model integrated continuously along the path. It self-
  // detects whether a sustained seizure occurs (markers === null = stayed at rest).
  const realOut = useMemo(
    () => realSimulate(pathPoly, { fs:200, dur:16, freq, noise, drift, seed }),
    [pathPoly, freq, noise, drift, seed]
  );
  const hasSeizure = realOut.markers != null;

  const out = useMemo(() => {
    if (engine === "real") return realOut;
    // normal-form engine: same rest/seizure verdict, but idealized per-dynamotype waveform
    if (!hasSeizure) return realSimulate(pathPoly, { fs:200, dur:16, freq, noise, drift, seed, quiescent:true });
    return synthesize(onsetKey, offsetKey, { fs:200, dur:16, freq, noise, drift, seed });
  }, [engine, realOut, hasSeizure, onsetKey, offsetKey, pathPoly, freq, noise, drift, seed]);

  // load a canonical dynamotype-class preset (sets path type + control points)
  const loadPreset = (name) => {
    const p = PRESETS.find((x) => x.name === name);
    if (!p) return;
    setPathType(p.type); setPts(p.pts.map((q) => q.slice())); setSelected(0);
  };

  const place = (m) => setPts((p) => p.map((q, i) => (i === selected ? m : q)));
  const dragPoint = (idx, m) => { setSelected(idx); setPts((p) => p.map((q, i) => (i === idx ? m : q))); };
  // switch path type: keep onset/offset, add/remove via points along the geodesic
  const changeType = (t) => {
    const need = PATH_NPTS[t];
    setPts((prev) => {
      const A = prev[0], B = prev[prev.length - 1];
      const out = [A];
      for (let i = 1; i <= need - 2; i++) out.push(slerpPt(A, B, i / (need - 1)));
      out.push(B);
      return out;
    });
    setSelected(0); setPathType(t);
  };

  return (
    <div style={{ fontFamily:"system-ui,-apple-system,sans-serif", color:C.ink, background:C.bg, minHeight:"100vh", padding:"22px 18px" }}>
      <div style={{ maxWidth:1060, margin:"0 auto" }}>
        <h1 style={{ fontSize:22, margin:"0 0 4px" }}>Seizure dynamotype map explorer</h1>
        <p style={{ color:C.inkDim, fontSize:14, margin:"0 0 18px", maxWidth:760 }}>
          This is Saggio's parameter <b style={{color:C.ink}}>sphere</b>, shaded by dynamical regime, with the real bifurcation
          curves. Drag the background to rotate, and <b style={{color:C.ink}}>drag the handles</b> to move the
          <span style={{color:"#e8748b"}}> onset</span>, <span style={{color:"#67b3d9"}}>offset</span>, and <span style={{color:"#cdb87a"}}>via</span> points.
          Choose a path type — <b style={{color:C.ink}}>arc</b>, <b style={{color:C.ink}}>circle</b>, or <b style={{color:C.ink}}>piecewise</b> — to route through
          parts of the map a straight arc can't reach. The model rests unless the dashed path runs through the
          <span style={{color:"#c98bb0"}}> seizure</span> region; the bifurcation curves it crosses set the dynamotype.
        </p>
        <div style={{ display:"grid", gridTemplateColumns:"460px 1fr", gap:22, alignItems:"start" }}>
          <div>
            <select value="" onChange={(e)=>{ if(e.target.value){ loadPreset(e.target.value); e.target.value=""; } }}
              style={{ width:"100%", marginBottom:8, padding:"8px 10px", borderRadius:8, fontSize:13,
                border:`1px solid ${C.line}`, background:C.panel2, color:C.ink, cursor:"pointer" }}>
              <option value="">Load a dynamotype class…</option>
              {PRESETS.map(p=>(
                <option key={p.name} value={p.name}>{p.name}  ({p.type})</option>
              ))}
            </select>
            <div style={{ display:"flex", gap:8, marginBottom:8 }}>
              {[["arc","Arc"],["circle","Circle"],["piecewise","Piecewise"]].map(([t,lab])=>(
                <button key={t} onClick={()=>changeType(t)}
                  style={{ flex:1, padding:"7px 0", borderRadius:8, cursor:"pointer", fontSize:13,
                    border:`1.5px solid ${pathType===t ? "#cdb87a" : C.line}`,
                    background: pathType===t ? "#cdb87a22" : C.panel2, color: pathType===t ? C.ink : C.inkDim }}>
                  {lab}
                </button>
              ))}
            </div>
            <div style={{ display:"flex", gap:6, marginBottom:8, alignItems:"center" }}>
              <span style={{ fontSize:11.5, color:C.inkFaint }}>Place / drag:</span>
              {pts.map((_, i)=>(
                <button key={i} onClick={()=>setSelected(i)}
                  style={{ flex:1, padding:"6px 0", borderRadius:7, cursor:"pointer", fontSize:12,
                    border:`1.5px solid ${selected===i ? ptColor(i, pts.length) : C.line}`,
                    background: selected===i ? ptColor(i, pts.length)+"22" : C.panel2,
                    color: selected===i ? C.ink : C.inkDim, textTransform:"capitalize" }}>
                  {ptLabel(i, pts.length)}
                </button>
              ))}
            </div>
            <SphereMap pts={pts} path={pathPoly} selected={selected} onPlace={place} onDragPoint={dragPoint} showRegions={showRegions} opaque={opaque} />
            <div style={{ display:"flex", alignItems:"center", gap:16, marginTop:8, fontSize:12, color:C.inkDim }}>
              <label style={{ display:"flex", alignItems:"center", gap:7, cursor:"pointer" }}>
                <input type="checkbox" checked={showRegions} onChange={e=>setShowRegions(e.target.checked)} style={{accentColor:"#cdb87a"}} />
                Shade dynamical regimes
              </label>
              <button onClick={()=>setOpaque(o=>!o)}
                style={{ padding:"5px 11px", borderRadius:7, cursor:"pointer", fontSize:12,
                  border:`1px solid ${C.line}`, background:C.panel2, color:C.inkDim }}>
                Sphere: {opaque ? "opaque" : "see-through"}
              </button>
            </div>
            {showRegions && (
              <div style={{ display:"flex", flexWrap:"wrap", gap:12, marginTop:6, fontSize:11.5, color:C.inkDim }}>
                {[["#EBEBEB","Active rest"],["#E4B4D3","Seizure"],["#F8F6B8","Bistable"]].map(([col,lab])=>(
                  <span key={lab} style={{display:"inline-flex",alignItems:"center",gap:5}}>
                    <span style={{width:13,height:13,borderRadius:3,background:col,display:"inline-block",opacity:0.7}} /> {lab}
                  </span>))}
              </div>
            )}
            <div style={{ display:"flex", flexWrap:"wrap", gap:10, marginTop:8, fontSize:11.5, color:C.inkDim }}>
              {Array.from(new Map(MAP.curves.map(c=>[c.label,c])).values()).map(c=>(
                <span key={c.label} style={{display:"inline-flex",alignItems:"center",gap:5}}>
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
              {engine === "real" && (
                <Slider label="Transition speed (κ)" value={k} min={0.01} max={0.06} step={0.005} onChange={setK} fmt={(v)=>v.toFixed(3)} />
              )}
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
