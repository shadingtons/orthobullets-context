"""Actual Qt cookie restart/isolation fixture. Never accesses an Anki collection."""
import sys,json,os,importlib.util,subprocess,tempfile,threading
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parent
if len(sys.argv)>1 and sys.argv[1]=='child':
 from aqt.qt import QApplication,QWebEngineView,QTimer,QEvent,QCoreApplication
 import aqt
 app=QApplication(['Orthobullets Session Test'])
 spec=importlib.util.spec_from_file_location('browser_session',ROOT/'components/browser_session.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 view=QWebEngineView();view.setWindowTitle('Orthobullets Session Test');view.resize(640,450)
 before=view.page().profile().isOffTheRecord()
 p=m.configure_browser(view,sys.argv[2],sys.argv[3]);assert not p.isOffTheRecord()
 assert p.persistentStoragePath()==str(m.session_directory(sys.argv[2],sys.argv[3])/'storage')
 from aqt.qt import QUrl
 result={}
 def finish(value):
  result.update(default_profile_off_the_record=before,persistent_session=True,fixture_cookie_present=value=='COOKIE_PRESENT')
  Path(sys.argv[5]).write_text(json.dumps(result))
  view.deleteLater()
  QTimer.singleShot(200,app.quit)
 def loaded(ok):
  if not ok:app.exit(2);return
  QTimer.singleShot(1500,lambda:view.page().runJavaScript('document.body.textContent.trim()',finish))
 view.loadFinished.connect(loaded);view.show();view.setUrl(QUrl(sys.argv[4]));QTimer.singleShot(12000,lambda:app.exit(3))
 code=app.exec();assert result and code==0
else:
 class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
   self.send_response(200);self.send_header('Content-Type','text/html')
   if self.path=='/set':self.send_header('Set-Cookie','ob_test=present; Max-Age=3600; Path=/; SameSite=Lax')
   self.end_headers();present='ob_test=present' in self.headers.get('Cookie','')
   self.wfile.write(('COOKIE_PRESENT' if present else 'COOKIE_ABSENT').encode())
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with tempfile.TemporaryDirectory() as tmp:
   rows=[]
   for name,path,expected in [('A','/set',False),('B','/check',False),('A','/check',True)]:
    out=Path(tmp)/(str(len(rows))+'.json')
    env={**os.environ,'QTWEBENGINE_CHROMIUM_FLAGS':'--disable-gpu'}
    r=subprocess.run([sys.executable,__file__,'child',tmp,name,f'http://127.0.0.1:{server.server_port}{path}',str(out)],env=env,capture_output=True,text=True,timeout=20)
    if r.returncode:raise AssertionError(r.stderr[-2500:])
    d=json.loads(out.read_text());assert d['fixture_cookie_present']==expected,d;rows.append({'profile':name,'phase':path,**d})
   (ROOT/'session_result.json').write_text(json.dumps({'restart_persistence_verified':True,'profile_isolation_verified':True,'cases':rows,'collection_writes':False},indent=2))
   print(json.dumps(rows,indent=2))
 finally:server.shutdown()
