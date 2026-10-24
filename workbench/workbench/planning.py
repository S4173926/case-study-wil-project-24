"""Clause-aware deterministic selection. These checks are not semantic validation.

No benchmark IDs or answer keys enter this module. Question parts are matched to
reusable source-linked claims. Missing parts remain visible instead of being
silently suppressed by a stronger keyword elsewhere in the question.
"""
from __future__ import annotations
import re
from typing import Any

# Background terms cannot alone justify an answer to an unrelated question.
BACKGROUND = set('each same all more only without where make making if not cite source support supported report collection state establish exact passage document text information context question answer relevant language model entire numerical correct precise provide contain need several multiple input output'.split())
CONDITION = r'\b(circumstances?|conditions?|trigger\w*|threshold|stride|frequen\w*|interval|omit\w*|leave out|empty|selective|low.confidence)\b'
NOISE = r'\b(noisy|noise|unhelpful|irrelevant|inadequate)\b'


def parts(query: str) -> list[str]:
    """Split explicit independent requests, not every occurrence of 'and'."""
    split = re.split(r'[?;]+\s*|,\s*(?=(?:and\s+)?(?:how|why|what|when|which|whether)\b)|\s+and\s+(?=(?:how|why|what|when|which|whether)\b)', query)
    from .core import words
    result=[]
    for part in split:
        part=re.sub(r'^and\s+', '',part.strip(' ,.?'))
        if not words(part):continue
        if re.match(r'^(?:answer only|if no|cite (?:the|an|a)|state that|say so|use (?:only )?(?:the )?sources)',part):continue
        result.append(part)
    return result


def facets(part: str) -> list[str]:
    """Detect intent locally; a contextual 'when' is not a trigger question."""
    out=[]
    training=bool(re.search(r'\b(train\w*|learn\w*|pre.?train\w*|fine.?tun\w*|warm.?up|supervis\w*|negative\w*|objective\w*)\b',part))
    inference=bool(re.search(r'\b(process\w*|compress\w*|generat\w*|decoder|fusion|combin\w*|ensemble\w*|predictions?|reader|softmax|logits?)\b|black.box|\bfrozen\b',part))
    condition=bool(re.search(CONDITION,part) or re.match(r'^(?:when|under what|in what circumstances)\b',part))
    representation=bool(re.search(r'\b(represent\w*|encod\w*|embedding\w*|sparse|dense|vectors?|late.interaction)\b',part))
    evaluation=bool(re.search(r'\b(evaluat\w*|benchmark\w*|metrics?|faithful\w*|judge\w*|assess\w*|reference.free|unanswered|out.of.knowledge|out.of.kb)\b',part))
    if re.search(r'answer relevance|context relevance|reference.free|reference answer|quality aspects|measure.*(?:quality|generation)',part):evaluation=True
    if evaluation and not re.search(r'\b(encoder|decoder|fusion)\b',part):inference=False
    efficiency=bool(re.search(r'\b(cost|efficien\w*|storage|space|footprint|latency|scal\w*|flops|regulari[sz]\w*)\b',part))
    if re.match(r'^why\b',part) and re.search(r'\b(more|many|number)\b',part) and re.search(r'\b(encod\w*|passages?)\b',part):efficiency=True
    limitations=bool(re.search(r'\b(limitations?|fail\w*|weakness\w*|risk\w*|trade.?off|disadvantage\w*)\b',part))
    # A score can mean a retrieval mechanism or an evaluation metric. Preserve
    # the explicit evaluation intent; otherwise request the operational mechanism.
    if re.search(r'\b(score|scoring|calculate|numerical|probabilit\w*)\b',part) and not training:
        if re.search(r'answer relevance|context relevance|\b(faithfulness|metric\w*|evaluat\w*|judge\w*|systems?)\b',part):evaluation=True
        else:inference=True
    if re.search(r'\b(give|feed|supply|prepend|incorporat\w*)\b.*\b(documents?|passages?)\b.*\b(model|reader|input)\b',part):inference=True
    if re.search(r'\b(mask\w*|construct\w*|formulat\w*|rewrite\w*)\b.*\b(quer\w*|search)\b',part):
        out.append('retrieval')
        inference=True
    if condition:out.append('condition')
    if training:out.append('training')
    # "How is a reader trained?" is not necessarily about inference. Distinct
    # clauses still carry their own requests and are never overwritten.
    if inference and not training:out.append('inference')
    if representation and not condition and (not training or re.search(r'\b(represent\w*|embedding\w*|sparse|dense)\b',part)):out.append('representation')
    if evaluation:out.append('evaluation')
    if efficiency and not condition:out.append('efficiency')
    if limitations:out.append('limitations')
    if not out and re.search(r'\b(retriev\w*|fetch|index|indices|quer\w*|search)\b',part):out.append('retrieval')
    if not out and re.search(r'\b(output|before|make use)\b',part):out.append('inference')
    return out


