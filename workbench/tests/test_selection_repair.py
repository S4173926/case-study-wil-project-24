"""Observed failures and developer-written perturbations, not an unseen benchmark."""
import unittest
from workbench.core import Workbench, normalize
from workbench.planning import check_coverage

class SelectionRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.w=Workbench()
    def ask(self,q): return self.w.answer(q,persist=False)
    def ids(self,r): return {b['claim_id'] for b in r['blocks']}
    def test_contextual_when_does_not_delete_inference(self):
        p=self.w.plan('How does REPLUG combine predictions when several retrieved documents are relevant?')
        self.assertIn('inference',p['facets']);self.assertNotIn('condition',p['facets'])
    def test_replug_weighted_ensemble_is_selected(self):
        r=self.ask('How does REPLUG combine language-model predictions when several different retrieved documents are relevant to the same question?')
        self.assertIn('replug.ensemble',self.ids(r));self.assertIn('similarity-weighted',r['blocks'][0]['text'])
        self.assertIn('next-token',r['blocks'][0]['text'])
    def test_replug_rephrasing(self):
        for q in ['REPLUG: explain how predictions are combined across retrieved documents.',
                  'How does REPLUG ensemble probabilities across documents?']:
            with self.subTest(q=q):self.assertIn('replug.ensemble',self.ids(self.ask(q)))
    def test_training_and_reader_parts_both_preserved(self):
        r=self.ask('Why does Atlas jointly pre-train its retriever and reader, and how does its reader make use of multiple retrieved passages?')
        self.assertTrue({'atlas.training','atlas.architecture'}<=self.ids(r))
        self.assertEqual(len(r['plan']['obligations']),2)
    def test_reordered_parts_still_have_both(self):
        r=self.ask('How does Atlas process multiple retrieved passages, and why is joint pre-training important?')
        self.assertTrue({'atlas.training','atlas.architecture'}<=self.ids(r))
    def test_atlas_architecture_contains_multi_passage_mechanism(self):
        c=self.w.by_claim['atlas.architecture'];self.assertIn('independently',c['text']);self.assertIn('cross-attention',c['text'])
        self.assertIn('atlas:s0008',{e['source_id'] for e in c['evidence']})
    def test_removed_reader_block_fails_detected_coverage(self):
        q='Why does Atlas jointly pre-train its retriever and reader, and how does its reader make use of multiple retrieved passages?'
        rows=check_coverage(self.w,self.w.plan(q),[self.w.by_claim['atlas.training']],['atlas'])
        self.assertTrue(any(not r['covered'] and r['facet']=='inference' for r in rows))
    def test_corrective_rag_longest_entity_span(self):
        self.assertEqual(self.w.names('Compare RECOMP and Corrective RAG (CRAG).'),['recomp','crag'])
    def test_explicit_original_rag_is_not_deleted(self):
        self.assertEqual(self.w.names('Compare RAG with Corrective RAG (CRAG).'),['rag','crag'])
    def test_retrieval_augmented_generic_label_not_another_paper(self):
        self.assertEqual(self.w.names('How do RAGAS and ARES evaluate RAG systems?'),['ragas','ares'])
    def test_noisy_evidence_decisions_and_mechanisms(self):
        r=self.ask('When retrieved information is noisy, how do RECOMP and Corrective RAG (CRAG) differ in what they do before the model generates its answer?')
        self.assertEqual(r['plan']['named_papers'],['recomp','crag'])
        self.assertTrue({'recomp.selective','recomp.compression','crag.evaluator','crag.refinement'}<=self.ids(r))
    def test_fid_not_filtered_by_replug_specific_property(self):
        r=self.ask('How do REPLUG and Fusion-in-Decoder combine information from multiple documents, and which method works with a frozen black-box language model?')
        self.assertTrue({'replug.method','replug.ensemble','fid.architecture'}<=self.ids(r))
        self.assertEqual(r['plan']['obligations'][-1]['scope'],'any')
    def test_fid_replug_reordered(self):
        r=self.ask('How do FiD and REPLUG combine retrieved passages, and which method uses a black-box language model?')
        self.assertTrue({'replug.method','replug.ensemble','fid.architecture'}<=self.ids(r))
    def test_splade_both_regularization_and_tradeoff(self):
        r=self.ask('What does the FLOPS regularizer in SPLADE try to reduce, and what trade-off does it create between retrieval quality and efficiency?')
        self.assertIn('splade.efficiency',self.ids(r));self.assertFalse(r['missing'])
        text=' '.join(b['text'] for b in r['blocks']);self.assertIn('sacrifice',text);self.assertIn('balanced',text)
    def test_unknown_second_part_is_visible(self):
        r=self.ask('How does Atlas process retrieved documents, and what is the favourite pizza topping of its authors?')
        self.assertTrue(r['blocks']);self.assertEqual(r['status'],'partial')
        self.assertTrue(any(not row['covered'] for row in r['clause_coverage']))
    def test_supported_measurement_still_available(self):
        r=self.ask('How many training examples does Atlas need to reach over 42% accuracy on Natural Questions?')
        self.assertIn('atlas.fewshot',self.ids(r))
    def test_deployment_measurements_not_replaced_by_method_details(self):
        for q in ['What exact cost per 1,000 queries was measured for RECOMP on AWS?',
                  'What measured p95 response latency did the Workbench achieve with 100 simultaneous users?']:
            with self.subTest(q=q):self.assertEqual(self.ask(q)['status'],'insufficient')
    def test_unrelated_domain_question_not_answered_by_generic_benchmark(self):
        r=self.ask('Which paper in this collection reports improved diabetic-retinopathy diagnosis accuracy from using ColBERTv2? Cite the experiment or state that the collection does not establish it.')
        self.assertEqual(r['status'],'insufficient');self.assertFalse(r['blocks'])
    def test_zero_hallucination_claim_not_asserted(self):
        r=self.ask('Does the indexed research prove that deployed retrieval-augmented generation systems have zero hallucinations? Identify the supporting experiment and error count, or explain why that claim is unsupported.')
        self.assertEqual(r['status'],'insufficient')
    def test_representation_and_learning_in_same_clause(self):
        r=self.ask('How do SPLADE and Contriever differ in their retrieval representations and learning approach?')
        self.assertTrue({'splade.representation','splade.learning','contriever.representation','contriever.training'}<=self.ids(r))
    def test_relevance_metric_not_replaced_by_only_reference_free_label(self):
        r=self.ask('How does RAGAS estimate answer relevance without comparing the generated answer to a human-written reference answer?')
        self.assertIn('ragas.relevance',self.ids(r))
    def test_evaluation_comparison_retains_ppi(self):
        r=self.ask('What exactly do BEIR and ARES evaluate, and how is their evaluation methodology different?')
        self.assertTrue({'beir.metric','ares.judges','ares.ppi'}<=self.ids(r))
    def test_query_construction_is_not_only_trigger(self):
        r=self.ask('Which approach masks out low-confidence tokens before using a sentence as a retrieval query?')
        self.assertIn('flare.query',self.ids(r))
    def test_unknown_parts_cannot_be_removed_by_optional_selector(self):
        class MissingReader:
            def select(self,*args):return ['atlas.training'],{'mock':True}
        r=self.w.answer('Why does Atlas jointly pre-train its retriever and reader, and how does its reader make use of retrieved passages?',persist=False,planner=MissingReader())
        self.assertTrue({'atlas.training','atlas.architecture'}<=self.ids(r))
        self.assertTrue(any('invalid' in warning for warning in r['warnings']))
    def test_exact_span_and_pending_review_remain(self):
        for cid in ['replug.ensemble','atlas.architecture','splade.efficiency']:
            c=self.w.by_claim[cid];self.assertEqual(c['independent_human_review'],'pending')
            for e in c['evidence']:
                self.assertEqual(normalize(self.w.by_source[e['source_id']]['text'])[e['start']:e['end']],e['quote'])

if __name__=='__main__':unittest.main()
