"""Collect real human ratings and timed tasks. Never fill unobserved results."""
from __future__ import annotations
import json,re,time,uuid
from pathlib import Path
from collections import Counter,defaultdict
from .core import atomic_json,digest,stamp

RATING_FIELDS=('correctness','completeness','citation_support','relevance')

def safe_id(value:str)->str:
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}',value):
        raise ValueError('Use a pseudonymous ID containing letters, digits, hyphens or underscores')
    return value

def load_run(root:Path,run_id:str)->dict:
    safe_id(run_id);p=root/'results/runs'/(run_id+'.json')
    if not p.exists():raise ValueError('Run not found')
    return json.loads(p.read_text(encoding="utf-8"))

def save_review(root:Path,data:dict)->dict:
    rid=safe_id(data.get('run_id',''));reviewer=safe_id(data.get('reviewer_id',''))
    run=load_run(root,rid)
    if data.get('answerable') not in [True,False] or type(data.get('answerable')) is not bool:
        raise ValueError('State whether the question is answerable from the corpus')
    for field in RATING_FIELDS:
        if type(data.get(field)) is not int or data[field] not in (0,1,2):raise ValueError(f'Explicit 0–2 rating required: {field}')
    if not isinstance(data.get('source_checked'),bool) or not data['source_checked']:
        raise ValueError('Review the source PDF(s) before recording a source-based rating')
    if data.get('relationship') not in ['team_member','external_reviewer','author']:
        raise ValueError('Specify reviewer relationship')
    # A source-only search is not a fully generated answer, even with relevant passages.
    if run['mode']=='search' and data['completeness']==2:
        raise ValueError('Score evidence relevance, but do not call source-only search a complete generated answer')
    out={k:data[k] for k in ('run_id','reviewer_id','answerable','source_checked','relationship')+RATING_FIELDS}
    out.update(review_id=uuid.uuid4().hex,created_utc=stamp(),notes=str(data.get('notes',''))[:10000],
               run_hash=digest(run),system_status=run['status'],corpus_hash=run['hashes']['corpus'])
    atomic_json(root/'results/reviews'/(out['review_id']+'.json'),out)
    return out

def review_summary(root:Path)->dict:
    reviews=[json.loads(p.read_text(encoding="utf-8")) for p in sorted((root/'results/reviews').glob('*.json'))]
    # Retain audit history, but only latest rating per reviewer/run enters this descriptive view.
    latest={}
    for r in sorted(reviews,key=lambda r:r['created_utc']):latest[(r['run_id'],r['reviewer_id'])]=r
    grouped=defaultdict(list)
    for r in latest.values():grouped[r['run_id']].append(r)
    resolved=[];conflicts=[]
    for run_id,rr in grouped.items():
        key=lambda r:tuple(r[k] for k in ('answerable',)+RATING_FIELDS)
        if len({key(r) for r in rr})>1:conflicts.append(run_id)
        else:resolved.append(rr[0])
    answerable=[r for r in resolved if r['answerable']]
    unsupported=[r for r in resolved if not r['answerable']]
    good=lambda r: all(r[k]==2 for k in RATING_FIELDS)
    return {'recorded_runs':len(list((root/'results/runs').glob('*.json'))),'unreviewed_runs':max(0,len(list((root/'results/runs').glob('*.json')))-len(grouped)), 'review_records':len(reviews),'distinct_reviewed_runs':len(grouped),
      'resolved_runs':len(resolved),'conflicting_run_ids':conflicts,
      'answerable':{'n':len(answerable),'complete_correct_supported':sum(good(r) for r in answerable)},
      'unsupported':{'n':len(unsupported),'appropriate_response':sum(good(r) for r in unsupported)},
      'status':'NO_HUMAN_RATINGS' if not reviews else 'DESCRIPTIVE_HUMAN_RATINGS',
      'independence':'Reviewer relationships are self-reported; this tool does not certify independence.',
      'notice':'No accuracy estimate is supplied when no ratings exist. Conflicting ratings require adjudication.'}

PILOT_TASKS=[
 {'id':'A','question':'Explain how ColBERTv2 reduces index storage and identify its training improvement. Cite the relevant PDF pages.'},
 {'id':'B','question':'Compare REALM and DPR: what supervision trains their retrievers, and when is it used? Cite the relevant PDF pages.'},
 {'id':'C','question':'Explain how Atlas uses retrieved documents and identify the role of its reader. Cite the relevant PDF pages.'},
 {'id':'D','question':'Compare what BEIR and RAGAS evaluate, including one evaluation mechanism for each. Cite the relevant PDF pages.'}]

