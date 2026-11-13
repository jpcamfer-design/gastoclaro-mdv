# GastoClaro · Contralor de gastos con IA para una planta de manufactura

> **Empresa ficticia** (Manufacturas del Valle S.A.) · **Modo SIMULADO**: nunca se emiten órdenes de compra ni pagos.
> Proyecto final individual · AI Tools · Tec de Monterrey · Juan Pablo Camacho Fernández

**Panel público:** https://jpcamfer-design.github.io/gastoclaro-mdv/ · **Bot:** Telegram (`/nuevo`, `/estado GAS-0001`) · **Voz:** widget ElevenLabs en el panel

## Problema y decisión
Las áreas de planta piden gastos por chat o correo. El Budget Owner aprueba sin ver cuánto presupuesto queda, sin comparar contra un precio de referencia y sin rastro. **Decisión que apoya el sistema:** aprobar, devolver, rechazar o escalar una solicitud de gasto con evidencia, antes de comprometer presupuesto.

## Qué lo hace distinto
| Capacidad | Qué hace | Dónde |
|---|---|---|
| 🧠 Orquestador + 4 agentes | A1 Intake → A2 Datos → A3 Análisis → A4 Revisor → humano | `n8n/2_orquestador.json` |
| 🚨 Detector de fraccionamiento (POL-07) | Detecta compras partidas para evadir el umbral de cotizaciones (mismo CC + ítem/proveedor, 7 días) | nodo `A4 vN · preparar` |
| 📈 Simulador de cierre de mes | Consumo hoy → si apruebas → cierre proyectado y día de agotamiento, con semáforo | nodo `A2 · verificar fuentes` |
| 🛡️ Servidor como autoridad | Si el revisor LLM aprueba algo incorrecto o **alucina** una falla, el código lo corrige y lo deja en la traza | nodo `A4 vN · veredicto` |
| 🎙️ Briefing de voz diario | 8:00 CDMX: nota de voz (ElevenLabs) en Telegram con pendientes, riesgos y alertas | `n8n/4_programadas_exportacion.json` |
| 🔎 Modo auditor por voz | "¿Por qué se rechazó GAS-0008?" → recorrido real de la traza | `n8n/3_voz_elevenlabs.json` |
| ⏯️ Caja negra | Repetición animada de un caso en el panel con costo por paso | `web/index.html` |

## Arquitectura
```
Telegram ─┐                                  ┌─ mdv_casos / mdv_trazas / mdv_eventos (n8n Data Tables, privado)
Voz ──────┼─> n8n: deduplica → permisos → ORQUESTADOR ─┤
          │      A1 → A2 → A3 ⇄ A4 (máx 3) → aprobación humana (botones, 24 h)
          │                                  └─ exportación sanitizada (webhook con clave)
Programadas: cada hora vence aprobaciones · 8:00 briefing de voz
GitHub Actions (push / manual / cada 6 h): exporta → valida (validate.py) → publica Pages
```

## Estructura
| Carpeta | Contenido |
|---|---|
| `n8n/` | 4 workflows exportados **sin secretos** (marcadores `__DT_*__`, `__CRED_*__`) |
| `scripts/` | `build_n8n.py` (genera los workflows), `validate.py` (controles de publicación) |
| `skills/` | `solicitud-gasto` (negocio) y `revision-politica` (calidad y seguridad) |
| `loops/` | Loop de calidad A3⇄A4 y loop de seguridad y costo |
| `agentes/` | Instrucciones y contratos JSON de los 5 roles |
| `datos/` | Presupuesto, catálogo y políticas POL-01…07 (ficticios) |
| `tests/` | Matriz P01–P14 con resultados |
| `costos/` | Registro por llamada, proyecciones y supuestos |
| `web/` | Panel de GitHub Pages |
| `evidencias/` | Capturas por requisito |

## Reproducir
1. Crear en n8n las Data Tables con las columnas de `agentes/contratos.md` y cargar `datos/*.csv`.
2. Crear credenciales (nombres en `.env.example`): Telegram, 2 Header Auth y ElevenLabs.
3. Importar `n8n/*.json`, reemplazar marcadores por los IDs propios y publicar: primero el orquestador.
4. En GitHub: Settings → Pages → Source: GitHub Actions; secretos `N8N_EXPORT_URL` y `N8N_EXPORT_KEY`.
5. Agente de ElevenLabs: herramienta webhook `POST /webhook/gastoclaro-voz` con encabezado `X-GastoClaro-Key` (secreto del workspace).

## Seguridad
Secretos solo en n8n Credentials, GitHub Secrets y secretos de ElevenLabs. El repo y el panel no contienen chats, nombres ni claves; `validate.py` bloquea la publicación si detecta alguno.
