/*
 * DIMACO · Servidor de las Estaciones de piso (TM-2P y Doblez) · Cloudflare Worker
 * ------------------------------------------------------------------------------
 * Guarda la llave de Katana para que nunca viaje a la tablet ni al teléfono.
 *
 * Variables (Settings → Variables and Secrets del Worker):
 *   KATANA_API_KEY  (secreto)  llave de API de Katana
 *   CODIGO_TABLET   (secreto)  código del iPad de la Estación TM-2P (6 a 10 dígitos)
 *   CODIGO_DOBLEZ   (secreto)  código del teléfono de la Estación Doblez (6 a 10 dígitos)
 *   CODIGO_LASER    (secreto)  código del teléfono de la Estación Láser y Router (6 a 10 dígitos)
 *   CODIGO_LIMPIEZA (secreto)  código del teléfono de la Estación Limpieza & SQA (Cynthia) (6 a 10 dígitos)
 *   CODIGO_HABILITADO (secreto) código del teléfono de la Estación Habilitado (Corte Sierra, racks)
 *   CODIGO_CORTE    (secreto)  código del teléfono de la Estación Corte (Corte Mafesa)
 *   CODIGO_PINTURA  (secreto)  código del teléfono de la Estación Pintura
 *   CODIGO_VESTIDO  (secreto)  código del teléfono de la Estación Rotulado y Vestido
 *   CODIGO_ARMADO1  (secreto)  código del teléfono de la Estación Armado y Soldadura 1
 *   CODIGO_TALADRO  (secreto)  código del teléfono de la Estación Taladro (MAFESA)
 *   PINES           (secreto)  JSON con el PIN de cada operador de la TM-2P, ej. {"Emiliano":"4821"}
 *   ORIGEN          (texto)    https://moisespena-web.github.io   (opcional)
 *
 *   DROPBOX_URL     (secreto)  link compartido de la carpeta Dropbox "Dimaco/Tablero TV" (el mismo que usa GitHub)
 *
 * Rutas:  GET /estado · GET /operadores · GET /cola · POST /pin · POST /evento
 *         GET /tablero (público: {datos, aviso} más recientes de Dropbox) · GET /tablero/aviso
 *
 * Qué escribe en Katana (solo en la operación cuyo Resource es el de la estación):
 *   start      → IN_PROGRESS + operador asignado
 *   pausa/fin  → PAUSED + avance en las notas de la MO (regla de avance parcial):
 *                "TM-2P (CNC SLT): Emiliano 30/142 (01/10/2026) · 1 h 05 min 12 s"
 *                (Katana solo acepta total_actual_time cuando la operación está COMPLETED)
 *   completar  → COMPLETED + total_actual_time (tiempo acumulado) + completed_by
 *   Nunca cierra la MO ni mueve inventario (eso es de Cynthia). Solo toca SU renglón de las notas.
 */

const KATANA = 'https://api.katanamrp.com/v1';
const ABIERTOS = ['NOT_STARTED', 'IN_PROGRESS', 'PAUSED', 'BLOCKED'];
const MEM = new Map();
const ESTACIONES = {
  tm2p:   { nombre: 'TM-2P',  recursos: ['TM-2P', 'Cuadrado Mafesa'], etiqueta: r => 'TM-2P (' + (r.operation_name || '').trim() + ')', conPin: true },
  doblez: { nombre: 'Doblez', recursos: ['Doblez Mafesa'],            etiqueta: () => 'Doblez', conPin: false, operador: 'Miguel' },
  laser:  { nombre: 'Láser y Router', recursos: ['Corte Laser', 'Router'], etiqueta: r => (r.operation_name || '').trim() || 'Láser', conPin: false, operador: 'Luis' },
  limpieza: { nombre: 'Limpieza & SQA', recursos: ['Limpieza & SQA'], etiqueta: () => 'Limpieza', conPin: false, operador: 'Cynthia' },
  habilitado: { nombre: 'Habilitado', recursos: ['Corte Sierra'], etiqueta: () => 'Corte', conPin: false, operador: 'Mario' },
  corte:    { nombre: 'Corte', recursos: ['Corte Mafesa'], etiqueta: () => 'Corte', conPin: false, operador: 'Operador' },
  pintura:  { nombre: 'Pintura', recursos: ['Pintura'], etiqueta: () => 'Pintura', conPin: false, operador: 'Operador' },
  vestido:  { nombre: 'Rotulado y Vestido', recursos: ['Vestido', 'Colocación Dunnage'], etiqueta: () => 'Vestido', conPin: false, operador: 'Operador' },
  armado1:  { nombre: 'Armado y Soldadura 1', recursos: ['Armado y Soldadura'], etiqueta: () => 'Armado y Soldadura', conPin: false, operador: 'Operador' },
  taladro:  { nombre: 'Taladro', recursos: ['Taladro Mafesa', 'Ø'], etiqueta: () => 'Taladro', conPin: false, operador: 'Operador' },
};

