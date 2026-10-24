'use strict';
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let config, papers=[], latestResult=null, pilot=null, timer=null;
let reviewRuns=[], selectedReviewId='', reviewSequence=0, reviewDirty=false;
const localSession={get:k=>{try{return sessionStorage.getItem(k);}catch{return null;}},set:(k,v)=>{try{sessionStorage.setItem(k,v);}catch{}},remove:k=>{try{sessionStorage.removeItem(k);}catch{}}};
const titles={ask:'Understand the method. See the evidence.',library:'Your research, in one place.',review:'Check the answer. Keep the evidence.',pilot:'Does the tool make research easier?'};
async function api(path,data){
 const options=data===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Workbench-Token':config.csrf},body:JSON.stringify(data)};
 const response=await fetch(path,options);let body;
 try{body=await response.json();}catch{throw new Error('The local server returned an unreadable response.');}
 if(!response.ok)throw new Error(body.error||'Request failed');return body;
}
function error(e){$('global-error').hidden=false;$('global-error').textContent=e.message||String(e);}
function clearError(){$('global-error').hidden=true;}
function refButtons(ids){return ids.map(id=>`<button class="source-ref" type="button" data-source="${esc(id)}">${esc(id)}</button>`).join(' ');}
function pageLabel(s){return Number(s.page_start)===Number(s.page_end)?'PDF p. '+s.page_start:'PDF pp. '+s.page_start+'–'+s.page_end;}
function sourceBlock(s){return `<details class="source-block"><summary>[${esc(s.source_id)}] ${esc(s.title)} · ${esc(pageLabel(s))}</summary><p class="source-text">${esc(s.text)}</p><div class="actions"><button type="button" class="secondary" data-source="${esc(s.source_id)}">Open source & PDF</button><a href="/pdf/${encodeURIComponent(s.paper_id)}.pdf#page=${Number(s.page_start)}" target="_blank" rel="noopener">Original PDF ↗</a></div></details>`;}
function resultHTML(r){
 const grouped={};r.blocks.forEach(b=>(grouped[b.paper_id]??=[]).push(b));
 let content=Object.entries(grouped).map(([pid,blocks])=>`<article class="answer-paper"><h3>${esc(({fid:'Fusion-in-Decoder',recomp:'RECOMP',replug:'REPLUG',icralm:'In-Context RALM'})[pid]||pid.toUpperCase())}</h3>${blocks.map(b=>`<p>${esc(b.text)}</p><div>${refButtons(b.source_ids)}</div>`).join('')}</article>`).join('');
 const label={source_linked_explanation:'SOURCE-LINKED EXPLANATION',partial:'PARTIAL EXPLANATION',insufficient:'SUPPORT NOT ESTABLISHED',source_evidence:'ORIGINAL SOURCE SEARCH'}[r.status]||r.status;
 const sources=r.citations.length?r.citations:r.retrieved;
 return `<article class="result-panel"><div class="result-heading"><span class="status">${esc(label)}</span><span class="result-meta">${Number(r.elapsed_seconds).toFixed(2)} s</span></div><p class="result-question">${esc(r.question)}</p><div class="stale-warning warning" hidden>Inputs have changed. This is still the result for the submitted question shown above; submit again for a new result.</div>${content?`<div class="answer-grid">${content}</div>`:''}${r.missing.length?`<div class="warning"><strong>What is not established</strong><p>${r.missing.map(esc).join('<br>')}</p><p class="small">This is a limit of the indexed claims, not proof that a fact does not exist anywhere in the papers.</p></div>`:''}<p class="small">${esc(r.mode==='search'?'Retrieved passages are search results, not a generated answer.':'Source-linked summaries. Verify the cited pages before relying on the answer.')}</p>${r.warnings.length?`<details><summary>Scope and limitations</summary>${r.warnings.map(w=>`<p>${esc(w)}</p>`).join('')}</details>`:''}${r.status==='insufficient'?`<details class="related-sources"><summary>Related search results, not support for the requested claim</summary><p class="small">These passages may discuss similar terms. They do not establish the missing measurement or prove its absence.</p>${sources.map(sourceBlock).join('')}</details>`:`<h3>${r.mode==='search'?'Retrieved passages':'Evidence behind the explanation'}</h3>${sources.map(sourceBlock).join('')}`}<div class="actions"><a href="/api/run/${esc(r.run_id)}?format=md">Export answer + evidence</a><a href="/api/run/${esc(r.run_id)}" target="_blank" rel="noopener">Full JSON run record</a><button class="secondary" type="button" data-review="${esc(r.run_id)}">Review this result</button></div><p class="result-meta">Run ${esc(r.run_id)} · ${esc(r.plan.named_papers.join(', ')||'discovery search')} · ${r.blocks.length} source-linked claim(s). Status is not an accuracy score.</p></article>`;
}
async function openSource(id){
 const s=await api('/api/source/'+encodeURIComponent(id));
 $('source-content').innerHTML=`<span class="eyebrow">ORIGINAL SOURCE CONTEXT</span><h2>${esc(s.title)}</h2><p class="small">[${esc(s.source_id)}] · ${esc(s.section)} · PDF pages ${s.page_start}–${s.page_end}</p><p class="source-text">${esc(s.text)}</p><p><a href="/pdf/${encodeURIComponent(s.paper_id)}.pdf#page=${s.page_start}" target="_blank" rel="noopener">Open the full original PDF ↗</a></p><iframe title="Original research paper" src="/pdf/${encodeURIComponent(s.paper_id)}.pdf#page=${s.page_start}"></iframe>`;
 $('source-dialog').showModal();
}
function showPage(page){document.querySelectorAll('.page').forEach(el=>el.hidden=el.id!=='page-'+page);document.querySelectorAll('.nav').forEach(el=>el.classList.toggle('active',el.dataset.page===page));$('page-title').textContent=titles[page];document.querySelectorAll('.nav').forEach(el=>el.setAttribute('aria-current',el.dataset.page===page?'page':'false'));if(page==='review')refreshReviews().catch(error);if(page==='pilot')refreshPilot().catch(error);}
function markStale(){if(!latestResult)return;const changed=$('question').value.trim()!==latestResult.question||$('mode').value!==latestResult.mode||$('method').value!==latestResult.method_selected||false!==latestResult.model_selected;document.querySelectorAll('#result .stale-warning').forEach(e=>e.hidden=!changed);}
$('question').addEventListener('input',markStale);['mode','method'].forEach(id=>$(id).addEventListener('change',()=>{markStale();$('ask-button').textContent=$('mode').value==='search'?'Find source passages':'Build explanation';}));
$('ask-form').addEventListener('submit',async e=>{e.preventDefault();clearError();const b=$('ask-button');b.disabled=true;b.textContent=false?'Selecting local claims…':'Retrieving source claims…';try{const request={question:$('question').value,mode:$('mode').value,method:$('method').value,use_model:false};const r=await api('/api/ask',request);r.method_selected=request.method;r.model_selected=false;latestResult=r;$('result').innerHTML=resultHTML(r);markStale();$('result').scrollIntoView({behavior:'smooth',block:'start'});}catch(e){error(e);}finally{b.disabled=false;b.textContent=$('mode').value==='search'?'Find source passages':'Build explanation';}});
document.addEventListener('click',async e=>{const element=e.target.closest('button');if(!element)return;try{if(element.dataset.page)showPage(element.dataset.page);if(element.dataset.example){$('question').value=element.dataset.example;markStale();$('question').focus();}if(element.dataset.source)await openSource(element.dataset.source);if(element.dataset.review){showPage('review');await refreshReviews();await selectReviewById(element.dataset.review);}}catch(err){error(err);}});
$('close-source').addEventListener('click',()=>$('source-dialog').close());
function renderPapers(){const q=$('paper-filter').value.toLowerCase();const filtered=papers.filter(p=>(p.id+' '+p.title).toLowerCase().includes(q));$('paper-list').innerHTML=filtered.length?filtered.map(p=>`<article class="paper-card"><span class="eyebrow">${esc(p.id)}</span><h3>${esc(p.title)}</h3><p class="small">${esc(p.role||'')} · frozen source version</p><a href="/pdf/${encodeURIComponent(p.id)}.pdf" target="_blank" rel="noopener">Read original PDF ↗</a></article>`).join(''):'<div class="empty-state"><h3>No matching papers</h3><p>Try a method name, title or identifier from this collection.</p></div>';}
$('paper-filter').addEventListener('input',renderPapers);
const dimensions={correctness:'Factual correctness',completeness:'Question completeness',citation_support:'Claim-to-source support',relevance:'Relevance'};
$('rating-fields').innerHTML=Object.entries(dimensions).map(([key,label])=>`<label>${label}<select id="rating-${key}" required><option value="">Choose</option><option value="0">0 · Incorrect / absent</option><option value="1">1 · Partial</option><option value="2">2 · Fully meets</option></select></label>`).join('');

