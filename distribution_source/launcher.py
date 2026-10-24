"""Portable, local-only distribution launcher. Uses only the Python standard library.

Code and source PDFs are unpacked into a version-specific working directory.
Original workspaces are read only. Saved ratings are never created by this launcher.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile
import time
import zipfile

CATEGORIES = {'runs': 'run_id', 'reviews': 'review_id', 'pilot': 'session_id'}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def safe_relative(name: str) -> Path:
    p = PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
        raise ValueError('Unsafe package path')
    return Path(*p.parts)

def reject_links(path: Path) -> None:
    for p in [path, *path.parents]:
        if p.is_symlink():
            raise ValueError('Workspace paths must not contain symbolic links: ' + str(p))

def prepare(archive: Path, workspace: Path) -> tuple[Path, dict]:
    """Verify all bundled bytes, then extract only to this build's own directory."""
    reject_links(workspace)
    with zipfile.ZipFile(archive) as z:
        manifest = json.loads(z.read('bundle_manifest.json'))
        entries = manifest['files']
        build_id=manifest.get('build_id','')
        if not build_id or not all(c.isalnum() or c in '-_' for c in build_id):
            raise ValueError('Invalid application build identifier')
        for name, expected in entries.items():
            safe_relative(name)
            if sha(z.read('payload/' + name)) != expected:
                raise ValueError('Application package is damaged: ' + name)
        root = workspace / 'releases' / manifest['build_id']
        reject_links(root)
        # A root created by this application contains an install marker. No unrelated
        # directory is reused or replaced. Assets are immutable; records are separate.
        marker = root / '.installed.json'
        if root.exists():
            if not marker.is_file():
                raise ValueError('Existing directory has no installation marker: ' + str(root))
            state = json.loads(marker.read_text(encoding='utf-8'))
            if state.get('build_id') != manifest['build_id']:
                raise ValueError('Application directory identifies another build')
            for name, expected in entries.items():
                if name.startswith('results/'):
                    continue
                path = root / safe_relative(name)
                reject_links(path)
                if not path.is_file() or sha(path.read_bytes()) != expected:
                    raise ValueError('An installed application asset was modified: ' + name + '. Use a new --workspace directory to keep that copy unchanged.')
            return root, manifest
        root.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='.install-', dir=root.parent))
        try:
            for name in entries:
                p = stage / safe_relative(name)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(z.read('payload/' + name))
            (stage / '.installed.json').write_text(json.dumps({'build_id':manifest['build_id'],'format':1}), encoding='utf-8')
            stage.rename(root)
        finally:
            if stage.exists(): shutil.rmtree(stage)
        return root, manifest

def import_records(source: Path, destination: Path) -> dict:
    """Copy valid saved records; preserve all conflicts separately, never overwrite."""
    result={'source':str(source),'copied':0,'identical':0,'conflicts':0,'skipped':0}
    if not source.is_dir() or source.resolve()==destination.resolve():return result
    reject_links(source); reject_links(destination)
    for category,key in CATEGORIES.items():
        src=source/'results'/category
        if not src.exists():continue
        reject_links(src)
        for f in sorted(src.glob('*.json')):
            try:
                reject_links(f)
                if not f.is_file() or f.stat().st_size>10_000_000:
                    raise ValueError('Invalid record size')
                data=f.read_bytes(); row=json.loads(data)
                if not isinstance(row,dict) or row.get(key)!=f.stem:
                    raise ValueError('Record ID mismatch')
                if not all(c.isalnum() or c in '_-' for c in f.stem):
                    raise ValueError('Invalid record ID')
                target=destination/'results'/category/f.name
                reject_links(target); target.parent.mkdir(parents=True,exist_ok=True)
                if target.exists():
                    if target.read_bytes()==data:
                        result['identical']+=1;continue
                    conflict=destination/'results'/'import_conflicts'/sha(str(source).encode())[:12]/category/f.name
                    reject_links(conflict);conflict.parent.mkdir(parents=True,exist_ok=True)
                    if not conflict.exists():conflict.write_bytes(data)
                    elif conflict.read_bytes()!=data:
                        conflict=conflict.with_name(conflict.stem+'_'+sha(data)[:12]+'.json')
                        if not conflict.exists():conflict.write_bytes(data)
                    result['conflicts']+=1;continue
                with target.open('xb') as out:out.write(data)
                result['copied']+=1
            except (OSError,ValueError,TypeError):
                result['skipped']+=1
    return result

