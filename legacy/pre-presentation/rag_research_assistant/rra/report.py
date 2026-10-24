"""Render results/latest.json as a self-contained HTML dashboard (no external scripts)."""
from __future__ import annotations

import html
import json
from pathlib import Path

CSS = """
:root{--surface:#fcfcfb;--panel:#ffffff;--border:#e4e3df;--text:#0b0b0b;--text2:#52514e;--muted:#8a8984;
--s1:#2a78d6;--s2:#eb6834;--good:#008300;--bad:#e34948;
--heat-ink:#fff;--q0:#f0efec;--q1:#cde2fb;--q2:#9ec5f4;--q3:#6da7ec;--q4:#3987e5;--q5:#256abf;--q6:#184f95;--q7:#0d366b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--surface:#1a1a19;--panel:#222221;--border:#383835;
--text:#fff;--text2:#c3c2b7;--muted:#8f8e86;--s1:#3987e5;--s2:#d95926;--good:#2fa52f;--bad:#e66767;
--heat-ink:#0b0b0b;--q0:#2a2a28;--q1:#104281;--q2:#184f95;--q3:#1c5cab;--q4:#256abf;--q5:#3987e5;--q6:#6da7ec;--q7:#9ec5f4;color-scheme:dark}}
:root[data-theme="dark"]{--surface:#1a1a19;--panel:#222221;--border:#383835;--text:#fff;--text2:#c3c2b7;--muted:#8f8e86;
--s1:#3987e5;--s2:#d95926;--good:#2fa52f;--bad:#e66767;--q0:#2a2a28;--q1:#104281;--q2:#184f95;--q3:#1c5cab;
--q4:#256abf;--q5:#3987e5;--q6:#6da7ec;--q7:#9ec5f4;--heat-ink:#0b0b0b;color-scheme:dark}
*{box-sizing:border-box}body{margin:0;background:var(--surface);color:var(--text);
font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1080px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:24px;margin:0 0 4px}h2{font-size:17px;margin:32px 0 8px}p.sub{color:var(--text2);margin:0 0 16px}
.meta{color:var(--muted);font-size:12px}.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.tile{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:12px}
.tile .k{color:var(--text2);font-size:12px}.tile .v{font-size:24px;font-weight:600;font-variant-numeric:tabular-nums}
.tile .d{font-size:12px;color:var(--text2)}.up{color:var(--good)}.down{color:var(--bad)}
.card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:16px;overflow-x:auto}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{text-align:left;padding:6px 8px;
border-bottom:1px solid var(--border);vertical-align:top}th{color:var(--text2);font-weight:500;font-size:12px}
.heat{table-layout:fixed}.heat td.cell{text-align:center;border:2px solid var(--panel);border-radius:6px;min-width:84px;font-weight:600}
.pill{display:inline-block;padding:1px 8px;border-radius:99px;font-size:12px;border:1px solid var(--border)}
.pill.ok{color:var(--good)}.pill.err{color:var(--bad)}select{font:inherit;padding:4px 8px;border-radius:6px;
border:1px solid var(--border);background:var(--panel);color:var(--text)}.legend{display:flex;gap:16px;font-size:12px;color:var(--text2)}
.sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}
.ans{color:var(--text2);font-size:12px;max-width:420px}svg text{fill:var(--text2);font-size:11px}
#tip{position:fixed;pointer-events:none;background:var(--panel);border:1px solid var(--border);border-radius:6px;
padding:6px 8px;font-size:12px;display:none;box-shadow:0 2px 8px rgba(0,0,0,.15)}
"""

METRICS = [("recall@K", "Recall@K", True), ("mrr", "MRR", True), ("paper_recall@K", "Paper recall@K", True),
           ("citation_precision", "Citation precision", True), ("citation_support", "Citation support", True),
           ("faithfulness", "Faithfulness", True), ("abstain_correct", "Unsupported flagged", True),
           ("false_abstain", "False abstain", False)]


def _m(run: dict, key: str, k: int):
    return run["metrics"].get(key.replace("@K", f"@{k}"))


def _fmt(v):
    return "–" if v is None else f"{v:.2f}"


