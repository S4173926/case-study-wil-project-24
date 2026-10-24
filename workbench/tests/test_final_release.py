"""Review-index and record-preservation regressions. Fixtures are isolated."""
from __future__ import annotations
import copy,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from workbench.review_index import run_index
from workbench.core import ROOT
from tools.import_workspace import copy_records

class IndexTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        (self.root/'config').mkdir();(self.root/'results/runs').mkdir(parents=True)
        self.engine=SimpleNamespace(corpus_hash='C',claim_hash='K',code_hash='S',papers={'fid':{'title':'Fusion-in-Decoder'}})
        self.r={'run_id':'20261024_A','question':'How does FiD work?','status':'source_linked_explanation','created_utc':'2026-10-24T01:00:00Z','hashes':{'corpus':'C','knowledge':'K','code':'S'},'plan':{'named_papers':['fid']}}
    def tearDown(self):self.temp.cleanup()
    def save(self,r):
        (self.root/'results/runs'/(r['run_id']+'.json')).write_text(json.dumps(r))
    def test_current_version_identified(self):
        self.save(self.r);r=run_index(self.root,self.engine)[0];self.assertTrue(r['current_answer_set']);self.assertEqual(r['version_label'],'Current release')
    def test_old_code_not_current_without_explicit_compatibility(self):
        self.r['hashes']['code']='OLD';self.save(self.r);self.assertFalse(run_index(self.root,self.engine)[0]['current_answer_set'])
    def test_exact_compatible_repair_retained(self):
        self.r['hashes']['code']='OLD';self.save(self.r)
        (self.root/'config/release_compatibility.json').write_text(json.dumps({'compatible_answer_sets':[dict(self.r['hashes'],label='Repaired evaluation')]}))
        self.assertTrue(run_index(self.root,self.engine)[0]['current_answer_set'])
    def test_compatible_hash_mismatch_not_accepted(self):
        (self.root/'config/release_compatibility.json').write_text(json.dumps({'compatible_answer_sets':[{'corpus':'WRONG','knowledge':'K','code':'OLD','label':'Repaired'}]}))
        self.r['hashes']['code']='OLD';self.save(self.r);self.assertFalse(run_index(self.root,self.engine)[0]['current_answer_set'])
    def test_all_170_records_available_not_truncated(self):
        for i in range(170):
            r=copy.deepcopy(self.r);r['run_id']=f'run_{i:04}';self.save(r)
        self.assertEqual(len(run_index(self.root,self.engine)),170)
    def test_question_id_inferred_only_for_display(self):
        (self.root/'config/review_question_ids.json').write_text(json.dumps([{'id':'F01','question':self.r['question']}]))
        self.save(self.r);before=(self.root/'results/runs'/(self.r['run_id']+'.json')).read_bytes()
        self.assertEqual(run_index(self.root,self.engine)[0]['question_id'],'F01')
        self.assertEqual(before,(self.root/'results/runs'/(self.r['run_id']+'.json')).read_bytes())
    def test_native_question_id_preserved(self):
        self.r['evaluation_question_id']='ACTUAL';self.save(self.r);self.assertEqual(run_index(self.root,self.engine)[0]['question_id'],'ACTUAL')
    def test_paper_titles_available_for_search(self):
        self.save(self.r);self.assertEqual(run_index(self.root,self.engine)[0]['paper_titles'],['Fusion-in-Decoder'])
    def test_corrupt_record_does_not_hide_valid_runs(self):
        self.save(self.r);(self.root/'results/runs/broken.json').write_text('invalid')
        rows=run_index(self.root,self.engine);self.assertEqual(len(rows),2);self.assertEqual(sum(r['available'] for r in rows),1)
    def test_review_names_are_not_invented(self):
        self.save(self.r);self.assertEqual(run_index(self.root,self.engine)[0]['reviewed_by'],[])
    def test_actual_reviewer_names_listed(self):
        (self.root/'results/reviews').mkdir();(self.root/'results/reviews/fixture.json').write_text(json.dumps({'run_id':self.r['run_id'],'reviewer_id':'TEST_FIXTURE_ONLY'}))
        self.save(self.r);self.assertEqual(run_index(self.root,self.engine)[0]['reviewed_by'],['TEST_FIXTURE_ONLY'])
    def test_mismatched_filename_is_unavailable(self):
        (self.root/'results/runs/different.json').write_text(json.dumps(self.r));self.assertFalse(run_index(self.root,self.engine)[0]['available'])