def expand(part: str) -> str:
    """Small, declared synonym expansions; never complete expected answers."""
    extra=[]
    if re.search(r'\bwhere\b.*\b(input|context|passage|document)\b',part):extra.extend(['position','location'])
    if re.search(r'\bevaluat\w*\b|\bscore\b.*\bsystems?\b',part):extra.extend(['evaluation','metrics','judges','scores'])
    if re.search(NOISE,part):extra.extend(['irrelevant','unhelpful','inadequate','confidence'])
    if re.search(r'\b(combin\w*|ensemble\w*)\b',part):extra.extend(['fusion','probabilities'])
    if re.search(r'\bdocuments?\b',part):extra.append('passages')
    if re.search(r'\bpassages?\b',part):extra.append('documents')
    return part+' '+' '.join(extra)


def build_plan(query: str, named: list[str], measures: dict[str,str]) -> dict[str,Any]:
    obligations=[]
    for index,part in enumerate(parts(query)):
        detected=facets(part)
        # "Which method has property X?" asks for a supported match, not a
        # false assertion that every compared method has that property.
        scope='any' if len(named)>1 and re.match(r'^which\s+(?:method|one|approach|system)\b',part) else 'each'
        obligations.append({'id':f'part{index+1}','text':part,'facets':detected or ['purpose'],
                            'explicit':bool(detected),'scope':scope})
    empty=not obligations
    if empty:
        defaults=['purpose','representation','training'] if len(named)>1 else ['purpose','inference']
        obligations=[{'id':'part1','text':query or 'overview','facets':defaults,'explicit':False,'scope':'each'}]
    requested=list(dict.fromkeys(f for o in obligations for f in o['facets']))
    return {'named_papers':named,'facets':requested or ['purpose','inference'],
            'explicit_facets':any(o['explicit'] for o in obligations),
            'measures':[name for name,pattern in measures.items() if re.search(pattern,query)],
            'is_comparison':len(named)>=2,'obligations':obligations,
            'generic_overview':empty or (len(named)>=2 and not any(o['explicit'] for o in obligations) and task_tokens(query)<={'better','best','accurate','outperform','faster'}),
            'planner':'clause-aware lexical intent matching; not a semantic completeness certificate'}


def task_tokens(text: str) -> set[str]:
    from .core import words
    return set(words(text))-BACKGROUND


def claim_text(claim: dict) -> str:
    return claim['text']+' '+' '.join(claim['tags'])


def meaningful_match(part: str, claim: dict) -> bool:
    """Reject an unrelated request even when a paper name or broad facet matches."""
    if matched_phrases(part,claim):return True
    tokens=task_tokens(expand(part))
    if not tokens:return True
    target=task_tokens(claim_text(claim))
    if len(tokens & target)/len(tokens)>=0.18:return True
    if re.search(NOISE,part) and re.search(NOISE,claim_text(claim),re.I):return True
    return False


def matched_phrases(part: str, claim: dict) -> list[str]:
    # Preserve labels such as "answer relevance" whose individual words can be
    # background elsewhere. This operates on catalogue tags, not question IDs.
    clean=lambda x:re.sub(r'[^a-z0-9]+',' ',x.lower()).strip()
    q=' '+clean(part)+' '
    return [t for t in claim['tags'] if len(clean(t).split())>=2 and ' '+clean(t)+' ' in q]


def local_scores(workbench, part: str) -> dict[str,float]:
    requested=set(facets(part))
    return {c['id']:score+0.09*min(3,len(requested & set(c['facets'])))+0.20*bool(matched_phrases(part,c))
            for c,score in zip(workbench.claims,workbench.claim_index.scores(expand(part),'tfidf'))}


