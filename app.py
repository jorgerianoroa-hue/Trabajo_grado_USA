"""
Mercado laboral de Colombia (GEIH): análisis descriptivo.
Ejecutar con:  streamlit run app.py
"""

from pathlib import Path
from string import Template

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Mercado laboral de Colombia",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = Path(__file__).parent / "datos_reducidos.parquet"
MESES_ORDEN = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
               "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# ---------------------------------------------------------------------------
# TOKENS DE DISEÑO
# Formal / promedio = PRIMARY · No formal = NOFORMAL (teal) · Mediana = ACCENT
# ---------------------------------------------------------------------------
BG, SURFACE = "#F8FAFC", "#FFFFFF"
TEXT, MUTED = "#111827", "#64748B"
PRIMARY, SECONDARY, ACCENT = "#164E63", "#0F766E", "#D97706"
NOFORMAL = "#5BA8A0"
BORDER, GRIDLINE = "#E2E8F0", "#EEF2F6"
F_DISPLAY, F_BODY = "Manrope", "Inter"

CSS = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family:'$F_BODY',sans-serif; color:$TEXT; }
.stApp { background:$BG; }
.block-container { max-width:1440px; padding:1.2rem 2.4rem 3rem; }
header[data-testid="stHeader"] { background:transparent; }
footer { visibility:hidden; }
h1,h2,h3 { font-family:'$F_DISPLAY',sans-serif; }

/* Navegación superior */
.brand { font-family:'$F_DISPLAY',sans-serif; font-weight:700; font-size:1.1rem; color:$PRIMARY; letter-spacing:-0.01em; padding-top:.3rem; }
.st-key-nav button { width:auto; min-height:0; padding:.35rem 0 .45rem; background:transparent; border:none;
    border-bottom:2px solid transparent; border-radius:0; color:$MUTED; font-weight:500; font-size:.95rem;
    transition:color .15s, border-color .15s; }
.st-key-nav button:hover { color:$TEXT; background:transparent; border-bottom-color:$BORDER; }
.st-key-nav button[kind="primary"], .st-key-nav button[data-testid="stBaseButton-primary"],
.st-key-nav button[kind="primary"]:hover, .st-key-nav button[data-testid="stBaseButton-primary"]:hover {
    color:$PRIMARY; font-weight:600; border-bottom-color:$PRIMARY; background:transparent; }
.st-key-nav button p, div[class*="st-key-link_"] button p { color:inherit; font-size:inherit; font-weight:inherit; }

/* Enlaces de texto (Explorar →) */
div[class*="st-key-link_"] button { width:auto; min-height:0; padding:0; background:transparent; border:none;
    color:$PRIMARY; font-weight:500; font-size:.95rem; justify-content:flex-start; transition:color .15s; }
div[class*="st-key-link_"] button:hover { color:$SECONDARY; background:transparent; text-decoration:underline; text-underline-offset:4px; }