class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();p=Path(self.temp.name);self.source=p/'old';self.dest=p/'new';self.source.mkdir();self.dest.mkdir()
    def tearDown(self):self.temp.cleanup()
    def record(self,category='runs',ident='example'):
        key={'runs':'run_id','reviews':'review_id','pilot':'session_id'}[category]
        p=self.source/'results'/category/(ident+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({key:ident,'note':'Isolated test fixture'}));return p
    def test_copy_preserves_bytes_and_original(self):
        p=self.record();before=p.read_bytes();r=copy_records(self.source,self.dest);self.assertEqual(r['copied'],1);self.assertEqual(before,p.read_bytes());self.assertEqual(before,(self.dest/'results/runs/example.json').read_bytes())
    def test_idempotent(self):
        self.record();copy_records(self.source,self.dest);r=copy_records(self.source,self.dest);self.assertEqual(r['copied'],0);self.assertEqual(r['identical'],1)
    def test_all_three_record_categories_preserved(self):
        for category in ('runs','reviews','pilot'):self.record(category)
        self.assertEqual(copy_records(self.source,self.dest)['copied'],3)
    def test_conflict_aborts_before_any_new_copy(self):
        self.record(ident='a');self.record(ident='z');p=self.dest/'results/runs/z.json';p.parent.mkdir(parents=True);p.write_text('{"run_id":"z","note":"do not overwrite"}')
        before=p.read_bytes()
        with self.assertRaises(ValueError):copy_records(self.source,self.dest)
        self.assertEqual(before,p.read_bytes());self.assertFalse((self.dest/'results/runs/a.json').exists())
    def test_invalid_json_rejected_without_changes(self):
        p=self.record();p.write_text('not json')
        with self.assertRaises(ValueError):copy_records(self.source,self.dest)
        self.assertFalse((self.dest/'results').exists())
    def test_identity_mismatch_rejected(self):
        p=self.record();p.write_text('{"run_id":"another"}')
        with self.assertRaises(ValueError):copy_records(self.source,self.dest)
    def test_symlink_rejected(self):
        p=self.record();target=p.with_name('link.json');target.symlink_to(p)
        with self.assertRaises(ValueError):copy_records(self.source,self.dest)
    def test_missing_previous_workspace_is_ok(self):
        self.assertEqual(copy_records(self.source/'not_there',self.dest)['status'],'NO_PREVIOUS_WORKSPACE')
    def test_same_workspace_no_change(self):
        self.record();self.assertEqual(copy_records(self.source,self.source)['status'],'SAME_WORKSPACE')
    def test_unrelated_files_are_not_imported(self):
        (self.source/'.env').write_text('TEST ONLY');self.record();copy_records(self.source,self.dest);self.assertFalse((self.dest/'.env').exists())

class PresentationTests(unittest.TestCase):
    def test_search_and_version_controls_present(self):
        page=(ROOT/'web/index.html').read_text()
        for id in ('run-search','run-version','run-status','run-meta'):self.assertIn('id="'+id+'"',page)
    def test_neutral_source_linked_interface(self):
        text=' '.join((ROOT/'web'/p).read_text() for p in ('index.html','app.js'))
        self.assertIn('Source-linked summaries',text)
        self.assertIn('Open a citation to inspect the original paper',text)
    def test_source_context_warning_kept(self):
        self.assertIn('Verify the cited pages',(ROOT/'web/app.js').read_text())
    def test_scores_reset_on_run_change(self):
        script=(ROOT/'web/app.js').read_text();self.assertIn('resetReviewScores()',script);self.assertIn("$('source-checked').checked=false",script)
    def test_historical_json_export_unmodified(self):
        server=(ROOT/'workbench/server.py').read_text();self.assertIn('else:self.send(200,r)',server)
    def test_source_search_method_label_explicit(self):
        self.assertIn('Explanation selection uses the fixed claim index',(ROOT/'web/index.html').read_text())

if __name__=='__main__':unittest.main()