function versionDate(r){
 const date=new Date(r.created_utc);
 return Number.isNaN(date.getTime())?r.run_id:date.toLocaleString(undefined,{year:'numeric',month:'short',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit'});
}
function resetReviewScores(){
 ['answerable','review-notes'].forEach(id=>$(id).value='');
 Object.keys(dimensions).forEach(k=>$('rating-'+k).value='');
 $('source-checked').checked=false;$('review-message').textContent='';reviewDirty=false;
}
function filterRunRows(){
 const tokens=$('run-search').value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
 const version=$('run-version').value,status=$('run-status').value;
 // Version qualification precedes deduplication: a newer historical record must not hide a compatible repaired run.
 let rows=reviewRuns.filter(r=>version!=='current'||r.current_answer_set);
 if(version!=='all'){
   const seen=new Set();rows=rows.filter(r=>{const key=r.question.trim().toLocaleLowerCase().replace(/\s+/g,' ')+'|'+(r.mode||'explain');if(seen.has(key))return false;seen.add(key);return true;});
 }
 return rows.filter(r=>(!status||r.status===status)&&tokens.every(t=>(r.question_id+' '+r.question+' '+r.run_id+' '+(r.paper_ids||[]).join(' ')+' '+(r.paper_titles||[]).join(' ')).toLocaleLowerCase().includes(t)));
}
function renderRunOptions(){
 const rows=filterRunRows(), old=$('review-run').value;
 const keep=rows.some(r=>r.run_id===old);
 $('review-run').innerHTML='<option value="">'+(rows.length?'Choose a matching run':'No matching runs')+'</option>'+rows.map(r=>`<option title="${esc(r.question+' · '+r.run_id)}" value="${esc(r.run_id)}" ${r.available===false?'disabled':''}>${esc(r.question_id? r.question_id+' · ':'')}${esc(r.question.slice(0,110))} · ${esc(r.version_label)} · ${esc(versionDate(r))}</option>`).join('');
 if(keep)$('review-run').value=old;
 else if(old){selectedReviewId='';resetReviewScores();$('review-preview').innerHTML='';$('run-meta').hidden=true;reviewSequence++;}
 $('run-count').textContent=`${rows.length} matching ${rows.length===1?'run':'runs'} · ${reviewRuns.length} saved records. ${$('run-version').value==='current'?'Current answer set includes the verified repaired batch; older versions stay available under All saved versions.':''}`;
}
async function refreshReviews(){
 const [runs,stats]=await Promise.all([api('/api/runs'),api('/api/reviews')]);reviewRuns=runs;renderRunOptions();
 $('review-stats').innerHTML=`<div class="stats-row"><div class="stat"><strong>${stats.distinct_reviewed_runs} / ${stats.recorded_runs}</strong><span>Saved runs with human ratings, across all versions</span></div><div class="stat"><strong>${stats.answerable.n?stats.answerable.complete_correct_supported+'/'+stats.answerable.n:'Not measured'}</strong><span>Fully rated answers in resolved records</span></div><div class="stat"><strong>${stats.conflicting_run_ids.length}</strong><span>Runs needing rating adjudication</span></div></div><p class="small">${esc(stats.notice)} ${esc(stats.independence)} Historical and current runs are not a single final-version accuracy benchmark.</p>`;
}
async function previewReview(){
 const id=$('review-run').value,sequence=++reviewSequence;
 if(id!==selectedReviewId){resetReviewScores();selectedReviewId=id;}
 if(!id){$('review-preview').innerHTML='';$('run-meta').hidden=true;return;}
 const meta=reviewRuns.find(r=>r.run_id===id);
 $('run-meta').hidden=false;
 $('run-meta').textContent=`${meta?.question_id||'Ad hoc question'} · ${meta?.version_label||'Saved version'}\nRun: ${id}\n${meta?.current_answer_set?'Current/repaired answer set.':'Historical or unverified version: do not combine this rating with final-version results.'}${meta?.reviewed_by?.length?'\nPreviously rated by: '+meta.reviewed_by.join(', '):''}`;
 $('review-preview').innerHTML='<p role="status">Loading the selected answer…</p>';
 const r=await api('/api/run/'+encodeURIComponent(id));
 if(sequence!==reviewSequence||id!==$('review-run').value)return;
 $('review-preview').innerHTML=resultHTML(r);
}
async function selectReviewById(id){
 if(reviewDirty&&!window.confirm('Discard the unsaved rating before changing runs?'))return;
 $('run-search').value='';$('run-status').value='';$('run-version').value='all';renderRunOptions();$('review-run').value=id;await previewReview();
}
function filtersChanged(e){
 if(reviewDirty&&!window.confirm('Changing the filter may discard this unsaved rating. Continue?')){e.target.value=e.target.dataset.previous||'';return;}
 e.target.dataset.previous=e.target.value;reviewDirty=false;renderRunOptions();
}
$('run-search').addEventListener('input',filtersChanged);
['run-version','run-status'].forEach(id=>$(id).addEventListener('change',filtersChanged));
$('run-version').dataset.previous='current';
$('review-run').addEventListener('change',()=>{
 if(reviewDirty&&!window.confirm('Discard the unsaved rating before changing runs?')){$('review-run').value=selectedReviewId;return;}
 previewReview().catch(error);
});
['answerable','review-notes','source-checked',...Object.keys(dimensions).map(k=>'rating-'+k)].forEach(id=>$(id).addEventListener('input',()=>reviewDirty=true));
['reviewer-id','relationship'].forEach(id=>{
 const saved=localSession.get('reviewer-'+id);if(saved)$(id).value=saved;
 $(id).addEventListener('change',()=>localSession.set('reviewer-'+id,$(id).value));
});
$('review-form').addEventListener('submit',async e=>{
 e.preventDefault();clearError();if(!$('review-form').reportValidity())return;
 const data={run_id:$('review-run').value,reviewer_id:$('reviewer-id').value,relationship:$('relationship').value,answerable:$('answerable').value==='yes',source_checked:$('source-checked').checked,notes:$('review-notes').value};
 Object.keys(dimensions).forEach(k=>data[k]=Number($('rating-'+k).value));
 const button=$('save-review');button.disabled=true;
 try{await api('/api/review',data);reviewDirty=false;$('review-message').textContent='Rating saved for this exact run. No scores were assigned automatically.';await refreshReviews();}
 catch(e){error(e);}finally{button.disabled=false;}
});
function updateTimer(){if(!pilot)return;const seconds=Math.max(0,Math.floor(Date.now()/1000-pilot.started_timestamp));$('pilot-timer').textContent=Math.floor(seconds/60)+':'+String(seconds%60).padStart(2,'0');}
function activatePilot(r){pilot=r;$('pilot-start').hidden=true;$('active-pilot').hidden=false;$('pilot-question').textContent=r.task.question;$('pilot-instructions').textContent=r.condition==='manual'?'Use the Paper library and PDF viewer only. Do not view assisted explanations. Include source checking in your time.':'Use Ask & compare, then verify the supporting original PDF pages. Keep the timer running during verification.';localSession.set('activePilot',JSON.stringify(r));clearInterval(timer);timer=setInterval(updateTimer,1000);updateTimer();}
$('pilot-start').addEventListener('submit',async e=>{e.preventDefault();try{activatePilot(await api('/api/pilot/start',{participant_id:$('participant-id').value,task_id:$('pilot-task').value,condition:$('pilot-condition').value,consent:$('pilot-consent').checked,participant_role:$('participant-role').value}));}catch(e){error(e);}});
$('pilot-finish').addEventListener('submit',async e=>{e.preventDefault();if(!pilot)return;try{const r=await api('/api/pilot/finish',{session_id:pilot.session_id,answer:$('pilot-answer').value,sources:$('pilot-sources').value,help_received:$('pilot-help').value});clearInterval(timer);pilot=null;localSession.remove('activePilot');$('active-pilot').hidden=true;$('pilot-start').hidden=false;$('pilot-finish').reset();$('pilot-message').textContent=`Recorded ${r.seconds_including_verification.toFixed(1)} seconds, including verification. Correctness and source support remain unscored until human review.`;}catch(e){error(e);}});
(async()=>{try{config=await api('/api/config');$('corpus-stats').textContent=`${config.papers} papers · ${config.passages} passages · ${config.claims} claims`;papers=await api('/api/papers');renderPapers();const saved=localSession.get('activePilot');if(saved)activatePilot(JSON.parse(saved));}catch(e){error(e);}})();

let pilotRows=[];
async function refreshPilot(){const data=await api('/api/pilot');pilotRows=data.sessions.filter(r=>r.completed);$('pilot-summary').innerHTML=`<div class="stats-row">${Object.entries(data.by_condition||{}).map(([name,v])=>`<div class="stat"><span class="stat-label">${esc(name==='manual'?'Manual PDF search':'Assistant + source check')}</span><strong>${esc(v.completed??v.n??v.count??0)}</strong><span>Completed tasks</span><p class="small">${esc(v.median_verified_success_seconds==null?'Timing interpreted only after source-based review.':'Median verified task time: '+Number(v.median_verified_success_seconds).toFixed(1)+' s')}</p></div>`).join('')}</div><p class="small">${esc(data.notice)}</p>`;$('pilot-rate-session').innerHTML='<option value="">Choose a completed task</option>'+pilotRows.map(r=>`<option value="${esc(r.session_id)}">${esc(r.participant_id)} · ${esc(r.task.id)} · ${esc(r.condition)}</option>`).join('');}
$('refresh-pilot').addEventListener('click',()=>refreshPilot().catch(error));
$('pilot-rate-session').addEventListener('change',()=>{const r=pilotRows.find(r=>r.session_id===$('pilot-rate-session').value);$('pilot-rate-preview').textContent=r?`Question: ${r.task.question}\nAnswer: ${r.answer}\nSources: ${r.sources}`:'';});
$('pilot-rating').addEventListener('submit',async e=>{e.preventDefault();try{await api('/api/pilot/rate',{session_id:$('pilot-rate-session').value,reviewer_id:$('pilot-rater').value,correct:$('pilot-correct').value==='yes',source_supported:$('pilot-supported').value==='yes',source_checked:$('pilot-rating-source-checked').checked,notes:$('pilot-rating-notes').value});$('pilot-message').textContent='Source-based task rating saved.';await refreshPilot();}catch(e){error(e);}});
