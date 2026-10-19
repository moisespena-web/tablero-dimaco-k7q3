"""Importa al tablero Caja chica los correos "CAJA CHICA PATY" que manda la Estación Caja chica (app-caja/).
Uso: python3 -I importar.py <correos.json> <export_dir> <aplicado.json> <salida_dir>
  correos.json: [{"id": "...", "from": "...", "date": "ISO", "body": "texto"}]  (cualquier orden)
  export_dir:   fondos/ entradas/ salidas/ del tablero (ArtifactData list con out_dir), para no duplicar
  aplicado.json: ledger {"folios": {folio: {"col","id","correo"}}, "cancelados": [folio, ...]}
Escribe en <salida_dir>:
  nuevos.json     -> lista de {"collection","doc_id","data"} para crear (ArtifactData batch op "set" SIN if_version)
  cancelar.json   -> lista de {"collection","doc_id","motivo","folio"}: get + update con if_version
  aplicado.json   -> ledger actualizado (cópialo sobre el del repo SOLO si las escrituras salieron bien)
  reporte.txt     -> resumen para el cierre
Regla: el folio es la llave; repetir un correo no duplica nada. Nunca se borra nada."""
import json, glob, os, re, sys, datetime

corr_p, exp, apl_p, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
PATY = 'patricia.pena@dimaco-mx.com'
CATS = {'NÓMINA': ['Nómina semanal', 'Sueldo en efectivo', 'Diferencia de nómina', 'Becario', 'PTU', 'Otro'],
        'DESTAJO': ['Destajo por pieza', 'Pago por horas', 'Obra y mantenimiento', 'Otro'],
        'PRÉSTAMO': ['Préstamo a trabajador', 'Otro'], 'VIÁTICOS': ['Comida en viaje', 'Cena en viaje', 'Caseta', 'Otro'],
        'COMPRAS': ['Tornillería', 'Mangueras', 'Refacciones y piezas', 'Herramienta', 'Material eléctrico', 'Otro'],
        'VEHÍCULOS': ['Talacha y llantas', 'Gasolina', 'Reparación', 'Multa o verificación', 'Lavado', 'Otro'],
        'SERVICIOS': ['Agua oficinas', 'Basura', 'Paquetería', 'Comida de perros', 'Impresiones', 'Báscula', 'Limpieza y terreno', 'Otro'],
        'PERSONAL': ['Médico y medicamento', 'Pastel de cumpleaños', 'Recarga de celular', 'Regalo', 'Otro'],
        'DIRECCIÓN': ['Bebidas', 'Comida', 'Otro'], 'OTROS': ['Otro']}
TIPOS = ['DIRECCIÓN', 'CHEQUE', 'CLIENTE', 'REPOSICIÓN']
COMPS = {'Ticket': 'Ticket', 'Nota': 'Nota', 'Factura': 'Factura', 'Recibo firmado': 'Recibo firmado', 'Sin comprobante': 'Sin factura'}

def docs(c):
    r = {}
    for p in glob.glob(os.path.join(exp, c, '*.json')):
        j = json.load(open(p)); d = j.get('data', j) if isinstance(j.get('data'), dict) else j
        r[j.get('id') or os.path.basename(p)[:-5]] = d
    return r
F, E, S = docs('fondos'), docs('entradas'), docs('salidas')
apl = json.load(open(apl_p)) if os.path.exists(apl_p) else {}
apl.setdefault('folios', {}); apl.setdefault('cancelados', [])
existentes = {**{k: 'fondos' for k in F}, **{k: 'entradas' for k in E}, **{k: 'salidas' for k in S}}
ligados = {v['id'] for v in apl['folios'].values()}

money = lambda n: '${:,.2f}'.format(n)
def num(s): return round(float(s.replace('$', '').replace(',', '').strip()), 2)
def fecha(s):
    d, m, y = s.strip().split('/'); return f'{y}-{int(m):02d}-{int(d):02d}'
def campo(parts, pref):
    for p in parts:
        if p.startswith(pref): v = p[len(pref):].strip(); return '' if v == '-' else v
    return ''

