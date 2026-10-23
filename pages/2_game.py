# pages/2_game.py
# CRISPR-Cas9 유전자 가위 실습실 (드래그 앤 드롭 게임)
#
# SyntaxError 방지 설계
#  - HTML/CSS/JS 는 f-string 이 아닌 "일반 문자열" 상수(GAME_HTML)로 둔다.
#    -> 중괄호 { } 를 이스케이프할 필요가 없다.
#  - 파이썬 데이터는 __CONFIG__ 자리표시자 하나만 JSON 으로 치환해서 넘긴다.

import json
import random

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="유전자 가위 실습실", page_icon="🧬", layout="wide")

# ---------------------------------------------------------------------------
# 1) 1페이지에서 넘어온 gRNA 정보 읽기 (구조가 달라도 최대한 견디도록 방어적으로 작성)
# ---------------------------------------------------------------------------
DEMO_SPACER = "CTTGCCCCACAGGGCAGTAA"  # 1페이지 선택값이 없을 때 쓰는 예시 서열


def _clean(seq):
    s = str(seq).upper().replace("U", "T")
    return "".join(c for c in s if c in "ACGT")


def _to_dict(sel):
    if sel is None:
        return {}
    if isinstance(sel, dict):
        return sel
    if hasattr(sel, "to_dict"):  # pandas Series 등
        try:
            return sel.to_dict()
        except Exception:
            return {}
    if isinstance(sel, str):
        return {"sequence": sel}
    return {}


def _find_number(d, key_part):
    for k, v in d.items():
        if key_part in str(k).lower():
            try:
                return round(float(v), 3)
            except (TypeError, ValueError):
                return None
    return None


def build_config():
    d = _to_dict(st.session_state.get("selected_top_grna"))
    spacer, pam, demo = "", "", False

    for cand in ("grna", "guide", "spacer", "sequence", "seq"):
        for k, v in d.items():
            if cand in str(k).lower() and isinstance(v, str):
                s = _clean(v)
                if len(s) >= 20:
                    spacer = s[:20]
                    if len(s) >= 23 and s[21:23] == "GG":
                        pam = s[20:23]
                    break
        if spacer:
            break

    if not spacer:
        spacer, demo = DEMO_SPACER, True

    gene = ""
    for k, v in d.items():
        if "gene" in str(k).lower():
            gene = str(v)
            break

    return {
        "spacer": spacer,
        "pam": pam,
        "gene": gene or "예시 유전자",
        "mit": _find_number(d, "mit"),
        "doench": _find_number(d, "doench"),
        "demo": demo,
        "seed": random.randint(1, 10**6),
    }


# ---------------------------------------------------------------------------
# 2) 게임 본체 (일반 문자열: 중괄호 자유롭게 사용 가능)
# ---------------------------------------------------------------------------
GAME_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{
  --bg:#0d1b26; --panel:#14293a; --ink:#e8f1f5; --mute:#8fa6b5; --line:#2a4259;
  --rna:#ff9a2e; --cas:#3ddc84; --dna1:#6fb8ff; --bad:#ff5d6c; --gold:#ffe14d;
}
*{box-sizing:border-box}
html,body{margin:0}
body{
  background:var(--bg); color:var(--ink); padding:14px 16px 18px; border-radius:14px;
  font-family:"Pretendard","Noto Sans KR","Malgun Gothic","Apple SD Gothic Neo",sans-serif;
}
header{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
h1{font-size:20px;margin:0;font-weight:700}
.tgt{font-size:13px;color:var(--mute)}
.tgt b{color:var(--rna);font-family:ui-monospace,Consolas,"D2Coding",monospace;font-weight:600}

#steps{list-style:none;display:flex;gap:8px;padding:0;margin:12px 0;counter-reset:s}
#steps li{counter-increment:s;flex:1;padding:8px 10px;border:1px solid var(--line);
  border-radius:8px;font-size:13px;color:var(--mute);transition:all .3s}
#steps li::before{content:counter(s) ". "}
#steps li.active{border-color:var(--rna);color:var(--ink);background:#1b3248}
#steps li.done{border-color:var(--cas);color:var(--cas)}