/* Filtros compactos */
.st-key-filters label p { font-size:.78rem; color:$MUTED; font-weight:500; }
.st-key-filters [data-baseweb="select"] > div { background:$SURFACE; border:1px solid $BORDER; border-radius:8px; min-height:38px; font-size:.88rem; }
.st-key-filters [data-baseweb="tag"] { background:#E4EEF1; color:$PRIMARY; border-radius:6px; }
.aux { color:$MUTED; font-size:.84rem; margin:.3rem 0 1rem; }

/* Tipografía editorial */
.eyebrow { color:$SECONDARY; font-weight:500; font-size:.95rem; margin-top:2.6rem; margin-bottom:.8rem; }
.hero { font-family:'$F_DISPLAY',sans-serif; font-size:3.4rem; font-weight:600; line-height:1.08; letter-spacing:-0.028em; }
.hero-sub { color:$MUTED; font-size:1.1rem; line-height:1.55; max-width:520px; padding-bottom:.5rem; }
.page-title { font-family:'$F_DISPLAY',sans-serif; font-size:2.2rem; font-weight:600; letter-spacing:-0.02em; margin-top:1.4rem; }
.page-sub { color:$MUTED; font-size:1.02rem; margin-top:.3rem; max-width:480px; }
.sec-title { font-family:'$F_DISPLAY',sans-serif; font-size:1.6rem; font-weight:600; letter-spacing:-0.015em; }
.sec-sub { color:$MUTED; font-size:.95rem; margin-top:.4rem; max-width:300px; }
.item { border-top:1px solid $BORDER; padding-top:1rem; }
.item-cat { color:$MUTED; font-size:.84rem; margin-bottom:.35rem; }
.item-title { font-family:'$F_DISPLAY',sans-serif; font-size:1.3rem; font-weight:600; margin-bottom:.35rem; }
.item-text { color:$MUTED; font-size:.95rem; line-height:1.5; margin-bottom:.5rem; min-height:3rem; }
.tag { color:$ACCENT; font-size:.78rem; font-weight:500; border:1px solid $ACCENT; border-radius:999px; padding:0 .5rem; margin-left:.6rem; }
.chart-title { font-family:'$F_DISPLAY',sans-serif; font-size:1rem; font-weight:600; margin:1.6rem 0 .2rem; }
.rule { border:none; border-top:1px solid $BORDER; margin:1rem 0 1.2rem; }
.foot { border-top:1px solid $BORDER; color:$MUTED; font-size:.82rem; margin-top:4rem; padding-top:1rem; }
.canvas-empty { min-height:460px; border:1px dashed $BORDER; border-radius:10px; display:flex; align-items:center; justify-content:center; color:$MUTED; font-size:.95rem; margin-top:1.5rem; }

/* KPIs: número grande + etiqueta + divisor vertical */
.kpi-v { font-family:'$F_BODY',sans-serif; font-size:2.4rem; font-weight:600; line-height:1.1; letter-spacing:-0.02em; font-variant-numeric:tabular-nums; }
.kpi-l { color:$MUTED; font-size:.88rem; margin-top:.2rem; }
.k-primary { color:$PRIMARY; } .k-teal { color:$SECONDARY; } .k-accent { color:$ACCENT; }
.st-key-kpis [data-testid="stColumn"]:not(:first-child), .st-key-kpis [data-testid="column"]:not(:first-child) {
    border-left:1px solid $BORDER; padding-left:1.5rem; }

/* Tabs minimalistas */
.stTabs [data-baseweb="tab-list"] { gap:1.7rem; border-bottom:1px solid $BORDER; background:transparent; }
.stTabs [data-baseweb="tab"] { background:transparent; padding:.5rem 0; color:$MUTED; font-weight:500; font-size:.95rem; transition:color .15s; }
.stTabs [data-baseweb="tab"]:hover { color:$TEXT; background:transparent; }
.stTabs [aria-selected="true"] { color:$TEXT; font-weight:600; }
.stTabs [data-baseweb="tab-highlight"] { background:$PRIMARY; height:2px; }
.stTabs [data-baseweb="tab-border"] { background:transparent; }

/* Asistente virtual: panel de chat fijo a la derecha, visible en todas las secciones */
[data-testid="stToolbar"] { display:none; }
.st-key-chat { position:fixed; top:0; right:0; bottom:0; width:380px !important; z-index:100; background:$SURFACE;
    border-left:1px solid $BORDER; padding:1.4rem 1.2rem 1rem; overflow-y:auto; }
.chat-title { font-family:'$F_DISPLAY',sans-serif; font-size:1.2rem; font-weight:600; }
.chat-sub { color:$MUTED; font-size:.9rem; margin-top:.2rem; }
.st-key-chat [data-testid="stChatMessage"] { background:transparent; padding:.35rem 0; }
.st-key-chat [data-testid="stChatInput"] { border:1px solid $BORDER; border-radius:10px; background:$SURFACE; }
div[class*="st-key-sug_"] button { width:100%; min-height:0; justify-content:flex-start; text-align:left; background:transparent;
    border:none; border-top:1px solid $BORDER; border-radius:0; padding:.55rem 0; color:$TEXT; font-size:.9rem; font-weight:400; transition:color .15s; }
div[class*="st-key-sug_"] button:hover { color:$PRIMARY; background:transparent; }
div[class*="st-key-sug_"] button p { color:inherit; font-size:inherit; }
.st-key-chat_reset button { width:auto; min-height:0; padding:0; background:transparent; border:none; color:$MUTED; font-size:.84rem; }
.st-key-chat_reset button:hover { color:$PRIMARY; background:transparent; text-decoration:underline; }
@media (min-width:1100px) { .block-container { max-width:none; padding-right:420px; } }
@media (max-width:1099px) { .st-key-chat { position:static; width:100% !important; border-left:none;
    border-top:1px solid $BORDER; margin-top:2rem; padding:1.2rem 0 0; } }

@media (max-width:900px) {
    .block-container { padding:1rem 1rem 2rem; }
    .hero { font-size:2.3rem; }
    .st-key-nav [data-testid="stHorizontalBlock"] { flex-wrap:wrap; gap:.2rem 1.3rem; }
    .st-key-nav [data-testid="stColumn"] { min-width:0 !important; flex:0 0 auto !important; width:auto !important; }
    .st-key-nav [data-testid="stColumn"]:first-child { flex:1 0 100% !important; }
    .st-key-kpis [data-testid="stColumn"]:not(:first-child) { border-left:none; padding-left:0; }
}
</style>
""")


def inject_css():
    st.markdown(CSS.safe_substitute(
        F_BODY=F_BODY, F_DISPLAY=F_DISPLAY, TEXT=TEXT, BG=BG, SURFACE=SURFACE, MUTED=MUTED,
        PRIMARY=PRIMARY, SECONDARY=SECONDARY, ACCENT=ACCENT, BORDER=BORDER,
    ), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# FORMATO (separadores colombianos: 1.850.000 y 61,4%)
# ---------------------------------------------------------------------------
def fmt_n(x):
    return f"{x:,.0f}".replace(",", ".")


def fmt_cop(x):
    return "$" + fmt_n(x)


def fmt_pct(x):
    return f"{x:.1%}".replace(".", ",")


# ---------------------------------------------------------------------------
# CARGA DE DATOS Y MEDIDAS (sin cambios de lógica)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Cargando datos...")
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["Mes Letras"] = pd.Categorical(
        df["mes"].map(dict(zip(range(1, 13), MESES_ORDEN))),
        categories=MESES_ORDEN, ordered=True,
    )
    for c in ["departamento", "sexo", "estado_civil", "etnia", "nivel_educativo",
              "tipo_contrato", "posicion_ocupacional", "lugar_trabajo",
              "sector_economico_seccion", "oficio_gran_grupo"]:
        df[c] = df[c].astype("category")
    return df


def pct_formal_no_formal(df):
    if len(df) == 0:
        return 0.0, 0.0
    return (df["empleo_formal_pleno"] == 1).sum() / len(df), (df["empleo_formal_pleno"] == 0).sum() / len(df)


def promedio_mediana_ingreso(df):
    if len(df) == 0:
        return 0.0, 0.0
    return df["ingreso_laboral_total"].mean(), df["ingreso_laboral_total"].median()


def agrupar(df, dim, col, funcs, por_n=True):
    out = df.groupby(dim, observed=True)[col].agg([*funcs, "count"]).reset_index()
    out.columns = [dim, *funcs, "n"]
    return out.sort_values("n", ascending=False) if por_n else out.sort_values(dim)


# ---------------------------------------------------------------------------
# TEMA PLOTLY CENTRALIZADO
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family=F_BODY, size=12, color=MUTED),
    legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title=dict(text=""),
                font=dict(size=12, color=MUTED)),
    margin=dict(t=34, b=8, l=4, r=16),
    hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER, font=dict(family=F_BODY, size=12, color=TEXT)),
    separators=",.",
    bargap=0.4,
)
PLOT_CONFIG = {"displayModeBar": False}


def estilizar_figura(fig, altura, pct, horizontal, apilado=False, margen_der=16):
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(height=altura, barmode="stack" if apilado else "group",
                      margin=dict(t=34, b=8, l=4, r=margen_der))
    valor = dict(showgrid=True, gridcolor=GRIDLINE, zeroline=False, showline=False,
                 tickfont=dict(size=11), tickformat=".0%" if pct else ",.0f",
                 tickprefix="" if pct else "$")
    if pct and horizontal:
        valor["range"] = [0, 1]
    categoria = dict(showgrid=False, zeroline=False, showline=False, ticks="", type="category",
                     automargin=True, tickfont=dict(size=12, color=TEXT))
    if horizontal:
        fig.update_xaxes(**valor)
        fig.update_yaxes(**categoria)
    else:
        fig.update_yaxes(**valor)
        fig.update_xaxes(**categoria)
    return fig


def grafico_barras(d, dim, series, pct, apilado=False, marcador=None, key=None):
    """Barras horizontales (ranking). series: (nombre, columna, color, color_texto)."""
    cat = d[dim].astype(str)
    fmt, pre = ".1%" if pct else ",.0f", "" if pct else "$"
    fig = go.Figure()
    for nombre, col, color, txt in series:
        fig.add_bar(
            name=nombre, y=cat, x=d[col], orientation="h", marker=dict(color=color),
            customdata=d["n"], texttemplate=f"{pre}%{{x:{fmt}}}", cliponaxis=False,
            textposition="inside" if apilado else "outside", textfont=dict(color=txt, size=11),
            hovertemplate=f"<b>%{{y}}</b><br>{nombre}: {pre}%{{x:{fmt}}}<br>Registros: %{{customdata:,}}<extra></extra>",
        )
    if marcador:
        nombre, col, color = marcador
        fig.add_scatter(
            name=nombre, y=cat, x=d[col], mode="markers", customdata=d["n"],
            marker=dict(symbol="diamond", size=9, color=color, line=dict(color=SURFACE, width=1)),
            hovertemplate=f"<b>%{{y}}</b><br>{nombre}: {pre}%{{x:{fmt}}}<extra></extra>",
        )
    estilizar_figura(fig, max(240, 30 * len(d) + 90), pct, True, apilado, margen_der=16 if pct else 70)
    st.plotly_chart(fig, config=PLOT_CONFIG, key=key)


def grafico_tendencia(d, dim, series, pct, key=None):
    """Líneas finas con punto pequeño; etiqueta solo en el último punto. series: (nombre, columna, color)."""
    x = d[dim].astype(str)
    fmt, pre = ".1%" if pct else ",.0f", "" if pct else "$"
    fig = go.Figure()
    for nombre, col, color in series:
        y = d[col]
        etiquetas = [""] * (len(d) - 1) + [fmt_pct(y.iloc[-1]) if pct else fmt_cop(y.iloc[-1])]
        fig.add_scatter(
            name=nombre, x=x, y=y, mode="lines+markers+text", text=etiquetas,
            textposition="top center", textfont=dict(color=color, size=11), cliponaxis=False,
            line=dict(color=color, width=2), marker=dict(size=6, color=color),
            hovertemplate=f"<b>%{{x}}</b><br>{nombre}: {pre}%{{y:{fmt}}}<extra></extra>",
        )
    estilizar_figura(fig, 320, pct, False, margen_der=40)
    st.plotly_chart(fig, config=PLOT_CONFIG, key=key)


def titulo_grafico(texto):
    st.markdown(f'<div class="chart-title">{texto}</div>', unsafe_allow_html=True)


def sin_datos():
    st.caption("No hay registros para los filtros seleccionados.")


def grafico_formalidad(df, dim, titulo, tendencia=False):
    titulo_grafico(titulo)
    if df.empty:
        return sin_datos()
    d = agrupar(df, dim, "empleo_formal_pleno", ["mean"], por_n=not tendencia)
    d["no"] = 1 - d["mean"]
    series = [("Trabajo formal", "mean", PRIMARY, "#FFFFFF"), ("Trabajo no formal", "no", NOFORMAL, TEXT)]
    if tendencia:
        grafico_tendencia(d, dim, [s[:3] for s in series], True, key=f"ch_formalidad_{dim}")
    else:
        grafico_barras(d.sort_values("mean"), dim, series, True, apilado=True, key=f"ch_formalidad_{dim}")


def grafico_ingreso(df, dim, titulo, tendencia=False):
    titulo_grafico(titulo)
    if df.empty:
        return sin_datos()
    d = agrupar(df, dim, "ingreso_laboral_total", ["mean", "median"], por_n=not tendencia)
    if tendencia:
        grafico_tendencia(d, dim, [("Promedio", "mean", PRIMARY), ("Mediana", "median", ACCENT)],
                          False, key=f"ch_ingreso_{dim}")
    else:
        grafico_barras(d.sort_values("mean"), dim, [("Promedio", "mean", PRIMARY, MUTED)], False,
                       marcador=("Mediana", "median", ACCENT), key=f"ch_ingreso_{dim}")


# Organización por pestañas: cada fila es una lista de gráficos que se muestran lado a lado
GRUPOS = [
    ("Departamento", [[("departamento", "Por departamento", {})]]),
    ("Tiempo", [[("anio", "Por año", {"tendencia": True}), ("Mes Letras", "Por mes", {"tendencia": True})]]),
    ("Educación", [[("nivel_educativo", "Por nivel educativo", {})]]),
    ("Demografía", [[("sexo", "Por sexo", {}), ("estado_civil", "Por estado civil", {})],
                    [("etnia", "Por etnia", {})]]),
    ("Contrato", [[("tipo_contrato", "Por tipo de contrato", {}), ("posicion_ocupacional", "Por posición ocupacional", {})],
                  [("lugar_trabajo", "Por lugar de trabajo", {})]]),
    ("Sector", [[("sector_economico_seccion", "Por sector económico", {})]]),
    ("Oficio", [[("oficio_gran_grupo", "Por oficio", {})]]),
]


def bloque_graficos(df, fn):
    tabs = st.tabs([g[0] for g in GRUPOS])
    for tab, (_, filas) in zip(tabs, GRUPOS):
        with tab:
            for fila in filas:
                cols = st.columns(len(fila), gap="large")
                for col, (dim, tit, opts) in zip(cols, fila):
                    with col:
                        fn(df, dim, tit, **opts)


# ---------------------------------------------------------------------------
# COMPONENTES DE INTERFAZ
# ---------------------------------------------------------------------------
def kpi(valor, etiqueta, clase):
    st.markdown(f'<div class="kpi-v {clase}">{valor}</div><div class="kpi-l">{etiqueta}</div>',
                unsafe_allow_html=True)


def ir(pagina):
    st.session_state.page = pagina


NAV = [("inicio", "Inicio"), ("formalidad", "Formalidad"), ("ingresos", "Ingresos"),
       ("salario", "Salarios"), ("empleo", "Empleo")]


def barra_nav():
    with st.container(key="nav"):
        marca, *botones = st.columns([5, 1, 1.3, 1.1, 1.1, 1.1], vertical_alignment="center")
        marca.markdown('<div class="brand">Mercado laboral</div>', unsafe_allow_html=True)
        for col, (k, etiqueta) in zip(botones, NAV):
            col.button(etiqueta, key=f"nav_{k}", on_click=ir, args=(k,),
                       type="primary" if st.session_state.page == k else "secondary")
    st.markdown('<hr class="rule">', unsafe_allow_html=True)


FILTROS = [("anio", "Año"), ("Mes Letras", "Mes"), ("departamento", "Departamento"),
           ("sexo", "Sexo"), ("nivel_educativo", "Educación")]


def barra_filtros(df_raw, clave):
    """Filtros horizontales; vacío = Todos. Devuelve el DataFrame filtrado."""
    sel = {}
    with st.container(key="filters"):
        for col, (c, etiqueta) in zip(st.columns(len(FILTROS), gap="medium"), FILTROS):
            opciones = MESES_ORDEN if c == "Mes Letras" else sorted(df_raw[c].dropna().unique().tolist(), key=str)
            sel[c] = col.multiselect(etiqueta, opciones, placeholder="Todos", key=f"f_{clave}_{c}")
        df = df_raw
        for c, valores in sel.items():
            if valores:
                df = df[df[c].isin(valores)]
        st.markdown(f'<div class="aux">{fmt_n(len(df))} registros seleccionados de {fmt_n(len(df_raw))}</div>',
                    unsafe_allow_html=True)
    return df


def seccion(titulo, texto, items):
    cols = st.columns([1.1, 1.5, 1.5], gap="large")
    cols[0].markdown(f'<div class="sec-title">{titulo}</div><div class="sec-sub">{texto}</div>',
                     unsafe_allow_html=True)
    for col, (clave, cat, tit, txt, destino, pendiente) in zip(cols[1:], items):
        with col:
            tag = '<span class="tag">En desarrollo</span>' if pendiente else ""
            st.markdown(f'<div class="item"><div class="item-cat">{cat}{tag}</div>'
                        f'<div class="item-title">{tit}</div><div class="item-text">{txt}</div></div>',
                        unsafe_allow_html=True)
            with st.container(key=f"link_{clave}"):
                st.button("Abrir sección →" if pendiente else "Explorar →", key=f"go_{clave}",
                          on_click=ir, args=(destino,))


def encabezado(titulo, subtitulo):
    st.markdown(f'<div class="page-title">{titulo}</div><div class="page-sub">{subtitulo}</div>',
                unsafe_allow_html=True)


def pie():
    st.markdown('<div class="foot">Fuente: Gran Encuesta Integrada de Hogares (GEIH), DANE.</div>',
                unsafe_allow_html=True)


BIENVENIDA = {"role": "assistant", "content": "Hola. Estoy en desarrollo, pero pronto podré responder "
              "tus preguntas sobre los datos de cada sección."}
SUGERENCIAS = {
    "formalidad": ["¿Qué departamento tiene mayor formalidad?",
                   "¿Cómo cambia la formalidad según el nivel educativo?",
                   "¿Cuál es el porcentaje de trabajo formal?"],
    "ingresos": ["¿Qué diferencia hay entre promedio y mediana?",
                 "¿Cómo ha cambiado el ingreso por año?",
                 "¿Qué sector tiene mayor ingreso promedio?"],
}
SUGERENCIAS_BASE = ["¿Qué datos puedo consultar aquí?", "¿Qué significa trabajo formal?"]


def responder(pregunta, pagina):
    """Punto de integración del asistente: reemplazar por la llamada al modelo."""
    return ("Todavía no puedo responder preguntas. Estoy en desarrollo y pronto podré "
            "ayudarte a interpretar los datos de esta sección.")


def enviar(pregunta):
    st.session_state.chat += [
        {"role": "user", "content": pregunta},
        {"role": "assistant", "content": responder(pregunta, st.session_state.page)},
    ]


def reiniciar_chat():
    st.session_state.chat = [BIENVENIDA]


def asistente():
    """Chatbot fijo y desplegado en todas las secciones."""
    if "chat" not in st.session_state:
        st.session_state.chat = [BIENVENIDA]
    with st.container(key="chat"):
        st.markdown('<div class="chat-title">Asistente virtual<span class="tag">En desarrollo</span></div>'
                    '<div class="chat-sub">Pregunta sobre los datos de esta sección.</div>',
                    unsafe_allow_html=True)
        mensajes = st.container(height=320, border=False)
        if len(st.session_state.chat) == 1:
            for i, q in enumerate(SUGERENCIAS.get(st.session_state.page, SUGERENCIAS_BASE)):
                with st.container(key=f"sug_{i}"):
                    st.button(q, key=f"sug_btn_{i}", on_click=enviar, args=(q,))
        pregunta = st.chat_input("Escribe tu pregunta", key="chat_input")
        if pregunta:
            enviar(pregunta)
        if len(st.session_state.chat) > 1:
            with st.container(key="chat_reset"):
                st.button("Nueva conversación", key="chat_reset_btn", on_click=reiniciar_chat)
        with mensajes:
            for m in st.session_state.chat:
                avatar = ":material/smart_toy:" if m["role"] == "assistant" else ":material/person:"
                st.chat_message(m["role"], avatar=avatar).write(m["content"])


# ---------------------------------------------------------------------------
# PÁGINAS
# ---------------------------------------------------------------------------
def pagina_inicio(df_raw):
    a0, a1 = int(df_raw["anio"].min()), int(df_raw["anio"].max())
    periodo = f"{a0}–{a1}" if a0 != a1 else f"{a0}"
    c1, c2 = st.columns([1.7, 1], gap="large", vertical_alignment="bottom")
    c1.markdown(f'<div class="eyebrow">Análisis descriptivo · GEIH {periodo}</div>'
                '<div class="hero">Cómo se distribuyen<br>el empleo formal y los ingresos</div>',
                unsafe_allow_html=True)
    c2.markdown('<div class="hero-sub">Panorama de la población ocupada en Colombia. Compara formalidad e '
                'ingresos por departamento, educación, sexo, contrato, sector y oficio.</div>',
                unsafe_allow_html=True)
    st.markdown('<div style="height:2.2rem"></div>', unsafe_allow_html=True)

    pf, pnf = pct_formal_no_formal(df_raw)
    prom, med = promedio_mediana_ingreso(df_raw)
    with st.container(key="kpis"):
        k = st.columns(4)
        with k[0]: kpi(fmt_pct(pf), "Trabajo formal", "k-primary")
        with k[1]: kpi(fmt_pct(pnf), "Trabajo no formal", "k-teal")
        with k[2]: kpi(fmt_cop(prom), "Ingreso promedio", "k-primary")
        with k[3]: kpi(fmt_cop(med), "Mediana", "k-accent")

    st.markdown('<div style="height:3.2rem"></div>', unsafe_allow_html=True)
    seccion("Análisis descriptivo", "Explora cómo cambia el mercado laboral según las características de las personas ocupadas.", [
        ("formalidad", "Descriptivo", "Formalidad laboral",
         "Porcentaje de trabajo formal y no formal por departamento, tiempo, educación, demografía, contrato, sector y oficio.",
         "formalidad", False),
        ("ingresos", "Descriptivo", "Ingresos",
         "Promedio y mediana del ingreso laboral total con los mismos desgloses.", "ingresos", False),
    ])
    st.markdown('<div style="height:2.4rem"></div>', unsafe_allow_html=True)
    seccion("Modelos", "Herramientas de estimación para un perfil específico.", [
        ("salario", "Modelo", "Proyección de salario",
         "Estimar el ingreso esperado según el perfil de la persona.", "salario", True),
        ("empleo", "Modelo", "Probabilidad de empleo formal",
         "Estimar la probabilidad de conseguir un empleo formal según el perfil.", "empleo", True),
    ])
    pie()


def pagina_formalidad(df_raw):
    cabecera = st.container()
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    df = barra_filtros(df_raw, "formalidad")
    pf, pnf = pct_formal_no_formal(df)
    with cabecera, st.container(key="kpis"):
        c0, c1, c2 = st.columns([1.6, 1, 1], gap="large", vertical_alignment="center")
        with c0: encabezado("Formalidad laboral", "Proporción de personas ocupadas con empleo formal y no formal.")
        with c1: kpi(fmt_pct(pf), "Trabajo formal", "k-primary")
        with c2: kpi(fmt_pct(pnf), "Trabajo no formal", "k-teal")
    bloque_graficos(df, grafico_formalidad)
    pie()


def pagina_ingresos(df_raw):
    cabecera = st.container()
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    df = barra_filtros(df_raw, "ingresos")
    prom, med = promedio_mediana_ingreso(df)
    with cabecera, st.container(key="kpis"):
        c0, c1, c2 = st.columns([1.6, 1, 1], gap="large", vertical_alignment="center")
        with c0: encabezado("Ingresos", "Promedio y mediana del ingreso laboral total.")
        with c1: kpi(fmt_cop(prom), "Ingreso promedio", "k-primary")
        with c2: kpi(fmt_cop(med), "Mediana", "k-accent")
    bloque_graficos(df, grafico_ingreso)
    pie()


def pagina_vacia(titulo, subtitulo):
    encabezado(titulo, subtitulo)
    st.markdown('<div class="canvas-empty">Esta sección está en desarrollo</div>', unsafe_allow_html=True)
    pie()


# ---------------------------------------------------------------------------
# APP
# ---------------------------------------------------------------------------
inject_css()
if "page" not in st.session_state:
    st.session_state.page = "inicio"

df_raw = load_data(DATA_PATH)
barra_nav()

pagina = st.session_state.page
if pagina == "inicio":
    pagina_inicio(df_raw)
elif pagina == "formalidad":
    pagina_formalidad(df_raw)
elif pagina == "ingresos":
    pagina_ingresos(df_raw)
elif pagina == "salario":
    pagina_vacia("Proyección de salario", "Estimación del ingreso laboral según el perfil de la persona.")
else:
    pagina_vacia("Probabilidad de empleo formal", "Estimación de la probabilidad de conseguir un empleo formal.")

asistente()
