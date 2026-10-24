"""Packaging and layout-contract tests. No real reviewer records are created."""
from pathlib import Path
import hashlib,json,tempfile,unittest,zipfile
from tools.portable_launcher import prepare,import_records,safe_relative
from workbench.core import ROOT

class PortableTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def archive(self,content=b'original',name='web/index.html',corrupt=False):
  p=self.d/'test.pyz'
  with zipfile.ZipFile(p,'w') as z:
   z.writestr('payload/'+name,content)
   z.writestr('bundle_manifest.json',json.dumps({'build_id':'fixture','files':{name:'0'*64 if corrupt else hashlib.sha256(content).hexdigest()}}))
  return p
 def record(self,root,category='runs',rid='record_01',value=1):
  p=root/'results'/category/(rid+'.json');p.parent.mkdir(parents=True,exist_ok=True)
  key={'runs':'run_id','reviews':'review_id','pilot':'session_id'}[category]
  p.write_text(json.dumps({key:rid,'value':value}),encoding='utf-8');return p
 def test_onefile_extract_and_validate(self):
  root,m=prepare(self.archive(),self.d/'workspace');self.assertEqual((root/'web/index.html').read_bytes(),b'original')
 def test_onefile_repeat_is_idempotent(self):
  a=self.archive();r,m=prepare(a,self.d/'workspace');p=self.record(r);b=p.read_bytes();r2,_=prepare(a,self.d/'workspace');self.assertEqual(r,r2);self.assertEqual(p.read_bytes(),b)
 def test_package_corruption_rejected(self):
  with self.assertRaises(ValueError):prepare(self.archive(corrupt=True),self.d/'workspace')
 def test_package_path_escape_rejected(self):
  with self.assertRaises(ValueError):prepare(self.archive(name='../escape'),self.d/'workspace')
 def test_absolute_path_rejected(self):
  with self.assertRaises(ValueError):safe_relative('/tmp/escape')
 def test_windows_path_rejected(self):
  with self.assertRaises(ValueError):safe_relative('C:\\escape')
 def test_unrelated_directory_not_overwritten(self):
  root=self.d/'workspace/releases/fixture';root.mkdir(parents=True);(root/'myfile').write_text('keep')
  with self.assertRaises(ValueError):prepare(self.archive(),self.d/'workspace')
  self.assertEqual((root/'myfile').read_text(),'keep')
 def test_changed_assets_not_silently_overwritten(self):
  a=self.archive();r,_=prepare(a,self.d/'workspace');(r/'web/index.html').write_text('my edits')
  with self.assertRaises(ValueError):prepare(a,self.d/'workspace')
  self.assertEqual((r/'web/index.html').read_text(),'my edits')
 def test_record_migration_three_categories(self):
  src=self.d/'old';dst=self.d/'new'
  for c in ['runs','reviews','pilot']:self.record(src,c)
  r=import_records(src,dst);self.assertEqual(r['copied'],3)
 def test_record_migration_preserves_source(self):
  src=self.d/'old';p=self.record(src);b=p.read_bytes();import_records(src,self.d/'new');self.assertEqual(p.read_bytes(),b)
 def test_record_migration_repeat(self):
  src=self.d/'old';self.record(src);dst=self.d/'new';import_records(src,dst);r=import_records(src,dst);self.assertEqual(r['identical'],1);self.assertEqual(r['copied'],0)
 def test_record_conflict_preserved_separately(self):
  src=self.d/'old';dst=self.d/'new';p=self.record(src,value=2);d=self.record(dst,value=1);b=d.read_bytes();r=import_records(src,dst)
  self.assertEqual(r['conflicts'],1);self.assertEqual(d.read_bytes(),b);self.assertEqual(list((dst/'results/import_conflicts').rglob('*.json'))[0].read_bytes(),p.read_bytes())
 def test_invalid_record_not_imported(self):
  src=self.d/'old';p=self.record(src);p.write_text('{"run_id":"wrong"}');r=import_records(src,self.d/'new');self.assertEqual(r['skipped'],1);self.assertEqual(r['copied'],0)
 def test_unknown_files_not_imported(self):
  src=self.d/'old';self.record(src);(src/'secret.env').write_text('dummy');import_records(src,self.d/'new');self.assertFalse((self.d/'new/secret.env').exists())
 def test_only_four_user_pages(self):
  text=(ROOT/'web/index.html').read_text(encoding='utf-8');self.assertEqual(text.count('class="page"'),4);self.assertNotIn('page-rubric',text);self.assertNotIn('page-audit',text)
 def test_ui_has_no_device_specific_model_control(self):
  text=(ROOT/'web/index.html').read_text(encoding='utf-8');self.assertNotIn('use-model',text);self.assertNotIn('MLX',text);self.assertNotIn('Apple M4',text)
 def test_review_helpers_not_inside_misaligned_labels(self):
  text=(ROOT/'web/index.html').read_text(encoding='utf-8');self.assertIn('identity-note',text);self.assertIn('field-grid cols-3',text)
 def test_narrow_screen_layout_defined(self):
  text=(ROOT/'web/style.css').read_text(encoding='utf-8');self.assertIn('max-width:760px',text);self.assertIn('minmax(0,1fr)',text)
 def test_source_warning_retained(self):
  text=(ROOT/'web/index.html').read_text(encoding='utf-8');self.assertIn('they can be incomplete',text);self.assertIn('Open a citation to inspect the original paper',text)
 def test_no_online_fonts_or_scripts(self):
  text=(ROOT/'web/index.html').read_text(encoding='utf-8');self.assertNotIn('src="http',text);self.assertNotIn('fonts.googleapis',text)
