# Loop 2 · Seguridad y costo (antes de cada llamada al modelo)

**Secuencia:** evaluar permisos y presupuesto → ejecutar paso autorizado → registrar consumo → revisar límite y resultado → continuar o detener.

| Elemento | Definición |
|---|---|
| Entrada | Estado del caso con `uso` (llamadas, tokens estimados, USD) y `limites` |
| Responsable | Orquestador (función `control()` en cada nodo `· preparar`) + IF `Presupuesto Ax` |
| Permisos | Antes del loop: chat en `mdv_usuarios`, rol `solicitante`/`ambos` para crear, `aprobador`/`ambos` para decidir |
| Límites por caso | 8 llamadas LLM · 12 000 tokens estimados · USD 0.01 · reserva de salida 500 tokens |
| Regla | `llamadas < 8` **y** `tokens_usados + tokens_prompt + reserva ≤ límite` **y** `usd + costo_previsto ≤ 0.01` |
| Registro | `registrarLLM()` suma tokens estimados (caracteres/4) y costo con tarifa de lista; traza `llm_ok` por llamada |
| Máximo de iteraciones | 8 evaluaciones (una por posible llamada: A1, A2, A3×3, A4×3 = 8) |
| Tiempo límite | 30 s por llamada, 1 reintento |
| Acción al exceder | No se llama al modelo; traza `detenido_presupuesto`; estado final `detenido_presupuesto`; mensaje al usuario |
| Reconciliación | Los tokens **medidos** (tokenUsage reportado por el proveedor en la ejecución de n8n) se concilian en `costos/costos.csv` |

**Prueba P11:** con el límite forzado a 2 llamadas, GAS-0013 se detuvo después de A2 (`detenido_presupuesto`, 2 llamadas, ~$0.00017) sin llamar a A3.

## Autoevaluación (0–4)
| Aspecto | Puntos | Razón |
|---|---|---|
| Claridad o propósito | 4 | Regla numérica única y documentada |
| Contexto o secuencia | 4 | Se evalúa antes de cada llamada, nunca después |
| Evidencia | 4 | Trazas `presupuesto_ok` / `detenido_presupuesto` con cifras |
| Control o retorno | 4 | Detiene sin excepción; estado final explícito |
| Utilidad | 3 | Estimación por caracteres; se concilia con medido después |
| **Total** | **19/20** | |
