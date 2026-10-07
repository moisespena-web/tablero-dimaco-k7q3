"""Uso: python3 enriquecer_tv.py tv_datos.json mo1.json [mo2.json ...]
Agrega a cada row de tv_datos.json plan (planned_quantity) y entr (completed_quantity) — regla 6-oct-2026.
Correr DESPUÉS de build_entregas.py y ANTES de escribir tv/datos y de armar PDF/widget/Excel."""
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from pz6 import enriquecer
def cargar(p):
    j=json.load(open(p)); 
    if isinstance(j,dict): j=j.get('data',j.get('manufacturing_orders',[]))
    return j if isinstance(j,list) else []
D=json.load(open(sys.argv[1])); mos=[m for p in sys.argv[2:] for m in cargar(p)]
rows=(D.get('datos') or D).get('rows') if isinstance(D.get('datos'),dict) else D.get('rows')
enriquecer(rows,mos); json.dump(D,open(sys.argv[1],'w'),ensure_ascii=False)
sin=[r['mo'] for r in rows if 'plan' not in r]
print('rows:',len(rows),'con plan/entr:',len(rows)-len(sin),'sin MO en Katana:',sin)
