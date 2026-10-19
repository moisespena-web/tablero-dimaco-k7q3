"""Publica para la Estación Caja chica (app-caja/) el saldo y el libro de solo lectura.
Uso: python3 -I publicar.py <export_dir> <app-caja dir> <aplicado.json> <ahora ISO>
export_dir = carpetas fondos/ entradas/ salidas/ con un JSON por documento (ArtifactData list out_dir).
NO publica notas internas, alertas de revisión ni historial: solo lo que Paty capturó o puede consultar."""
import json, glob, os, sys
exp, app, apl, ahora = sys.argv[1:5]
def docs(c):
    out = []
    for p in glob.glob(os.path.join(exp, c, '*.json')):
        j = json.load(open(p)); d = j.get('data', j); d['_id'] = j.get('id') or os.path.basename(p)[:-5]; out.append(d)
    return out
F, E, S = docs('fondos'), docs('entradas'), docs('salidas')
act = lambda x: x.get('estado', 'activa') != 'cancelada'
ing = [x for x in F + E]
saldo = round(sum(x.get('monto') or 0 for x in ing if act(x)) - sum(x.get('monto') or 0 for x in S if act(x)), 2)
aplicado = json.load(open(apl)) if os.path.exists(apl) else {}
folios = sorted(aplicado.get('folios', {}).keys())
cancel = sorted(aplicado.get('cancelados', []))
year = ahora[:4]
libro = []
for x in S:
    if not str(x.get('fecha', '')).startswith(year): continue
    libro.append(dict(f=x['fecha'], k='S', c=x.get('categoria') or 'OTROS', d=x.get('subconcepto') or '', q=x.get('concepto') or '',
                      p=x.get('persona') or '', m=round(x.get('monto') or 0, 2), x=0 if act(x) else 1))
for x in ing:
    if not str(x.get('fecha', '')).startswith(year): continue
    libro.append(dict(f=x['fecha'], k='E', c=x.get('tipo') or 'DIRECCIÓN', d='', q=x.get('concepto') or '', p=x.get('persona') or '',
                      m=round(x.get('monto') or 0, 2), x=0 if act(x) else 1))
libro.sort(key=lambda r: (r['f'], r['k']), reverse=True)
json.dump(dict(saldo=saldo, al=ahora, folios=folios, cancelados=cancel), open(os.path.join(app, 'saldo.json'), 'w'), ensure_ascii=False)
json.dump(dict(al=ahora, movs=libro), open(os.path.join(app, 'libro.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('saldo', saldo, 'movs', len(libro), 'folios', len(folios))
