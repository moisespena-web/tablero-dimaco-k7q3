#!/usr/bin/env python3
"""Sube PDF/Excel/HTML a Dropbox desde la nube, por el robot cifrado .github/workflows/subir_dropbox.yml.
Uso: python3 subir.py --repo <clon> --id <FS o texto> archivo1=<ns>:<ruta dropbox> [archivo2=...]
  <ns>  namespace de Dropbox (ns_path que da el conector: 283552413 = carpeta de Moisés "Dimaco/…",
        15270085859 = TRM Mafesa). <ruta> relativa a ese namespace, ej. "/Dimaco/Mafesa/MO en proceso/X.pdf".
Cifra con subir_pub.pem (el robot tiene la llave privada en el secreto SUBIR_PRIV), hace commit + push y espera
(hasta 6 min) entrega/<id>.json con el resultado. Imprime el resultado y sale 0 si todo subió."""
import argparse, json, os, shutil, subprocess, sys, tarfile, tempfile, time
A=argparse.ArgumentParser(); A.add_argument('--repo',required=True); A.add_argument('--id',required=True); A.add_argument('items',nargs='+')
a=A.parse_args(); R=a.repo; D=os.path.join(R,'herramientas/subir'); ID=a.id.replace('/','-').replace(' ','_')
def sh(*c,**k): return subprocess.run(c,cwd=R,check=True,capture_output=True,text=True,**k).stdout
if not os.path.exists(os.path.join(D,'refresh.enc')): sys.exit('FALTA_TOKEN: aún no existe herramientas/subir/refresh.enc (Moisés debe correr "Dropbox · sacar token").')
W=tempfile.mkdtemp(); dest=[]
for it in a.items:
    f,_,d=it.partition('='); ns,_,ruta=d.partition(':')
    n=os.path.basename(f); shutil.copy(f,os.path.join(W,n)); dest.append({"archivo":n,"ns":ns,"ruta":ruta})
json.dump(dest,open(os.path.join(W,'_destino.json'),'w'),ensure_ascii=False)
W2=tempfile.mkdtemp(); tgz=os.path.join(W2,ID+'.tgz')
with tarfile.open(tgz,'w:gz') as t:
    for n in os.listdir(W): t.add(os.path.join(W,n),arcname=n)
k=os.path.join(W2,ID+'.k'); open(k,'w').write(os.urandom(32).hex())
enc=os.path.join(D,'pedido',ID+'.enc'); key=os.path.join(D,'pedido',ID+'.key')
subprocess.run(['openssl','enc','-aes-256-cbc','-pbkdf2','-salt','-in',tgz,'-out',enc,'-pass','file:'+k],check=True)
subprocess.run(['openssl','pkeyutl','-encrypt','-pubin','-inkey',os.path.join(D,'subir_pub.pem'),'-pkeyopt','rsa_padding_mode:oaep','-in',k,'-out',key],check=True)
shutil.rmtree(W); shutil.rmtree(W2)
sh('git','add',enc,key); sh('git','commit','-m','Subir a Dropbox '+ID)
for i in range(3):
    try: sh('git','pull','-q','--rebase'); sh('git','push','-q'); break
    except subprocess.CalledProcessError: time.sleep(5)
res='herramientas/subir/entrega/%s.json'%ID
for i in range(24):
    time.sleep(15); sh('git','fetch','-q','origin','main')
    try: out=json.loads(sh('git','show','origin/main:'+res)); break
    except subprocess.CalledProcessError: out=None
if out is None: sys.exit('SIN_RESPUESTA: el robot no contestó en 6 min (revisa Actions → "Subir archivos a Dropbox").')
sh('git','pull','-q','--rebase'); print(json.dumps(out,ensure_ascii=False,indent=1))
sys.exit(0 if all(x['ok'] for x in out) else 2)
