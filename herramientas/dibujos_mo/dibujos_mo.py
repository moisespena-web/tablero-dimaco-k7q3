"""Dibujos de MO nuevas MAFESA · revisión de proceso (pedido de Moisés, 8-oct-2026).

Una hoja (7 MO por hoja; más hojas solo si hay más de 7) con, por MO: la pieza recortada del plano,
el proceso cargado en Katana en orden (operación · seg/pz · verde = terminada) y lo que muestra el plano.
Moisés NO quiere medidas a detalle: quiere ver la pieza y revisar si el proceso de Katana es correcto.

Reglas fijas:
- Solo MAFESA. Cada MO sale UNA sola vez: las que ya están en enviadas.json no se repiten aunque sigan abiertas.
- MOs con remaining_quantity = 0 no entran.
- Una MO cuyo SKU no tiene recorte en catalogo.json sale con aviso "sin recorte" y NO se registra
  (vuelve a salir la noche siguiente, ya con su recorte).

Uso:
  python3 dibujos_mo.py armar --mos mos.json --out "<carpeta>" --fs DD-MM_HH-MM --stamp "DD/MM HH:MM"
      mos.json = [{"mo":"MO-397","id":19504372,"sku":"36B9157-0021","falt":20,"tot":20,
                   "ops":[["Corte","Corte Mafesa",40,"NOT_STARTED"], ...]}, ...]   (ops en orden de rank)
      Imprime el nombre del PDF (o "NADA" si no hay MO nuevas) y deja registro_pendiente.json.
  python3 dibujos_mo.py registrar     (después de entregar el PDF: pasa registro_pendiente.json a enviadas.json)
"""
import sys, os, json, argparse, datetime as dt
from PIL import Image
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.utils import simpleSplit

AQUI = os.path.dirname(os.path.abspath(__file__))
CAT = os.path.join(AQUI, 'catalogo.json')
ENV = os.path.join(AQUI, 'enviadas.json')
PEND = os.path.join(AQUI, 'registro_pendiente.json')
REC = os.path.join(AQUI, 'recortes')


def cargar(p, d):
    try:
        return json.load(open(p))
    except FileNotFoundError:
        return d


def observaciones(m, cat):
    obs = []
    ops = m['ops']
    nombres = [o[0] for o in ops]
    for i, (op, res, t, st) in enumerate(ops):
        if float(t) == 0:
            antes = [o for o in ops[:i] if o[1] == 'TM-2P']
            if op == 'Taladro' and antes:
                obs.append('Taladro con 0 s/pz después de la TM-2P: ¿lo hace la TM-2P y sobra Taladro?')
            else:
                obs.append('%s con 0 s/pz en Katana.' % op)
    if ops and all(o[3] == 'COMPLETED' for o in ops) and m['falt'] > 0:
        obs.append('Las %d operaciones están completas en Katana, pero la MO sigue abierta con %s pz.' % (len(ops), '{:,}'.format(m['falt'])))
    if len(set(nombres)) != len(nombres):
        obs.append('Operación repetida en la ruta de Katana.')
    c = cat.get(m['sku'])
    if c and c.get('nota'):
        obs.append(c['nota'])
    if not c:
        obs.append('SKU sin recorte de plano todavía: revisar el plano en Dropbox (Dibujos MAFESA).')
    return obs


