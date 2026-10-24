"""Source-linked research explanations with bounded, inspectable claim composition.

Runtime reads source text and reusable per-paper claims, never benchmark answers.
Mechanical provenance is checked; semantic relevance still needs independent review.
"""
from __future__ import annotations
import hashlib, json, math, re, time, unicodedata, uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STOP = set('exactly entirely actually specific specifically together compared different methodology technique techniques approach improve improvement improved at least a an the and or of to in on for by with from as at is are was were be been being it its this that these those do does did how what which when why who can could would should will may into through between than their they them we our us use using used based paper papers model models method methods approach approaches system systems describe explain compare compared comparison differ difference differences tell me please according about'.split())

def normalize(text: str) -> str:
    text = unicodedata.normalize('NFKC', text)
    return re.sub(r'\s+', ' ', text).strip()

def words(text: str) -> list[str]:
    text=normalize(text).lower().replace('–','-').replace('—','-').replace('‑','-')
    out=[]
    for token in re.findall(r'[a-z0-9]+',text):
        if token in STOP or len(token)<2: continue
        # Modest morphological normalisation, not a semantic model.
        if token.endswith('ies') and len(token)>5:token=token[:-3]+'y'
        elif token.endswith('ing') and len(token)>6:token=token[:-3]
        elif token.endswith('s') and len(token)>4 and not token.endswith('ss'):token=token[:-1]
        
        for prefix,stem in [('encod','encode'),('represent','represent'),('evaluat','evaluate'),('generat','generate'),('retriev','retrieve'),('experimen','experiment'),('supervis','supervise'),('probabil','probability'),('relevan','relevant'),('pretrain','pretrain'),('fine','fine'),('calculat','score'),('comput','compute'),('combin','combine')]:
            if token.startswith(prefix): token=stem;break
        out.append(token)
    return out

def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).hexdigest()

def stamp() -> str:return datetime.now(timezone.utc).isoformat()

def atomic_json(path:Path,obj:Any)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex[:8]+'.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(path)

class LexicalIndex:
    def __init__(self,records:list[dict],texts:list[str]):
        self.records=records;self.counts=[Counter(words(t)) for t in texts]
        self.df=Counter(t for c in self.counts for t in c)
        self.n=len(records);self.lens=[sum(c.values()) for c in self.counts]
        self.avg=sum(self.lens)/max(1,self.n)
        self.idf={t:1+math.log((1+self.n)/(1+n)) for t,n in self.df.items()}
        self.norms=[math.sqrt(sum(((1+math.log(v))*self.idf[t])**2 for t,v in c.items())) or 1 for c in self.counts]
    def scores(self,query:str,method:str='hybrid')->list[float]:
        if method not in {'hybrid','bm25','tfidf'}:raise ValueError('Unknown retrieval method')
        q=Counter(words(query));qt={t:(1+math.log(v))*self.idf[t] for t,v in q.items() if t in self.idf}
        qnorm=math.sqrt(sum(v*v for v in qt.values())) or 1
        tf=[];bm=[]
        for i,c in enumerate(self.counts):
            tf.append(sum((1+math.log(c[t]))*self.idf[t]*v for t,v in qt.items() if c[t])/(self.norms[i]*qnorm))
            b=0.0
            for t in q:
                f=c.get(t,0)
                if f:
                    di=self.df[t];idf=math.log(1+(self.n-di+0.5)/(di+0.5))
                    b+=idf*f*2.2/(f+1.2*(0.25+0.75*self.lens[i]/max(self.avg,1)))
            bm.append(b)
        if method=='tfidf':return tf
        if method=='bm25':return bm
        result=[0.0]*self.n
        for scores in (tf,bm):
            for rank,i in enumerate(sorted(range(self.n),key=lambda i:(-scores[i],i))):
                if scores[i]>0:result[i]+=1/(61+rank)
        return result

FACETS = {
 'condition':r'\b(when|circumstances?|conditions?|trigger\w*|stride|frequency|interval|omit|leave out|empty|threshold|selective)\b',
 'training':r'\b(train\w*|learn\w*|pre-?train\w*|fine.?tun\w*|warm.?up|supervis\w*|negative\w*|objective\w*)\b',
 'representation':r'\b(represent\w*|encod\w*|embedding\w*|sparse|dense|vectors?|late.interaction)\b',
 'inference':r'\b(process\w*|generat\w*|decoder|fusion|combin\w*|score|scoring|probabilit\w*|softmax|logits?)\b',
 'retrieval':r'\b(retriev\w*|fetch|index|indices|quer\w*|search)\b',
 'evaluation':r'\b(evaluat\w*|benchmark\w*|metrics?|measure\w*|quality|faithful\w*|judge\w*|assess\w*|relevance|reference.free|perform\w*|unanswered|out.of.knowledge|out.of.kb)\b',
 'efficiency':r'\b(cost|efficien\w*|storage|space|footprint|latency|scal\w*|compress\w*)\b',
 'limitations':r'\b(limitations?|fail\w*|weakness\w*|risk\w*|trade.?off|disadvantage\w*)\b'
}
FACET_LABELS={'condition':'Decision or trigger','training':'Learning and supervision','representation':'Representation',
              'inference':'How the method works','retrieval':'Retrieval and queries','evaluation':'Evaluation and support',
              'efficiency':'Efficiency','limitations':'Limits and trade-offs','scale':'Reported scale','purpose':'Role'}
