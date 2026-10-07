"""Las 5 estaciones MAFESA iguales, formato teléfono (pedido de Moisés, 6-oct-2026 21:31).
Base: la plantilla de teléfono (la de Limpieza, la más completa: avisos, alarma de parada, 'lista para…', espera, sonido).
Se le agrega lo que solo tenía TM-2P: cola EN VIVO desde Katana cuando el teléfono está conectado, y elegir operador con PIN
(solo TM-2P, donde hay varios operadores). El avance por proceso (AVP) se lee en vivo del datos.json de la TV.
Uso: python3 gen.py [--repo RUTA] [--plantilla app-limpieza/index.html]
Conserva los DATOS de cada estación (lee el arreglo que tenga hoy cada app, en formato DATA o el viejo mos:[...] de TM-2P)
y las claves de almacenamiento de cada teléfono (no se pierden los lapsos). Idempotente: se puede correr las veces que sea."""
import re,json,sys,os,argparse
AP=argparse.ArgumentParser(); AP.add_argument('--repo',default=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..')))
AP.add_argument('--plantilla',default=os.path.join(os.path.dirname(os.path.abspath(__file__)),'plantilla.html'))
A=AP.parse_args(); R=A.repo
CFG={
 'corte':  dict(hecho='cortadas',porh='por cortar',app='Corte',tith='Corte',maq='Corte',op='Operador',nota='Corte(?![ \\t]*L[aá]ser)',lista='LISTA PARA CORTAR',kpi='CORTE',cola='COLA DE CORTE · ORDEN DE LA TV',rec='Corte Mafesa',vista='VISTA DE CORTE',verbo='cortaste',parada='CORTE PARADO',ger='cortando',limp='15*60000',wa=True,waest='Corte',pzd=False,pin=False,avp='Corte',espera=False),
 'taladro':dict(hecho='taladradas',porh='por taladrar',app='Taladro',tith='Taladro',maq='Taladro',op='Operador',nota='Taladro',lista='LISTA PARA TALADRAR',kpi='TALADRO',cola='COLA DE TALADRO · ORDEN DE LA TV',rec='Taladro Mafesa',vista='VISTA DE TALADRO',verbo='taladraste',parada='TALADRO PARADO',ger='taladrando',limp='15*60000',wa=True,waest='Taladro',pzd=False,pin=False,avp='Taladro',espera=False),
 'tm2p':   dict(hecho='maquinadas',porh='por maquinar',app='TM-2P',tith='TM-2P',maq='TM-2P',op='Operador',nota='TM-2P',lista='LISTA PARA TM-2P',kpi='TM-2P',cola='COLA DE LA TM-2P · ORDEN DE LA TV',rec='TM-2P',vista='VISTA DE TM-2P',verbo='terminaste',parada='TM-2P PARADA',ger='trabajando',limp='15*60000',wa=True,waest='TM-2P',pzd=False,pin=True,avp='TM-2P',espera=False),
 'doblez': dict(hecho='dobladas',porh='por doblar',app='Estación Doblez',tith='Doblez',maq='Doblez',op='Miguel',nota='Doblez',lista='LISTA PARA DOBLAR',kpi='DOBLEZ',cola='COLA DE DOBLEZ · ORDEN DE LA TV',rec='Doblez Mafesa',vista='VISTA DEL DOBLEZ',verbo='doblaste',parada='DOBLADORA PARADA',ger='doblando',limp='15*60000',wa=True,waest='Dobladora',pzd=True,pin=False,avp='Doblez',espera=False),
 'limpieza':dict(hecho='limpias',porh='por limpiar',app='Limpieza & SQA',tith='Limpieza &amp; SQA',maq='Limpieza & SQA',op='Cynthia',nota='Limpieza',lista='LISTA PARA LIMPIEZA',kpi='LIMPIEZA',cola='COLA DE LIMPIEZA &amp; SQA · LISTAS PRIMERO',rec='Limpieza & SQA',vista='VISTA DE LIMPIEZA',verbo='limpiaste',parada='LIMPIEZA PARADA',ger='limpiando',limp='1e12',wa=False,waest='Limpieza & SQA',pzd=True,pin=False,avp='Limpieza',espera=True),
}
WA0='https://script.google.com/macros/s/AKfycbxAaapz3Qdb8ZKz65vS_4jeQJW9X_Ujaghla5cX6XFbN_NDDpWruWqbHFSPWPUnLE5v/exec'

def arr_at(t,i):
    d=0
    for j in range(i,len(t)):
        c=t[j]
        if c=='[': d+=1
        elif c==']':
            d-=1
            if d==0: return j+1
def datos_de(slug):
    t=open(f'{R}/app-{slug}/index.html').read()
    m=re.search(r'var DATA=\[',t)
    if m:
        i=m.end()-1; return json.loads(t[i:arr_at(t,i)])
    i=t.index('mos:[{')+4; raw=t[i:arr_at(t,i)].replace(',"st":nuevo()','')
    return [tm2p_a_data(x) for x in json.loads(raw)]
def tm2p_a_data(x):
    ruta=[[r[0],r[1],r[0]=='TM-2P'] for r in x.get('ruta',[]) if r and r[1] is not None]
    return {k:v for k,v in dict(mo=x['mo'],sec=x.get('sec'),nombre=x.get('nombre',''),sku=x.get('sku',''),piezas=x.get('piezas',0),ent=x.get('ent',''),
        deadline=x.get('deadline') or x.get('ent',''),prio=bool(x.get('prio')),paso=x.get('paso',''),recurso='TM-2P',planeado=x.get('planeado',0),fuenteT=x.get('fuenteT',''),
        recursoMal=False,ruta=ruta,ingSku=x.get('ingSku',''),ingNombre=x.get('ingNombre',''),ingTot=x.get('ingIn',0),ingUom='in',notas=x.get('notas','') or 'Sin notas.',
        hechas=x.get('hechas',0),entregadas=x.get('entregadas'),rowId=x.get('rowId')).items() if v is not None or k=='rowId'}
def pie_de(slug):
    t=open(f'{R}/app-{slug}/index.html').read(); m=re.search(r'MOs de Katana al ([0-9]{1,2}-[a-z]{3} [0-9]{1,2}:[0-9]{2})',t)
    return m.group(1) if m else ''

P=open(A.plantilla).read()
def js(s): return json.dumps(s,ensure_ascii=False)
for slug,c in CFG.items():
    t=P
    rep={'@@APPTIT@@':c['app'],'@@TITH@@':c['tith'],'@@SLUG@@':slug,'@@MAQJS@@':js(c['maq']),'@@OPJS@@':js(c['op']),'@@NOTARE@@':c['nota'].replace('\\','\\\\'),
         '@@LISTA@@':c['lista'],'@@KPI@@':c['kpi'],'@@COLA@@':c['cola'],'@@RECJS@@':js(c['rec']),'@@VISTA@@':c['vista'],'@@VERBO@@':c['verbo'],
         '@@PARADA@@':c['parada'],'@@GER@@':c['ger'],'@@LIMP@@':c['limp'],'@@WA@@':js(WA0 if c['wa'] else ''),'@@WAEST@@':js(c['waest']),
         '@@USAPZD@@':'true' if c['pzd'] else 'false','@@PINOPS@@':'true' if c['pin'] else 'false','@@AVPN@@':js(c['avp']),'@@ESPERA@@':'true' if c['espera'] else 'false',
         '@@HECHO@@':c['hecho'],'@@PORH@@':c['porh'],'@@PORHC@@':c['porh'][0].upper()+c['porh'][1:],'@@PORHU@@':c['porh'].upper(),'@@PIE@@':pie_de(slug) or '—','@@DATA@@':json.dumps(datos_de(slug),ensure_ascii=False)}
    for k,v in rep.items(): t=t.replace(k,v)
    falta=re.findall(r'@@[A-Z]+@@',t); assert not falta,(slug,falta)
    open(f'{R}/app-{slug}/index.html','w').write(t); print('ok',slug,len(json.loads(rep['@@DATA@@'])),'MOs')
    if not os.path.exists(f'{R}/app-{slug}/aviso.json'):
        open(f'{R}/app-{slug}/aviso.json','w').write('{"texto": "", "nivel": "aviso", "actualizado": "2026-10-06T00:00:00.000Z"}\n')
