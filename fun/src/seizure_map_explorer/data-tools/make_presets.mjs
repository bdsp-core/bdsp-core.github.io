// Generate src/data/presets.json: one preset per realizable onset x offset
// dynamotype class. For each pair we search our actual bifurcation curves for
// control points that produce a seizure the model classifies as that exact
// pair, choosing the simplest path type (arc -> circle -> piecewise) that works.
//
// Run from this directory:  node make_presets.mjs
import { simulate } from "../src/model.js";
import MAP from "../src/data/curves.json" with { type: "json" };
import { writeFileSync } from "node:fs";

const R = 0.4, TSTEP = 0.02;
const ICTAL = [-0.043, -0.209, -0.338];           // a vigorous seizure-core direction (model frame)

/* ---- geometry (mirrors App.jsx) ---- */
const onR = v => { const m = Math.hypot(...v) || 1e-9; return [v[0]/m*R, v[1]/m*R, v[2]/m*R]; };
const dot = (a,b) => a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
const cross = (a,b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
const segN = (ang,k) => Math.max(2, Math.round(ang/(k*TSTEP)));
function geoArc(A,B,k){ A=onR(A);B=onR(B); const th=Math.acos(Math.max(-1,Math.min(1,dot(A,B)/(R*R)))); if(th<1e-4)return[A.slice()]; const s=Math.sin(th),n=segN(th,k),o=[]; for(let i=0;i<=n;i++){const t=i/n,a=Math.sin((1-t)*th)/s,b=Math.sin(t*th)/s;o.push([a*A[0]+b*B[0],a*A[1]+b*B[1],a*A[2]+b*B[2]]);} return o; }
function circleArc(A,V,B,k){ A=onR(A);V=onR(V);B=onR(B); let nr=cross([V[0]-A[0],V[1]-A[1],V[2]-A[2]],[B[0]-A[0],B[1]-A[1],B[2]-A[2]]); const nl=Math.hypot(...nr); if(nl<1e-7)return geoArc(A,B,k); nr=[nr[0]/nl,nr[1]/nl,nr[2]/nl]; const d=dot(nr,A),C=[nr[0]*d,nr[1]*d,nr[2]*d],r=Math.sqrt(Math.max(1e-9,R*R-d*d)); let E=[A[0]-C[0],A[1]-C[1],A[2]-C[2]]; const el=Math.hypot(...E); E=[E[0]/el,E[1]/el,E[2]/el]; const F=cross(nr,E); const ang=p=>{const q=[p[0]-C[0],p[1]-C[1],p[2]-C[2]];return Math.atan2(dot(q,F),dot(q,E));}; const TAU=2*Math.PI,wrap=x=>{x%=TAU;return x<0?x+TAU:x;}; const aV=wrap(ang(V)),aB=wrap(ang(B)); let dir,total; if(aV<=aB){dir=1;total=aB;}else{dir=-1;total=TAU-aB;} const n=segN(total,k),o=[]; for(let i=0;i<=n;i++){const th=dir*total*i/n,c=Math.cos(th),s=Math.sin(th);o.push([C[0]+r*(c*E[0]+s*F[0]),C[1]+r*(c*E[1]+s*F[1]),C[2]+r*(c*E[2]+s*F[2])]);} return o; }
function piece(P,k){ let o=[]; for(let i=0;i<P.length-1;i++){const s=geoArc(P[i],P[i+1],k);o=o.concat(i?s.slice(1):s);} return o; }

/* ---- classify (mirrors App.jsx) ---- */
const minD = (p,cv) => { let m=1e9; for(const q of cv.pts){const d=Math.hypot(p[0]-q[0],p[1]-q[1],p[2]-q[2]); if(d<m)m=d;} return m; };
function classify(point, role){
  let best=1e9, hit=null;
  for(const cv of MAP.curves){ if(cv.role!=="both"&&cv.role!==role)continue; const dm=minD(point,cv); if(dm<best){best=dm;hit=cv;} }
  if(hit && role==="onset" && (hit.dyno==="SN"||hit.dyno==="SupH")){
    for(const d of ["SNIC","SubH"]){ const cv=MAP.curves.find(c=>c.dyno===d); if(cv&&minD(point,cv)<0.03)return cv; }
  }
  return hit;
}
const ONSET = new Set(["SN","SNIC","SupH","SubH"]);
const OFFSET = new Set(["SNIC","SH","SupH","FLC"]);
const ptsOf = dyno => [].concat(...MAP.curves.filter(c=>c.dyno===dyno).map(c=>c.pts));

const niceMargins = m => m && m.onset>0.08 && m.onset<0.45 && m.offset>0.55 && m.offset<0.94;

// score a candidate: returns {ok, score} — prefer clean margins, seizure present, correct class
function evalPath(path, oD, fD){
  const o = simulate(path, { fs:200, dur:16, freq:10, noise:0, drift:0, seed:7 });
  if(!o.markers) return null;
  const onPt = path[0], offPt = path[path.length-1];
  if(classify(onPt,"onset").dyno !== oD) return null;
  if(classify(offPt,"offset").dyno !== fD) return null;
  // score: closeness of margins to ideal (on 0.2 / off 0.8)
  const s = Math.abs(o.markers.onset-0.2) + Math.abs(o.markers.offset-0.8) + (niceMargins(o.markers)?0:0.5);
  return { score:s, markers:o.markers };
}

const FRACS = [0.15,0.3,0.45,0.6,0.75,0.9];
const VIA_CANDS = [ICTAL, [0.0,-0.3,-0.1], [-0.1,-0.25,0.1], [0.1,-0.28,-0.05], [-0.2,-0.2,-0.2]];
const K = 0.02;

// path type the DfD tutorial associates with each family
function preferType(oD, fD){
  if(oD === "SN" || oD === "SubH") return "arc";        // hysteresis-loop family
  if(oD === "SupH" && fD === "SupH") return "piecewise"; // piecewise family
  return "circle";                                       // slow-wave family
}

function searchType(type, A, B, oD, fD){
  const pick = (arr,f)=>arr[Math.floor(f*(arr.length-1))];
  let best=null;
  if(type==="arc"){
    for(const fa of FRACS) for(const fb of FRACS){ const on=pick(A,fa),off=pick(B,fb);
      const r=evalPath(geoArc(on,off,K),oD,fD); if(r&&(!best||r.score<best.score)) best={type,pts:[on,off],...r}; }
  } else if(type==="circle"){
    for(const fa of [0.2,0.4,0.6,0.8]) for(const fb of [0.2,0.4,0.6,0.8]) for(const via of VIA_CANDS){ const on=pick(A,fa),off=pick(B,fb);
      const r=evalPath(circleArc(on,via,off,K),oD,fD); if(r&&(!best||r.score<best.score)) best={type,pts:[on,via,off],...r}; }
  } else {
    for(const fa of [0.3,0.6]) for(const fb of [0.4,0.7]) for(const via of VIA_CANDS){ const on=pick(A,fa),off=pick(B,fb);
      const v2=[(via[0]+off[0])/2,(via[1]+off[1])/2,(via[2]+off[2])/2];
      const r=evalPath(piece([on,via,v2,off],K),oD,fD); if(r&&(!best||r.score<best.score)) best={type,pts:[on,via,v2,off],...r}; }
  }
  return best;
}

function findPreset(oD, fD){
  const A = ptsOf(oD).filter(p=>classify(p,"onset").dyno===oD);
  const B = ptsOf(fD).filter(p=>classify(p,"offset").dyno===fD);
  if(!A.length||!B.length) return null;
  const pref = preferType(oD, fD);
  const order = [pref, ...["arc","circle","piecewise"].filter(t=>t!==pref)];
  const found = {};
  for(const t of order){ const r = searchType(t, A, B, oD, fD); if(r) found[t]=r; }
  // use the preferred type if it verifies reasonably cleanly; else the best available
  if(found[pref] && found[pref].score < 0.8) return found[pref];
  let best=null; for(const t in found) if(!best||found[t].score<best.score) best=found[t];
  return best;
}

const round4 = p => p.map(v=>Math.round(v*1e4)/1e4);
const presets = [];
for(const oD of ["SN","SNIC","SupH","SubH"]) for(const fD of ["SH","FLC","SNIC","SupH"]){
  const r = findPreset(oD, fD);
  const name = `${oD} / ${fD}`;
  if(r){
    presets.push({ name, onset:oD, offset:fD, type:r.type, pts:r.pts.map(round4) });
    console.log(`${name.padEnd(14)} -> ${r.type.padEnd(9)} on${(r.markers.onset*100)|0}%/off${(r.markers.offset*100)|0}%`);
  } else {
    console.log(`${name.padEnd(14)} -> (no realizable path found)`);
  }
}
writeFileSync(new URL("../src/data/presets.json", import.meta.url), JSON.stringify(presets));
console.log(`\nwrote presets.json: ${presets.length} classes`);