#msg{min-height:44px;padding:10px 12px;border-radius:8px;background:var(--panel);
  font-size:14px;line-height:1.5;margin-bottom:8px;border-left:4px solid var(--dna1)}
#msg.bad{border-left-color:var(--bad)}
#msg.good{border-left-color:var(--cas)}

svg{width:100%;height:auto;display:block;border-radius:12px;background:#0a1620;touch-action:none;user-select:none}
.lt{font-family:ui-monospace,Consolas,"D2Coding",monospace;font-weight:700;font-size:13px;fill:#0b1620;pointer-events:none}
.cap{font-size:12px;fill:#8fa6b5}

.base{transition:transform .7s cubic-bezier(.3,1.5,.5,1)}
.base .t{transition:transform .8s cubic-bezier(.3,1.4,.5,1)}
.base .r{opacity:0;transition:opacity .6s .25s}
.base.open .t{transform:translateY(-46px)}
.base.open .r{opacity:1}
.base.left{transform:translateX(-16px)}
.base.right{transform:translateX(16px)}

.drag{cursor:grab}
.grab{cursor:grabbing}
.glow{filter:drop-shadow(0 0 12px #3ddc84)}
.pulse{animation:pulse 1.2s ease-in-out infinite}
@keyframes pulse{50%{opacity:.4}}
.burst{transform-box:fill-box;transform-origin:center;animation:burst .9s ease-out forwards}
@keyframes burst{from{transform:scale(.1);opacity:1}to{transform:scale(1);opacity:0}}
.shake{animation:shake .4s}
@keyframes shake{25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}

#ctrl{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.btn{border:1px solid var(--line);background:var(--panel);color:var(--ink);padding:9px 14px;
  border-radius:8px;font-size:14px;cursor:pointer;font-family:inherit}
.btn:hover{border-color:var(--dna1)}
.btn:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
.btn.main{background:var(--rna);border-color:var(--rna);color:#2a1700;font-weight:700}

#result{margin-top:12px}
#result .card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
#result h2{margin:0 0 8px;font-size:17px}
#result p{margin:6px 0;font-size:14px;line-height:1.6}
.seq{font-family:ui-monospace,Consolas,"D2Coding",monospace;font-size:14px;letter-spacing:1px;
  background:#0a1620;border-radius:6px;padding:8px 10px;overflow-x:auto;white-space:nowrap}
.seq .m{background:var(--rna);color:#2a1700;border-radius:2px}
.seq .del{background:var(--bad);color:#2a0008;border-radius:2px}
.lbl{font-size:12px;color:var(--mute);margin-top:8px}

@media (prefers-reduced-motion: reduce){
  .base,.base .t,.base .r{transition:none}
  .pulse,.burst,.shake{animation:none}
}
@media (max-width:640px){ #steps{flex-direction:column} }
</style>
</head>
<body>
<header>
  <h1>유전자 가위 실습실</h1>
  <div class="tgt" id="tgt"></div>
</header>

<ol id="steps">
  <li>gRNA와 Cas9 결합</li>
  <li>표적 DNA에 결합</li>
  <li>DNA 절단</li>
  <li>수리와 결과</li>
</ol>

<div id="msg"></div>

<svg id="stage" viewBox="0 0 900 520" role="img" aria-label="유전자 가위 시뮬레이션 화면">
  <defs>
    <radialGradient id="casG" cx="50%" cy="40%" r="70%">
      <stop offset="0" stop-color="#4be59a"/>
      <stop offset="1" stop-color="#1c8f56"/>
    </radialGradient>
    <pattern id="dots" width="26" height="26" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.2" fill="#16303f"/>
    </pattern>
  </defs>
</svg>

<div id="ctrl"></div>
<div id="result"></div>

<script>
(function(){
"use strict";
var CFG = __CONFIG__;

var NS = "http://www.w3.org/2000/svg";
var svg = document.getElementById("stage");
var msgEl = document.getElementById("msg");
var ctrl = document.getElementById("ctrl");
var resEl = document.getElementById("result");
var stepEls = Array.prototype.slice.call(document.querySelectorAll("#steps li"));

var W = 900;
var DX = 22;
var YT = 392, YB = 434;           // 위쪽/아래쪽 가닥의 y
var FL = 8, FR = 6;               // 좌/우 flank 길이
var PAM_START = FL + 20;          // 28
var CUT_AFTER = FL + 16;          // 24: 이 인덱스까지 왼쪽, 다음부터 오른쪽
var CAS_HOME = {x: 690, y: 150};
var GR_HOME = {x: 150, y: 150};
var CAS_BOUND_Y = 262;

var COMP = {A: "T", T: "A", G: "C", C: "G"};
var COLORS = {A: "#ff8fa3", T: "#ffd166", G: "#67e3a5", C: "#74c0ff"};

/* ---------- 서열 만들기 (한 번만) ---------- */
function hashStr(s){
  var h = 2166136261;
  for (var i = 0; i < s.length; i++){ h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
function mulberry(a){
  return function(){
    a |= 0; a = a + 0x6D2B79F5 | 0;
    var t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
var rnd = mulberry(hashStr(CFG.spacer) ^ CFG.seed);
function randBase(){ return "ACGT".charAt(Math.floor(rnd() * 4)); }
function randSeq(n){ var s = ""; for (var i = 0; i < n; i++) s += randBase(); return s; }

var SP = CFG.spacer;
var PAM = (CFG.pam && CFG.pam.length === 3) ? CFG.pam : (randBase() + "GG");
var FULL = randSeq(FL) + SP + PAM + randSeq(FR);
var N = FULL.length;
var X0 = (W - N * DX) / 2;
var TARGET_X = X0 + (FL + 11.5) * DX;

/* ---------- 작은 도우미들 ---------- */
function el(name, attrs, parent){
  var e = document.createElementNS(NS, name);
  for (var k in attrs){ if (Object.prototype.hasOwnProperty.call(attrs, k)) e.setAttribute(k, attrs[k]); }
  if (parent) parent.appendChild(e);
  return e;
}
function svgPt(ev){
  var p = svg.createSVGPoint();
  p.x = ev.clientX; p.y = ev.clientY;
  return p.matrixTransform(svg.getScreenCTM().inverse());
}
function setPos(g, x, y){
  g._x = x; g._y = y;
  g.setAttribute("transform", "translate(" + x + " " + y + ")");
}
function tween(g, x, y, ms, cb){
  var x0 = g._x, y0 = g._y, t0 = performance.now();
  function f(t){
    var k = Math.min(1, (t - t0) / ms);
    var e = 1 - Math.pow(1 - k, 3);
    setPos(g, x0 + (x - x0) * e, y0 + (y - y0) * e);
    if (k < 1) requestAnimationFrame(f); else if (cb) cb();
  }
  requestAnimationFrame(f);
}
function clamp(v, a, b){ return Math.max(a, Math.min(b, v)); }
function dist(a, b){ return Math.hypot(a._x - b._x, a._y - b._y); }

function setMsg(t, kind){ msgEl.textContent = t; msgEl.className = kind || ""; }
function setStep(k){
  stepEls.forEach(function(li, i){
    li.className = i < k ? "done" : (i === k ? "active" : "");
  });
}
function setCtrl(list){
  ctrl.innerHTML = "";
  list.forEach(function(b){
    var x = document.createElement("button");
    x.className = "btn " + (b.cls || "");
    x.textContent = b.label;
    x.onclick = b.fn;
    ctrl.appendChild(x);
  });
}

/* ---------- 상태 ---------- */
var state, penalty, cas, gr, gDNA, cutLine, hintEl, bases, pamBox, pamLbl, scanner;

function tile(parent, cls, cx, cy, ch, fill){
  var g = el("g", {"class": cls}, parent);
  el("rect", {x: cx - 9.5, y: cy - 11, width: 19, height: 22, rx: 4, fill: fill}, g);
  var t = el("text", {x: cx, y: cy + 4.5, "text-anchor": "middle", "class": "lt"}, g);
  t.textContent = ch;
  return g;
}

function build(){
  // defs 만 남기고 모두 제거
  Array.prototype.slice.call(svg.children).forEach(function(c){
    if (c.tagName.toLowerCase() !== "defs") svg.removeChild(c);
  });
  state = "merge"; penalty = 0; bases = [];
  resEl.innerHTML = "";

  var tg = document.getElementById("tgt");
  tg.innerHTML = "";
  var parts = ["표적: " + CFG.gene + " · gRNA "];
  tg.appendChild(document.createTextNode(parts[0]));
  var b = document.createElement("b"); b.textContent = SP; tg.appendChild(b);
  var extra = "";
  if (CFG.mit !== null && CFG.mit !== undefined) extra += " · MIT " + CFG.mit;
  if (CFG.doench !== null && CFG.doench !== undefined) extra += " · Doench " + CFG.doench;
  if (CFG.demo) extra += " (예시 서열)";
  tg.appendChild(document.createTextNode(extra));

  el("rect", {x: 0, y: 0, width: 900, height: 520, fill: "url(#dots)"}, svg);

  // DNA 레인
  el("rect", {x: 14, y: 300, width: 872, height: 200, rx: 16, fill: "#0f2433", stroke: "#1f3b52"}, svg);
  var lt = el("text", {x: 30, y: 324, "class": "cap"}, svg);
  lt.textContent = "게놈 DNA (" + CFG.gene + ")";

  gDNA = el("g", {}, svg);
  var t5 = el("text", {x: X0 - 8, y: YT + 4, "text-anchor": "end", "class": "cap"}, gDNA); t5.textContent = "5'";
  var t3 = el("text", {x: X0 + N * DX + 8, y: YT + 4, "class": "cap"}, gDNA); t3.textContent = "3'";
  var b3 = el("text", {x: X0 - 8, y: YB + 4, "text-anchor": "end", "class": "cap"}, gDNA); b3.textContent = "3'";
  var b5 = el("text", {x: X0 + N * DX + 8, y: YB + 4, "class": "cap"}, gDNA); b5.textContent = "5'";

  for (var i = 0; i < N; i++){
    var cx = X0 + (i + 0.5) * DX;
    var ch = FULL.charAt(i);
    var g = el("g", {"class": "base"}, gDNA);
    el("line", {x1: cx, x2: cx, y1: YT + 11, y2: YB - 11, stroke: "#3b5a75", "stroke-width": 2}, g);
    tile(g, "b", cx, YB, COMP[ch], COLORS[COMP[ch]]);
    tile(g, "t", cx, YT, ch, COLORS[ch]);
    if (i >= FL && i < FL + 20){
      var rc = ch === "T" ? "U" : ch;
      tile(g, "r", cx, YT, rc, "#ff9a2e");
    }
    bases.push(g);
  }

  // PAM 표시
  var pcx = X0 + (PAM_START + 1.5) * DX;
  pamBox = el("rect", {x: X0 + PAM_START * DX + 1, y: YT - 16, width: 3 * DX - 2, height: 32,
    rx: 6, fill: "none", stroke: "#ff9a2e", "stroke-width": 2, "stroke-dasharray": "4 3", "class": "pulse"}, gDNA);
  pamLbl = el("text", {x: pcx, y: YT - 24, "text-anchor": "middle", "class": "cap", fill: "#ff9a2e"}, gDNA);
  pamLbl.setAttribute("style", "fill:#ff9a2e");
  pamLbl.textContent = "PAM (NGG)";

  // 표적 20 nt 괄호
  var bx1 = X0 + FL * DX + 2, bx2 = X0 + (FL + 20) * DX - 2;
  el("path", {d: "M" + bx1 + " " + (YB + 24) + " v6 H" + bx2 + " v-6", fill: "none", stroke: "#4c6f8a", "stroke-width": 1.5}, gDNA);
  var bt = el("text", {x: (bx1 + bx2) / 2, y: YB + 48, "text-anchor": "middle", "class": "cap"}, gDNA);
  bt.textContent = "gRNA와 상보적인 표적 서열 (20 nt)";

  // 절단선
  var cutX = X0 + (CUT_AFTER + 1) * DX;
  cutLine = el("line", {x1: cutX, x2: cutX, y1: YT - 62, y2: YB + 18, stroke: "#ffe14d",
    "stroke-width": 3, "stroke-dasharray": "6 4", opacity: 0}, svg);

  // 힌트 타원
  hintEl = el("ellipse", {cx: TARGET_X, cy: CAS_BOUND_Y, rx: 134, ry: 68, fill: "none", stroke: "#3ddc84",
    "stroke-width": 2, "stroke-dasharray": "8 6", opacity: 0, "class": "pulse"}, svg);

  scanner = el("line", {x1: 0, x2: 0, y1: 0, y2: 0, stroke: "#3ddc84", "stroke-width": 2,
    "stroke-dasharray": "3 4", opacity: 0}, svg);

  cas = makeCas9();
  gr = makeGRNA();

  setStep(0);
  setMsg("주황색 gRNA를 잡아서 초록색 Cas9 위로 끌어다 놓으세요.");
  setCtrl([{label: "힌트", fn: hint}]);
}

/* ---------- 드래그 가능한 두 주인공 ---------- */
function makeCas9(){
  var g = el("g", {"class": "drag"}, svg);
  var inner = el("g", {}, g);
  el("ellipse", {cx: 0, cy: 0, rx: 130, ry: 64, fill: "url(#casG)", stroke: "#1f9e5c", "stroke-width": 2}, inner);
  el("ellipse", {cx: -62, cy: -20, rx: 66, ry: 46, fill: "#2fbf74", opacity: 0.85}, inner);
  el("ellipse", {cx: 70, cy: 12, rx: 58, ry: 40, fill: "#59e79b", opacity: 0.7}, inner);
  var guide = el("path", {d: "M-100 26 C -70 0, -50 52, -20 26 S 30 0, 60 26 S 90 44, 104 22",
    fill: "none", stroke: "#ff9a2e", "stroke-width": 6, "stroke-linecap": "round", opacity: 0}, inner);
  guide.setAttribute("class", "guide");
  var t1 = el("text", {x: 0, y: -8, "text-anchor": "middle", "font-size": 22, "font-weight": 800, fill: "#06301b"}, inner);
  t1.textContent = "Cas9";
  var t2 = el("text", {x: 0, y: 52, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: "#06301b", opacity: 0}, inner);
  t2.textContent = "RNP 복합체";
  g._inner = inner; g._guide = guide; g._tag = t2;
  setPos(g, CAS_HOME.x, CAS_HOME.y);
  attachDrag(g, {
    can: function(){ return state === "dock"; },
    denied: function(){
      if (state === "merge"){ setMsg("먼저 gRNA를 Cas9에 결합시켜야 합니다.", "bad"); shake(g); }
      else if (state === "cut"){ doCut(); }
    },
    move: function(x, y){
      var near = y > 190;
      scanner.setAttribute("x1", x); scanner.setAttribute("x2", x);
      scanner.setAttribute("y1", y + 64); scanner.setAttribute("y2", YT - 16);
      scanner.setAttribute("opacity", near ? 0.7 : 0);
    },
    drop: onCasDrop
  });
  return g;
}

function makeGRNA(){
  var g = el("g", {"class": "drag"}, svg);
  el("rect", {x: -100, y: -44, width: 220, height: 92, fill: "transparent"}, g);
  el("path", {d: "M-80 0 H 10", stroke: "#ff9a2e", "stroke-width": 9, "stroke-linecap": "round", fill: "none"}, g);
  for (var i = 0; i < 6; i++){
    el("circle", {cx: -70 + i * 13, cy: 0, r: 2.6, fill: "#2a1700"}, g);
  }
  el("path", {d: "M10 0 C 25 -30, 45 30, 60 0 S 92 -30, 104 0", fill: "none", stroke: "#ffc27a",
    "stroke-width": 6, "stroke-linecap": "round"}, g);
  var a = el("text", {x: 12, y: -30, "text-anchor": "middle", "font-size": 15, "font-weight": 800, fill: "#ff9a2e"}, g);
  a.textContent = "gRNA";
  var s = el("text", {x: 12, y: 32, "text-anchor": "middle", "font-size": 11, fill: "#ffd9a8",
    "font-family": "ui-monospace,Consolas,monospace"}, g);
  s.textContent = "5'-" + SP + "-3'";
  setPos(g, GR_HOME.x, GR_HOME.y);
  attachDrag(g, {
    can: function(){ return state === "merge"; },
    move: function(){
      if (dist(g, cas) < 130) cas.classList.add("glow"); else cas.classList.remove("glow");
    },
    drop: onGrDrop
  });
  return g;
}

function attachDrag(g, h){
  var dragging = false, off = {x: 0, y: 0};
  g.style.touchAction = "none";
  g.addEventListener("pointerdown", function(e){
    if (!h.can()){ if (h.denied) h.denied(); return; }
    e.preventDefault();
    g.setPointerCapture(e.pointerId);
    var p = svgPt(e);
    off = {x: p.x - g._x, y: p.y - g._y};
    dragging = true;
    g.classList.add("grab");
  });
  g.addEventListener("pointermove", function(e){
    if (!dragging) return;
    var p = svgPt(e);
    var x = clamp(p.x - off.x, 60, 840);
    var y = clamp(p.y - off.y, 50, 320);
    setPos(g, x, y);
    if (h.move) h.move(x, y);
  });
  function end(){
    if (!dragging) return;
    dragging = false;
    g.classList.remove("grab");
    if (h.drop) h.drop(g._x, g._y);
  }
  g.addEventListener("pointerup", end);
  g.addEventListener("pointercancel", end);
}

function shake(g){
  g.classList.remove("shake");
  void g.getBoundingClientRect();
  g.classList.add("shake");
  setTimeout(function(){ g.classList.remove("shake"); }, 450);
}

/* ---------- 1단계: gRNA + Cas9 ---------- */
function onGrDrop(){
  cas.classList.remove("glow");
  if (dist(gr, cas) < 130){
    state = "busy";
    tween(gr, cas._x, cas._y + 8, 350, function(){
      gr.style.display = "none";
      cas._guide.setAttribute("opacity", 1);
      cas._tag.setAttribute("opacity", 1);
      cas.classList.add("glow");
      setTimeout(function(){ cas.classList.remove("glow"); }, 900);
      state = "dock";
      setStep(1);
      setMsg("RNP 복합체 완성! 이제 Cas9를 DNA 위로 끌고 가서 표적 서열에 올려놓으세요. 힌트: PAM(NGG) 바로 앞 20 nt가 gRNA와 같은 곳입니다.", "good");
    });
  } else {
    setMsg("gRNA가 Cas9에 닿지 않았습니다. 초록색 Cas9 위에 겹치도록 놓으세요.", "bad");
    tween(gr, GR_HOME.x, GR_HOME.y, 350);
  }
}

/* ---------- 2단계: 표적 찾기 ---------- */
function onCasDrop(x, y){
  scanner.setAttribute("opacity", 0);
  if (y <= 190){
    setMsg("DNA 쪽으로 더 가까이 내려놓아야 Cas9가 서열을 탐색할 수 있습니다.");
    return;
  }
  if (Math.abs(x - TARGET_X) <= 33){
    bindTarget();
    return;
  }
  penalty++;
  var s = Math.round((x - X0) / DX - 0.5 - 11);
  var text;
  if (s < 0 || s + 23 > N){
    text = "DNA 가장자리입니다. 표적 서열이 있는 가운데 쪽으로 옮겨 보세요.";
  } else if (FULL.charAt(s + 21) !== "G" || FULL.charAt(s + 22) !== "G"){
    text = "이 위치에는 PAM(NGG)이 없어 Cas9가 DNA를 풀지 못합니다.";
  } else {
    var mm = 0;
    for (var i = 0; i < 20; i++){ if (FULL.charAt(s + i) !== SP.charAt(i)) mm++; }
    text = "PAM은 있지만 gRNA와 " + mm + "개 염기가 맞지 않습니다. 오프타깃이라 결합이 불안정합니다.";
  }
  setMsg(text + " 다시 시도해 보세요.", "bad");
  tween(cas, CAS_HOME.x, CAS_HOME.y, 450);
  if (penalty >= 2) hint();
}

function bindTarget(){
  state = "busy";
  hintEl.setAttribute("opacity", 0);
  pamBox.setAttribute("class", "");
  tween(cas, TARGET_X, CAS_BOUND_Y, 450, function(){
    svg.insertBefore(cas, gDNA);          // Cas9를 DNA 뒤로 보내 글자가 위에 보이게
    cas.classList.add("glow");
    for (var i = FL; i < FL + 20; i++){
      (function(idx){
        setTimeout(function(){ bases[idx].classList.add("open"); }, (idx - FL) * 40);
      })(i);
    }
    setTimeout(function(){
      cas.classList.remove("glow");
      state = "cut";
      setStep(2);
      setMsg("PAM을 인식하고 DNA 이중나선이 풀렸습니다(R-loop). 주황색 gRNA(U)가 아래 가닥과 짝을 이룹니다. Cas9를 클릭하거나 아래 버튼으로 절단하세요.", "good");
      setCtrl([{label: "Cas9로 절단하기", cls: "main", fn: doCut}]);
    }, 20 * 40 + 700);
  });
}

/* ---------- 3단계: 절단 ---------- */
function doCut(){
  if (state !== "cut") return;
  state = "busy";
  setCtrl([]);
  var cx = parseFloat(cutLine.getAttribute("x1"));
  var burst = el("circle", {cx: cx, cy: (YT + YB) / 2, r: 46, fill: "none", stroke: "#ffe14d", "stroke-width": 4}, svg);
  burst.setAttribute("class", "burst");
  cutLine.setAttribute("opacity", 1);
  setTimeout(function(){
    for (var i = 0; i < N; i++){
      bases[i].classList.add(i <= CUT_AFTER ? "left" : "right");
    }
  }, 250);
  setTimeout(function(){
    if (burst.parentNode) burst.parentNode.removeChild(burst);
    state = "repair";
    setStep(3);
    setMsg("이중가닥절단(DSB)이 일어났습니다. PAM에서 3 bp 앞이 잘렸어요. 세포가 어떤 방법으로 수리할지 선택하세요.", "good");
    setCtrl([
      {label: "NHEJ (비상동 말단 연결)", cls: "main", fn: function(){ repair("nhej"); }},
      {label: "HDR (도너 DNA로 정밀 교정)", fn: function(){ repair("hdr"); }}
    ]);
  }, 1300);
}

/* ---------- 4단계: 수리와 결과 ---------- */
function spans(items){
  return items.map(function(o){
    return o.k ? '<span class="' + o.k + '">' + o.c + "</span>" : o.c;
  }).join("");
}
function toItems(str){ return str.split("").map(function(c){ return {c: c}; }); }

function repair(kind){
  if (state !== "repair") return;
  state = "done";
  setCtrl([]);
  for (var i = 0; i < N; i++){ bases[i].classList.remove("left", "right"); }
  cutLine.setAttribute("opacity", 0);

  var cutIdx = CUT_AFTER + 1;
  var before = toItems(FULL), after, title, body;

  if (kind === "nhej"){
    var left = toItems(FULL.slice(0, cutIdx));
    var right = toItems(FULL.slice(cutIdx));
    if (rnd() < 0.5){
      var ins = randBase();
      after = left.concat([{c: ins, k: "m"}], right);
      title = "NHEJ 결과: 염기 1개 삽입 (+1)";
    } else {
      var k = 1 + Math.floor(rnd() * 2);
      for (var j = 0; j < k; j++){ before[cutIdx + j].k = "del"; }
      var gap = [];
      for (var q = 0; q < k; q++) gap.push({c: "-", k: "del"});
      after = left.concat(gap, right.slice(k));
      title = "NHEJ 결과: 염기 " + k + "개 결실 (-" + k + ")";
    }
    body = "끊어진 말단이 오류를 남기며 이어 붙었습니다. 3의 배수가 아닌 길이 변화는 읽기틀을 밀어(프레임시프트) 단백질 기능을 잃게 만들 수 있어, 유전자 녹아웃에 쓰입니다.";
  } else {
    var pos = cutIdx + 1;
    var orig = FULL.charAt(pos);
    var choices = "ACGT".replace(orig, "");
    var nb = choices.charAt(Math.floor(rnd() * 3));
    before[pos].k = "m";
    after = toItems(FULL);
    after[pos] = {c: nb, k: "m"};
    title = "HDR 결과: 도너 DNA에 따라 염기 1개 교정 (" + orig + " → " + nb + ")";
    body = "도너 DNA를 주형으로 절단 부위가 정확하게 고쳐졌습니다. 다만 HDR은 세포가 분열하는 시기에 주로 일어나 효율이 낮은 편이며, 실제 실험에서는 재절단을 막기 위해 도너에 PAM 변이를 함께 넣기도 합니다.";
  }

  var score = Math.max(40, 100 - penalty * 10);
  var grade = penalty === 0 ? "완벽한 첫 시도!" : (penalty < 3 ? "훌륭해요" : "연습하면 더 좋아져요");

  resEl.innerHTML =
    '<div class="card"><h2>' + title + "</h2>" +
    '<div class="lbl">수리 전</div><div class="seq">' + spans(before) + "</div>" +
    '<div class="lbl">수리 후</div><div class="seq">' + spans(after) + "</div>" +
    "<p>" + body + "</p>" +
    "<p><b>실습 점수 " + score + "점</b> · 표적 찾기 실패 " + penalty + "회 · " + grade + "</p></div>";

  setStep(4);
  setMsg("실습 완료! 다른 수리 경로도 비교해 보세요.", "good");
  setCtrl([{label: "다시 하기", cls: "main", fn: build}]);
}

/* ---------- 힌트 ---------- */
function hint(){
  if (state === "merge"){
    setMsg("힌트: gRNA를 오른쪽 위의 초록색 Cas9 위로 가져가세요.");
    cas.classList.add("glow");
    setTimeout(function(){ cas.classList.remove("glow"); }, 1500);
  } else if (state === "dock"){
    hintEl.setAttribute("opacity", 0.9);
    setMsg("힌트: 점선 타원 안으로 Cas9를 옮기세요. 주황색 점선 상자(PAM)가 그 오른쪽 끝에 닿아 있습니다.");
  }
}

build();
})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 3) 페이지 렌더링
# ---------------------------------------------------------------------------
st.title("🧬 유전자 가위 실습실")
st.caption(
    "gRNA와 Cas9를 직접 끌어다 놓아 DNA를 절단하고, 세포의 수리 경로까지 체험해 보세요. "
    "PC 화면에서 하면 가장 잘 보입니다."
)

cfg = build_config()
if cfg["demo"]:
    st.info(
        "1페이지에서 선택된 gRNA가 없어 예시 서열로 실습합니다. "
        "스크리닝 도구에서 후보를 고르면 그 서열로 이어집니다."
    )

# '</' 가 들어 있어도 <script> 블록이 끊기지 않도록 이스케이프
config_json = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
html = GAME_HTML.replace("__CONFIG__", config_json)

components.html(html, height=930, scrolling=True)

with st.expander("실습 순서 보기"):
    st.markdown(
        "1. 주황색 **gRNA**를 초록색 **Cas9**에 끌어다 붙입니다 (RNP 복합체).\n"
        "2. RNP를 DNA의 **PAM(NGG) 바로 앞 20 nt 표적** 위에 올려놓습니다.\n"
        "3. Cas9를 클릭해 **DSB(이중가닥절단)** 를 일으킵니다.\n"
        "4. **NHEJ** 또는 **HDR** 수리 경로를 골라 결과를 확인합니다."
    )