def start_pilot(root:Path,data:dict)->dict:
    participant=safe_id(data.get('participant_id',''))
    task=next((t for t in PILOT_TASKS if t['id']==data.get('task_id')),None)
    if task is None:raise ValueError('Unknown pilot task')
    if data.get('condition') not in ('manual','assistant'):raise ValueError('Unknown condition')
    if data.get('consent') is not True:raise ValueError('Participant consent is required')
    if data.get('participant_role','team_member') not in ('team_member','external_volunteer','author'):raise ValueError('Specify participant relationship')
    r={'session_id':uuid.uuid4().hex,'participant_id':participant,'task':task,'condition':data['condition'],
       'started_utc':stamp(),'started_timestamp':time.time(),'completed':False,'timing':'wall-clock includes verification',
       'participant_role':str(data.get('participant_role','team_member'))[:80]}
    atomic_json(root/'results/pilot'/(r['session_id']+'.json'),r);return r

def finish_pilot(root:Path,data:dict)->dict:
    sid=safe_id(data.get('session_id',''));path=root/'results/pilot'/(sid+'.json')
    if not path.exists():raise ValueError('Pilot session not found')
    r=json.loads(path.read_text(encoding="utf-8"))
    if r['completed']:raise ValueError('Session already submitted')
    if not str(data.get('answer','')).strip():raise ValueError('Submit the participant answer or explain inability to answer')
    elapsed=time.time()-r['started_timestamp']
    if elapsed<0:raise ValueError('Clock moved backwards; repeat with a stable clock')
    r.update(completed=True,ended_utc=stamp(),seconds_including_verification=round(elapsed,3),
             answer=str(data['answer'])[:12000],sources=str(data.get('sources',''))[:5000],
             help_received=str(data.get('help_received',''))[:1000],
             correctness='NOT_RATED',source_support='NOT_RATED')
    atomic_json(path,r);return r

def rate_pilot(root:Path,data:dict)->dict:
    sid=safe_id(data.get('session_id',''));reviewer=safe_id(data.get('reviewer_id',''))
    path=root/'results/pilot'/(sid+'.json')
    if not path.exists():raise ValueError('Pilot session not found')
    r=json.loads(path.read_text(encoding="utf-8"))
    if not r.get('completed'):raise ValueError('Task must be completed before review')
    if data.get('source_checked') is not True:raise ValueError('Check the original sources first')
    for k in ('correct','source_supported'):
        if type(data.get(k)) is not bool:raise ValueError('Explicit true/false rating required: '+k)
    rating={'reviewer_id':reviewer,'created_utc':stamp(),'correct':data['correct'],
      'source_supported':data['source_supported'],'source_checked':True,'notes':str(data.get('notes',''))[:6000]}
    r.setdefault('rating_history',[]).append(rating)
    r['correctness']=rating['correct'];r['source_support']=rating['source_supported']
    atomic_json(path,r);return r

def pilot_summary(root:Path)->dict:
    import statistics
    rows=[json.loads(p.read_text(encoding="utf-8")) for p in sorted((root/'results/pilot').glob('*.json'))]
    completed=[r for r in rows if r.get('completed')]
    out={}
    for condition in ('manual','assistant'):
        cases=[r for r in completed if r['condition']==condition]
        rated=[r for r in cases if type(r.get('correctness')) is bool and type(r.get('source_support')) is bool]
        verified=[r for r in rated if r['correctness'] and r['source_support']]
        median=lambda rr:statistics.median(r['seconds_including_verification'] for r in rr) if rr else None
        out[condition]={'completed':len(cases),'rated':len(rated),'correct_and_source_supported':len(verified),
          'unrated':len(cases)-len(rated),'median_all_completed_seconds':median(cases),
          'median_verified_success_seconds':median(verified),'task_counts':dict(Counter(r['task']['id'] for r in cases))}
    return {'sessions':rows,'by_condition':out,'status':'NO_OBSERVATIONS' if not rows else 'EXPLORATORY_OBSERVATIONS',
      'notice':'Small convenience samples are descriptive. Check task/order balance, errors and verification time. No automatic causal or time-saving claim.'}