def write_report(data: dict, out: Path) -> Path:
    k = data["k"]
    runs = {r["config"]: r for r in data["runs"]}
    base, best = runs.get(data["baseline"]), runs[data["best"]]
    chunkers = list(dict.fromkeys(r["chunker"] for r in data["runs"]))
    retrs = list(dict.fromkeys(r["config"].split("/")[1] for r in data["runs"]))
    rname = {r["config"].split("/")[1]: r["retriever"] for r in data["runs"]}

    tiles = []
    for key, label, higher in METRICS:
        v = _m(best, key, k)
        b = _m(base, key, k) if base else None
        delta = ""
        if v is not None and b is not None:
            d = v - b
            good = (d > 0) == higher and abs(d) > 1e-9
            cls = "up" if good else ("down" if abs(d) > 1e-9 else "")
            delta = f'<div class="d"><span class="{cls}">{d:+.2f}</span> vs baseline {_fmt(b)}</div>'
        tiles.append(f'<div class="tile"><div class="k">{label.replace("K", str(k)) if "@K" in label else label}</div>'
                     f'<div class="v">{_fmt(v)}</div>{delta}</div>')

    grid = {c: {r: runs.get(f"{c}/{r}") for r in retrs} for c in chunkers}
    heat_data = {c: {r: (grid[c][r]["metrics"] if grid[c][r] else {}) for r in retrs} for c in chunkers}

    sweep = data["tau_sweep"]["points"]
    W, H, P = 520, 220, 36
    x = lambda t: P + (t - 0.3) / 0.6 * (W - 2 * P)
    y = lambda v: H - P + 8 - (v or 0) * (H - 2 * P)
    svg = [f'<svg viewBox="0 0 {W} {H}" width="100%" style="max-width:{W}px" role="img" '
           f'aria-label="Abstention threshold sweep">']
    for g in (0, .5, 1):
        svg.append(f'<line x1="{P}" x2="{W-P}" y1="{y(g)}" y2="{y(g)}" stroke="var(--border)"/>'
                   f'<text x="{P-6}" y="{y(g)+4}" text-anchor="end">{g:.1f}</text>')
    for p in sweep:
        svg.append(f'<text x="{x(p["tau"])}" y="{H-8}" text-anchor="middle">{p["tau"]:.1f}</text>')
    for key, var, label in (("abstain_correct", "--s1", "Unsupported flagged"), ("false_abstain", "--s2", "False abstain")):
        pts = " ".join(f"{x(p['tau']):.1f},{y(p[key]):.1f}" for p in sweep)
        svg.append(f'<polyline points="{pts}" fill="none" stroke="var({var})" stroke-width="2"/>')
        for p in sweep:
            svg.append(f'<circle cx="{x(p["tau"]):.1f}" cy="{y(p[key]):.1f}" r="5" fill="var({var})" '
                       f'stroke="var(--panel)" stroke-width="2" data-tip="{label} at τ={p["tau"]}: {_fmt(p[key])}"/>')
    svg.append("</svg>")

    def qrows(run):
        rows = []
        for q in run["questions"]:
            err = q["error"]
            pill = f'<span class="pill err">{err}</span>' if err else '<span class="pill ok">ok</span>'
            rows.append(f"<tr><td>{q['qid']}</td><td>{q['qtype']}</td><td>{q['first_relevant_rank'] or '–'}</td>"
                        f"<td>{_fmt(q['papers_hit']) if q['qtype'] != 'unsupported' else '–'}</td><td>{pill}</td>"
                        f"<td class='ans'>{html.escape(q['answer'][:260])}</td></tr>")
        return "".join(rows)

    def err_counts(run):
        c = {}
        for q in run["questions"]:
            if q["error"]:
                c[q["error"]] = c.get(q["error"], 0) + 1
        return c

    errs_best, errs_base = err_counts(best), err_counts(base) if base else {}
    cats = sorted(set(errs_best) | set(errs_base))
    err_table = "".join(f"<tr><td>{c}</td><td>{errs_base.get(c, 0)}</td><td>{errs_best.get(c, 0)}</td></tr>" for c in cats) \
        or "<tr><td colspan=3>no errors</td></tr>"

    problems = data.get("ground_truth_problems") or []
    gt_note = (f'<div class="card" style="border-color:var(--bad)"><b>Ground-truth warnings ({len(problems)})</b><br>'
               + "<br>".join(html.escape(p) for p in problems) + "</div>") if problems else ""

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Paper-Grounded RAG Evaluation</title>
<style>{CSS}</style></head><body><main>
<h1>Source-grounded RAG research assistant — evaluation</h1>
<p class="sub">Baseline <b>{data['baseline']}</b> vs best configuration <b>{data['best']}</b> on the same labelled question set.
Best = highest {html.escape(data.get('selection_rule', 'MRR'))}.</p>
<p class="meta">run {data['run_id']} · corpus {data['corpus_version']} · questions {data['questions_sha']} ·
generator {best['generator']} · k={k} · {best['metrics']['n_answerable']} answerable + {best['metrics']['n_unsupported']} unsupported questions</p>
{gt_note}
<div class="tiles">{''.join(tiles)}</div>

