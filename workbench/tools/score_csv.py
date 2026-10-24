"""Score explicit source-reviewed ratings; missing rows are never invented."""
import argparse,csv,json,sys
from collections import Counter
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('scorecard',type=Path);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--allow-partial',action='store_true');args=parser.parse_args()
rows=list(csv.DictReader(args.scorecard.open(encoding='utf-8')));rated=[];missing=[];seen=set()
fields=('correctness','completeness','citation_support','relevance')
for i,row in enumerate(rows,2):
 key=(row.get('run_id'),row.get('reviewer_id'))
 if not row.get('reviewer_id') or any(not str(row.get(k,'')).strip() for k in fields):
  missing.append(row.get('question_id') or f'row {i}');continue
 if key in seen:raise SystemExit(f'Duplicate run/reviewer pair at row {i}')
 seen.add(key)
 if row.get('source_checked','').lower() not in ('true','yes','1'):raise SystemExit(f'Source-check confirmation missing at row {i}')
 if row.get('relationship') not in ('team_member','external_reviewer','author'):raise SystemExit(f'Reviewer relationship missing at row {i}')
 if row.get('answerable','').lower() not in ('true','false','yes','no','1','0'):raise SystemExit(f'Answerability missing at row {i}')
 try:scores={k:int(row[k]) for k in fields}
 except ValueError:raise SystemExit(f'Invalid score at row {i}')
 if any(v not in (0,1,2) for v in scores.values()):raise SystemExit(f'Scores must be 0–2 at row {i}')
 rated.append({**row,**scores,'answerable':row['answerable'].lower() in ('true','yes','1')})
if missing and not args.allow_partial:raise SystemExit(f'{len(missing)} unscored rows. Complete them or explicitly use --allow-partial; no missing result will be imputed.')
# Report reviewer observations rather than silently treating duplicate raters as independent questions.
out={'scorecard_rows':len(rows),'rated_observations':len(rated),'unscored_rows':missing,
 'unique_runs':len({r['run_id'] for r in rated}),'relationships':dict(Counter(r['relationship'] for r in rated)),
 'independent_accuracy':'NOT_CERTIFIED','notice':'Descriptive reviewer observations. Multiple raters must be adjudicated, not counted as independent test questions. Partial review can be selection-biased.'}
for answerable,label in ((True,'answerable'),(False,'unsupported')):
 subset=[r for r in rated if r['answerable']==answerable]
 out[label]={'reviewer_observations':len(subset),'all_dimensions_fully_satisfied':sum(all(r[k]==2 for k in fields) for r in subset),
             'dimension_totals':{k:sum(r[k] for r in subset) for k in fields}}
args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(out,indent=2), encoding="utf-8");print(json.dumps(out,indent=2))
