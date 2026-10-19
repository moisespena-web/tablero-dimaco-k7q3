"""Extrae del tablero "Asistencia y Nómina DIMACO" (su index.html) el efectivo de nómina por semana.
Uso: python cuadre_asistencia.py <index.html de Asistencia> <salida.json>
Por semana: efectivo a entregar (neto - tarjeta, sin Dirección), lo que reponen los colaboradores
(tarjeta > neto), préstamos descontados en nómina y personas sin tarjeta."""
import json, re, sys

src, out = sys.argv[1:3]
s = open(src, encoding='utf-8').read()
sc = re.findall(r'<script[^>]*>(.*?)</script>', s, re.S)
sc = next(x for x in sc if 'const DATA = ' in x)
i = sc.index('const DATA = ') + len('const DATA = ')
D, _ = json.JSONDecoder().raw_decode(sc[i:])

def ded_of(rfc, p):
    pr = p.get('prestamo') or 0
    if p.get('ded_paty'):
        dp = p['ded_paty']
        ot = sum(dp.get(k, 0) or 0 for k in ['Caja De Ahorro', 'Credito Infonavit', 'Pension Alimenticia'])
        return (dp.get('ISR', 0) or 0) + (dp.get('IMSS', 0) or 0) + ot + pr
    d = D['ded'].get(rfc)
    if not d:
        return pr
    return d['isr'] + d['imss'] + sum(d['otras'].values()) - (d.get('subsidio') or 0) + pr

def title(n):
    return ' '.join(w.capitalize() for w in n.split())

res = []
for sm in D['semanas']:
    num = int(re.sub(r'\D', '', sm['etiqueta']))
    w = dict(semana=num, etiqueta=sm['etiqueta'], lunes=sm['lunes'], fecha_pago=None,
             neto=0.0, tarjeta=0.0, efectivo=0.0, repone_total=0.0, prestamos_total=0.0,
             efectivo_personas=[], repone=[], prestamos=[], sin_tarjeta=[], direccion=[])
    for p in sm['personas']:
        w['fecha_pago'] = w['fecha_pago'] or p.get('fecha_pago')
        neto = p['bruto'] + (p.get('otros_pagos') or 0) - ded_of(p['rfc'], p)
        nom = title(p['nombre'])
        if p['tipo'] == 'Dirección':
            w['direccion'].append(dict(nombre=nom, neto=round(neto, 2), tarjeta=p.get('tarjeta')))
            continue
        w['neto'] += neto
        if p.get('prestamo'):
            w['prestamos_total'] += p['prestamo']
            w['prestamos'].append(dict(nombre=nom, monto=p['prestamo']))
        if p.get('tarjeta') is None:
            w['sin_tarjeta'].append(dict(nombre=nom, neto=round(neto, 2)))
            w['efectivo'] += neto
            w['efectivo_personas'].append(dict(nombre=nom, monto=round(neto, 2)))
            continue
        w['tarjeta'] += p['tarjeta']
        e = neto - p['tarjeta']
        if e >= 0:
            w['efectivo'] += e
            if e >= 0.5:
                w['efectivo_personas'].append(dict(nombre=nom, monto=round(e, 2)))
        else:
            w['repone_total'] += -e
            if -e >= 0.5:
                w['repone'].append(dict(nombre=nom, monto=round(-e, 2)))
    for k in ('neto', 'tarjeta', 'efectivo', 'repone_total', 'prestamos_total'):
        w[k] = round(w[k], 2)
    res.append(w)
json.dump(res, open(out, 'w'), ensure_ascii=False, indent=1)
for w in res:
    print(w['etiqueta'], 'pago', w['fecha_pago'], 'efectivo', w['efectivo'], 'repone', w['repone_total'], 'prestamos', w['prestamos_total'])
