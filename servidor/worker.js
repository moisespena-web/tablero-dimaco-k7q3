/*
 * DIMACO · Servidor de la app de piso TM-2P  (Cloudflare Worker)
 * ----------------------------------------------------------------
 * Guarda la llave de Katana para que nunca viaje a la tablet.
 *
 * Variables (Settings → Variables and Secrets del Worker):
 *   KATANA_API_KEY   (secreto)  llave de API de Katana
 *   CODIGO_TABLET    (secreto)  código que se teclea una sola vez en la tablet
 *   PINES            (secreto)  JSON con el PIN de cada operador, ej. {"Emiliano":"4821","Luis":"1937"}
 *   ORIGEN           (texto)    https://moisespena-web.github.io
 *   RECURSOS         (texto)    TM-2P,Cuadrado Mafesa        (opcional; éste es el valor por omisión)
 *
 * Rutas:
 *   GET  /estado       prueba de conexión con Katana
 *   GET  /operadores   nombres de operadores (sin PIN)
 *   GET  /cola         MOs abiertas con operación en la TM-2P, con ingredientes y ruta
 *   POST /pin          valida el PIN de un operador antes de arrancar
 *   POST /evento       START / PAUSA / FIN / COMPLETAR sobre la operación TM-2P (pide PIN)
 *
 * Reglas que respeta:
 *   - Solo toca operaciones cuyo recurso sea TM-2P (o el legado "Cuadrado Mafesa").
 *   - Nunca cierra MOs ni mueve inventario: eso lo sigue haciendo Cynthia.
 *   - No toca notas de la MO.
 */

