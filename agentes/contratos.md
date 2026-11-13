# Contratos de entrada y salida (JSON)

Todos los roles comparten un **estado de caso** que viaja por el flujo de n8n. Cada rol lee solo lo que necesita y agrega su salida. Ningún contrato guarda secretos ni razonamiento interno: solo decisiones, validaciones y resultados observables.

## Entrada mínima del caso (de Telegram o voz → orquestador)
```json
{ "canal": "telegram | voz | prueba", "chat_id": "seudónimo interno (no se publica)", "usuario": "alias autorizado",
  "texto": "solicitud en lenguaje natural", "limite_tokens": 12000, "limite_llamadas": 8 }
```
El orquestador agrega: `caso_id` (GAS-####), `modo: "SIMULADO"`, `objetivo: "solicitud_gasto"`, `limites`, `uso`, `plan`, `trazas[]`.

## Salida mínima por paso (fila de `mdv_trazas`)
```json
{ "caso_id": "GAS-0007", "paso": 12, "rol": "A3 Análisis", "version": 1, "estado": "propuesta_v1",
  "skill": "solicitud-gasto@1.2.0", "entrada": "≤480 car.", "salida": "≤1400 car. (JSON del rol)",
  "tokens_in_est": 431, "tokens_out_est": 88, "costo_est_usd": 0.00011745, "duracion_ms": 1730, "ejecucion_id": "42" }
```
`ejecucion_id` liga la fila con el log de n8n, donde está el consumo **medido** (tokenUsage) que se concilia en `costos/costos.csv`.

## Por rol
| Rol | Recibe | Devuelve (JSON) | Validación del servidor |
|---|---|---|---|
| **Orquestador** | entrada mínima | `plan`, `estado`, `limites`, `detener{motivo,paso}`, mensaje final | guardrails de entrada (longitud, inyección, enmascarado), presupuesto antes de cada llamada, estado final único |
| **A1 Intake** | `texto` | `{centro_costo, concepto, cantidad, precio_unitario, proveedor, urgencia, justificacion, cotizaciones, faltantes[]}` | regex `CC-###`, números > 0, urgencia en catálogo, recalcula `faltantes` |
| **A2 Datos** | `req.concepto`, catálogo autorizado | `{item_id \| SIN_COINCIDENCIA, confianza, categoria_restringida, razon}` | el `item_id` debe existir en `mdv_catalogo`; confianza ≥ 0.5; presupuesto leído de `mdv_presupuesto` (no del modelo) |
| **A3 Análisis** | `req`, `datos`, `calc` (determinista), correcciones previas | `{recomendacion, resumen, supuestos[], condiciones[]}` | cálculos hechos en código; A3 solo redacta |
| **A4 Revisor** | propuesta A3 + `politicas[]` (código) | `{veredicto: aprobado\|devuelto, correcciones[], advertencias[]}` | override: recomendación ∈ esperado, folio, "resultado simulado", cifras permitidas, ≥1 supuesto |
| **Aprobación humana** | botón `d\|ap\|GAS-####\|v` o `d\|rc\|…` | `estado: aprobado_simulado \| rechazado_aprobador` | rol aprobador, estado `pendiente_aprobacion`, versión vigente, no expirado (24 h) |

## Estados finales posibles
`pendiente_aprobacion`, `aprobado_simulado`, `rechazado_aprobador`, `rechazado_politica`, `devuelto_solicitante`, `escalado_gerencia`, `requiere_aclaracion`, `rechazado_entrada`, `detenido_presupuesto`, `detenido_calidad`, `error_controlado`, `expirado`.
