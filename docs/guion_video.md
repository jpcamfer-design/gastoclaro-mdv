# Guion del video (≈5 min)

1. **Problema (30 s):** el Budget Owner aprueba gastos sin ver presupuesto ni precio de referencia. Decisión: aprobar, devolver, rechazar o escalar con evidencia.
2. **Arquitectura (45 s):** mostrar el orquestador en n8n (65 nodos): A1 → A2 → A3 ⇄ A4 → humano. El orquestador es código, no LLM.
3. **Demo Telegram (60 s):** `/nuevo CC-310 2 calibraciones de báscula a 4800…` → acuse → propuesta con simulador de cierre → botón ✅ → `/estado`.
4. **Loop de calidad (45 s):** panel → caja negra GAS-0008: V1 devuelta por el servidor, V2 aprobada, alerta POL-07 "con GAS-0007 suman $58,800".
5. **Seguridad (45 s):** inyección bloqueada con 0 llamadas (GAS-0010); límite de costo (GAS-0013); webhook sin clave = 403; validador bloquea datos inválidos en GitHub Actions.
6. **Voz (45 s):** agente ElevenLabs: "¿Por qué se rechazó GAS-0008?" y alta de GAS-0009 con confirmación. Briefing de voz de las 8:00.
7. **Costos y cierre (30 s):** caso normal $0.00048 USD medido; 1,000 casos ≈ $0.63. Limitaciones y qué aprendí.
