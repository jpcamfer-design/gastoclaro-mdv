# Loop 1 · Calidad de negocio (A3 ⇄ A4)

**Secuencia:** generar (A3) → medir campos, cálculos y fuentes (A4 + servidor) → diagnosticar → corregir (A3 vN+1) → validar → liberar solo si supera los criterios.

| Elemento | Definición |
|---|---|
| Entrada | Requerimiento A1, datos A2, cálculos deterministas, propuesta A3 vN |
| Responsable | A4 Revisor (LLM) + control del servidor en el nodo `A4 vN · veredicto` |
| Criterios de salida (todos) | 1) recomendación ∈ recomendaciones válidas según POL-01…06; 2) resumen incluye folio; 3) resumen incluye "resultado simulado"; 4) ninguna cifra del resumen es ajena a los cálculos; 5) al menos un supuesto; 6) veredicto LLM = aprobado |
| Máximo de iteraciones | **3** (v1, v2, v3). Justificación: con temperatura 0, si en 3 versiones no converge, el problema no es redacción sino datos → mejor detener |
| Tiempo límite | 30 s por llamada al modelo (`timeout` del nodo) + 1 reintento técnico |
| Presupuesto | Lo controla el Loop 2 antes de cada llamada |
| Acción de retorno | Correcciones concretas de A4 se inyectan en el prompt de A3 vN+1 |
| Estado al agotar | `detenido_calidad` → se notifica al solicitante; no se pide aprobación humana |

**Implementación en n8n:** desenrollado en tres pares de nodos (`A3 v1/v2/v3 · …`, `A4 v1/v2/v3 · …`) unidos por `¿Liberar tras v1?` y `¿Liberar tras v2?`. Se desenrolló a propósito: cada versión queda como nodo visible en la ejecución y en la traza, y es imposible un ciclo infinito.

**Override del servidor:** si el LLM revisor responde `aprobado` pero algún criterio verificable falla, el código fuerza `devuelto` y registra `revision_devuelto_override_servidor`. Ninguna instrucción del usuario cambia este código.

**Evidencia V1 → V2:** ver `evidencias/` (caso con precio 24 % sobre referencia: A3 v1 recomienda `aprobar`, A4 devuelve por POL-03, A3 v2 recomienda `devolver_al_solicitante`).

## Autoevaluación (0–4)
| Aspecto | Puntos | Razón |
|---|---|---|
| Claridad o propósito | 4 | Criterios binarios y verificables por código |
| Contexto o secuencia | 4 | Orden fijo A3→A4, correcciones viajan en el estado |
| Evidencia | 4 | Traza por versión con veredicto y correcciones |
| Control o retorno | 4 | Máx. 3, override servidor, estado final explícito |
| Utilidad | 3 | Evita aprobaciones incoherentes; aumenta costo cuando itera |
| **Total** | **19/20** | |
