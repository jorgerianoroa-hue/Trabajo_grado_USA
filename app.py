"""
Mercado laboral (GEIH): landing + dashboards + secciones en desarrollo.
Ejecutar con:  streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Estadística descriptiva - Mercado laboral",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = Path(__file__).parent / "datos_reducidos.parquet"
MESES_ORDEN = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
               "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# ---------------------------------------------------------------------------
# TOKENS: papel claro frío; PRIMARY = formal / promedio, ACCENT = no formal / mediana
# ---------------------------------------------------------------------------
BG = "#F8FAFC"
SURFACE = "#FFFFFF"
TEXT = "#111827"
MUTED = "#64748B"
BORDER = "#E2E8F0"
GRID = "#E5E7EB"
PRIMARY = "#164E63"
SECONDARY = "#0F766E"
ACCENT = "#D97706"
FORMAL = PRIMARY
NON_FORMAL = SECONDARY
F_DISPLAY = "Manrope"
F_BODY = "Inter"


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: '{F_BODY}', sans-serif;
            color: {TEXT};
        }}

        .stApp {{
            background: {BG};
        }}

        .block-container {{
            max-width: 1480px;
            padding-top: 1.1rem;
            padding-bottom: 3rem;
            padding-left: 2.4rem;
            padding-right: 2.4rem;
        }}

        section[data-testid="stSidebar"] {{
            background: {SURFACE};
            border-right: 1px solid {BORDER};
        }}

        footer {{ visibility: hidden; }}

        h1, h2, h3, h4, h5 {{
            font-family: '{F_DISPLAY}', sans-serif;
            color: {TEXT};
            letter-spacing: -0.025em;
        }}

        /* Navegación superior */
        .topbar {{
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:2rem;
            padding:.35rem 0 .9rem;
            border-bottom:1px solid {BORDER};
            margin-bottom:1.5rem;
        }}

        .brand {{
            font-family:'{F_DISPLAY}',sans-serif;
            font-size:1.02rem;
            font-weight:700;
            letter-spacing:-.02em;
            white-space:nowrap;
        }}

        .brand-dot {{
            display:inline-block;
            width:8px;
            height:8px;
            border-radius:50%;
            background:{PRIMARY};
            margin-right:.45rem;
            vertical-align:1px;
        }}

        .nav-caption {{
            color:{MUTED};
            font-size:.76rem;
            letter-spacing:.08em;
            text-transform:uppercase;
        }}

        /* Botones */
        .stButton > button {{
            width:100%;
            background:transparent;
            color:{MUTED};
            border:0;
            border-bottom:2px solid transparent;
            border-radius:0;
            padding:.45rem .2rem;
            font-family:'{F_BODY}',sans-serif;
            font-weight:500;
            font-size:.88rem;
            transition:color .15s, border-color .15s;
        }}

        .stButton > button:hover {{
            color:{PRIMARY};
            border-color:{PRIMARY};
            background:transparent;
        }}

        .stButton > button[kind="primary"],
        .stButton > button[data-testid="stBaseButton-primary"] {{
            background:transparent;
            color:{PRIMARY};
            border-color:{PRIMARY};
        }}

        /* Hero */
        .eyebrow {{
            color:{PRIMARY};
            font-size:.76rem;
            font-weight:700;
            letter-spacing:.11em;
            text-transform:uppercase;
            margin-top:.5rem;
            margin-bottom:.65rem;
        }}

        .hero {{
            font-family:'{F_DISPLAY}',sans-serif;
            font-size:clamp(2.7rem, 5vw, 4.8rem);
            font-weight:700;
            line-height:.98;
            letter-spacing:-.055em;
            max-width:900px;
            margin:.4rem 0 1rem;
        }}

        .hero-sub {{
            color:{MUTED};
            font-size:1.05rem;
            line-height:1.6;
            max-width:760px;
            margin-bottom:2rem;
        }}

        .page-title {{
            font-family:'{F_DISPLAY}',sans-serif;
            font-size:2.5rem;
            font-weight:700;
            letter-spacing:-.045em;
            margin:.7rem 0 .35rem;
        }}

        .page-sub {{
            color:{MUTED};
            max-width:760px;
            font-size:.98rem;
            line-height:1.5;
            margin-bottom:1.4rem;
        }}

        /* KPI editorial */
        .kpi-strip {{
            display:grid;
            grid-template-columns:repeat(4,1fr);
            border-top:1px solid {BORDER};
            border-bottom:1px solid {BORDER};
            margin:1.5rem 0 2.5rem;
        }}

        .kpi-item {{
            padding:1.15rem 1.2rem 1.2rem 0;
            margin-right:1.2rem;
            border-right:1px solid {BORDER};
        }}

        .kpi-item:last-child {{
            border-right:0;
            margin-right:0;
        }}

        .kpi-value {{
            font-family:'{F_DISPLAY}',sans-serif;
            font-size:2.35rem;
            font-weight:700;
            line-height:1;
            letter-spacing:-.045em;
            font-variant-numeric:tabular-nums;
        }}

        .kpi-label {{
            color:{MUTED};
            font-size:.82rem;
            margin-top:.45rem;
        }}

        .kpi-primary {{ color:{PRIMARY}; }}
        .kpi-secondary {{ color:{SECONDARY}; }}
        .kpi-accent {{ color:{ACCENT}; }}

        .section-kicker {{
            color:{MUTED};
            font-size:.74rem;
            font-weight:700;
            letter-spacing:.11em;
            text-transform:uppercase;
            margin-top:2rem;
            margin-bottom:.35rem;
        }}

        .group-title {{
            font-family:'{F_DISPLAY}',sans-serif;
            font-size:1.45rem;
            font-weight:700;
            letter-spacing:-.025em;
            margin:.1rem 0 .25rem;
        }}

        .group-sub {{
            color:{MUTED};
            font-size:.9rem;
            margin-bottom:1rem;
        }}

        /* Cards muy ligeras */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background:{SURFACE};
            border:1px solid {BORDER};
            border-radius:10px;
            box-shadow:none;
        }}

        .card-title {{
            font-family:'{F_DISPLAY}',sans-serif;
            font-size:1.18rem;
            font-weight:700;
            margin-bottom:.3rem;
        }}

        .card-text {{
            color:{MUTED};
            font-size:.88rem;
            line-height:1.55;
            min-height:2.7rem;
            margin-bottom:.7rem;
        }}

        .tag {{
            color:{ACCENT};
            font-size:.68rem;
            font-weight:700;
            border:1px solid #F2C48B;
            border-radius:999px;
            padding:.12rem .5rem;
            margin-left:.45rem;
            vertical-align:middle;
        }}

        .canvas-empty {{
            min-height:360px;
            border:1px dashed {BORDER};
            border-radius:10px;
            display:flex;
            align-items:center;
            justify-content:center;
            color:{MUTED};
            font-size:.9rem;
            background:{SURFACE};
        }}

        .rule {{
            border:none;
            border-top:1px solid {BORDER};
            margin:1.5rem 0;
        }}

        .foot {{
            color:{MUTED};
            font-size:.78rem;
            margin-top:3rem;
            padding-top:1rem;
            border-top:1px solid {BORDER};
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap:1.4rem;
            border-bottom:1px solid {BORDER};
        }}

        .stTabs [data-baseweb="tab"] {{
            font-family:'{F_BODY}',sans-serif;
            font-weight:500;
            color:{MUTED};
            padding:.55rem 0 .7rem;
            background:transparent;
        }}

        .stTabs [aria-selected="true"] {{
            color:{TEXT};
        }}

        /* Selectores compactos */
        div[data-baseweb="select"] > div {{
            border-color:{BORDER};
            border-radius:8px;
            background:{SURFACE};
        }}

        /* Dataframes / métricas nativas */
        [data-testid="stMetricValue"] {{
            font-family:'{F_DISPLAY}',sans-serif;
            letter-spacing:-.04em;
        }}

        @media (max-width: 900px) {{
            .block-container {{
                padding-left:1rem;
                padding-right:1rem;
            }}
            .kpi-strip {{
                grid-template-columns:repeat(2,1fr);
            }}
            .kpi-item:nth-child(2) {{
                border-right:0;
            }}
        }}

        @media (max-width: 600px) {{
            .hero {{ font-size:2.55rem; }}
            .kpi-strip {{ grid-template-columns:1fr; }}
            .kpi-item {{
                border-right:0;
                border-bottom:1px solid {BORDER};
                padding-right:0;
                margin-right:0;
            }}
            .kpi-item:last-child {{ border-bottom:0; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )



# ---------------------------------------------------------------------------
# DATOS Y MEDIDAS
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
# GRÁFICOS
# ---------------------------------------------------------------------------
def estilizar_figura(fig, height=390, showlegend=True):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=F_BODY, size=11, color=TEXT),
        title=dict(
            font=dict(family=F_DISPLAY, size=16, color=TEXT),
            x=0, xanchor="left",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            font=dict(size=11, color=MUTED),
        ) if showlegend else dict(visible=False),
        height=height,
        margin=dict(t=58, b=28, l=8, r=8),
        hoverlabel=dict(
            bgcolor=SURFACE,
            bordercolor=BORDER,
            font=dict(family=F_BODY, size=12, color=TEXT),
        ),
    )
    return fig


def barras(d, dim, series, titulo, horizontal, pct, apilado=False):
    fig = go.Figure()
    fmt = ".0%" if pct else ",.0f"
    cat = d[dim].astype(str)

    for nombre, col, color in series:
        v = d[col]
        fig.add_bar(
            name=nombre,
            x=v if horizontal else cat,
            y=cat if horizontal else v,
            orientation="h" if horizontal else "v",
            marker=dict(
                color=color,
                line=dict(width=0),
            ),
            texttemplate=f"%{{{'x' if horizontal else 'y'}:{fmt}}}",
            cliponaxis=False,
            textposition="outside" if not apilado else "inside",
            textfont=dict(
                color=TEXT if not apilado else "#FFFFFF",
                size=10,
            ),
            hovertemplate=f"{nombre}: %{{{'x' if horizontal else 'y'}:{fmt}}}<extra></extra>",
        )

    fig.update_layout(
        title=titulo,
        barmode="stack" if apilado else "group",
        bargap=0.28,
    )

    val = dict(
        showgrid=True,
        gridcolor=GRID,
        gridwidth=1,
        zeroline=False,
        tickformat=fmt,
        showline=False,
    )

    if pct:
        val["range"] = [0, 1]

    cats = dict(
        showgrid=False,
        zeroline=False,
        type="category",
        automargin=True,
        showline=False,
    )

    if horizontal:
        fig.update_xaxes(**val)
        fig.update_yaxes(**cats)
        height = max(360, 28 * len(d) + 125)
    else:
        fig.update_yaxes(**val)
        fig.update_xaxes(**cats)
        height = 380

    estilizar_figura(fig, height=height)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def grafico_tendencia(df, dim, titulo, col="ingreso_laboral_total"):
    d = agrupar(df, dim, col, ["mean", "median"], por_n=False)
    x = d[dim].astype(str)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x,
        y=d["mean"],
        mode="lines+markers",
        name="Promedio",
        line=dict(color=PRIMARY, width=2.5),
        marker=dict(size=6, color=PRIMARY),
        hovertemplate="Promedio: $%{y:,.0f}<extra></extra>",
    ))

    if dim == "anio":
        fig.add_trace(go.Scatter(
            x=x,
            y=d["median"],
            mode="lines+markers",
            name="Mediana",
            line=dict(color=ACCENT, width=2, dash="dot"),
            marker=dict(size=5, color=ACCENT),
            hovertemplate="Mediana: $%{y:,.0f}<extra></extra>",
        ))

    fig.update_layout(title=titulo)
    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        tickprefix="$",
        tickformat=",.0f",
        showline=False,
    )
    fig.update_xaxes(showgrid=False, showline=False, type="category")

    estilizar_figura(fig, height=340)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def grafico_formalidad(df, dim, titulo, horizontal=False, por_n=True):
    d = agrupar(df, dim, "empleo_formal_pleno", ["mean"], por_n)
    d["no"] = 1 - d["mean"]
    if horizontal:
        d = d.sort_values("mean", ascending=True)
    barras(
        d,
        dim,
        [
            ("Trabajo formal", "mean", PRIMARY),
            ("Trabajo no formal", "no", SECONDARY),
        ],
        titulo,
        horizontal,
        pct=True,
        apilado=True,
    )


def grafico_ingreso(df, dim, titulo, horizontal=False, por_n=True):
    if dim in ("anio", "Mes Letras"):
        grafico_tendencia(
            df,
            dim,
            titulo,
            col="ingreso_laboral_total",
        )
        return

    d = agrupar(df, dim, "ingreso_laboral_total", ["mean", "median"], por_n)
    if horizontal:
        d = d.sort_values("mean", ascending=True)

    series = [("Promedio", "mean", PRIMARY)]
    if dim == "anio":
        series.append(("Mediana", "median", ACCENT))

    barras(d, dim, series, titulo, horizontal, pct=False)


GRUPOS = [
    ("Departamento / Año / Mes", [
        [("departamento", "Por Departamento", {})],
        [("anio", "Por Año", {"por_n": False}), ("Mes Letras", "Por Mes", {"por_n": False})]]),
    ("Educación / Estado civil / Etnia / Sexo", [
        [("nivel_educativo", "Por Educación", {})],
        [("estado_civil", "Por Estado Civil", {})],
        [("etnia", "Por Etnia", {}), ("sexo", "Por Sexo", {})]]),
    ("Contrato / Posición / Lugar", [
        [("tipo_contrato", "Por Tipo de Contrato", {})],
        [("posicion_ocupacional", "Por Posición Ocupacional", {})],
        [("lugar_trabajo", "Por Lugar de Trabajo", {})]]),
    ("Sector económico", [[("sector_economico_seccion", "Por Sector Económico", {"horizontal": True})]]),
    ("Oficio", [[("oficio_gran_grupo", "Por Oficio", {"horizontal": True})]]),
]


def bloque_graficos(df, fn):
    tabs = st.tabs([g[0] for g in GRUPOS])
    for tab, (_, filas) in zip(tabs, GRUPOS):
        with tab:
            for fila in filas:
                cols = st.columns(len(fila)) if len(fila) > 1 else [st.container()]
                for col, (dim, tit, opts) in zip(cols, fila):
                    with col:
                        fn(df, dim, tit, **opts)


# ---------------------------------------------------------------------------
# COMPONENTES DE INTERFAZ
# ---------------------------------------------------------------------------
def kpi_block(value, label, color="kpi-primary"):
    return f"""
    <div class="kpi-item">
        <div class="kpi-value {color}">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """


def kpis_formalidad(df):
    pf, pnf = pct_formal_no_formal(df)
    st.markdown(
        '<div class="kpi-strip">'
        + kpi_block(f"{pf:.1%}", "Trabajo formal", "kpi-primary")
        + kpi_block(f"{pnf:.1%}", "Trabajo no formal", "kpi-secondary")
        + '</div>',
        unsafe_allow_html=True,
    )


def kpis_ingreso(df):
    prom, med = promedio_mediana_ingreso(df)
    st.markdown(
        '<div class="kpi-strip">'
        + kpi_block(f"${prom:,.0f}", "Promedio de ingreso laboral", "kpi-primary")
        + kpi_block(f"${med:,.0f}", "Mediana", "kpi-accent")
        + '</div>',
        unsafe_allow_html=True,
    )


def ir(pagina):
    st.session_state.page = pagina


NAV = [("inicio", "Inicio"), ("formalidad", "Formalidad"), ("ingresos", "Ingresos"),
       ("salario", "Proyección salarial"), ("empleo", "Empleo formal")]


def barra_nav():
    marca, *botones = st.columns([2.1, 1, 1, 1, 1.1, 1.25], vertical_alignment="center")
    marca.markdown(
        '<div class="brand"><span class="brand-dot"></span>Mercado laboral</div>',
        unsafe_allow_html=True,
    )
    for col, (k, etiqueta) in zip(botones, NAV):
        with col:
            st.button(
                etiqueta,
                key=f"nav_{k}",
                on_click=ir,
                args=(k,),
                type="primary" if st.session_state.page == k else "secondary",
            )


def tarjeta(clave, titulo, texto, boton, destino, pendiente=False):
    with st.container(border=True):
        marca = '<span class="is-pending"></span>' if pendiente else ""
        tag = '<span class="tag">En desarrollo</span>' if pendiente else ""
        st.markdown(f'{marca}<div class="card-title">{titulo}{tag}</div><div class="card-text">{texto}</div>',
                    unsafe_allow_html=True)
        st.button(boton, key=f"card_{clave}", on_click=ir, args=(destino,))


def cabecera(titulo, subtitulo):
    st.markdown('<div class="eyebrow">Mercado laboral · GEIH</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-title">{titulo}</div><div class="page-sub">{subtitulo}</div>',
        unsafe_allow_html=True,
    )


def pagina_vacia(titulo, subtitulo):
    cabecera(titulo, subtitulo)
    st.markdown('<div class="canvas-empty">Esta sección está en desarrollo</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# PÁGINAS
# ---------------------------------------------------------------------------
def pagina_inicio(df, df_raw):
    a0, a1 = int(df_raw["anio"].min()), int(df_raw["anio"].max())
    pf, pnf = pct_formal_no_formal(df)
    prom, med = promedio_mediana_ingreso(df)

    st.markdown('<div class="eyebrow">GEIH · DANE · Análisis descriptivo</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero">Cómo se distribuyen el empleo formal y los ingresos en Colombia</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="hero-sub">Explora la población ocupada según la GEIH entre {a0} y {a1}. '
        'Compara formalidad e ingresos por territorio, educación, sexo, contrato, sector económico y otras dimensiones.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="kpi-strip">'
        + kpi_block(f"{pf:.1%}", "Trabajo formal", "kpi-primary")
        + kpi_block(f"{pnf:.1%}", "Trabajo no formal", "kpi-secondary")
        + kpi_block(f"${prom:,.0f}", "Ingreso promedio", "kpi-primary")
        + kpi_block(f"${med:,.0f}", "Mediana", "kpi-accent")
        + '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-kicker">Análisis descriptivo</div>', unsafe_allow_html=True)
    st.markdown('<div class="group-title">Dos perspectivas para entender el mercado laboral</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="group-sub">Selecciona un tablero para explorar los principales indicadores y sus desgloses.</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2, gap="large")
    with c1:
        tarjeta(
            "formalidad",
            "Formalidad laboral",
            "Participación del empleo formal y no formal por departamento, tiempo, educación, "
            "demografía, contrato, posición, lugar, sector y oficio.",
            "Explorar →",
            "formalidad",
        )
    with c2:
        tarjeta(
            "ingresos",
            "Ingresos laborales",
            "Promedio y mediana del ingreso laboral total, con comparaciones por las principales dimensiones de la GEIH.",
            "Explorar →",
            "ingresos",
        )

    st.markdown('<div class="section-kicker">Modelos</div>', unsafe_allow_html=True)
    st.markdown('<div class="group-title">Nuevas herramientas analíticas</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="group-sub">Secciones preparadas para incorporar modelos predictivos.</div>',
        unsafe_allow_html=True,
    )

    c3, c4 = st.columns(2, gap="large")
    with c3:
        tarjeta(
            "salario",
            "Proyección de salario",
            "Estimar el ingreso esperado según las características observables del perfil.",
            "Abrir →",
            "salario",
            pendiente=True,
        )
    with c4:
        tarjeta(
            "empleo",
            "Probabilidad de empleo formal",
            "Estimar la probabilidad de acceder a un empleo formal según el perfil.",
            "Abrir →",
            "empleo",
            pendiente=True,
        )

    st.markdown('<div class="foot">Fuente: Gran Encuesta Integrada de Hogares (GEIH), DANE.</div>', unsafe_allow_html=True)


def pagina_formalidad(df):
    cabecera("Formalidad laboral", "Proporción de personas ocupadas con empleo formal y no formal.")
    kpis_formalidad(df)
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    bloque_graficos(df, grafico_formalidad)


def pagina_ingresos(df):
    cabecera("Ingresos", "Promedio y mediana del ingreso laboral total.")
    kpis_ingreso(df)
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    bloque_graficos(df, grafico_ingreso)


# ---------------------------------------------------------------------------
# APP
# ---------------------------------------------------------------------------
inject_css()
if "page" not in st.session_state:
    st.session_state.page = "inicio"

df_raw = load_data(DATA_PATH)

anios = sorted(df_raw["anio"].unique())

with st.expander("Filtros de análisis", expanded=True):
    f1, f2, f3 = st.columns([1, 1, 2], gap="medium")
    with f1:
        anios_sel = st.multiselect("Año", anios, default=anios)
    with f2:
        meses_sel = st.multiselect("Mes", MESES_ORDEN, default=MESES_ORDEN)
    with f3:
        st.caption("Cobertura seleccionada")
        st.markdown(
            f"**{len(df_raw[df_raw['anio'].isin(anios_sel) & df_raw['Mes Letras'].isin(meses_sel)]):,}** "
            f"registros de **{len(df_raw):,}**",
        )

df = df_raw[
    df_raw["anio"].isin(anios_sel)
    & df_raw["Mes Letras"].isin(meses_sel)
]

barra_nav()
pagina = st.session_state.page
if pagina == "inicio":
    pagina_inicio(df, df_raw)
elif pagina == "formalidad":
    pagina_formalidad(df)
elif pagina == "ingresos":
    pagina_ingresos(df)
elif pagina == "salario":
    pagina_vacia("Proyección de salario", "Estimación del ingreso laboral según el perfil de la persona.")
else:
    pagina_vacia("Probabilidad de empleo formal", "Estimación de la probabilidad de conseguir un empleo formal.")