const KATANA = 'https://api.katanamrp.com/v1';
const ABIERTOS = ['NOT_STARTED', 'IN_PROGRESS', 'PAUSED', 'BLOCKED'];
const MEM = new Map(); // caché en memoria del isolate: url -> {t, v}

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

    // Toda llamada necesita el código de la tablet
    if (!iguales(req.headers.get('X-Tablet') || '', env.CODIGO_TABLET || '')) {
      return json({ ok: false, error: 'Tablet no autorizada' }, 401);
    }
    if (!env.KATANA_API_KEY) return json({ ok: false, error: 'Falta KATANA_API_KEY en el servidor' }, 500);

    const k = katana(env.KATANA_API_KEY);
    const recursos = new Set((env.RECURSOS || 'TM-2P,Cuadrado Mafesa').split(',').map(s => s.trim()).filter(Boolean));

    try {
      if (req.method === 'GET' && ruta === '/estado') {
        await k.get('/operators?limit=1');
        return json({ ok: true, katana: true, hora: new Date().toISOString() });
      }
      if (req.method === 'GET' && ruta === '/operadores') {
        return json({ ok: true, operadores: Object.keys(pines(env)) });
      }
      if (req.method === 'GET' && ruta === '/cola') {
        return json({ ok: true, hora: new Date().toISOString(), mos: await cola(k, recursos) });
      }
      if (req.method === 'POST' && ruta === '/pin') {
        let b = {}; try { b = await req.json(); } catch (e) {}
        const P = pines(env), op = String(b.operador || '');
        return (P[op] && iguales(String(b.pin || ''), String(P[op]))) ? json({ ok: true }) : json({ ok: false, error: 'PIN incorrecto' }, 403);
      }
      if (req.method === 'POST' && ruta === '/evento') {
        let body;
        try { body = await req.json(); } catch (e) { return json({ ok: false, error: 'JSON inválido' }, 400); }
        const r = await evento(k, recursos, pines(env), body);
        return json(r, r.ok ? 200 : (r.status || 400));
      }
      return json({ ok: false, error: 'Ruta no encontrada' }, 404);
    } catch (e) {
      return json({ ok: false, error: String(e && e.message || e) }, 502);
    }
  },
};

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
        const msg = data && (data.message || data.name) || ('HTTP ' + r.status);
        const err = new Error('Katana ' + method + ' ' + path.split('?')[0] + ': ' + msg);
        err.status = r.status; err.data = data;
        throw err;
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
  async function todas(path) { // paginado
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

/* ---------------- Cola de la máquina ---------------- */
function esTM2P(row, recursos) { return recursos.has((row.resource_name || '').trim()); }

/* Mismo criterio que el tablero de TV: recurso TM-2P => "CNC"; paso "CNC…" en otra máquina => "Taladro" */
function normop(row, recursos) {
  const n = (row.operation_name || '').trim();
  if (esTM2P(row, recursos)) return 'CNC';
  if (n.toUpperCase().startsWith('CNC')) return 'Taladro';
  return n;
}

async function cola(k, recursos) {
  // 1) operaciones abiertas en la TM-2P
  const abiertas = [];
  for (const st of ABIERTOS) abiertas.push(...await k.todas('/manufacturing_order_operation_rows?status=' + st));
  const tm = abiertas.filter(r => !r.deleted_at && esTM2P(r, recursos));
  const moIds = [...new Set(tm.map(r => r.manufacturing_order_id))];

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
    const fila = ops.find(o => esTM2P(o, recursos) && o.status !== 'COMPLETED') || tm.find(o => o.manufacturing_order_id === id);
    const ingredientes = [];
    for (const rr of ((recD && recD.data) || []).filter(x => !x.deleted_at)) {
      let v = null;
      try { v = await k.getCache('/variants/' + rr.variant_id + '?extend=product_or_material', 6 * 3600e3); } catch (e) {}
      const pm = v && v.product_or_material || {};
      const porUnidad = num(rr.planned_quantity_per_unit);
      ingredientes.push({ sku: v && v.sku || '', nombre: pm.name || '', uom: pm.uom || '', porUnidad, total: +(porUnidad * num(mo.planned_quantity)).toFixed(3) });
    }
    const pm = variante && variante.product_or_material || {};
    mos.push({
      id: mo.id,
      mo: mo.order_no,
      sku: variante && variante.sku || '',
      nombre: pm.name || '',
      piezas: num(mo.planned_quantity),
      deadline: (mo.production_deadline_date || '').slice(0, 10),
      estadoMO: mo.status,
      notas: mo.additional_info || '',
      ruta: ops.map(o => ({ nombre: normop(o, recursos), paso: o.operation_name, recurso: o.resource_name, status: o.status })),
      op: {
        rowId: fila.id,
        paso: fila.operation_name,
        recurso: fila.resource_name,
        status: fila.status,
        planeado: num(fila.planned_time_parameter),
        tiempoReal: num(fila.total_actual_time),
        asignados: (fila.assigned_operators || []).map(o => o.name),
      },
      ingredientes,
    });
  }
  return mos;
}

/* ---------------- Eventos de la tablet ---------------- */
const ACCIONES = {
  start:     { status: 'IN_PROGRESS', suma: false },
  pausa:     { status: 'PAUSED',      suma: true  },
  fin:       { status: 'PAUSED',      suma: true  },  // terminó un tramo pero faltan piezas
  completar: { status: 'COMPLETED',   suma: true  },  // terminó todas las piezas de la operación
};

