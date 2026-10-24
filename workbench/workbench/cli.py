"""Reproducible batch collection and retrieval ablations, not automatic grading."""
from __future__ import annotations
import argparse,csv,hashlib,json,sys,time,zipfile
from collections import Counter
from pathlib import Path
from .core import Workbench,ROOT,normalize,atomic_json,markdown,stamp

def doctor(root:Path=ROOT)->dict:
    w=Workbench(root)
    pdfs=[]
    for pid,p in w.papers.items():
        path=root/'corpus/pdfs'/(pid+'.pdf')
        ok=path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==p['pdf_sha256']
        pdfs.append({'paper':pid,'hash_matches':ok})
    return {'python':sys.version.split()[0],'papers':len(w.papers),'passages':len(w.sources),
      'claims':len(w.claims),'exact_evidence_links':sum(len(c['evidence']) for c in w.claims),
      'pdf_checks':pdfs,'passed':all(p['hash_matches'] for p in pdfs),
      'hashes':{'corpus':w.corpus_hash,'knowledge':w.claim_hash,'code':w.code_hash},
      'notice':'Mechanical source integrity only. It does not establish correctness, completeness or stakeholder value.'}

def evaluate(question_file:Path,out:Path,root:Path=ROOT,*,publish_runs:bool=False)->dict:
    if out.exists() and any(out.iterdir()):raise ValueError('Use a new output directory; old results must not be overwritten')
    out.mkdir(parents=True,exist_ok=True);w=Workbench(root)
    questions=[json.loads(l) for l in question_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    if len({q['id'] for q in questions})!=len(questions):raise ValueError('Duplicate question IDs')
    rows=[];reports=[]
    for q in questions:
        # Only the question text enters runtime. Evidence/answers are used below solely for diagnostics.
        r=w.answer(q['question'],persist=False);r['evaluation_question_id']=q['id']
        atomic_json(out/(q['id']+'.json'),r)
        if publish_runs:atomic_json(root/'results/runs'/(r['run_id']+'.json'),r)
        (out/(q['id']+'.md')).write_text(markdown(r),encoding='utf-8')
        evidence=q.get('evidence',[])
        hit=lambda sid,e:normalize(e['quote']).casefold() in normalize(w.by_source[sid]['text']).casefold()
        citation_ids=[s['source_id'] for s in r['citations']]
        quote_hits=sum(any(hit(sid,e) for sid in citation_ids) for e in evidence)
        represented={w.by_source[sid]['paper_id'] for sid in citation_ids}
        expected=set(q.get('expected_papers',[]))
        record={'question_id':q['id'],'category':q['type'],'status':r['status'],
          'claim_count':len(r['blocks']),'cited_passages':len(citation_ids),
          'labelled_quotes':len(evidence),'labelled_quotes_in_cited_passages':quote_hits,
          'expected_papers_cited':sorted(expected & represented), 'elapsed_seconds':r['elapsed_seconds']}
        reports.append(record)
        rows.append({'run_id':r['run_id'],'question_id':q['id'],'question':q['question'],
          'category':q['type'],'status':r['status'],'reviewer_id':'','relationship':'',
          'answerable':'','correctness':'','completeness':'','citation_support':'','relevance':'','source_checked':'','notes':''})
    fields=list(rows[0]) if rows else []
    if rows:
        with (out/'human_scorecard.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fields);writer.writeheader();writer.writerows(rows)
    summary={'created_utc':stamp(),'questions':len(reports),'status_counts':dict(Counter(r['status'] for r in reports)),
      'human_accuracy':'NOT_MEASURED','independent_validation':'NOT_PERFORMED',
      'evaluation_status':'development/regression; catalogue was curated with prior access to these questions',
      'catalogue_intervention':'Added a language-model-drafted, source-linked catalogue; not a model-only improvement or an unseen-question validation.',
      'question_file_sha256':hashlib.sha256(question_file.read_bytes()).hexdigest(),
      'hashes':doctor(root)['hashes'],'records':reports,
      'notice':'Output availability and labelled-quote coverage are not semantic answer correctness. Source-only and partial outputs must be scored separately.'}
    atomic_json(out/'summary.json',summary)
    with zipfile.ZipFile(out.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.iterdir()):z.write(p,p.name)
    return summary

def ablation(question_file:Path,out:Path,root:Path=ROOT)->dict:
    w=Workbench(root);questions=[json.loads(l) for l in question_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    answerable=[q for q in questions if q.get('evidence')];summary=[];records=[]
    for method in ('bm25','tfidf','hybrid'):
        for route in (False,True):
            any_hits=all_papers=all_quotes=0
            for q in answerable:
                passages=w.search(q['question'],method=method,route=route,k=5)['first_stage']
                quotes=q['evidence'];hits=[any(normalize(e['quote']).casefold() in normalize(s['text']).casefold() for s in passages) for e in quotes]
                paperhits={e['paper'] for e,h in zip(quotes,hits) if h}
                a=any(hits);b=set(q['expected_papers'])<=paperhits;c=all(hits)
                any_hits+=a;all_papers+=b;all_quotes+=c
                records.append({'method':method,'route':route,'question':q['id'],'any_labelled_quote':a,
                  'labelled_evidence_from_every_expected_paper':b,'all_labelled_quotes':c,
                  'passages':[s['source_id'] for s in passages]})
            summary.append({'method':method,'routing':route,'k':5,'n':len(answerable),
              'at_least_one_labelled_quote':any_hits,'labelled_evidence_every_expected_paper':all_papers,
              'all_labelled_quotes':all_quotes})
    result={'created_utc':stamp(),'comparison':'Same corpus, same k=5, same labelled questions. Pure-Python implementation; not numerically identical to prior sklearn implementation.',
      'human_accuracy':'NOT_MEASURED','independent_test':False,'results':summary,'records':records}
    atomic_json(out,result);return result

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('doctor')
    q=sub.add_parser('ask');q.add_argument('question');q.add_argument('--mode',choices=['explain','search'],default='explain')
    for cmd in ('evaluate','ablation'):
        a=sub.add_parser(cmd);a.add_argument('--questions',type=Path,default=ROOT/'eval/all52_development.jsonl');a.add_argument('--out',type=Path,required=True)
        if cmd=='evaluate':a.add_argument('--publish-runs',action='store_true')
    a=p.parse_args()
    if a.command=='doctor':r=doctor();print(json.dumps(r,indent=2));sys.exit(0 if r['passed'] else 1)
    elif a.command=='ask':print(markdown(Workbench().answer(a.question,mode=a.mode)))
    elif a.command=='evaluate':
        r=evaluate(a.questions,a.out,publish_runs=a.publish_runs);print(json.dumps({k:v for k,v in r.items() if k!='records'},indent=2));print('Review bundle:',a.out.with_suffix('.zip'))
    else:
        r=ablation(a.questions,a.out);print(json.dumps({k:v for k,v in r.items() if k!='records'},indent=2))
if __name__=='__main__':main()