export default {
  async fetch(req, env) {
    const origen = env.ORIGEN || 'https://moisespena-web.github.io';
    const cors = {
      'Access-Control-Allow-Origin': origen,
      'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type,X-Tablet',
      'Access-Control-Max-Age': '86400',
      'Vary': 'Origin',
    };
    const json = (obj, status = 200) =>
      new Response(JSON.stringify(obj), { status, headers: { ...cors, 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' } });
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });

    const url = new URL(req.url);
    const ruta = url.pathname.replace(/\/+$/, '') || '/';

    // --- Buzón del Tablero de TV (6-oct-2026): lee la carpeta Dropbox "Tablero TV" directo, sin esperar a GitHub ---
    if (req.method === 'GET' && (ruta === '/tablero' || ruta === '/tablero/aviso')) {
      try {
        const t = await tablero(env);
        if (!t) return json({ ok: false, error: 'Falta DROPBOX_URL o la carpeta no tiene datos' }, 503);
        return json(ruta === '/tablero' ? t : (t.aviso || {}));
      } catch (e) { return json({ ok: false, error: String(e && e.message || e) }, 502); }
    }

    const codigo = req.headers.get('X-Tablet') || '';
    let est = null;
    if (iguales(codigo, env.CODIGO_TABLET || '')) est = ESTACIONES.tm2p;
    else if (iguales(codigo, env.CODIGO_DOBLEZ || '')) est = ESTACIONES.doblez;
    else if (iguales(codigo, env.CODIGO_LASER || '')) est = ESTACIONES.laser;
    else if (iguales(codigo, env.CODIGO_LIMPIEZA || '')) est = ESTACIONES.limpieza;
    else if (iguales(codigo, env.CODIGO_HABILITADO || '')) est = ESTACIONES.habilitado;
    else if (iguales(codigo, env.CODIGO_CORTE || '')) est = ESTACIONES.corte;
    else if (iguales(codigo, env.CODIGO_PINTURA || '')) est = ESTACIONES.pintura;
    else if (iguales(codigo, env.CODIGO_VESTIDO || '')) est = ESTACIONES.vestido;
    else if (iguales(codigo, env.CODIGO_ARMADO1 || '')) est = ESTACIONES.armado1;
    else if (iguales(codigo, env.CODIGO_TALADRO || '')) est = ESTACIONES.taladro;
    if (!est) return json({ ok: false, error: 'Dispositivo no autorizado' }, 401);
    if (!env.KATANA_API_KEY) return json({ ok: false, error: 'Falta KATANA_API_KEY en el servidor' }, 500);

    const k = katana(env.KATANA_API_KEY);
    try {
      if (req.method === 'GET' && ruta === '/estado') {
        await k.get('/operators?limit=1');
        return json({ ok: true, katana: true, estacion: est.nombre, hora: new Date().toISOString() });
      }
      if (req.method === 'GET' && ruta === '/operadores') {
        return json({ ok: true, operadores: est.conPin ? Object.keys(pines(env)) : [est.operador] });
      }
      if (req.method === 'GET' && ruta === '/cola') {
        return json({ ok: true, hora: new Date().toISOString(), mos: await cola(k, est) });
      }
      if (req.method === 'POST' && ruta === '/pin') {
        let b = {}; try { b = await req.json(); } catch (e) {}
        return pinOk(est, env, b) ? json({ ok: true }) : json({ ok: false, error: 'PIN incorrecto' }, 403);
      }
      if (req.method === 'POST' && ruta === '/evento') {
        let body;
        try { body = await req.json(); } catch (e) { return json({ ok: false, error: 'JSON inválido' }, 400); }
        const r = await evento(k, est, env, body);
        return json(r, r.ok ? 200 : (r.status || 400));
      }
      return json({ ok: false, error: 'Ruta no encontrada' }, 404);
    } catch (e) {
      return json({ ok: false, error: String(e && e.message || e) }, 502);
    }
  },
};

function pinOk(est, env, b) {
  if (!est.conPin) return true;
  const P = pines(env), op = String(b.operador || '');
  return !!(P[op] && iguales(String(b.pin || ''), String(P[op])));
}

/* ---------------- Katana ---------------- */
function katana(key) {
  async function call(method, path, body) {
    for (let intento = 0; intento < 3; intento++) {
      const r = await fetch(KATANA + path, {
        method,
        headers: { Authorization: 'Bearer ' + key, Accept: 'application/json', ...(body ? { 'Content-Type': 'application/json' } : {}) },
        body: body ? JSON.stringify(body) : undefined,
      });
      if (r.status === 429) { await dormir(1500 * (intento + 1)); continue; }
      const txt = await r.text();
      let data = null;
      try { data = txt ? JSON.parse(txt) : null; } catch (e) { data = txt; }
      if (!r.ok) {
        const msg = data && ((data.error && data.error.message) || data.message || data.name) || ('HTTP ' + r.status);
        const err = new Error('Katana ' + method + ' ' + path.split('?')[0] + ': ' + msg);
        err.status = r.status; throw err;
      }
      return data;
    }
    throw new Error('Katana: demasiadas solicitudes, intenta en un minuto');
  }
  async function getCache(path, ttlMs) {
    const hit = MEM.get(path);
    if (hit && Date.now() - hit.t < ttlMs) return hit.v;
    const v = await call('GET', path);
    MEM.set(path, { t: Date.now(), v });
    return v;
  }
  async function todas(path) {
    const out = [];
    for (let page = 1; page <= 20; page++) {
      const sep = path.includes('?') ? '&' : '?';
      const d = await call('GET', path + sep + 'limit=250&page=' + page);
      const rows = (d && d.data) || [];
      out.push(...rows);
      if (rows.length < 250) break;
    }
    return out;
  }
  return { get: p => call('GET', p), patch: (p, b) => call('PATCH', p, b), getCache, todas };
}

/* ---------------- Cola de la estación ---------------- */
function esDeEst(row, est) { return est.recursos.includes((row.resource_name || '').trim()); }
function normop(row) {
  const n = (row.operation_name || '').trim(), r = (row.resource_name || '').trim();
  if (r === 'TM-2P' || r === 'Cuadrado Mafesa') return 'CNC';
  if (n.toUpperCase().startsWith('CNC')) return 'Taladro';
  return n;
}

async function cola(k, est) {
  const abiertas = [];
  for (const st of ABIERTOS) abiertas.push(...await k.todas('/manufacturing_order_operation_rows?status=' + st));
  const mias = abiertas.filter(r => !r.deleted_at && esDeEst(r, est));
  const moIds = [...new Set(mias.map(r => r.manufacturing_order_id))];
  const mos = [];
  for (const id of moIds) {
    const mo = await k.get('/manufacturing_orders/' + id);
    if (!mo || mo.deleted_at || mo.status === 'DONE') continue;
    const [opsD, recD, variante] = await Promise.all([
      k.get('/manufacturing_order_operation_rows?manufacturing_order_id=' + id + '&limit=250'),
      k.get('/manufacturing_order_recipe_rows?manufacturing_order_id=' + id + '&limit=250'),
      k.getCache('/variants/' + mo.variant_id + '?extend=product_or_material', 6 * 3600e3),
    ]);
    const ops = ((opsD && opsD.data) || []).filter(o => !o.deleted_at).sort((a, b) => (a.rank || 0) - (b.rank || 0));
    const fila = ops.find(o => esDeEst(o, est) && o.status !== 'COMPLETED') || mias.find(o => o.manufacturing_order_id === id);
    const ingredientes = [];
    for (const rr of ((recD && recD.data) || []).filter(x => !x.deleted_at)) {
      let v = null;
      try { v = await k.getCache('/variants/' + rr.variant_id + '?extend=product_or_material', 6 * 3600e3); } catch (e) {}
      const pm = v && v.product_or_material || {};
      const porUnidad = num(rr.planned_quantity_per_unit);
      ingredientes.push({ sku: v && v.sku || '', nombre: pm.name || '', uom: pm.uom || '', porUnidad, total: +(porUnidad * num(mo.planned_quantity)).toFixed(3) });
    }
    const pm = variante && variante.product_or_material || {};
    const av = leerAvance(mo.additional_info, est.etiqueta(fila));
    mos.push({
      id: mo.id, mo: mo.order_no, sku: variante && variante.sku || '', nombre: pm.name || '',
      piezas: num(mo.planned_quantity), entregadas: num(mo.completed_quantity), hechas: av ? av.pz : 0,   // 5-oct-2026: la estación muestra piezas − entregadas
      deadline: (mo.production_deadline_date || '').slice(0, 10), estadoMO: mo.status,
      notas: mo.additional_info || '',
      ruta: ops.map(o => ({ nombre: normop(o), paso: o.operation_name, recurso: o.resource_name, status: o.status })),
      op: { rowId: fila.id, paso: fila.operation_name, recurso: fila.resource_name, status: fila.status,
            planeado: num(fila.planned_time_parameter), tiempoReal: av ? av.seg : num(fila.total_actual_time),
            asignados: (fila.assigned_operators || []).map(o => o.name) },
      ingredientes,
    });
  }
  return mos;
}

/* ---------------- Avance en las notas de la MO ---------------- */
// Renglón: "<etiqueta>: <operadores> <pz>/<total> (<dd/mm/aaaa>) · <h> h <mm> min <ss> s"
function escRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
function reLinea(etq) { return new RegExp('^' + escRe(etq) + ':\\s*(.*?)\\s+(\\d+)\\/(\\d+)\\s*\\(([^)]*)\\)(.*)$'); }
function leerAvance(notas, etq) {
  const lines = String(notas || '').split('\n');
  for (const l of lines) {
    const m = l.trim().match(reLinea(etq));
    if (!m) continue;
    const resto = m[5] || '';
    const h = (resto.match(/(\d+)\s*h\b/) || [])[1], mi = (resto.match(/(\d+)\s*min/) || [])[1], s = (resto.match(/(\d+)\s*s\b/) || [])[1];
    return { ops: m[1].split(',').map(x => x.trim()).filter(Boolean), pz: +m[2], total: +m[3], fecha: m[4], seg: (+h || 0) * 3600 + (+mi || 0) * 60 + (+s || 0) };
  }
  return null;
}
function durTxt(seg) {
  seg = Math.round(seg); const h = Math.floor(seg / 3600), m = Math.floor(seg % 3600 / 60), s = seg % 60;
  return (h ? h + ' h ' + String(m).padStart(2, '0') + ' min' : m + ' min') + (s ? ' ' + s + ' s' : '');
}
function fechaMX(d) {
  const p = {}; new Intl.DateTimeFormat('en-GB', { timeZone: 'America/Mexico_City', day: '2-digit', month: '2-digit', year: 'numeric' })
    .formatToParts(d).forEach(x => p[x.type] = x.value);
  return p.day + '/' + p.month + '/' + p.year;
}
function escribirAvance(notas, etq, av) {
  const linea = etq + ': ' + av.ops.join(', ') + ' ' + av.pz + '/' + av.total + ' (' + av.fecha + ')' + (av.seg > 0 ? ' · ' + durTxt(av.seg) : '');
  const lines = String(notas || '').split('\n');
  const re = reLinea(etq);
  const i = lines.findIndex(l => re.test(l.trim()));
  if (i >= 0) lines[i] = linea; else lines.push(linea);
  return lines.filter((l, j) => l !== '' || j < lines.length - 1).join('\n').replace(/^\n+/, '');
}

/* ---------------- Eventos ---------------- */
const ACCIONES = { start: 'IN_PROGRESS', pausa: 'PAUSED', fin: 'PAUSED', completar: 'COMPLETED' };

async function evento(k, est, env, b) {
  const status = ACCIONES[b && b.accion];
  if (!status) return { ok: false, error: 'Acción inválida' };
  const operador = est.conPin ? String(b.operador || '') : est.operador;
  if (!pinOk(est, env, { operador, pin: b.pin })) return { ok: false, status: 403, error: 'PIN incorrecto' };
  const rowId = parseInt(b.rowId, 10);
  if (!rowId) return { ok: false, error: 'Falta la operación' };
  const seg = Math.max(0, Math.round(num(b.segundos)));
  if (seg > 16 * 3600) return { ok: false, error: 'Tiempo fuera de rango (más de 16 h en un lapso)' };
  const pzLapso = Math.max(0, Math.round(num(b.piezas)));

  const row = await k.get('/manufacturing_order_operation_rows/' + rowId);
  if (!row || row.deleted_at) return { ok: false, status: 404, error: 'La operación ya no existe en Katana' };
  if (!esDeEst(row, est)) return { ok: false, status: 403, error: 'Esa operación no es de la Estación ' + est.nombre };
  const mo = await k.get('/manufacturing_orders/' + row.manufacturing_order_id);
  if (mo.status === 'DONE') return { ok: false, status: 409, error: mo.order_no + ' ya está cerrada en Katana' };
  if (row.status === 'COMPLETED') {
    if (b.accion === 'completar') return { ok: true, repetido: true, mo: mo.order_no, op: resumen(row, null) };
    return { ok: false, status: 409, error: 'La operación ya está completada en Katana' };
  }

  const etq = est.etiqueta(row);
  // 5-oct-2026: si la estación aún no tiene renglón y la MO ya tiene entregas parciales, el avance arranca en lo entregado
  // (las notas cuentan sobre la MO completa: x/planeadas)
  const prev = leerAvance(mo.additional_info, etq) || { ops: [], pz: num(mo.completed_quantity), total: num(mo.planned_quantity), fecha: '', seg: 0 };
  const suma = b.accion !== 'start';

  // reintento de un evento ya aplicado (el dispositivo perdió la respuesta): no sumar dos veces
  if (suma && b.esperado != null && seg > 0 && row.status === status && Math.abs(prev.seg - (num(b.esperado) + seg)) < 2) {
    return { ok: true, repetido: true, mo: mo.order_no, op: resumen(row, prev) };
  }

  let opId = null;
  try {
    const ops = await k.getCache('/operators?limit=250', 3600e3);
    const hit = ((ops && ops.data) || []).find(o => (o.operator_name || o.name || '').trim().toLowerCase() === operador.trim().toLowerCase());
    if (hit) opId = hit.id;
  } catch (e) {}
  const conOp = lista => {
    const out = (lista || []).map(o => ({ operator_id: o.operator_id }));
    const ya = (lista || []).some(o => (opId && o.operator_id === opId) || (o.name || '').toLowerCase() === operador.toLowerCase());
    if (!ya && opId) out.push({ operator_id: opId });
    return out;
  };

  // 1) avance en las notas (pausa / fin / completar)
  let nuevo = prev;
  if (suma) {
    const total = num(mo.planned_quantity);
    nuevo = {
      ops: prev.ops.includes(operador) ? prev.ops : prev.ops.concat(operador),
      pz: b.accion === 'completar' ? total : Math.min(total, prev.pz + pzLapso),
      total, fecha: fechaMX(new Date()), seg: prev.seg + seg,
    };
    if (seg > 0 || pzLapso > 0 || b.accion === 'completar') {
      const moAhora = await k.get('/manufacturing_orders/' + mo.id);   // releer: Cynthia pudo editar las notas
      await k.patch('/manufacturing_orders/' + mo.id, { additional_info: escribirAvance(moAhora.additional_info, etq, nuevo) });
    }
  }

  // 2) la operación: se reenvían sus campos tal como están (sin manufacturing_order_id)
  const cuerpo = {
    status,
    operation_id: row.operation_id,
    resource_id: row.resource_id,
    type: row.type,
    planned_time_parameter: num(row.planned_time_parameter),
    assigned_operators: conOp(row.assigned_operators),
    completed_by_operators: status === 'COMPLETED' ? conOp(row.completed_by_operators) : (row.completed_by_operators || []).map(o => ({ operator_id: o.operator_id })),
  };
  if (status === 'COMPLETED') cuerpo.total_actual_time = Math.round(nuevo.seg);
  if (row.cost_parameter != null) cuerpo.cost_parameter = num(row.cost_parameter);
  if (row.custom_fields) cuerpo.custom_fields = row.custom_fields;
  if (status !== row.status || status === 'COMPLETED' || b.accion === 'start') {
    await k.patch('/manufacturing_order_operation_rows/' + rowId, cuerpo);
  }

  const despues = await k.get('/manufacturing_order_operation_rows/' + rowId);
  const bien = despues.status === status && (status !== 'COMPLETED' || Math.abs(num(despues.total_actual_time) - nuevo.seg) < 2);
  return bien
    ? { ok: true, mo: mo.order_no, op: resumen(despues, nuevo) }
    : { ok: false, status: 502, error: 'Katana no guardó el cambio como se esperaba', op: resumen(despues, nuevo) };
}

function resumen(r, av) {
  return { rowId: r.id, status: r.status, tiempoReal: av ? av.seg : num(r.total_actual_time), hechas: av ? av.pz : 0,
           asignados: (r.assigned_operators || []).map(o => o.name), completadoPor: (r.completed_by_operators || []).map(o => o.name) };
}

/* ---------------- utilidades ---------------- */
function pines(env) { try { return JSON.parse(env.PINES || '{}'); } catch (e) { return {}; } }
function num(x) { const n = parseFloat(x); return isFinite(n) ? n : 0; }
function dormir(ms) { return new Promise(r => setTimeout(r, ms)); }
function iguales(a, b) {
  if (!a || !b || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}


/* ---------- Buzón del Tablero de TV ----------
   Descarga la carpeta compartida de Dropbox como ZIP (dl=1), toma el datos-*.json más nuevo y el aviso-*.json más nuevo
   que sea JSON válido (si no hay aviso-*, usa el aviso que trae el datos). Mismo criterio que el robot de GitHub.
   Se guarda 20 s en la caché del Worker para no pegarle a Dropbox en cada consulta de la TV. */
async function tablero(env) {
  if (!env.DROPBOX_URL) return null;
  const cache = caches.default, key = new Request('https://tablero.cache/v1');
  const hit = await cache.match(key);
  if (hit) return await hit.json();
  let u = String(env.DROPBOX_URL).replace('dl=0', 'dl=1');
  if (!/[?&]dl=1/.test(u)) u += (u.includes('?') ? '&' : '?') + 'dl=1';
  const r = await fetch(u, { redirect: 'follow' });
  if (!r.ok) throw new Error('Dropbox respondió ' + r.status);
  const files = await leerZip(new Uint8Array(await r.arrayBuffer()), n => /(^|\/)(datos|aviso)-[^/]*\.json$/.test(n));
  const base = n => n.split('/').pop();
  const datosN = Object.keys(files).filter(n => base(n).startsWith('datos-')).sort((a, b) => base(a) < base(b) ? -1 : 1);
  const avisoN = Object.keys(files).filter(n => base(n).startsWith('aviso-')).sort((a, b) => base(a) < base(b) ? 1 : -1);
  let datos = null, avisoDatos = null, archivo = null;
  for (let i = datosN.length - 1; i >= 0; i--) {
    try { const j = JSON.parse(files[datosN[i]]); if (j && j.datos && j.datos.rows && j.datos.rows.length) { datos = j.datos; avisoDatos = j.aviso || null; archivo = base(datosN[i]); break; } } catch (e) {}
  }
  if (!datos) return null;
  let aviso = null;
  for (const n of avisoN) { try { aviso = JSON.parse(files[n]); break; } catch (e) {} }
  if (!aviso && !avisoN.length) aviso = avisoDatos;
  delete datos.requisicion; (datos.rows || []).forEach(x => { delete x.ocs; });   // la página es pública
  const out = { datos, aviso: aviso || {}, fuente: archivo, leido: new Date().toISOString() };
  await cache.put(key, new Response(JSON.stringify(out), { headers: { 'Content-Type': 'application/json', 'Cache-Control': 'max-age=20' } }));
  return out;
}

async function leerZip(b, quiero) {
  const dv = new DataView(b.buffer, b.byteOffset, b.byteLength), td = new TextDecoder();
  let e = -1;
  for (let i = b.length - 22; i >= Math.max(0, b.length - 70000); i--) { if (dv.getUint32(i, true) === 0x06054b50) { e = i; break; } }
  if (e < 0) throw new Error('ZIP de Dropbox inválido');
  const n = dv.getUint16(e + 10, true); let p = dv.getUint32(e + 16, true); const out = {};
  for (let k = 0; k < n; k++) {
    if (dv.getUint32(p, true) !== 0x02014b50) break;
    const metodo = dv.getUint16(p + 10, true), csize = dv.getUint32(p + 20, true);
    const nl = dv.getUint16(p + 28, true), xl = dv.getUint16(p + 30, true), cl = dv.getUint16(p + 32, true), loc = dv.getUint32(p + 42, true);
    const nombre = td.decode(b.subarray(p + 46, p + 46 + nl));
    p += 46 + nl + xl + cl;
    if (!quiero(nombre)) continue;
    const ini = loc + 30 + dv.getUint16(loc + 26, true) + dv.getUint16(loc + 28, true), crudo = b.subarray(ini, ini + csize);
    let datos;
    if (metodo === 0) datos = crudo;
    else if (metodo === 8) datos = new Uint8Array(await new Response(new Blob([crudo]).stream().pipeThrough(new DecompressionStream('deflate-raw'))).arrayBuffer());
    else continue;
    out[nombre] = td.decode(datos);
  }
  return out;
}
