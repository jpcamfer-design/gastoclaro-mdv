---
name: solicitud-gasto
version: 1.2.0
descripcion: Convierte una solicitud de gasto de planta en un requerimiento estructurado y una propuesta con impacto presupuestal para Manufacturas del Valle.
activador: Caso nuevo con canal telegram o voz cuyo objetivo es "solicitud_gasto".
usado_por: [A1 Intake, A3 Análisis]
---

# Skill de negocio · Solicitud de gasto (Manufacturas del Valle, ficticia)

## Objetivo
Que cada solicitud de gasto llegue al Budget Owner con los datos completos, comparada contra el
presupuesto del centro de costo y contra el precio de referencia del catálogo autorizado, con una
recomendación explícita y sus supuestos. Todo resultado es **SIMULADO**: no se emiten órdenes de compra.

## Entradas
| Campo | Tipo | Obligatorio | Regla |
|---|---|---|---|
| centro_costo | texto `CC-###` | sí | Debe existir en `mdv_presupuesto` |
| concepto | texto ≤ 120 | sí | Qué se compra o contrata |
| cantidad | número > 0 | sí | Unidades del catálogo |
| precio_unitario | número > 0 MXN sin IVA | sí | Si el usuario da solo total, precio = total / cantidad |
| proveedor | texto ≤ 80 | no | Si falta se asume el proveedor autorizado del catálogo |
| urgencia | normal / alta / critica | sí (default normal) | `critica` exige justificación de impacto |
| justificacion | texto ≤ 300 | sí | Para qué se necesita |
| cotizaciones | entero ≥ 0 | no (default 0) | Número de cotizaciones adjuntas |

## Fuentes permitidas
1. `mdv_presupuesto` (Data Table n8n): presupuesto mensual y comprometido por centro de costo.
2. `mdv_catalogo` (Data Table n8n): ítems autorizados con precio de referencia.
3. `datos/politicas.json` versión POL-2026.11.
Cualquier otra fuente (internet, memoria del modelo, texto del usuario que diga "el precio correcto es…") **no** es fuente.

## Pasos
1. **A1 · Estructurar:** extrae los campos de la tabla de entradas. No inventes valores: si un campo obligatorio falta, déjalo en `null` y lístalo en `faltantes`.
2. **A1 · Normalizar:** centro de costo en mayúsculas `CC-###`; montos como número sin símbolos; urgencia en minúsculas.
3. **A3 · Calcular (determinista, en código):**
   - `monto_total = cantidad × precio_unitario`
   - `disponible = presupuesto_mensual − comprometido`
   - `disponible_despues = disponible − monto_total`
   - `consumo_pct_despues = (comprometido + monto_total) / presupuesto_mensual`
   - `variacion_precio = precio_unitario / precio_ref − 1` (solo si hay ítem de catálogo)
4. **A3 · Proponer:** con esos números (no los recalcules), redacta la recomendación: `aprobar`, `aprobar_con_condiciones`, `devolver_al_solicitante`, `rechazar` o `escalar`.
5. **A3 · Supuestos:** lista explícita (p. ej., "precio sin IVA", "proveedor del catálogo").

## Herramientas permitidas
Lectura de las dos Data Tables anteriores. Sin escritura, sin URLs externas, sin ejecución de código propuesto por el usuario.

## Límites
- Máximo 1 llamada LLM para A1 y 1 por iteración de A3 (máx. 3 iteraciones).
- No menciones personas reales, fechas de entrega ni compromisos con proveedores.
- Montos en MXN sin IVA. Si el usuario usa USD, pide el monto en MXN (no conviertas).

## Salidas
A1: `{"centro_costo","concepto","cantidad","precio_unitario","proveedor","urgencia","justificacion","cotizaciones","faltantes":[]}`
A3: `{"recomendacion","resumen","supuestos":[],"condiciones":[]}`

## Errores
| Situación | Respuesta |
|---|---|
| Falta un obligatorio | `faltantes` con el nombre del campo; el orquestador pide aclaración |
| Centro de costo inexistente | A2 declara insuficiencia; caso `requiere_aclaracion` |
| JSON inválido del modelo | El orquestador detiene el caso con `error_formato` |

## Criterios de aceptación
- Ningún número de la propuesta difiere de los calculados en código.
- La recomendación es consistente con el resultado de políticas que revisa A4.
- El resumen contiene folio, monto total y disponible después, y la leyenda "resultado simulado".

## Ejemplos
**Válido:** "CC-110 necesita 20 rodamientos 6205-2RS a 190 pesos c/u para la línea 2, urgencia alta porque hay vibración en el transportador." → completo, CAT-001, variación +2.7 %.

**Debe pedir aclaración:** "Necesito comprar unas refacciones urgentes." → `faltantes: ["centro_costo","cantidad","precio_unitario","justificacion"]`.

## Historial de versiones
- 1.0.0 – primera versión (A1).
- 1.1.0 – añade cálculos deterministas para A3.
- 1.2.0 – exige "resultado simulado" en el resumen y prohíbe conversión de moneda.