def armar(a):
    cat = cargar(CAT, {})
    env = set(cargar(ENV, {}).get('mos', []))
    mos = json.load(open(a.mos))
    nuevas = [m for m in mos if m['mo'] not in env and m.get('falt', 0) > 0]
    nuevas.sort(key=lambda m: int(''.join(ch for ch in m['mo'] if ch.isdigit()) or 0))
    if not nuevas:
        json.dump({'mos': []}, open(PEND, 'w'))
        print('NADA')
        return
    os.makedirs(a.out, exist_ok=True)
    nombre = 'Dibujos MO nuevas Mafesa_%s.pdf' % a.fs
    out = os.path.join(a.out, nombre)

    W, H = landscape(letter)
    M = 22
    NAVY, ORANGE, GREY, LIGHT, RED, GREEN = (HexColor(x) for x in ('#14213d', '#e07a1f', '#666666', '#eef1f6', '#b42318', '#2e7d32'))
    PER = 7
    pages = [nuevas[i:i + PER] for i in range(0, len(nuevas), PER)]
    allobs = {m['mo']: observaciones(m, cat) for m in nuevas}
    nrev = sum(1 for v in allobs.values() if v)
    X_MO, X_IMG, X_RUTA = M, M + 118, M + 118 + 300
    W_IMG = X_RUTA - X_IMG - 10
    c = canvas.Canvas(out, pagesize=(W, H))
    c.setTitle('MO nuevas MAFESA · revisión de proceso')
    for pn, rows in enumerate(pages, 1):
        c.setFillColor(NAVY); c.rect(0, H - 44, W, 44, fill=1, stroke=0)
        c.setFillColor(white); c.setFont('Helvetica-Bold', 16)
        c.drawString(M, H - 27, 'MO NUEVAS MAFESA · REVISIÓN DE PROCESO')
        c.setFont('Helvetica', 8.5)
        c.drawRightString(W - M, H - 20, '%d MO nuevas · %d por revisar' % (len(nuevas), nrev))
        c.drawRightString(W - M, H - 32, a.stamp + (' · Hoja %d de %d' % (pn, len(pages)) if len(pages) > 1 else ''))
        top = H - 54
        c.setFillColor(GREY); c.setFont('Helvetica-Bold', 7.5)
        c.drawString(X_MO + 3, top - 8, 'MO / SKU')
        c.drawString(X_IMG + 3, top - 8, 'PIEZA (PLANO)')
        c.drawString(X_RUTA + 3, top - 8, 'PROCESO EN KATANA (en orden · seg/pz · verde = terminada)')
        y = top - 12
        rh = (y - 22) / PER
        for i, m in enumerate(rows):
            ci = cat.get(m['sku'], {})
            obs = allobs[m['mo']]
            y0 = y - rh
            if obs:
                c.setFillColor(HexColor('#fdecea')); c.rect(M, y0, W - 2 * M, rh, fill=1, stroke=0)
            elif i % 2 == 0:
                c.setFillColor(LIGHT); c.rect(M, y0, W - 2 * M, rh, fill=1, stroke=0)
            c.setFillColor(NAVY); c.setFont('Helvetica-Bold', 12.5)
            c.drawString(X_MO + 3, y - 14, m['mo'])
            c.setFont('Helvetica-Bold', 8.5); c.drawString(X_MO + 3, y - 25, m['sku'])
            desc = ci.get('desc', '')
            if ' .' in desc:
                nom, med = desc.split(' .', 1); med = '.' + med
            else:
                nom, med = desc, ''
            c.setFillColor(black); c.setFont('Helvetica', 7); c.drawString(X_MO + 3, y - 35, nom[:24])
            c.setFillColor(GREY); c.setFont('Helvetica', 6.5); c.drawString(X_MO + 3, y - 44, med)
            c.setFillColor(ORANGE); c.setFont('Helvetica-Bold', 7.5)
            c.drawString(X_MO + 3, y - 55, 'Faltan {:,} de {:,}'.format(m['falt'], m['tot']))
            # pieza
            imgs = [os.path.join(REC, n) for n in ci.get('imgs', []) if os.path.exists(os.path.join(REC, n))]
            if not imgs:
                c.setFillColor(RED); c.setFont('Helvetica-Bold', 9)
                c.drawString(X_IMG + 8, y - rh / 2, 'Sin recorte de plano')
            else:
                ims = [Image.open(p) for p in imgs]
                bh = rh - 6
                if len(ims) == 2 and ims[0].width / ims[0].height > 5:
                    A, B = ims
                    ha = min((W_IMG - 6) * A.height / A.width, bh * 0.4); wa = ha * A.width / A.height
                    hb = bh - ha - 3; wb = hb * B.width / B.height
                    c.drawImage(imgs[0], X_IMG + 3, y - 3 - ha, wa, ha)
                    c.drawImage(imgs[1], X_IMG + 3, y0 + 3, wb, hb)
                else:
                    ratios = [im.width / im.height for im in ims]
                    tw = sum(r * bh for r in ratios) + 6 * (len(ims) - 1)
                    if tw > W_IMG - 6:
                        bh *= (W_IMG - 6) / tw
                    x = X_IMG + 3
                    for p, r in zip(imgs, ratios):
                        c.drawImage(p, x, y0 + (rh - bh) / 2, r * bh, bh)
                        x += r * bh + 6
            # proceso
            ops = m['ops']
            rx, ry = X_RUTA + 3, y - 15
            for j, (op, res, t, st) in enumerate(ops):
                lab = ('TM-2P · ' + op) if res == 'TM-2P' else op
                done = st == 'COMPLETED'
                zero = float(t) == 0
                c.setFont('Helvetica-Bold', 8.5)
                wl = c.stringWidth(lab, 'Helvetica-Bold', 8.5) + 10 + (8 if done else 0)
                if rx + wl > W - M - 3:
                    rx, ry = X_RUTA + 3, ry - 22
                c.setFillColor(HexColor('#e8f5e9') if done else white)
                c.setStrokeColor(RED if zero else (GREEN if done else NAVY))
                c.roundRect(rx, ry - 4, wl, 14, 3, fill=1, stroke=1)
                c.setFillColor(NAVY); c.drawString(rx + 5, ry, lab)
                if done:
                    c.setStrokeColor(GREEN); c.setLineWidth(1.3)
                    cx = rx + wl - 10
                    c.line(cx, ry + 3, cx + 2, ry); c.line(cx + 2, ry, cx + 6, ry + 6)
                    c.setLineWidth(1)
                c.setFont('Helvetica', 6.5); c.setFillColor(RED if zero else GREY)
                c.drawCentredString(rx + wl / 2, ry - 11, '%d s' % float(t))
                rx += wl
                if j < len(ops) - 1:
                    c.setFillColor(GREY); c.setFont('Helvetica', 9)
                    c.drawString(rx + 2, ry, '›'); rx += 11
            c.setFillColor(GREY); c.setFont('Helvetica', 7.5)
            c.drawString(X_RUTA + 3, ry - 23, 'Plano: ' + (ci.get('plano') or '—'))
            if obs:
                c.setFillColor(RED); c.setFont('Helvetica-Bold', 7.5)
                lines = simpleSplit('Revisar: ' + ' '.join(obs), 'Helvetica-Bold', 7.5, W - M - X_RUTA - 8)[:2]
                for k, ln in enumerate(lines):
                    c.drawString(X_RUTA + 3, ry - 33 - 9 * k, ln)
            c.setStrokeColor(HexColor('#d0d5dd')); c.setLineWidth(0.4)
            c.line(M, y0, W - M, y0)
            y = y0
        c.setStrokeColor(GREY); c.setLineWidth(0.4)
        c.line(X_IMG, top - 12, X_IMG, y); c.line(X_RUTA, top - 12, X_RUTA, y)
        c.setFillColor(GREY); c.setFont('Helvetica', 6.5)
        c.drawString(M, 10, 'DIMACO METALMECANICA · Renglón rojo = revisar · Recuadro rojo = operación con 0 s/pz · Verde = operación terminada · Planos: Dropbox MAFESA/Dibujos MAFESA')
        c.showPage()
    c.save()
    reg = [m['mo'] for m in nuevas if m['sku'] in cat]
    json.dump({'mos': reg, 'fs': a.fs, 'sin_recorte': [m['mo'] + ' ' + m['sku'] for m in nuevas if m['sku'] not in cat]},
              open(PEND, 'w'), ensure_ascii=False)
    print(nombre)
    for m in nuevas:
        print(' ', m['mo'], m['sku'], '| REVISAR: ' + ' '.join(allobs[m['mo']]) if allobs[m['mo']] else '')


def registrar(a):
    p = cargar(PEND, {'mos': []})
    e = cargar(ENV, {'mos': [], 'historial': []})
    nuevos = [x for x in p.get('mos', []) if x not in e['mos']]
    e['mos'] = sorted(set(e['mos']) | set(nuevos), key=lambda s: int(''.join(ch for ch in s if ch.isdigit()) or 0))
    e.setdefault('historial', []).append({'fs': p.get('fs'), 'mos': nuevos})
    json.dump(e, open(ENV, 'w'), ensure_ascii=False, indent=1)
    os.remove(PEND)
    print('registradas', len(nuevos))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('accion', choices=['armar', 'registrar'])
    ap.add_argument('--mos'); ap.add_argument('--out', default='/home/claude/dibujos')
    ap.add_argument('--fs', default=dt.datetime.now().strftime('%d-%m_%H-%M'))
    ap.add_argument('--stamp', default='')
    a = ap.parse_args()
    armar(a) if a.accion == 'armar' else registrar(a)
