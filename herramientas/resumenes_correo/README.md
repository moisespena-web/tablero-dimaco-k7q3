# Resúmenes de estaciones por correo → Katana (Moisés, 8-oct-2026)

(Historia: hasta el 14-oct-2026 Corte, Taladro, TM-2P y Doblez no se conectaban a Katana. Desde el 14-oct las 5 van en vivo; ver el candado.)

**CANDADO ANTI-DUPLICADO (Moisés, 14-oct-2026) — manda sobre las excepciones de abajo:** desde el 14-oct-2026 LAS 5 estaciones
(Corte, Taladro, TM-2P, Doblez y Limpieza) escriben EN VIVO a Katana y además siguen mandando su resumen por correo. Antes de aplicar
cualquier renglón (MO · estación · fecha) lee la nota (`additional_info`) y el estado de esa operación en Katana:
- Si la nota YA trae un segmento de esa estación con esa fecha (lo escribió el servidor en vivo o una corrida anterior) →
  NO se aplica nada; anota en el ledger el N del correo para que no se vuelva a revisar. Si el N del correo no coincide con
  lo que dice Katana, va como duda ("Katana dice X, el correo dice N"), nunca se suma.
- Si la operación ya está COMPLETED → no se toca.
- Solo si Katana NO tiene nada de esa estación en esa fecha se aplica con la regla normal (delta = N − aplicado).
Así, si Miguel o Cynthia no conectaron el teléfono ese día, el correo sí entra; y si sí conectaron, no se duplica.

**EXCEPCIÓN DOBLEZ EN VIVO (Moisés, 14-oct-2026):** desde el 14-oct-2026 la Estación Doblez (Miguel) también va EN VIVO a Katana.
Su correo "RESUMEN DOBLEZ" se revisa con el CANDADO ANTI-DUPLICADO de arriba (no se ignora a ciegas).

**EXCEPCIÓN LIMPIEZA EN VIVO (Moisés, 13-oct-2026):** desde el 13-oct-2026 la Estación Limpieza & SQA está conectada a Katana EN VIVO
(`PAUSA_KATANA=false`, la opera Cynthia en su iPhone): cada START / PAUSA / FIN ya escribe en Katana por el servidor de Cloudflare.
Su correo "RESUMEN LIMPIEZA" se revisa con el CANDADO ANTI-DUPLICADO de arriba: lo normal es que Katana ya lo tenga y no se aplique nada.
Lupita (Corte, Taladro, TM-2P, Limpieza) y Miguel (Doblez) mandan el **Resumen del turno** (botón 📋 Resumen → "Enviar a Ing. Moisés" → Mail)
a **moises.pena@dimaco-mx.com** dos veces al día (~11:45 y ~18:30). Las corridas de las 12:00, 17:00 y 22:00 lo pasan a Katana con esta regla.

## Formato del correo (texto)
```
RESUMEN CORTE · Operador · jueves 8 de octubre
MO-386 · Corte · 54 pz · 1 min · TERMINADO
MO-366 · Limpieza & SQA · 70 pz · 0 min          ← sin TERMINADO = avance parcial
Lapsos:
09:23–09:24 MO-386 · 1 min · 54 pz
```
El resumen es ACUMULADO del día: por estación usa solo el correo más nuevo de cada fecha. N = piezas del día de esa MO en esa estación.

## Qué correos buscar (Moisés, 11-oct-2026)
Busca con Gmail `RESUMEN Lapsos newer_than:4d` (últimos 4 días, NO solo 24 h): así entra lo que llegó en sábado, domingo o puente, cuando no corre ninguna tarea.
El ledger evita duplicar (delta = N − aplicado). Ignora resúmenes con fecha anterior al 08/10/2026.
Un resumen capturado después (fecha del correo ≠ día real) se aplica con el día que fije Moisés y se registra en el ledger bajo la fecha que trae el correo, para que no se vuelva a aplicar.

## Ledger `aplicado.json`
`{"AAAA-MM-DD": {"MO-xxx|Estación": piezas_ya_aplicadas_ese_día}}` — Estación = Corte | Taladro | TM-2P | Doblez | Limpieza.
Delta = N − aplicado. Si delta ≤ 0 → no se escribe nada. Después de aplicar, guarda N y haz commit ("Resúmenes aplicados <FS>"). Así el resumen de cierre (que trae todo el día) solo aplica lo que falta, y repetir un correo no duplica nada.

## Cómo se aplica (por MO y estación, solo si N > 0)
Operación = renglón de la MO cuyo resource es: Corte Mafesa · Taladro Mafesa · TM-2P (o Cuadrado Mafesa) · Doblez Mafesa · Limpieza & SQA.
1. **Estado**: TERMINADO → COMPLETED. Sin TERMINADO → PAUSED (solo si estaba NOT_STARTED o IN_PROGRESS). Nunca reabrir una COMPLETED. N = 0 → no tocar nada (arranques por error).
2. **Nota** (`additional_info`, solo el renglón de esa estación; el resto de la nota no se toca):
   - Sin renglón previo: `Corte: Operador 54/54 (08/10/2026)`
   - Con avance de días anteriores: `Corte: Operador 48 (07/10/2026) · 4 min 47 s + 2 (08/10/2026) = 50/50`
   - Ya hay segmento de HOY (de una corrida anterior): se REEMPLAZA su número por N (nunca se agrega otro segmento del mismo día).
   - Etiquetas: `Corte`, `Taladro`, `TM-2P (<operation_name>)` (ej. `TM-2P (CNC SLT)`), `Doblez`, `Limpieza`. Operador = el del encabezado del correo (si viene "—", usa "Operador").
   - **TM-2P SIN OPERADOR (Moisés, 11-oct-2026, fase de pruebas hasta el 11-nov-2026):** el renglón de TM-2P va sin nombre: `TM-2P (CNC Ø): 20/20 (10/10/2026)`. Las demás estaciones siguen con operador. Moisés decide el 11-nov si se regresan.
   - Tiempo (` · 1 h 25 min`) SOLO si los lapsos de esa MO no se traslapan con lapsos de otra MO en la misma estación; si se traslapan, sin tiempo.
3. **Verifica** cada escritura con api-read. Si una falla, detente con esa MO y repórtala.

## NO aplicar — reportar como duda
- La MO no existe, está DONE, o no tiene operación de esa estación (ej. 8-oct: Lupita tecleó en Taladro lo que era Doblez de MO-379).
- N > planned_quantity, o el total del día + días anteriores > planned_quantity.
- La estación queda ADELANTE de la anterior en la ruta (piezas > lo hecho en la operación anterior según su estado/nota), salvo que la anterior esté COMPLETED.
  Excepción conocida: Limpieza de una MO cuyo Doblez dice x/plan con x = plan − 1 se reporta igual como duda.

## Candado de cierre (DONE)
Si completar la operación dejaría TODAS las operaciones de la MO en COMPLETED, Katana cierra la MO sola (DONE) y mueve inventario/consumo.
NO la completes: déjala PAUSED con la nota x/x y repórtala como "lista para cerrar — confirma" (Moisés da el OK en el chat).

## Reporte
Si se aplicó algo o hubo dudas: Gmail send_message a moises.pena@dimaco-mx.com, asunto `Resúmenes de estaciones · DD/MM HH:MM`, cuerpo corto:
aplicado (MO · estación · pz · estado), dudas (MO · estación · por qué) y listas para cerrar. Si no hubo correos nuevos ni nada que aplicar: silencio.
