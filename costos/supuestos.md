# Costos de IA · supuestos y método

- Modelo: gpt-4o-mini vía Gateway credits de n8n. Para el alumno el costo fue $0 (créditos incluidos); se calcula el **equivalente a precio de lista**: entrada 0.15 USD / 1M tokens, salida 0.60 USD / 1M tokens (consultado 2026-11-04).
- **Medido:** `costos.csv` sale de los logs de ejecución de n8n (tokenUsage de cada nodo del modelo), 23 llamadas, casos GAS-0006 a GAS-0009 y GAS-0012. Las ejecuciones anteriores ya no estaban en el historial.
- **Estimado en el flujo:** caracteres/4. Queda 9–16 % por debajo del medido (promedio 12 %), por eso las proyecciones usan el medido.
- Caso normal: 4 llamadas, ~$0.00048 USD. Con 3 revisiones: 8 llamadas, ~$0.00106 USD.
- Proyección (mezcla 60/25/15 %, supuesto): 100 casos ≈ $0.06, 1,000 ≈ $0.63, 10,000 ≈ $6.35 USD al mes. Ver `costos.xlsx` (fórmulas vivas).
- Límite duro por caso: 8 llamadas / 12,000 tokens / 0.01 USD. Probado en P11.
- No incluido: plan de n8n Cloud (prueba gratis), ElevenLabs (plan gratis, minutos limitados), GitHub (gratis).