<h2>Chunking × retrieval grid</h2>
<p class="sub">Each cell is one full run over the question set. Darker = better (for false abstain, lower is better).
<label>Metric <select id="metric">{''.join(f'<option value="{key.replace("@K", f"@{k}")}">{lbl.replace("@K", f"@{k}")}</option>' for key, lbl, _ in METRICS)}</select></label></p>
<div class="card"><table class="heat"><thead><tr><th>chunking \\ retrieval</th>
{''.join(f'<th>{r}' + (f'<br><span class="meta">{rname[r]}</span>' if rname[r] != r else '') + '</th>' for r in retrs)}</tr></thead><tbody id="heat"></tbody></table></div>

<h2>Unsupported-question handling vs abstention threshold τ</h2>
<p class="sub">Config {data['tau_sweep']['config']}. Raising τ flags more unsupported questions but refuses more answerable ones; pick τ where the lines separate most.</p>
<div class="card"><div class="legend"><span><span class="sw" style="background:var(--s1)"></span>Unsupported flagged (higher is better)</span>
<span><span class="sw" style="background:var(--s2)"></span>False abstain on answerable (lower is better)</span></div>{''.join(svg)}</div>

<h2>Error analysis</h2>
<div class="card"><table><thead><tr><th>error category</th><th>baseline ({data['baseline']})</th><th>best ({data['best']})</th></tr></thead>
<tbody>{err_table}</tbody></table></div>

<h2>Per-question results — best configuration</h2>
<div class="card"><table><thead><tr><th>id</th><th>type</th><th>first relevant rank</th><th>papers hit</th><th>outcome</th><th>answer (with citations)</th></tr></thead>
<tbody>{qrows(best)}</tbody></table></div>
{'<h2>Per-question results — baseline</h2><div class="card"><table><thead><tr><th>id</th><th>type</th><th>first relevant rank</th><th>papers hit</th><th>outcome</th><th>answer</th></tr></thead><tbody>' + qrows(base) + '</tbody></table></div>' if base and base is not best else ''}
</main><div id="tip"></div>
<script>
const HEAT={json.dumps(heat_data)};const CH={json.dumps(chunkers)};const RE={json.dumps(retrs)};
const LOWER=new Set(["false_abstain"]);
function draw(m){{const vals=[];CH.forEach(c=>RE.forEach(r=>{{const v=HEAT[c][r][m];if(v!=null)vals.push(v)}}));
const lo=Math.min(...vals),hi=Math.max(...vals);
document.getElementById('heat').innerHTML=CH.map(c=>'<tr><th>'+c+'</th>'+RE.map(r=>{{const v=HEAT[c][r][m];
if(v==null)return '<td class="cell">–</td>';let t=hi>lo?(v-lo)/(hi-lo):1;if(LOWER.has(m))t=1-t;const s=Math.round(t*7);
const ink=s>=4?'var(--heat-ink)':'var(--text)';return '<td class="cell" style="background:var(--q'+s+');color:'+ink+'" data-tip="'+c+' / '+r+': '+m+' = '+v.toFixed(3)+'">'+v.toFixed(2)+'</td>'}}).join('')+'</tr>').join('');}}
const sel=document.getElementById('metric');sel.value='mrr';sel.onchange=()=>draw(sel.value);draw('mrr');
const tip=document.getElementById('tip');
document.addEventListener('mousemove',e=>{{const t=e.target.closest('[data-tip]');if(!t){{tip.style.display='none';return}}
tip.textContent=t.dataset.tip;tip.style.display='block';tip.style.left=(e.clientX+12)+'px';tip.style.top=(e.clientY+12)+'px'}});
</script></body></html>"""
    out.write_text(page)
    return out
