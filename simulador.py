"""
simulador.py — Simulador de la tesis: ingreso laboral y probabilidad de empleo formal.

Usa los dos LightGBM exportados por "Modelos R/Exportar modelos simulador.R"
(reentrenados con el 100% de la base GEIH 2023-2025) y el archivo
simulador_config.json (niveles -> código, cuantiles por grupo, smearing,
anio_ref, umbral y límites de validación).

Uso desde el front:

    from simulador import predecir_ingreso, predecir_formalidad, validar_respuestas

    respuestas = {
        "edad": 30, "sexo": "Femenino", "estado_civil": "Soltero(a)",
        "sabe_leer_escribir": "Sí", "asiste_institucion_educ": "No",
        "nivel_educativo": "Universitaria",
        "area_titulo_campo_amplio": "04 ADMINISTRACIÓN DE EMPRESAS Y DERECHO",
        "departamento": "Bogotá D.C.", "zona": "Cabecera", "tipo_contrato": "Indefinido",
        "lugar_trabajo": "Local fijo / oficina / fábrica",
        "medio_consiguio_empleo": "Envió hoja de vida a empresas",
        "sector_economico_seccion": "K - ACTIVIDADES FINANCIERAS Y DE SEGUROS",
        "oficio_gran_grupo": "PROFESIONALES, CIENTÍFICOS E INTELECTUALES",
        "minutos_desplazamiento": 40,
    }
    ingreso = predecir_ingreso(respuestas)        # dict
    formal  = predecir_formalidad(respuestas)     # dict

- Las opciones válidas de cada pregunta están en opciones(variable).
- El texto se compara exacto y, si no coincide, sin tildes/mayúsculas/espacios extra.
- Si la validación encuentra un ERROR (combinación que prácticamente no existe en
  los datos), la función devuelve {"ok": False, "errores": [...], ...} y no predice.
  Las ADVERTENCIAS (combinaciones raras) no bloquean: se devuelven junto a la predicción.

Prueba de equivalencia con R:
    python simulador.py --probar            (usa la carpeta por defecto)
    python simulador.py --probar <carpeta>  (carpeta con el export de R)

Requisitos: numpy y lightgbm 4.x  (pip install lightgbm numpy)
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
import unicodedata
from pathlib import Path

import numpy as np
import lightgbm as lgb

# ---------------------------------------------------------------------------
# Textos para la interfaz
# ---------------------------------------------------------------------------
ETIQUETAS = {
    "edad": "Edad",
    "sexo": "Sexo",
    "estado_civil": "Estado civil",
    "sabe_leer_escribir": "Saber leer y escribir",
    "asiste_institucion_educ": "Estudiar actualmente",
    "nivel_educativo": "Nivel educativo",
    "area_titulo_campo_amplio": "Área del título",
    "departamento": "Departamento",
    "zona": "Zona",
    "tipo_contrato": "Tipo de contrato",
    "lugar_trabajo": "Lugar de trabajo",
    "medio_consiguio_empleo": "Medio de búsqueda de empleo",
    "sector_economico_seccion": "Sector económico",
    "oficio_gran_grupo": "Oficio",
    "minutos_desplazamiento": "Tiempo de desplazamiento",
}
UMBRAL_EFECTO_INGRESO_PCT = 1.0      # factores con efecto < 1% no se listan
UMBRAL_EFECTO_FORMAL_PP = 0.5        # factores con efecto < 0.5 pp no se listan

# Variables que no dependen de la persona: se muestran como brecha observada en el mercado,
# no como algo que "sube" o "baja" su resultado (decisión 21 oct 2026: no ocultarlas, contextualizarlas).
VARIABLES_BRECHA = {"sexo"}


def _mensaje_brecha(f: dict, modulo: str) -> str:
    sentido = "más" if f["efecto"] > 0 else "menos"
    grupo = {"Femenino": "las mujeres", "Masculino": "los hombres"}.get(f["valor"], f"las personas con {f['valor'].lower()}")
    if modulo == "ingreso":
        dato = f"{grupo} con un perfil similar al tuyo ganan en promedio ~{abs(f['efecto']):.0f}% {sentido}"
    else:
        dato = f"{grupo} con un perfil similar al tuyo tienen ~{abs(f['efecto']):.1f} puntos {sentido} de probabilidad de empleo formal"
    return (f"{f['etiqueta']} ({f['valor']}): en el mercado laboral colombiano (GEIH 2023-2025) {dato}. "
            f"Es una brecha observada en los datos, no algo que dependa de ti.")


def _normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFKD", str(texto))
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.lower().split())


def _sigmoide(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _dir_por_defecto() -> Path:
    env = os.environ.get("SIMULADOR_EXPORT_DIR")
    if env:
        return Path(env)
    aqui = Path(__file__).resolve().parent
    for cand in (aqui / "simulador_export", aqui.parent / "Modelos R" / "simulador_export",
                 aqui / "Modelos R" / "simulador_export"):
        if (cand / "simulador_config.json").exists():
            return cand
    raise FileNotFoundError("No encontré simulador_config.json. Pasa la carpeta del export o define SIMULADOR_EXPORT_DIR.")


def _valor_txt(v) -> str:
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


# ---------------------------------------------------------------------------
# Simulador
# ---------------------------------------------------------------------------
class Simulador:
    def __init__(self, dir_export: str | Path | None = None):
        self.dir = Path(dir_export) if dir_export else _dir_por_defecto()
        with open(self.dir / "simulador_config.json", encoding="utf-8") as f:
            self.cfg = json.load(f)
        cfg = self.cfg
        self.niveles: dict[str, list[str]] = cfg["niveles"]
        self.num_vars: list[str] = cfg["variables_numericas"]
        self.vars_form: list[str] = cfg["variables_formulario"]
        self.anio_ref: str = str(cfg["anio_ref"])
        self._codigo = {v: {lab: i + 1 for i, lab in enumerate(labs)} for v, labs in self.niveles.items()}
        self._norm = {v: {_normalizar(lab): lab for lab in labs} for v, labs in self.niveles.items()}

        self.cfg_ing = cfg["modelos"]["ingreso"]
        self.cfg_for = cfg["modelos"]["formalidad"]
        self.m_ing = lgb.Booster(model_file=str(self.dir / self.cfg_ing["archivo"]))
        self.m_for = lgb.Booster(model_file=str(self.dir / self.cfg_for["archivo"]))
        if self.m_ing.feature_name() != self.cfg_ing["x_vars"]:
            raise ValueError("El orden de variables del modelo de ingreso no coincide con el JSON.")
        if self.m_for.feature_name() != self.cfg_for["x_vars"]:
            raise ValueError("El orden de variables del modelo de formalidad no coincide con el JSON.")
        if self.anio_ref not in self._codigo["anio"]:
            raise ValueError(f"anio_ref {self.anio_ref} no está en los niveles de anio.")
        self.val = cfg["validacion"]

    # ----------------------------------------------------------------- opciones
    def opciones(self, variable: str) -> list[str]:
        """Opciones válidas (texto exacto) de una pregunta categórica."""
        return list(self.niveles[variable])

    def _vars_modulo(self, modulo: str | None) -> list[str]:
        if modulo == "ingreso":
            return [v for v in self.cfg_ing["x_vars"] if v != "anio"]
        if modulo == "formalidad":
            return [v for v in self.cfg_for["x_vars"] if v != "anio"]
        return list(self.vars_form)

    # ------------------------------------------------------- canonizar entradas
    def _canonizar(self, respuestas: dict, variables: list[str]) -> tuple[dict, list[dict]]:
        canon, errores = {}, []
        for v in variables:
            if v not in respuestas or respuestas[v] is None or str(respuestas[v]).strip() == "":
                errores.append({"regla": "E0", "variable": v, "mensaje": f"Falta responder: {ETIQUETAS.get(v, v)}."})
                continue
            x = respuestas[v]
            if v in self.num_vars:
                try:
                    num = float(str(x).replace(",", "."))
                except ValueError:
                    errores.append({"regla": "E0", "variable": v,
                                    "mensaje": f"{ETIQUETAS.get(v, v)} debe ser un número (recibí '{x}')."})
                    continue
                if not math.isfinite(num):
                    errores.append({"regla": "E0", "variable": v, "mensaje": f"{ETIQUETAS.get(v, v)} no es válido."})
                    continue
                if v == "edad" and not float(num).is_integer():
                    errores.append({"regla": "E0", "variable": v, "mensaje": "La edad debe ser un número entero de años."})
                    continue
                canon[v] = num
            else:
                txt = str(x).strip()
                if txt in self._codigo[v]:
                    canon[v] = txt
                elif _normalizar(txt) in self._norm[v]:
                    canon[v] = self._norm[v][_normalizar(txt)]
                else:
                    errores.append({"regla": "E0", "variable": v,
                                    "mensaje": f"Opción no válida para {ETIQUETAS.get(v, v)}: '{txt}'.",
                                    "opciones": self.opciones(v)})
        return canon, errores

    # ---------------------------------------------------------------- validación
    def validar_respuestas(self, respuestas: dict, modulo: str | None = None) -> dict:
        """Valida tipos, opciones y coherencia con los datos. modulo: 'ingreso', 'formalidad' o None (formulario completo).

        Errores (bloquean): E0 falta/opción inválida | E1 edad fuera de rango | E2 edad menor que la mínima
        plausible para el nivel educativo | E3 combinación de respuestas casi inexistente | E4 minutos fuera de rango.
        Advertencias: A2 edad atípica para el nivel | A3 combinación poco frecuente |
        A4 desplazamiento muy largo | A5 opción con muy pocos casos.
        """
        variables = self._vars_modulo(modulo)
        canon, errores = self._canonizar(respuestas, variables)
        advertencias: list[dict] = []
        if errores:
            return {"ok": False, "errores": errores, "advertencias": advertencias, "respuestas": canon}

        val, reglas = self.val, self.val["reglas"]
        n_bloq, n_raro, n_nivel_raro = reglas["n_bloqueo"], reglas["n_raro"], reglas["n_nivel_raro"]

        # Edad
        if "edad" in canon:
            e = canon["edad"]
            if e < val["edad"]["min"] or e > val["edad"]["max"]:
                errores.append({"regla": "E1", "variable": "edad",
                                "mensaje": f"La edad debe estar entre {_valor_txt(val['edad']['min'])} y {_valor_txt(val['edad']['max'])} años."})
            if "nivel_educativo" in canon:
                nv = canon["nivel_educativo"]
                lim = val["edad"]["por_nivel"][nv]
                if e < lim["edad_min_plausible"]:
                    errores.append({"regla": "E2", "variable": "edad",
                                    "mensaje": f"Con nivel educativo '{nv}' casi no hay personas menores de "
                                               f"{_valor_txt(lim['edad_min_plausible'])} años en los datos (GEIH 2023-2025). "
                                               f"Revisa la edad o el nivel educativo."})
                if e < lim["p1"] or e > lim["p99"]:
                    advertencias.append({"regla": "A2", "variable": "edad",
                                         "mensaje": f"La edad es atípica para el nivel '{nv}' (el 98% está entre "
                                                    f"{lim['p1']:.0f} y {lim['p99']:.0f} años)."})

        # Minutos de desplazamiento
        if "minutos_desplazamiento" in canon:
            mi, lm = canon["minutos_desplazamiento"], val["minutos_desplazamiento"]
            if mi < lm["min"] or mi > lm["max"]:
                errores.append({"regla": "E4", "variable": "minutos_desplazamiento",
                                "mensaje": f"Los minutos de desplazamiento deben estar entre {_valor_txt(lm['min'])} y {_valor_txt(lm['max'])}."})
            if mi > lm["p99"]:
                advertencias.append({"regla": "A4", "variable": "minutos_desplazamiento",
                                     "mensaje": f"Un desplazamiento de más de {_valor_txt(lm['p99'])} minutos es muy poco frecuente."})

        # Pares de categorías
        for nombre, par in val["pares"].items():
            a, b = par["var_a"], par["var_b"]
            if a not in canon or b not in canon:
                continue
            n = par["conteos"].get(canon[a], {}).get(canon[b], 0)
            desc = f"{ETIQUETAS.get(a, a)} '{canon[a]}' con {ETIQUETAS.get(b, b).lower()} '{canon[b]}'"
            if n < n_bloq:
                errores.append({"regla": "E3", "variable": f"{a}+{b}", "par": nombre,
                                "mensaje": f"La combinación {desc} prácticamente no existe en los datos ({n} casos). "
                                           f"Revisa tus respuestas."})
            elif n < n_raro:
                advertencias.append({"regla": "A3", "variable": f"{a}+{b}", "par": nombre,
                                     "mensaje": f"La combinación {desc} es poco frecuente ({n} casos): "
                                                f"la estimación es menos confiable."})

        # Opciones con muy pocos casos
        for v in variables:
            if v in self.num_vars or v not in canon:
                continue
            tot = val["conteo_niveles"][v].get(canon[v], 0)
            if tot < n_nivel_raro:
                advertencias.append({"regla": "A5", "variable": v,
                                     "mensaje": f"La opción '{canon[v]}' de {ETIQUETAS.get(v, v).lower()} tiene muy pocos casos "
                                                f"({tot}): la estimación es menos confiable."})

        return {"ok": not errores, "errores": errores, "advertencias": advertencias, "respuestas": canon}

    # ----------------------------------------------------------- codificación
    def _matriz(self, canon: dict, x_vars: list[str]) -> np.ndarray:
        fila = []
        for v in x_vars:
            if v == "anio":
                fila.append(float(self._codigo["anio"][self.anio_ref]))
            elif v in self.num_vars:
                fila.append(float(canon[v]))
            else:
                fila.append(float(self._codigo[v][canon[v]]))
        return np.array([fila], dtype=np.float64)

    def grupo(self, canon: dict) -> str:
        g = self.cfg_ing["grupos"]
        if canon["nivel_educativo"] in g["niveles_posgrado"]:
            return "Posgrado gran ciudad" if canon["departamento"] in g["deptos_gran_ciudad"] else "Posgrado resto"
        return "Sin posgrado"

    def _preparar(self, respuestas: dict, modulo: str, validar: bool):
        v = self.validar_respuestas(respuestas, modulo)
        if v["errores"] and (validar or any(e["regla"] == "E0" for e in v["errores"])):
            return None, v
        return v["respuestas"], v

    # ------------------------------------------------------------- factores SHAP
    def _factores(self, contrib: np.ndarray, x_vars: list[str], canon: dict, modulo: str,
                  raw: float, n_factores: int) -> dict:
        lista = []
        for j, v in enumerate(x_vars):
            if v == "anio":
                continue
            s = float(contrib[j])
            if modulo == "ingreso":
                efecto = 100.0 * (math.exp(s) - 1.0)          # % sobre el ingreso (multiplicativo, exacto)
                relevante = abs(efecto) >= UMBRAL_EFECTO_INGRESO_PCT
            else:
                efecto = 100.0 * (_sigmoide(raw) - _sigmoide(raw - s))   # pp: probabilidad vs. sin este factor
                relevante = abs(efecto) >= UMBRAL_EFECTO_FORMAL_PP
            valor = _valor_txt(canon[v]) + (" min" if v == "minutos_desplazamiento" else " años" if v == "edad" else "")
            lista.append({"variable": v, "etiqueta": ETIQUETAS.get(v, v), "valor": valor,
                          "shap": s, "efecto": efecto, "relevante": relevante})
        suben = sorted([f for f in lista if f["shap"] > 0 and f["relevante"]], key=lambda f: -f["shap"])[:n_factores]
        bajan = sorted([f for f in lista if f["shap"] < 0 and f["relevante"]], key=lambda f: f["shap"])[:n_factores]
        mensajes = []
        for f in suben + bajan:
            f["tipo"] = "brecha_observada" if f["variable"] in VARIABLES_BRECHA else "factor"
        for f in suben:
            if f["tipo"] == "brecha_observada":
                mensajes.append(_mensaje_brecha(f, modulo))
            elif modulo == "ingreso":
                mensajes.append(f"{f['etiqueta']} ({f['valor']}) sube tu ingreso estimado en {f['efecto']:.0f}% frente al perfil promedio.")
            else:
                mensajes.append(f"{f['etiqueta']} ({f['valor']}) sube tu probabilidad de empleo formal en {f['efecto']:.1f} puntos.")
        for f in bajan:
            if f["tipo"] == "brecha_observada":
                mensajes.append(_mensaje_brecha(f, modulo))
            elif modulo == "ingreso":
                mensajes.append(f"{f['etiqueta']} ({f['valor']}) reduce tu ingreso estimado en {abs(f['efecto']):.0f}% frente al perfil promedio.")
            else:
                mensajes.append(f"{f['etiqueta']} ({f['valor']}) reduce tu probabilidad de empleo formal en {abs(f['efecto']):.1f} puntos.")
        limpiar = lambda fs: [{k: f[k] for k in ("variable", "etiqueta", "valor", "shap", "efecto", "tipo")} for f in fs]
        return {"factores_suben": limpiar(suben), "factores_bajan": limpiar(bajan), "mensajes": mensajes,
                "contribuciones": {f["variable"]: f["shap"] for f in lista}}

    # --------------------------------------------------------------- ingreso
    def predecir_ingreso(self, respuestas: dict, validar: bool = True, n_factores: int = 3) -> dict:
        """Ingreso laboral mensual estimado (COP). mediana = expm1(pred_log); intervalo 80% por grupo;
        media con smearing de Duan por grupo. SHAP en log -> efecto % multiplicativo."""
        canon, v = self._preparar(respuestas, "ingreso", validar)
        if canon is None:
            return {"ok": False, "errores": v["errores"], "advertencias": v["advertencias"]}
        x_vars = self.cfg_ing["x_vars"]
        X = self._matriz(canon, x_vars)
        contrib = self.m_ing.predict(X, pred_contrib=True)[0]
        pred_log = float(contrib.sum())
        pred_directa = float(self.m_ing.predict(X)[0])
        if abs(pred_log - pred_directa) > 1e-8:
            raise RuntimeError("SHAP no suma la predicción (ingreso).")
        g = self.grupo(canon)
        q = self.cfg_ing["intervalo"]["cuantiles_por_grupo"][g]
        S = self.cfg_ing["smearing"]["por_grupo"][g]
        j_anio = x_vars.index("anio")
        base_log = float(contrib[-1] + contrib[j_anio])          # promedio del modelo + efecto del año de referencia
        fac = self._factores(contrib, x_vars, canon, "ingreso", pred_log, n_factores)
        return {
            "ok": True,
            "ingreso_mediana": math.expm1(pred_log),
            "ingreso_media": math.exp(pred_log) * S - 1.0,
            "intervalo_80": {"p10": math.expm1(pred_log + q["q10"]), "p90": math.expm1(pred_log + q["q90"])},
            "grupo": g,
            "pred_log": pred_log,
            "ingreso_base_promedio": math.expm1(base_log),
            **fac,
            "advertencias": v["advertencias"],
            "errores_ignorados": v["errores"],     # solo si validar=False
            "anio_ref": self.anio_ref,
        }

    # ------------------------------------------------------------ formalidad
    def predecir_formalidad(self, respuestas: dict, validar: bool = True, n_factores: int = 3) -> dict:
        """Probabilidad de empleo formal pleno. SHAP en log-odds -> efecto en puntos porcentuales
        (probabilidad actual menos la probabilidad si ese factor fuera el promedio)."""
        canon, v = self._preparar(respuestas, "formalidad", validar)
        if canon is None:
            return {"ok": False, "errores": v["errores"], "advertencias": v["advertencias"]}
        x_vars = self.cfg_for["x_vars"]
        X = self._matriz(canon, x_vars)
        contrib = self.m_for.predict(X, pred_contrib=True)[0]
        raw = float(contrib.sum())
        prob = _sigmoide(raw)
        prob_directa = float(self.m_for.predict(X)[0])
        if abs(prob - prob_directa) > 1e-8:
            raise RuntimeError("SHAP no suma la predicción (formalidad).")
        umbral = float(self.cfg_for["umbral"])
        j_anio = x_vars.index("anio")
        fac = self._factores(contrib, x_vars, canon, "formalidad", raw, n_factores)
        return {
            "ok": True,
            "probabilidad": prob,
            "porcentaje": 100.0 * prob,
            "clasificacion": "Empleo formal" if prob >= umbral else "Empleo informal",
            "umbral": umbral,
            "probabilidad_base_promedio": _sigmoide(float(contrib[-1] + contrib[j_anio])),
            **fac,
            "advertencias": v["advertencias"],
            "errores_ignorados": v["errores"],
            "anio_ref": self.anio_ref,
        }


# ---------------------------------------------------------------------------
# API de módulo (instancia única, carga perezosa)
# ---------------------------------------------------------------------------
_SIM: Simulador | None = None


def cargar(dir_export: str | Path | None = None) -> Simulador:
    global _SIM
    _SIM = Simulador(dir_export)
    return _SIM


def _sim() -> Simulador:
    return _SIM if _SIM is not None else cargar()


def predecir_ingreso(respuestas: dict, **kw) -> dict:
    return _sim().predecir_ingreso(respuestas, **kw)


def predecir_formalidad(respuestas: dict, **kw) -> dict:
    return _sim().predecir_formalidad(respuestas, **kw)


def validar_respuestas(respuestas: dict, modulo: str | None = None) -> dict:
    return _sim().validar_respuestas(respuestas, modulo)


def opciones(variable: str) -> list[str]:
    return _sim().opciones(variable)


def formatear_cop(valor: float) -> str:
    return "$" + f"{round(valor):,}".replace(",", ".")


# ---------------------------------------------------------------------------
# Prueba de equivalencia contra R
# ---------------------------------------------------------------------------
def _leer_csv(ruta: Path) -> list[dict]:
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def probar(dir_export: str | Path | None = None, tol_rel: float = 1e-6, tol_abs: float = 1e-8) -> bool:
    sim = cargar(dir_export)
    perfiles = _leer_csv(sim.dir / "perfiles_prueba_R.csv")
    shap_ing = {r["id"]: r for r in _leer_csv(sim.dir / "shap_perfiles_ingreso_R.csv")}
    shap_for = {r["id"]: r for r in _leer_csv(sim.dir / "shap_perfiles_formalidad_R.csv")}

    def cerca(a: float, b: float) -> bool:
        return abs(a - b) <= max(tol_abs, tol_rel * abs(b))

    fallas, dif_max = [], {"pred_log": 0.0, "prob": 0.0, "shap_ing": 0.0, "shap_for": 0.0, "rel_pesos": 0.0}
    print(f"Prueba R vs Python | {len(perfiles)} perfiles | carpeta: {sim.dir}")
    print(f"lightgbm Python {lgb.__version__} | lightgbm R {sim.cfg.get('lightgbm_r')}\n")
    print(f"{'id':4} {'grupo':21} {'mediana':>13} {'p10':>13} {'p90':>13} {'media':>13} {'prob':>7} adv  ok")
    for p in perfiles:
        resp = {v: p[v] for v in sim.vars_form}
        val = sim.validar_respuestas(resp)
        r_i = sim.predecir_ingreso(resp, validar=False)
        r_f = sim.predecir_formalidad(resp, validar=False)
        ok = True
        comparaciones = [
            ("pred_log", r_i["pred_log"], float(p["pred_log_R"])),
            ("mediana", r_i["ingreso_mediana"], float(p["ingreso_mediana_R"])),
            ("p10", r_i["intervalo_80"]["p10"], float(p["ingreso_p10_R"])),
            ("p90", r_i["intervalo_80"]["p90"], float(p["ingreso_p90_R"])),
            ("media", r_i["ingreso_media"], float(p["ingreso_media_R"])),
            ("prob", r_f["probabilidad"], float(p["prob_formal_R"])),
        ]
        for nombre, py, r in comparaciones:
            if not cerca(py, r):
                ok = False; fallas.append(f"{p['id']} {nombre}: Python {py!r} vs R {r!r}")
        dif_max["pred_log"] = max(dif_max["pred_log"], abs(r_i["pred_log"] - float(p["pred_log_R"])))
        dif_max["prob"] = max(dif_max["prob"], abs(r_f["probabilidad"] - float(p["prob_formal_R"])))
        dif_max["rel_pesos"] = max(dif_max["rel_pesos"], abs(r_i["ingreso_mediana"] / float(p["ingreso_mediana_R"]) - 1))
        if r_i["grupo"] != p["grupo"]:
            ok = False; fallas.append(f"{p['id']} grupo: Python {r_i['grupo']} vs R {p['grupo']}")

        # SHAP por variable
        for modelo, shap_r, x_vars in (("shap_ing", shap_ing[p["id"]], sim.cfg_ing["x_vars"]),
                                       ("shap_for", shap_for[p["id"]], sim.cfg_for["x_vars"])):
            canon = val["respuestas"]
            m = sim.m_ing if modelo == "shap_ing" else sim.m_for
            contrib = m.predict(sim._matriz(canon, x_vars), pred_contrib=True)[0]
            for j, v in enumerate(list(x_vars) + ["BASE"]):
                d = abs(float(contrib[j]) - float(shap_r[v]))
                dif_max[modelo] = max(dif_max[modelo], d)
                if d > 1e-6:
                    ok = False; fallas.append(f"{p['id']} {modelo} {v}: Python {contrib[j]!r} vs R {shap_r[v]}")

        # Validación: mismas reglas que en R
        n_err, n_adv = len(val["errores"]), len(val["advertencias"])
        if n_err != int(p["n_errores_R"]) or n_adv != int(p["n_advertencias_R"]):
            ok = False
            fallas.append(f"{p['id']} validación: Python {n_err} errores/{n_adv} advertencias vs R "
                          f"{p['n_errores_R']}/{p['n_advertencias_R']}")
        if not ok:
            fallas.append("")
        print(f"{p['id']:4} {r_i['grupo']:21} {formatear_cop(r_i['ingreso_mediana']):>13} "
              f"{formatear_cop(r_i['intervalo_80']['p10']):>13} {formatear_cop(r_i['intervalo_80']['p90']):>13} "
              f"{formatear_cop(r_i['ingreso_media']):>13} {r_f['probabilidad']:7.4f} {n_adv:3}  {'OK' if ok else 'FALLA'}")

    print("\nDiferencias máximas | pred_log: {pred_log:.2e} | prob: {prob:.2e} | SHAP ingreso: {shap_ing:.2e} | "
          "SHAP formalidad: {shap_for:.2e} | relativa mediana pesos: {rel_pesos:.2e}".format(**dif_max))

    # Ejemplo de mensajes para el primer perfil
    p0 = {v: perfiles[0][v] for v in sim.vars_form}
    print(f"\nEjemplo de mensajes ({perfiles[0]['id']}):")
    for m in sim.predecir_ingreso(p0)["mensajes"] + sim.predecir_formalidad(p0)["mensajes"]:
        print("  -", m)

    # Demostración de validación: perfil incoherente (18 años + universitaria + directivo)
    raro = dict(p0, edad=18, nivel_educativo="Universitaria", oficio_gran_grupo="DIRECTORES Y GERENTES",
                tipo_contrato="Indefinido")
    vr = sim.validar_respuestas(raro)
    print("\nPerfil incoherente (18 años, Universitaria, Directores y gerentes):",
          "BLOQUEADO" if not vr["ok"] else "permitido con advertencias")
    for e in vr["errores"]:
        print("  ERROR", e["regla"], "-", e["mensaje"])
    for a in vr["advertencias"]:
        print("  AVISO", a["regla"], "-", a["mensaje"])
    malo = dict(p0, nivel_educativo="Universitario")
    print("Opción mal escrita:", sim.validar_respuestas(malo)["errores"][0]["mensaje"])

    print("\nRESULTADO:", "PASA — Python reproduce a R" if not fallas else "FALLA")
    for f in fallas[:40]:
        if f:
            print("  ", f)
    return not fallas


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--probar":
        sys.exit(0 if probar(sys.argv[2] if len(sys.argv) > 2 else None) else 1)
    print(__doc__)

