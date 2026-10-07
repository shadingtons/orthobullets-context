"""Public package installation/import and session fixtures; no private decks."""
import hashlib,importlib,json,os,shutil,sys,tempfile,weakref,zipfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import aqt,aqt.addons
from aqt.addons import AddonManager,InstallOk,download_addon,DownloadOk
from anki.httpclient import HttpClient
from anki.collection import Collection
from aqt.qt import QApplication,QMainWindow,QMenuBar,QAction
IDENTITY=1699391455
EXPECTED='5985be8b1a694b5b332831aa6faa76901a96be084e9b2c0997e01fc6a776e94f'
with HttpClient() as client:download=download_addon(client,IDENTITY)
assert isinstance(download,DownloadOk),download
assert hashlib.sha256(download.data).hexdigest()==EXPECTED,'Published release changed: rebind the reviewed artifact explicitly.'
assert (download.min_point_version,download.max_point_version)==(250904,-250904)
app=QApplication(['Orthobullets portable fixture'])
checks={}
with tempfile.TemporaryDirectory() as temp:
 root=Path(temp);addons=root/'addons21';addons.mkdir();archive=root/'public.ankiaddon';archive.write_bytes(download.data)
 w=QMainWindow();w.weakref=lambda:weakref.ref(w);w.pm=SimpleNamespace(name='Synthetic Test',addonFolder=lambda:str(addons));w.form=SimpleNamespace(menubar=QMenuBar(w),actionAdd_ons=QAction(w))
 aqt.mw=w;m=AddonManager(w);w.addonManager=m
 for name in ['orthobullets_context','orthobullets_context_beta']:
  p=addons/name;p.mkdir();(p/'__init__.py').write_text('# synthetic old add-on\n');(p/'user_files').mkdir();(p/'user_files/keep.txt').write_text('synthetic saved data');m.writeAddonMeta(name,{'disabled':False,'config':{'fixture_setting':True}})
 manifest={'package':str(IDENTITY),'name':download.filename,'mod':download.mod_time,'min_point_version':download.min_point_version,'max_point_version':download.max_point_version,'branch_index':download.branch_index}
 result=m.install(str(archive),manifest=manifest);assert isinstance(result,InstallOk) and result.compatible,result
 assert result.conflicts=={'orthobullets_context','orthobullets_context_beta'}
 assert all(not m.isEnabled(name) and (addons/name/'user_files/keep.txt').read_text()=='synthetic saved data' and m.addonMeta(name)['config']=={'fixture_setting':True} for name in result.conflicts)
 checks['fresh_install_and_conflict_preservation']=True
 installed=addons/str(IDENTITY);(installed/'user_files/keep.txt').write_text('new synthetic data');m.writeConfig(str(IDENTITY),{'enabled':True,'daily_prep_tag_root':'Synthetic::Prep'})
 def remove_test_only(path):
  p=Path(path).resolve();assert p.is_relative_to(addons.resolve());shutil.rmtree(p)
 with patch.object(aqt.addons,'send_to_trash',remove_test_only):result=m.install(str(archive),manifest=manifest)
 assert isinstance(result,InstallOk) and (installed/'user_files/keep.txt').read_text()=='new synthetic data' and m.getConfig(str(IDENTITY))['daily_prep_tag_root']=='Synthetic::Prep';checks['update_preserves_settings_and_files']=True
 sys.path.insert(0,str(addons));addon=importlib.import_module(str(IDENTITY));assert addon.VERSION=='0.1.0-beta.2';assert sum(x.text()=='Orthobullets' for x in w.form.menubar.actions())==1;checks['runtime_import_and_menu']=True
 col=Collection(str(root/'collection.anki2'))
 try:
  for name in ['Test * "Deck" _ 人','Test similar Deck']:
   did=col.decks.id(name);note=col.new_note(col.models.by_name('Basic'));note['Front']='Synthetic recall';note['Back']='Synthetic answer';col.add_note(note,did)
  selected=col.decks.all_names_and_ids();target=next(x for x in selected if x.name=='Test * "Deck" _ 人')
  query=importlib.import_module(str(IDENTITY)+'.deck_selection').deck_query(target.name)
  ids=col.find_cards(query);assert len(ids)==1 and col.get_card(ids[0]).did==target.id,(query,ids);checks['literal_deck_selection_on_real_backend']=True
 finally:col.close()
 w.close()
report={'platform':sys.platform,'python':sys.version.split()[0],'ankiweb_id':IDENTITY,'package_sha256':EXPECTED,'checks':checks,'personal_collection_accessed':False,'interactive_clinical_mapping_accuracy_tested':False,'embedded_account_login_tested':False}
Path(__file__).with_name('platform_result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
