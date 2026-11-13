#!/usr/bin/env python3
"""Controles previos a la publicación de GastoClaro en GitHub Pages.

Falla (exit 1) si:
  1. faltan archivos obligatorios del sitio o del proyecto;
  2. la exportación web/data/casos.json no cumple el esquema;
  3. un cálculo determinista no cuadra (monto_total = cantidad x precio_unitario, variación de precio);
  4. aparece un estado o veredicto fuera del catálogo permitido;
  5. el sitio publicado contiene posibles secretos o identificadores personales;
  6. las skills no tienen las secciones exigidas por la guía.
Uso: python3 scripts/validate.py [ruta_casos.json]
"""
import json, re, sys, pathlib
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]
errores, avisos = [], []

def err(m): errores.append(m)

# 1. Archivos obligatorios
for f in ["web/index.html", "web/data/casos.json", "datos/politicas.json", "datos/presupuesto.csv", "datos/catalogo.csv",
          "skills/solicitud-gasto/SKILL.md", "skills/revision-politica/SKILL.md", "loops/loop_calidad.md", "loops/loop_seguridad_costo.md",
          "README.md", ".env.example"]:
    if not (ROOT / f).exists():
        err(f"Falta archivo obligatorio: {f}")

# 2. Esquema de la exportación
ruta = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "web/data/casos.json"
try:
    data = json.loads(ruta.read_text(encoding="utf-8"))
except Exception as e:
    err(f"casos.json ilegible: {e}"); data = {}

ESTADOS = {"en_proceso", "pendiente_aprobacion", "aprobado_simulado", "rechazado_aprobador", "rechazado_politica", "devuelto_solicitante",
           "escalado_gerencia", "requiere_aclaracion", "rechazado_entrada", "detenido_presupuesto", "detenido_calidad", "error_controlado", "expirado"}
REQ = {"caso_id": str, "estado": str, "version": (int, float), "monto_total": (int, float), "cantidad": (int, float),
       "precio_unitario": (int, float), "llamadas_llm": (int, float), "costo_est_usd": (int, float)}

if data:
    for k in ["generado", "casos", "trazas", "presupuesto", "modo"]:
        if k not in data: err(f"casos.json sin clave '{k}'")
    if data.get("modo") != "SIMULADO": err("La exportación debe declarar modo SIMULADO")
    try: datetime.fromisoformat(str(data.get("generado", "")).replace("Z", "+00:00"))
    except Exception: err("'generado' no es una fecha ISO")
    vistos = set()
    for c in data.get("casos", []):
        cid = c.get("caso_id", "?")
        for k, t in REQ.items():
            if k not in c or c[k] is None or not isinstance(c[k], t):
                err(f"{cid}: campo '{k}' ausente o de tipo inválido")
        if not re.fullmatch(r"GAS-\d{4}", str(cid)): err(f"{cid}: folio con formato inválido")
        if cid in vistos: err(f"{cid}: folio duplicado")
        vistos.add(cid)
        if c.get("estado") not in ESTADOS: err(f"{cid}: estado no permitido '{c.get('estado')}'")
        if c.get("veredicto") not in ("", None, "aprobado", "devuelto"): err(f"{cid}: veredicto no permitido")
        # 3. Cálculos deterministas
        q, pu, m = c.get("cantidad") or 0, c.get("precio_unitario") or 0, c.get("monto_total") or 0
        if q and pu and abs(q * pu - m) > 0.01:
            err(f"{cid}: monto_total {m} ≠ cantidad×precio_unitario {round(q * pu, 2)}")
        pr = c.get("precio_ref") or 0
        if pr and pu and abs((pu / pr - 1) * 100 - (c.get("variacion_precio") or 0)) > 0.11:
            err(f"{cid}: variación de precio inconsistente")
        if c.get("estado") == "aprobado_simulado" and c.get("veredicto") != "aprobado":
            err(f"{cid}: aprobado sin revisión A4 aprobada (el revisor no puede ser omitido)")
        if (c.get("costo_est_usd") or 0) < 0: err(f"{cid}: costo negativo")
    for t in data.get("trazas", []):
        if t.get("caso_id") not in vistos: err(f"traza huérfana de {t.get('caso_id')}")
    for p in data.get("presupuesto", []):
        if not (0 <= p.get("comprometido", -1) <= p.get("presupuesto_mensual", 0)):
            err(f"{p.get('centro_costo')}: comprometido fuera de rango")

# 5. Secretos e identificadores en la zona pública
patrones = {
    "token de bot de Telegram": r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b",
    "API key estilo sk-": r"\bsk-[A-Za-z0-9_-]{16,}",
    "encabezado de autenticación con valor": r"X-GastoClaro-Key\s*[:=]\s*['\"]?[A-Za-z0-9_-]{12,}",
    "chat_id o teléfono": r"\"(chat_id|chat_solicitante|usuario|alias)\"\s*:",
    "correo electrónico": r"[\w.+-]+@(?!example\.)[\w-]+\.(com|mx|net|org|io)\b",
}
for f in (ROOT / "web").rglob("*"):
    if f.is_file() and f.suffix in {".html", ".js", ".json", ".css", ".md"}:
        txt = f.read_text(encoding="utf-8", errors="ignore")
        for nombre, rx in patrones.items():
            if re.search(rx, txt):
                err(f"Posible {nombre} en {f.relative_to(ROOT)}")

# 6. Skills con secciones obligatorias
for s in ["solicitud-gasto", "revision-politica"]:
    md = (ROOT / f"skills/{s}/SKILL.md").read_text(encoding="utf-8") if (ROOT / f"skills/{s}/SKILL.md").exists() else ""
    for sec in ["name:", "version:", "descripcion:", "activador:", "## Objetivo", "## Entradas", "## Fuentes", "## Pasos", "## Herramientas permitidas", "## Límites", "## Errores", "## Criterios de aceptación", "## Ejemplos"]:
        if sec not in md: err(f"skill {s}: falta sección '{sec}'")

# Políticas
try:
    pol = json.loads((ROOT / "datos/politicas.json").read_text(encoding="utf-8"))
    ids = [r["id"] for r in pol["reglas"]]
    if ids != [f"POL-0{i}" for i in range(1, 8)]: err("politicas.json: se esperaban POL-01..POL-07 en orden")
except Exception as e:
    err(f"politicas.json inválido: {e}")

n = len(data.get("casos", [])) if data else 0
if errores:
    print(f"VALIDACIÓN FALLIDA ({len(errores)} error(es)) — no se publica:")
    for e in errores: print("  ✗", e)
    sys.exit(1)
print(f"VALIDACIÓN OK · {n} casos · {len(data.get('trazas', []))} trazas · sin secretos detectados")