correos = json.load(open(corr_p))
correos.sort(key=lambda c: c.get('date', ''))
nuevos, cancelar, rep, dudas = [], [], [], []
vistos = set()
for c in correos:
    body = c.get('body', '').replace('\r', '')
    if 'CAJA CHICA PATY' not in body: continue
    # une renglones partidos por el cliente de correo
    L = []
    for ln in body.split('\n'):
        ln = ln.strip().lstrip('>').strip()
        if not ln: continue
        if re.match(r'^(SALIDA|ENTRADA|CANCELA|FIN|CAJA CHICA PATY|Saldo en la estación)', ln) or not L: L.append(ln)
        else: L[-1] += ' ' + ln
    remit = (c.get('from') or '').lower()
    ajeno = PATY not in remit
    cdate = (c.get('date') or '')[:19]
    for ln in L:
        parts = [p.strip() for p in ln.split(' · ')]
        tipo = parts[0]
        if tipo not in ('SALIDA', 'ENTRADA', 'CANCELA'): continue
        fol = parts[1] if len(parts) > 1 else ''
        if not re.fullmatch(r'P\d{6}-[A-Z0-9]{4}', fol):
            dudas.append(f'Renglón sin folio válido: {ln[:90]}'); continue
        if tipo == 'CANCELA':
            if fol in apl['cancelados'] or (fol, 'X') in vistos: continue
            vistos.add((fol, 'X'))
            mot = campo(parts, 'Motivo:') or 'sin motivo'
            ref = apl['folios'].get(fol)
            nuevo = next((n for n in nuevos if n['doc_id'] == fol), None)
            if nuevo: nuevo['data']['estado'] = 'cancelada'; nuevo['data']['motivoCancel'] = mot
            elif ref: cancelar.append(dict(collection=ref['col'], doc_id=ref['id'], motivo=mot, folio=fol))
            else: dudas.append(f'Cancelación de {fol} sin movimiento registrado (motivo: {mot})'); continue
            apl['cancelados'].append(fol); rep.append(f'Cancelado {fol}: {mot}'); continue
        if fol in apl['folios'] or (fol, 'M') in vistos: continue
        vistos.add((fol, 'M'))
        try:
            f, m = fecha(parts[2]), num(parts[3])
        except Exception:
            dudas.append(f'{fol}: fecha o monto ilegible'); continue
        rev = []
        if ajeno: rev.append(f'llegó desde {remit or "remitente desconocido"}, no del correo de Paty')
        base = dict(fecha=f, monto=m, estado='activa', capturadoPor='Paty (estación)', capturadoEn=cdate + ('Z' if cdate and not cdate.endswith('Z') else ''),
                    origen='estacion', folio=fol, historial=[])
        if tipo == 'SALIDA':
            cs = parts[4] if len(parts) > 4 else ''
            cat, _, sub = cs.partition(' › ')
            cat, sub = cat.strip(), sub.strip()
            if cat not in CATS: rev.append(f'concepto desconocido "{cat}"'); cat = 'OTROS'; sub = 'Otro'
            elif sub not in CATS[cat]: rev.append(f'detalle desconocido "{sub}"'); sub = 'Otro'
            desc, per = campo(parts, 'Qué:'), campo(parts, 'Recibe:')
            comp = COMPS.get(campo(parts, 'Comprobante:'), 'Sin factura')
            if len(desc) < 8: rev.append('descripción incompleta')
            if len(per) < 3: rev.append('sin quién recibe')
            data = dict(base, categoria=cat, subconcepto=sub, concepto=desc or sub, persona=per, comprobante=comp,
                        nota=campo(parts, 'Nota:'), fotoId=None)
            if rev: data['revisar'] = '; '.join(rev)
            nuevos.append(dict(collection='salidas', doc_id=fol, data=data))
            apl['folios'][fol] = dict(col='salidas', id=fol, correo=c.get('id'))
            rep.append(f'Salida {fol} · {f} · {money(m)} · {cat} › {sub} · {desc} · {per}')
        else:
            tp = parts[4] if len(parts) > 4 else ''
            if tp not in TIPOS: rev.append(f'tipo de entrada desconocido "{tp}"'); tp = 'CLIENTE'
            per, nota = campo(parts, 'De:'), campo(parts, 'Nota:')
            if tp == 'DIRECCIÓN':
                fd = datetime.date.fromisoformat(f)
                par = [k for k, d in F.items() if k not in ligados and (d.get('tipo') or 'DIRECCIÓN') == 'DIRECCIÓN'
                       and d.get('estado', 'activa') != 'cancelada' and abs((d.get('monto') or 0) - m) < 0.5
                       and d.get('fecha') and abs((datetime.date.fromisoformat(d['fecha']) - fd).days) <= 3]
                if par and not ajeno:
                    k = sorted(par, key=lambda k: abs((datetime.date.fromisoformat(F[k]['fecha']) - fd).days))[0]
                    ligados.add(k); apl['folios'][fol] = dict(col='fondos', id=k, correo=c.get('id'))
                    rep.append(f'Paty confirma entrega de dirección {fol} · {f} · {money(m)} = ya registrada ({k})'); continue
                rev.insert(0, 'Paty reporta haber recibido este efectivo de dirección; confírmalo')
                data = dict(base, tipo='DIRECCIÓN', concepto=nota or 'Efectivo de dirección (reportado por Paty)', persona=per, nota=nota)
                data['revisar'] = '; '.join(rev)
                nuevos.append(dict(collection='fondos', doc_id=fol, data=data))
                apl['folios'][fol] = dict(col='fondos', id=fol, correo=c.get('id'))
                rep.append(f'POR CONFIRMAR: Paty dice que recibió de dirección {money(m)} el {f} ({fol}); no estaba registrado')
                continue
            if len(per) < 3: rev.append('sin de quién')
            data = dict(base, tipo=tp, concepto=nota or tp, persona=per, nota=nota)
            if rev: data['revisar'] = '; '.join(rev)
            nuevos.append(dict(collection='entradas', doc_id=fol, data=data))
            apl['folios'][fol] = dict(col='entradas', id=fol, correo=c.get('id'))
            rep.append(f'Entrada {fol} · {f} · {money(m)} · {tp} · {per}')

for n in nuevos:
    if n['doc_id'] in existentes: dudas.append(f"{n['doc_id']} ya existe en {existentes[n['doc_id']]}; no se vuelve a crear")
nuevos = [n for n in nuevos if n['doc_id'] not in existentes]
json.dump(nuevos, open(os.path.join(out, 'nuevos.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(cancelar, open(os.path.join(out, 'cancelar.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(apl, open(os.path.join(out, 'aplicado.json'), 'w'), ensure_ascii=False, indent=1)
txt = [f'Nuevos {len(nuevos)} · cancelaciones {len(cancelar)} · dudas {len(dudas)}'] + rep + ['DUDA: ' + d for d in dudas]
open(os.path.join(out, 'reporte.txt'), 'w').write('\n'.join(txt) + '\n')
print('\n'.join(txt))
