"""Local-only HTTP interface. Standard library; no framework installation required."""
from __future__ import annotations
import argparse, io, json, mimetypes, os, re, secrets, threading, urllib.parse, webbrowser, zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .core import Workbench, ROOT, markdown
from .records import load_run, save_review, review_summary, start_pilot, finish_pilot, rate_pilot, pilot_summary, PILOT_TASKS

class Application:
    def __init__(self,root:Path=ROOT):
        self.root=root;self.engine=Workbench(root);self.csrf=secrets.token_urlsafe(32)
        self.planner=None;self.planner_lock=threading.Lock()
    def config(self):
        return {'release':'2.0-portable','papers':len(self.engine.papers),'passages':len(self.engine.sources),
          'claims':len(self.engine.claims),'csrf':self.csrf,'pilot_tasks':PILOT_TASKS,
          'catalogue_review':'Language-model-drafted catalogue; independent source review not established',
          'hashes':{'corpus':self.engine.corpus_hash,'knowledge':self.engine.claim_hash,'code':self.engine.code_hash}}
    def ask(self,data):
        planner=None
        if data.get('use_model'):
            with self.planner_lock:
                if self.planner is None:
                    from .model_planner import ClaimPlanner
                    self.planner=ClaimPlanner(self.root)
                planner=self.planner
        return self.engine.answer(data.get('question',''),mode=data.get('mode','explain'),
                                 method=data.get('method','hybrid'),planner=planner)


def make_handler(application:Application):
    class Handler(BaseHTTPRequestHandler):
        server_version='ResearchWorkbench/2.0'
        def log_message(self,fmt,*args):
            # Requests never place questions or participant answers in console logs.
            if not args or '/api/' not in str(args[0]):super().log_message(fmt,*args)
        def allowed_host(self):
            host=urllib.parse.urlparse('//'+self.headers.get('Host','')).hostname
            return host in ('127.0.0.1','localhost','::1')
        def send(self,status,body,content_type='application/json',filename=None):
            if isinstance(body,(dict,list)):body=json.dumps(body,ensure_ascii=False).encode()
            elif isinstance(body,str):body=body.encode()
            self.send_response(status)
            self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(len(body)))
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; frame-src 'self'; object-src 'self'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; form-action 'self'")
            if filename:self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
            self.end_headers();self.wfile.write(body)
        def do_GET(self):
            if not self.allowed_host():self.send(403,{'error':'Localhost requests only'});return
            parsed=urllib.parse.urlparse(self.path);path=parsed.path
            try:
                if path=='/api/config':self.send(200,application.config());return
                if path=='/api/papers':self.send(200,list(application.engine.papers.values()));return
                if path=='/api/claims':self.send(200,application.engine.claims);return
                if path=='/api/pilot':self.send(200,pilot_summary(application.root));return
                if path=='/api/reviews':self.send(200,review_summary(application.root));return
                if path=='/api/runs':
                    from .review_index import run_index
                    self.send(200,run_index(application.root,application.engine));return
                if path=='/api/audit':
                    p=application.root/'audit/validation_report.json'
                    self.send(200,json.loads(p.read_text(encoding="utf-8")) if p.exists() else {'status':'No recorded delivery validation report'});return
                if path.startswith('/api/run/'):
                    run_id=path.rsplit('/',1)[1];r=load_run(application.root,run_id)
                    fmt=urllib.parse.parse_qs(parsed.query).get('format',['json'])[0]
                    if fmt=='md':self.send(200,markdown(r),'text/markdown; charset=utf-8',run_id+'.md')
                    else:self.send(200,r)
                    return
                if path.startswith('/api/source/'):
                    sid=urllib.parse.unquote(path.split('/api/source/',1)[1]);s=application.engine.by_source.get(sid)
                    if s is None:self.send(404,{'error':'Source not found'})
                    else:self.send(200,s)
                    return
                if path=='/api/export':
                    data=io.BytesIO()
                    with zipfile.ZipFile(data,'w',zipfile.ZIP_DEFLATED) as z:
                        for category in ['runs','reviews','pilot']:
                            for p in sorted((application.root/'results'/category).glob('*.json')):
                                z.write(p,category+'/'+p.name)
                        z.writestr('review_summary.json',json.dumps(review_summary(application.root),indent=2))
                        z.writestr('pilot_summary.json',json.dumps(pilot_summary(application.root),indent=2))
                        z.writestr('README.txt','Actual local run and review records. Empty pilot/review folders mean no observations were collected. Do not infer successful answers from output status.\n')
                    self.send(200,data.getvalue(),'application/zip','workbench_review_bundle.zip');return
                if path.startswith('/pdf/'):
                    pid=path.split('/')[-1].removesuffix('.pdf')
                    if pid not in application.engine.papers:raise ValueError('Unknown paper')
                    p=application.root/'corpus/pdfs'/(pid+'.pdf')
                    self.send(200,p.read_bytes(),'application/pdf');return
                allowed={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css'}
                if path not in allowed:self.send(404,{'error':'Not found'});return
                p=application.root/'web'/allowed[path]
                self.send(200,p.read_bytes(),mimetypes.guess_type(p.name)[0] or 'text/plain')
            except (ValueError,KeyError) as exc:self.send(400,{'error':str(exc)})
            except Exception as exc:self.send(500,{'error':type(exc).__name__+': '+str(exc)})
        def do_POST(self):
            if not self.allowed_host():self.send(403,{'error':'Localhost requests only'});return
            origin=self.headers.get('Origin')
            if origin and urllib.parse.urlparse(origin).netloc!=self.headers.get('Host'):
                self.send(403,{'error':'Cross-origin mutation rejected'});return
            if self.headers.get('X-Workbench-Token')!=application.csrf:
                self.send(403,{'error':'Missing local session token'});return
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<250000:raise ValueError('Request body size out of range')
                if 'application/json' not in self.headers.get('Content-Type',''):raise ValueError('JSON required')
                data=json.loads(self.rfile.read(size));path=urllib.parse.urlparse(self.path).path
                if not isinstance(data,dict):raise ValueError('JSON object required')
                if path=='/api/ask':out=application.ask(data)
                elif path=='/api/review':out=save_review(application.root,data)
                elif path=='/api/pilot/start':out=start_pilot(application.root,data)
                elif path=='/api/pilot/finish':out=finish_pilot(application.root,data)
                elif path=='/api/pilot/rate':out=rate_pilot(application.root,data)
                else:self.send(404,{'error':'Not found'});return
                self.send(200,out)
            except (ValueError,KeyError,json.JSONDecodeError) as exc:self.send(400,{'error':str(exc)})
            except Exception as exc:self.send(500,{'error':type(exc).__name__+': '+str(exc)})
    return Handler

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);parser.add_argument('--open',action='store_true');args=parser.parse_args()
    if not 1024<=args.port<=65535:parser.error('Port must be between 1024 and 65535')
    app=Application()
    try:server=ThreadingHTTPServer(('127.0.0.1',args.port),make_handler(app))
    except OSError as exc:raise SystemExit(f'Cannot bind localhost:{args.port}: {exc}. Close the existing workbench or use --port 8766.')
    address=f'http://127.0.0.1:{args.port}'
    print(f'Research Workbench: {address}\n{len(app.engine.papers)} papers · {len(app.engine.claims)} source-linked claims.\nBound to localhost only. Press Control+C to stop.',flush=True)
    if args.open:webbrowser.open(address)
    try:server.serve_forever()
    except KeyboardInterrupt:print('\nStopped.')
    finally:server.server_close()