MEASURES={
 'electricity':r'\b(kilowatt|kwh|electricity|energy consumption)\b',
 'hosting_cost':r'\b(hosting cost|cloud cost|monthly cost|dollars|price|budget|cost per)\b',
 'deployment_latency':r'\b(p95|p99|concurrent|simultaneous)\b.*\b(latency|users|response)\b|\b(latency|response)\b.*\b(p95|p99|concurrent|simultaneous)\b',
 'attack_success':r'\b(attack success|prompt.injection|malicious instructions|security benchmark)\b',
 'learning_rate':r'\blearning.rate\b',
 'ndcg_score':r'\b(ndcg@?10|ndcg)\b.*\b(difference|measured|score|result)\b',
 'dataset_count':r'\bhow many\s+(?:\w+\s+){0,2}datasets\b',
 'database_tokens':r'\b(database|corpus)\b.*\b(large|size|trillion|tokens)\b|\b(how large|trillion tokens)\b',
 'training_example_count':r'\bhow many\s+(?:training\s+)?examples\b',
 'parameter_count':r'\b(how many|number of|size)\b.*\bparameters\b'
}

class Workbench:
    def __init__(self,root:Path=ROOT):
        self.root=Path(root)
        self.sources=json.loads((self.root/'corpus/sources.json').read_text(encoding="utf-8"))
        self.by_source={s['source_id']:s for s in self.sources}
        manifest=json.loads((self.root/'corpus/manifest.json').read_text(encoding="utf-8"))
        self.papers={p['id']:dict(p) for p in manifest['papers']}
        for pid,p in self.papers.items():
            s=next(s for s in self.sources if s['paper_id']==pid)
            p.update(title=s['title'],url=s['url'],pdf_file=s['pdf_file'],pdf_sha256=s['sha256'])
        self.claims=json.loads((self.root/'knowledge/claims.json').read_text(encoding="utf-8"))['claims']
        self.by_claim={c['id']:c for c in self.claims}
        self.validate_catalogue()
        self.source_index=LexicalIndex(self.sources,[s['title']+' '+s['section']+' '+s['text'] for s in self.sources])
        self.claim_index=LexicalIndex(self.claims,[c['text']+' '+(' '.join(c['tags'])+' ')*2+' '+' '.join(c['facets']) for c in self.claims])
        self.claim_hash=digest(self.claims);self.corpus_hash=digest(self.sources)
        self.code_hash=hashlib.sha256(b''.join(p.relative_to(self.root).as_posix().encode()+p.read_bytes() for folder in ['workbench','web','config','research_assistant'] for p in sorted((self.root/folder).glob('*')) if p.is_file())).hexdigest()
    def validate_catalogue(self)->None:
        if len(self.by_claim)!=len(self.claims):raise ValueError('Duplicate claim IDs')
        for c in self.claims:
            if not c.get('text') or not c.get('evidence'):raise ValueError('Claim without text or evidence')
            for e in c['evidence']:
                s=self.by_source.get(e['source_id'])
                if not s or s['paper_id']!=c['paper_id']:raise ValueError('Wrong-paper evidence link '+c['id'])
                text=normalize(s['text'])
                if text[e['start']:e['end']]!=e['quote']:raise ValueError('Evidence offset mismatch '+c['id'])
                if hashlib.sha256(text.encode()).hexdigest()!=e['source_sha256']:raise ValueError('Source text changed '+c['id'])
    def names(self,query:str)->list[str]:
        q=normalize(query).lower().replace('–','-').replace('—','-').replace('‑','-')
        matches=[]
        for pid,p in self.papers.items():
            for alias in sorted(set([pid]+p.get('aliases',[])),key=lambda a:(-len(a),a)):
                alias=alias.lower().replace('–','-').replace('—','-').replace('‑','-')
                for m in re.finditer(r'(?<![\w-])'+re.escape(alias)+r'(?![\w-])',q):
                    if pid=='rag' and alias=='rag' and re.match(r'\s+(?:systems?|pipelines?|evaluation|tools?|frameworks?)\b',q[m.end():]):
                        continue
                    matches.append((m.start(),m.end(),pid))
        # Longer entity spans own contained tokens: Corrective RAG is not also RAG.
        accepted=[]
        for start,end,pid in sorted(matches,key=lambda x:(-(x[1]-x[0]),x[0],x[2])):
            if not any(start < b and end > a for a,b,_ in accepted):
                accepted.append((start,end,pid))
        if re.search(r'\bhyde\b',q):accepted.append((q.index('hyde'),q.index('hyde')+4,'ragsurvey'))
        result=[]
        for _,_,pid in sorted(accepted):
            if pid not in result:result.append(pid)
        return result
    def search(self,query:str,*,method:str='hybrid',route:bool=True,k:int=5)->dict:
        if not isinstance(k,int) or not 1<=k<=30:raise ValueError('k must be 1–30')
        scores=self.source_index.scores(query,method)
        order=[i for i in sorted(range(len(scores)),key=lambda i:(-scores[i],i)) if scores[i]>0]
        named=self.names(query) if route else []
        if named:
            queues={pid:[i for i in order if self.sources[i]['paper_id']==pid] for pid in named};order=[]
            while any(queues.values()):
                for pid in named:
                    if queues[pid]:order.append(queues[pid].pop(0))
        return {'named_papers':named,'method':method,'first_stage':[dict(self.sources[i],score=scores[i]) for i in order[:k]],
                'score_notice':'Ranking scores are not probabilities of correctness.'}
    def semantic_query(self,question:str,named:list[str])->str:
        q=normalize(question).lower().replace('–','-').replace('—','-').replace('‑','-')
        aliases=sorted({a.lower() for pid in named for a in [pid]+self.papers[pid].get('aliases',[])},key=len,reverse=True)
        for a in aliases:q=re.sub(r'(?<![\w-])'+re.escape(a)+r'(?![\w-])',' ',q)
        return normalize(q)
    def plan(self,question:str)->dict:
        from .planning import build_plan
        named=self.names(question)
        return build_plan(self.semantic_query(question,named), named, MEASURES)
    def answer(self,question:str,*,mode:str='explain',method:str='hybrid',persist:bool=True,planner=None)->dict:
        if not isinstance(question,str) or not question.strip():raise ValueError('Enter a question')
        question=question.strip()
        if len(question)>4000:raise ValueError('Question is limited to 4,000 characters')
        if mode not in {'explain','search'}:raise ValueError('Unknown mode')
        begin=time.perf_counter();plan=self.plan(question)
        search=self.search(question,method=method,k=8)
        result={'run_id':datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:10],
          'created_utc':stamp(),'question':question,'mode':mode,'status':'source_evidence','plan':plan,
          'blocks':[],'comparison':[],'citations':[],'missing':[],'warnings':[],
          'first_stage':[s['source_id'] for s in search['first_stage']], 'retrieved':search['first_stage'],
          'hashes':{'corpus':self.corpus_hash,'knowledge':self.claim_hash,'code':self.code_hash},
          'notice':'This explanation is assembled from stored, source-linked summaries. Check the cited pages before relying on the answer; source links alone do not verify correctness.',
          'independently_verified':False,'attempts':[]}
        if mode=='explain':self._compose(question,plan,result,planner)
        result['elapsed_seconds']=time.perf_counter()-begin
        if persist:atomic_json(self.root/'results/runs'/(result['run_id']+'.json'),result)
        return result
    def _compose(self,q:str,plan:dict,result:dict,planner=None)->None:
        named=plan['named_papers'];semantic=self.semantic_query(q,named)
        scope=named or list(self.papers)
        measures=plan['measures']
        relevant_metrics={m for c in self.claims if c['paper_id'] in scope for m in c['metrics']}
        absent_metrics=[m for m in measures if m not in relevant_metrics]
        # Narrow, auditable concept-scope checks, not a general entailment detector.
        concepts={
            'prediction-powered inference':r'\bppi\b|prediction.powered inference',
            'Inverse Cloze Task':r'\bict\b|inverse cloze',
            'MaxSim':r'\bmaxsim\b',
            'LoRA':r'\blora\b|low.rank adaptation'}
        if len(named)==1:
            linked=' '.join(c['text']+' '+' '.join(c['tags']) for c in self.claims if c['paper_id']==named[0]).lower()
            missing_concepts=[label for label,pattern in concepts.items() if re.search(pattern,semantic) and not re.search(pattern,linked)]
            if missing_concepts:
                result['missing'].append('The indexed '+named[0].upper()+' claims do not establish the requested concept: '+', '.join(missing_concepts)+'. Inspect the source search instead of assuming this mechanism belongs to that paper.')
                result['status']='insufficient';return
        if absent_metrics:
            result['missing'].append('No source-linked claim establishes the requested measurement: '+', '.join(m.replace('_',' ') for m in absent_metrics)+'.')
            # No guessed measurements or substitutions from another benchmark.
            result['status']='insufficient';return
        from .planning import select_claims, check_coverage
        chosen,candidates,scope=select_claims(self,q,plan,result)
        if planner and candidates:
            try:
                candidate_claims=candidates[:35]
                selected_ids,trace=planner.select(q,candidate_claims,[c['id'] for c in chosen])
                result['attempts'].append(trace)
                allowed={c['id'] for c in candidate_claims}
                if not selected_ids or not set(selected_ids)<=allowed:raise ValueError('Unknown claim ID from planner')
                proposed=[self.by_claim[i] for i in dict.fromkeys(selected_ids)]
                if {c['paper_id'] for c in proposed}!={c['paper_id'] for c in chosen}:raise ValueError('Planner dropped or added a paper')
                if len(proposed)>16:raise ValueError('Planner selected too many claims')
                old=check_coverage(self,plan,chosen,scope)
                new=check_coverage(self,plan,proposed,scope)
                if any(a['covered'] and not b['covered'] for a,b in zip(old,new)):
                    raise ValueError('Planner removed requested clause coverage')
                chosen=proposed
            except Exception as e:
                if getattr(e,'trace',None):result['attempts'].append(e.trace)
                elif not result['attempts']:result['attempts'].append({'role':'claim_selector','error':str(e),'generated_factual_prose_displayed':False})
                result['warnings'].append('Optional selector unavailable or invalid; used deterministic selection. '+str(e))
        result['clause_coverage']=check_coverage(self,plan,chosen,scope)
        for row in result['clause_coverage']:
            if not row['covered']:
                label='/'.join(x.upper() for x in row['paper_ids']) or 'INDEXED PAPERS'
                result['missing'].append(label+': no selected claim covers the detected request "'+row['question_part']+'" ('+row['facet']+').')
        if not chosen:
            result['status']='insufficient';result['missing'].append('No supported explanation could be assembled.');return
        for c in chosen:
            result['blocks'].append({'claim_id':c['id'],'paper_id':c['paper_id'],'text':c['text'],
                                    'facets':c['facets'],'source_ids':list(dict.fromkeys(e['source_id'] for e in c['evidence']))})
        ids=list(dict.fromkeys(sid for b in result['blocks'] for sid in b['source_ids']))
        result['citations']=[self.by_source[sid] for sid in ids]
        if len(scope)>=2:
            # Parallel source-backed facts, never an invented causal relationship.
            for pid in scope:
                result['comparison'].append({'paper_id':pid,'title':self.papers[pid]['title'],
                    'claims':[b for b in result['blocks'] if b['paper_id']==pid]})
        if re.search(r'\bhyde\b',q,re.I):
            result['missing'].append('HyDE is represented here by a secondary survey summary; its original paper is not separately indexed. The explanation is limited to that source.')
        if len(scope)>=2 and re.search(r'\b(better|best|more accurate|outperforms?|faster|less memory|lower latency)\b',semantic):
            result['missing'].append('The selected method descriptions do not establish a controlled head-to-head winner. A common dataset, metric and comparable run are needed for that claim.')
        result['status']='partial' if result['missing'] else 'source_linked_explanation'
        result['coverage_notice']='Clause coverage is a lexical/facet heuristic, not proof of semantic completeness. Original source review is still required.'
        # Optional computationally true measurements are not extrapolated to unmeasured datasets.
        result['warnings'].append('Curated summaries can still contain errors or miss your intended question. Inspect the supporting passages and PDFs.')

def markdown(result:dict)->str:
    lines=['# Research Workbench result','',result['question'],'',f"**Status:** {result['status']}",'',result['notice'],'']
    for block in result['blocks']:
        lines += [f"### {block['paper_id'].upper()}",block['text']+' '+ ' '.join('['+i+']' for i in block['source_ids']),'']
    if result['missing']:lines+=['## Missing support']+[f'- {x}' for x in result['missing']]+['']
    lines+=['## Sources']
    for s in result.get('citations',[]) or result['retrieved']:
        lines += [f"### [{s['source_id']}] {s['title']} (PDF pp. {s['page_start']}–{s['page_end']})",s['text'],'']
    lines+=['## Reproducibility',json.dumps({'run_id':result['run_id'],'hashes':result['hashes'],'plan':result['plan']},indent=2)]
    return '\n'.join(lines)