async function evento(k, recursos, PIN, b) {
  const acc = ACCIONES[b && b.accion];
  if (!acc) return { ok: false, error: 'Acción inválida' };
  const operador = String(b.operador || '');
  if (!PIN[operador] || !iguales(String(b.pin || ''), String(PIN[operador]))) return { ok: false, status: 403, error: 'PIN incorrecto' };
  const rowId = parseInt(b.rowId, 10);
  if (!rowId) return { ok: false, error: 'Falta la operación' };
  const seg = Math.max(0, Math.round(num(b.segundos)));
  if (seg > 16 * 3600) return { ok: false, error: 'Tiempo fuera de rango (más de 16 h en un tramo)' };

  const row = await k.get('/manufacturing_order_operation_rows/' + rowId);
  if (!row || row.deleted_at) return { ok: false, status: 404, error: 'La operación ya no existe en Katana' };
  if (!esTM2P(row, recursos)) return { ok: false, status: 403, error: 'Esa operación no es de la TM-2P' };
  const mo = await k.get('/manufacturing_orders/' + row.manufacturing_order_id);
  if (mo.status === 'DONE') return { ok: false, status: 409, error: mo.order_no + ' ya está cerrada en Katana' };
  if (row.status === 'COMPLETED' && b.accion !== 'completar') return { ok: false, status: 409, error: 'La operación ya está completada en Katana' };

  const actual = num(row.total_actual_time);
  const nuevo = acc.suma ? actual + seg : actual;

  // Reintento de un evento que ya se aplicó (la tablet perdió la respuesta): no sumar dos veces
  if (b.esperado != null && acc.suma && seg > 0 && Math.abs(actual - (num(b.esperado) + seg)) < 1 && row.status === acc.status) {
    return { ok: true, repetido: true, mo: mo.order_no, op: resumenFila(row) };
  }

  // el operador se identifica por su id de Katana (así no se duplica)
  let opId = null;
  try {
    const ops = await k.getCache('/operators?limit=250', 3600e3);
    const hit = ((ops && ops.data) || []).find(o => (o.operator_name || '').trim().toLowerCase() === operador.trim().toLowerCase());
    if (hit) opId = hit.id;
  } catch (e) {}
  const conOp = (lista) => {
    const out = (lista || []).map(o => ({ operator_id: o.operator_id }));
    const ya = (lista || []).some(o => (opId && o.operator_id === opId) || (o.name || '').toLowerCase() === operador.toLowerCase());
    if (!ya) out.push(opId ? { operator_id: opId } : { name: operador });
    return out;
  };

  // read-modify-write: se reenvían los campos de la operación tal como están, cambiando solo estado, tiempo y operadores
  const cuerpo = {
    manufacturing_order_id: row.manufacturing_order_id,
    status: acc.status,
    operation_id: row.operation_id,
    resource_id: row.resource_id,
    type: row.type,
    planned_time_parameter: num(row.planned_time_parameter),
    total_actual_time: nuevo,
    assigned_operators: conOp(row.assigned_operators),
    completed_by_operators: b.accion === 'completar' ? conOp(row.completed_by_operators) : (row.completed_by_operators || []).map(o => ({ operator_id: o.operator_id })),
  };
  if (row.cost_parameter != null) cuerpo.cost_parameter = num(row.cost_parameter);
  if (row.custom_fields) cuerpo.custom_fields = row.custom_fields;

  await k.patch('/manufacturing_order_operation_rows/' + rowId, cuerpo);

  // verificar contra Katana
  const despues = await k.get('/manufacturing_order_operation_rows/' + rowId);
  const bien = despues.status === acc.status && Math.abs(num(despues.total_actual_time) - nuevo) < 1;
  return bien
    ? { ok: true, mo: mo.order_no, op: resumenFila(despues) }
    : { ok: false, status: 502, error: 'Katana no guardó el cambio como se esperaba', op: resumenFila(despues) };
}

function resumenFila(r) {
  return { rowId: r.id, status: r.status, tiempoReal: num(r.total_actual_time), asignados: (r.assigned_operators || []).map(o => o.name), completadoPor: (r.completed_by_operators || []).map(o => o.name) };
}

/* ---------------- utilidades ---------------- */
function pines(env) { try { return JSON.parse(env.PINES || '{}'); } catch (e) { return {}; } }
function num(x) { const n = parseFloat(x); return isFinite(n) ? n : 0; }
function dormir(ms) { return new Promise(r => setTimeout(r, ms)); }
function iguales(a, b) { // comparación en tiempo constante
  if (!a || !b || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}