def check_coverage(workbench, plan: dict, selected: list[dict], scope: list[str]) -> list[dict]:
    """Return explicit heuristic coverage, including unmatched subquestions."""
    rows=[]
    for obligation in plan['obligations']:
        groups=[scope] if obligation['scope']=='any' else [[p] for p in scope]
        for group in groups:
            for facet in obligation['facets']:
                matching=[c for c in selected if c['paper_id'] in group and
                          (facet in c['facets'] or not obligation['explicit'] or bool(set(plan['measures']) & set(c['metrics']))) and (plan.get('generic_overview') or meaningful_match(obligation['text'],c))]
                rows.append({'part_id':obligation['id'],'question_part':obligation['text'],
                             'paper_ids':group,'facet':facet,'covered':bool(matching),
                             'claim_ids':[c['id'] for c in matching],
                             'verification':'lexical/facet coverage only; human source review required'})
    return rows


def select_claims(workbench, question: str, plan: dict, result: dict) -> tuple[list[dict],list[dict],list[str]]:
    """Select independently for each requested clause and each named paper."""
    from .core import words
    named=plan['named_papers'];scope=named or list(workbench.papers)
    if len(scope)>4 and named:
        result['missing'].append('Compare at most four named papers at a time.')
        return [],[],scope
    whole=workbench.semantic_query(question,named)
    global_scores=local_scores(workbench,whole)
    by_part={o['id']:local_scores(workbench,o['text']) for o in plan['obligations']}
    measured=plan['measures']
    candidates=[]
    for claim in workbench.claims:
        if claim['paper_id'] not in scope:continue
        if measured and not any(m in claim['metrics'] for m in measured):continue
        applicable=[o for o in plan['obligations'] if plan.get('generic_overview') or meaningful_match(o['text'],claim)]
        if not applicable:continue
        score=max(by_part[o['id']][claim['id']] for o in applicable)+0.25*global_scores[claim['id']]
        if plan.get('generic_overview'):score+=0.1*int('purpose' in claim['facets'])+0.01
        if score<=0:continue
        candidates.append((score,claim))
    candidates.sort(key=lambda item:(-item[0],item[1]['id']))
    if not named:
        # Keep the previous conservative unscoped discovery requirement. Shared
        # background words cannot support deployment measurements or arbitrary facts.
        essential=task_tokens(whole)
        candidates=[(s,c) for s,c in candidates if not essential or
                    len(essential & task_tokens(claim_text(c)))/len(essential)>=0.50]
        if not candidates or candidates[0][0]<0.16:return [],[],[]
        scope=[candidates[0][1]['paper_id']]
        candidates=[(s,c) for s,c in candidates if c['paper_id'] in scope]
        result['warnings'].append('No paper was named. This is a candidate match, not an exhaustive comparison of the literature.')
    selected=[]
    allowed=[c for _,c in candidates]
    for obligation in plan['obligations']:
        groups=[scope] if obligation['scope']=='any' else [[pid] for pid in scope]
        for group in groups:
            local=[c for c in allowed if c['paper_id'] in group and (plan.get('generic_overview') or meaningful_match(obligation['text'],c))]
            local.sort(key=lambda c:(-by_part[obligation['id']][c['id']],c['id']))
            for facet in obligation['facets']:
                matches=[c for c in local if facet in c['facets'] or bool(set(plan['measures']) & set(c['metrics']))]
                if not matches and not obligation['explicit']:matches=local
                if matches and matches[0] not in selected:selected.append(matches[0])
            # Training and evaluation questions may require stages or metrics in
            # several claims. These are supplemental detail, not a success score.
            if any(f in obligation['facets'] for f in ['training','evaluation']):
                relevant=[c for c in local if set(c['facets']) & set(obligation['facets'])]
                if relevant:
                    top=by_part[obligation['id']][relevant[0]['id']]
                    for claim in relevant:
                        if sum(c['paper_id'] in group for c in selected)>=3:break
                        if claim not in selected and by_part[obligation['id']][claim['id']]>=top*0.30:selected.append(claim)
    # Stable paper order and a bounded display. Coverage is computed AFTER the cap.
    chosen=[]
    for pid in scope:
        chosen.extend([c for c in selected if c['paper_id']==pid][:4])
    # The optional planner sees all selected facts first, preventing truncation
    # from excluding a clause that was deterministically covered.
    ordered=chosen+[c for c in allowed if c not in chosen]
    return chosen,ordered,scope