def migrate(root: Path, workspace: Path, archive: Path, explicit: list[Path]) -> list[dict]:
    """Prefer the most recent named release; preserve differing older records."""
    bases=[archive.parent, Path.home()/'Downloads']
    candidates=list(explicit)
    for name in ('WIL_Research_Workbench_Final','WIL_Research_Workbench'):
        candidates.extend(base/name for base in bases)
    releases=workspace/'releases'
    if releases.exists():candidates.extend(sorted(releases.iterdir(),key=lambda p:p.stat().st_mtime,reverse=True))
    seen=set();results=[]
    for source in candidates:
        key=str(source.absolute())
        if key in seen or not source.is_dir() or source.resolve()==root.resolve():continue
        seen.add(key)
        try:results.append(import_records(source,root))
        except (ValueError,OSError) as exc:results.append({'source':str(source),'error':str(exc)})
    if results:
        folder=root/'results/migration';folder.mkdir(parents=True,exist_ok=True)
        (folder/('import_'+str(time.time_ns())+'.json')).write_text(json.dumps(results,indent=2),encoding='utf-8')
    return results

def main() -> None:
    p=argparse.ArgumentParser(description='Research Workbench: a portable, offline source-linked research application.')
    p.add_argument('--workspace',type=Path,default=Path.home()/'Research_Workbench_Data',help='Local storage folder. Originals are not modified.')
    p.add_argument('--port',type=int,default=8765,help='Preferred localhost port; the next available port is used when occupied.')
    p.add_argument('--no-open',action='store_true',help='Do not open the browser automatically.')
    p.add_argument('--no-import',action='store_true',help='Do not copy records from previous workspaces.')
    p.add_argument('--import-from',type=Path,action='append',default=[],help='Additional old workspace to read saved records from.')
    p.add_argument('--check',action='store_true',help='Run packaged software tests and source-integrity checks; do not launch the website.')
    p.add_argument('--evaluate',action='store_true',help='Record the 67 known development questions; no automatic accuracy grading.')
    p.add_argument('--export-source',type=Path,help='Copy the bundled application source to a new folder for inspection or GitHub.')
    args=p.parse_args()
    if sys.version_info<(3,10):p.error('Python 3.10 or newer is required.')
    if not 1024<=args.port<=65515:p.error('Port must be between 1024 and 65515.')
    archive=Path(sys.argv[0]).absolute()
    try:root,manifest=prepare(archive,args.workspace.expanduser().absolute())
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as exc:raise SystemExit('Could not start the application: '+str(exc))
    sys.path.insert(0,str(root))
    if args.export_source:
        out=args.export_source.expanduser().absolute();reject_links(out)
        if out.exists():raise SystemExit('Choose a new export directory; existing files are never replaced.')
        with zipfile.ZipFile(archive) as z:
            out.mkdir(parents=True)
            for name in manifest['files']:
                target=out/safe_relative(name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read('payload/'+name))
        print('Application source exported to:',out);return
    if args.check:
        import unittest
        from workbench.cli import doctor
        report=doctor(root)
        suite=unittest.defaultTestLoader.discover(str(root/'tests'),top_level_dir=str(root/'tests'))
        result=unittest.TextTestRunner(verbosity=1).run(suite)
        print(json.dumps(report,indent=2));sys.exit(0 if result.wasSuccessful() and report['passed'] else 1)
    if not args.no_import:
        results=migrate(root,args.workspace.expanduser().absolute(),archive,args.import_from)
        added=sum(r.get('copied',0) for r in results)
        conflicts=sum(r.get('conflicts',0) for r in results)
        print(f'Previous saved records copied: {added}. Originals remain unchanged.')
        if conflicts:print(f'{conflicts} differing records preserved in results/import_conflicts; existing saved records were not overwritten.')
        for item in results:
            if item.get('error') or item.get('skipped'):
                print('Import notice:',json.dumps(item))
    if args.evaluate:
        from workbench.cli import evaluate
        out=root/'results'/('portable_regression67_'+time.strftime('%Y%m%dT%H%M%S')+'_'+str(os.getpid()))
        r=evaluate(root/'eval/regression67_selection_repair.jsonl',out,root,publish_runs=True)
        print(json.dumps({k:v for k,v in r.items() if k!='records'},indent=2));print('Review bundle:',out.with_suffix('.zip'));return
    from workbench.server import Application,make_handler
    from http.server import ThreadingHTTPServer
    import webbrowser
    app=Application(root);server=None
    for port in range(args.port,args.port+20):
        try:server=ThreadingHTTPServer(('127.0.0.1',port),make_handler(app));break
        except OSError:continue
    if server is None:raise SystemExit('No free local port found. Close an older Workbench or use --port 8900.')
    server.daemon_threads=True
    address='http://127.0.0.1:'+str(server.server_address[1])
    print('\nResearch Workbench · portable edition\n'+address+'\n'+str(len(app.engine.papers))+' papers · '+str(len(app.engine.claims))+' source-linked claims.\nSaved records: '+str(root/'results')+'\nNo model, account or internet connection is needed.\nPress Control+C to stop.\n',flush=True)
    if not args.no_open:
        try:webbrowser.open(address)
        except Exception:print('Open the local address above in a browser.')
    try:server.serve_forever()
    except KeyboardInterrupt:print('\nStopped. Your saved records remain on this computer.')
    finally:server.server_close()

if __name__=='__main__':main()
