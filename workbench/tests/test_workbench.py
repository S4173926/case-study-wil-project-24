from __future__ import annotations
import contextlib,hashlib,http.client,json,shutil,tempfile,threading,time,unittest,zipfile
from pathlib import Path
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from workbench.core import Workbench,ROOT,normalize,markdown,atomic_json
from workbench.records import save_review,review_summary,start_pilot,finish_pilot,rate_pilot,pilot_summary
from workbench.server import Application,make_handler
from workbench.cli import doctor,evaluate

@contextlib.contextmanager
def isolated():
    with tempfile.TemporaryDirectory() as d:
        root=Path(d)
        for name in ['corpus','knowledge','workbench','web','config']:
            shutil.copytree(ROOT/name,root/name)
        (root/'results').mkdir()
        yield root

class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.w=Workbench()
    def test_catalogue_all_papers_have_supported_claims(self):
        w=self.w;self.assertEqual(len(w.papers),30);self.assertEqual(len(w.sources),1202)
        self.assertEqual({c['paper_id'] for c in w.claims},set(w.papers))
        for c in w.claims:
            with self.subTest(claim=c['id']):
                self.assertEqual(c['independent_human_review'],'pending')
                for e in c['evidence']:
                    self.assertEqual(normalize(w.by_source[e['source_id']]['text'])[e['start']:e['end']],e['quote'])
    def test_original_pdf_hashes(self):self.assertTrue(doctor()['passed'])
    def test_empty_question_rejected(self):
        for q in ['', '   ',None,42]:
            with self.subTest(q=q),self.assertRaises(ValueError):self.w.answer(q,persist=False)
    def test_too_long_question_rejected(self):
        with self.assertRaises(ValueError):self.w.answer('A'*4001,persist=False)
    def test_invalid_retrieval_mode(self):
        with self.assertRaises(ValueError):self.w.search('RAG',method='magic')
    def test_invalid_output_mode(self):
        with self.assertRaises(ValueError):self.w.answer('RAG',mode='certified',persist=False)
    def test_names_not_confused(self):
        self.assertEqual(self.w.names('How do RAGAS and ARES evaluate RAG systems?'),['ragas','ares'])
        self.assertEqual(self.w.names('How do monoBERT and monoT5 score relevance?'),['monobert','monot5'])
    def test_recomp_fid_correct_mechanisms(self):
        r=self.w.answer('How do RECOMP and Fusion-in-Decoder differ in how they process retrieved passages before generating an answer?',persist=False)
        blocks={pid:' '.join(b['text'] for b in r['blocks'] if b['paper_id']==pid) for pid in ['recomp','fid']}
        self.assertIn('shorter',blocks['recomp']);self.assertIn('prepends',blocks['recomp'])
        self.assertIn('independently',blocks['fid']);self.assertIn('decoder',blocks['fid'])
        self.assertNotIn('jointly in both',blocks['recomp'])
    def test_flare_trigger_including_otherwise(self):
        r=self.w.answer('When does FLARE retrieve documents to regenerate a sentence?',persist=False)
        text=' '.join(b['text'] for b in r['blocks']).lower()
        self.assertIn('below',text);self.assertIn('threshold',text);self.assertIn('any token',text)
        self.assertIn('without',text)
    def test_plural_trigger_comparison(self):
        r=self.w.answer('Compare the retrieval triggers in FLARE and In-Context RALM.',persist=False)
        self.assertIn('flare.trigger',{b['claim_id'] for b in r['blocks']})
        self.assertIn('icralm.stride',{b['claim_id'] for b in r['blocks']})
    def test_orqa_pretraining_and_supervision(self):
        r=self.w.answer('How does ORQA train a retriever without labelled supporting passages, and what task does it use to pre-train it?',persist=False)
        ids={b['claim_id'] for b in r['blocks']}
        self.assertIn('orqa.ict',ids);self.assertIn('orqa.supervision',ids)
    def test_recomp_empty_string(self):
        r=self.w.answer('Under what circumstances can RECOMP leave out retrieved context entirely, and what does the compressor output?',persist=False)
        text=' '.join(b['text'] for b in r['blocks']);self.assertIn('empty string',text);self.assertIn('irrelevant',text)
    def test_evaluation_comparison_does_not_swap_ppi(self):
        r=self.w.answer('How do RAGAS and ARES score RAG systems?',persist=False)
        a=' '.join(b['text'] for b in r['blocks'] if b['paper_id']=='ares')
        g=' '.join(b['text'] for b in r['blocks'] if b['paper_id']=='ragas')
        self.assertIn('synthetic',a);self.assertIn('prediction-powered',a);self.assertIn('without',g)
    def test_numeric_measurements_not_invented(self):
        for q in ['How many kilowatt-hours did SPLADE use in training?', 'What prompt-injection attack success rate did RECOMP report?', 'What precise nDCG@10 difference between SPLADE and Contriever was measured on a Kannada legal benchmark?','What is the monthly hosting cost of RAGAS?']:
            with self.subTest(q=q):
                r=self.w.answer(q,persist=False);self.assertEqual(r['status'],'insufficient');self.assertFalse(r['blocks'])
    def test_misattributed_concept_not_relabelled(self):
        r=self.w.answer('How does RAGAS use prediction-powered inference (PPI)?',persist=False)
        self.assertEqual(r['status'],'insufficient');self.assertFalse(r['blocks'])
    def test_superiority_question_has_explicit_limit(self):
        r=self.w.answer('Which is more accurate, SPLADE or Contriever?',persist=False)
        self.assertEqual(r['status'],'partial');self.assertTrue(r['missing'])
    def test_failed_model_trace_is_preserved(self):
        class FakeFailure(ValueError):
            trace={'completion':'invalid json','mock':True}
        class Planner:
            def select(self,*a):raise FakeFailure('Parse failed')
        r=self.w.answer('What does RECOMP do before generation?',persist=False,planner=Planner())
        self.assertTrue(r['blocks']);self.assertEqual(r['attempts'][0]['completion'],'invalid json')
    def test_irrelevant_named_question_not_filled_with_method(self):
        r=self.w.answer('What is the favourite pizza topping of the authors of ARES?',persist=False)
        self.assertEqual(r['status'],'insufficient')
    def test_unscoped_discovery_is_labelled(self):
        r=self.w.answer('Which method compresses retrieved documents into textual summaries?',persist=False)
        self.assertTrue(r['warnings'] or r['status']=='insufficient')
    def test_every_displayed_block_is_a_catalogue_claim(self):
        questions=[json.loads(l) for l in (ROOT/'eval/all52_development.jsonl').read_text().splitlines() if l.strip()]
        for q in questions:
            with self.subTest(q=q['id']):
                r=self.w.answer(q['question'],persist=False)
                for b in r['blocks']:
                    self.assertEqual(b['text'],self.w.by_claim[b['claim_id']]['text'])
                    self.assertTrue(all(s in self.w.by_source for s in b['source_ids']))
                    self.assertTrue(all(self.w.by_source[s]['paper_id']==b['paper_id'] for s in b['source_ids']))
    def test_runtime_never_reads_evaluation_files(self):
        original=Path.read_text
        def safe(path,*a,**kw):
            if 'eval' in path.parts:raise AssertionError('Evaluation leakage')
            return original(path,*a,**kw)
        with patch.object(Path,'read_text',safe):
            w=Workbench();r=w.answer('Compare the encoders in FiD and DPR.',persist=False)
            self.assertTrue(r['blocks'])
    def test_model_selector_cannot_invent_claims(self):
        class BadPlanner:
            def select(self,*args):return ['invented.falseclaim'],{'mock':True}
        r=self.w.answer('What does RECOMP do before generation?',persist=False,planner=BadPlanner())
        self.assertTrue(any('invalid' in w for w in r['warnings']));self.assertTrue(r['blocks'])
    def test_deterministic_default(self):
        a=self.w.answer('How does monoT5 score relevance?',persist=False)
        b=self.w.answer('How does monoT5 score relevance?',persist=False)
        self.assertEqual(a['blocks'],b['blocks']);self.assertEqual(a['status'],b['status'])
    def test_search_is_not_a_generated_answer(self):
        r=self.w.answer('What does FiD encode?',mode='search',persist=False)
        self.assertEqual(r['status'],'source_evidence');self.assertFalse(r['blocks']);self.assertTrue(r['retrieved'])
    def test_modified_quote_rejected(self):
        with isolated() as root:
            p=root/'knowledge/claims.json';data=json.loads(p.read_text());data['claims'][0]['evidence'][0]['quote']='invented'
            p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):Workbench(root)
    def test_wrong_paper_source_rejected(self):
        with isolated() as root:
            p=root/'knowledge/claims.json';data=json.loads(p.read_text());data['claims'][0]['paper_id']='recomp';p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):Workbench(root)
    def test_export_has_submitted_question(self):
        r=self.w.answer('How does RECOMP compress retrieved evidence?',persist=False)
        self.assertIn(r['question'],markdown(r));self.assertIn(r['run_id'],markdown(r))

class RecordsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.w=Workbench()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.run=self.w.answer('When does RECOMP return an empty summary?',persist=False)
        atomic_json(self.root/'results/runs'/(self.run['run_id']+'.json'),self.run)
    def tearDown(self):self.temp.cleanup()
    def rating(self,**kwargs):
        data={'run_id':self.run['run_id'],'reviewer_id':'QA_FIXTURE','relationship':'author','answerable':True,
              'correctness':2,'completeness':2,'citation_support':2,'relevance':2,'source_checked':True,'notes':'Synthetic test fixture, not a research observation.'};data.update(kwargs);return data
    def test_empty_ratings_are_not_accuracy(self):
        s=review_summary(self.root);self.assertEqual(s['status'],'NO_HUMAN_RATINGS');self.assertEqual(s['answerable']['n'],0)
    def test_missing_score_rejected(self):
        data=self.rating();del data['correctness']
        with self.assertRaises(ValueError):save_review(self.root,data)
    def test_source_check_required(self):
        with self.assertRaises(ValueError):save_review(self.root,self.rating(source_checked=False))
    def test_explicit_boolean_required(self):
        with self.assertRaises(ValueError):save_review(self.root,self.rating(answerable='yes'))
    def test_latest_same_reviewer_rating_only(self):
        save_review(self.root,self.rating(correctness=1));save_review(self.root,self.rating())
        s=review_summary(self.root);self.assertEqual(s['review_records'],2);self.assertEqual(s['resolved_runs'],1)
    def test_rater_disagreement_not_silently_averaged(self):
        save_review(self.root,self.rating());save_review(self.root,self.rating(reviewer_id='OTHER_FIXTURE',correctness=0))
        self.assertEqual(review_summary(self.root)['resolved_runs'],0)
    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):save_review(self.root,self.rating(reviewer_id='../test'))
    def test_pilot_requires_consent(self):
        with self.assertRaises(ValueError):start_pilot(self.root,{'participant_id':'QA','task_id':'A','condition':'manual'})
    def test_pilot_actual_clock_and_no_fabricated_rating(self):
        r=start_pilot(self.root,{'participant_id':'QA','task_id':'A','condition':'manual','consent':True})
        time.sleep(.01);done=finish_pilot(self.root,{'session_id':r['session_id'],'answer':'Synthetic fixture'})
        self.assertGreater(done['seconds_including_verification'],0);self.assertEqual(done['correctness'],'NOT_RATED')
        s=pilot_summary(self.root);self.assertEqual(s['by_condition']['manual']['unrated'],1)
        rate_pilot(self.root,{'session_id':r['session_id'],'reviewer_id':'QA','correct':True,'source_supported':False,'source_checked':True})
        self.assertEqual(pilot_summary(self.root)['by_condition']['manual']['correct_and_source_supported'],0)
        with self.assertRaises(ValueError):finish_pilot(self.root,{'session_id':r['session_id'],'answer':'Overwrite'})

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx=isolated();cls.root=cls.ctx.__enter__();cls.app=Application(cls.root)
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(cls.app));cls.port=cls.server.server_address[1]
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.ctx.__exit__(None,None,None)
    def request(self,path,body=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=30)
        h={'Content-Type':'application/json','X-Workbench-Token':self.app.csrf};h.update(headers or {})
        c.request('GET' if body is None else 'POST',path,json.dumps(body) if body is not None else None,h)
        r=c.getresponse();out=(r.status,r.getheaders(),r.read());c.close();return out
    def test_homepage(self):self.assertEqual(self.request('/')[0],200)
    def test_query_endpoint(self):
        status,_,body=self.request('/api/ask',{'question':'What does RECOMP compress?'})
        self.assertEqual(status,200);self.assertTrue(json.loads(body)['blocks'])
    def test_invalid_question_response(self):self.assertEqual(self.request('/api/ask',{'question':''})[0],400)
    def test_csrf_rejected(self):self.assertEqual(self.request('/api/ask',{'question':'test'},{'X-Workbench-Token':'wrong'})[0],403)
    def test_cross_origin_rejected(self):self.assertEqual(self.request('/api/ask',{'question':'test'},{'Origin':'https://untrusted.example'})[0],403)
    def test_unknown_paths(self):self.assertEqual(self.request('/../../knowledge/claims.json')[0],404)
    def test_pdf_served(self):
        status,_,body=self.request('/pdf/fid.pdf');self.assertEqual(status,200);self.assertTrue(body.startswith(b'%PDF'))
    def test_no_remote_host(self):self.assertEqual(self.request('/api/config',headers={'Host':'attacker.example'})[0],403)
    def test_real_export_structure(self):
        import io
        status,_,body=self.request('/api/export');self.assertEqual(status,200)
        with zipfile.ZipFile(io.BytesIO(body)) as z:self.assertIn('review_summary.json',z.namelist())

if __name__=='__main__':unittest.main()
