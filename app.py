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
# TOKENS: papel claro frío; PETROL = formal / promedio, OCRE = no formal / mediana
# ---------------------------------------------------------------------------
BG, SURFACE = "#F6F7F4", "rgba(255,255,255,0.72)"
INK, INK_MUTED = "#1C1F23", "#6B7078"
HAIRLINE, LINE = "#E1E3DD", "#C9CCC3"
GRID_DOT = "rgba(28, 31, 35, 0.10)"
PETROL, OCRE = "#1F3A5F", "#C98A2C"
F_DISPLAY, F_BODY = "Space Grotesk", "Inter"


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');
        html, body, [class*="css"] {{ font-family:'{F_BODY}',sans-serif; color:{INK}; }}
        .stApp {{ background-color:{BG}; background-image:radial-gradient({GRID_DOT} 1px, transparent 1px); background-size:26px 26px; }}
        .block-container {{ max-width:1160px; padding-top:1.6rem; padding-bottom:4rem; }}
        section[data-testid="stSidebar"] {{ background:{BG}; border-right:1px solid {HAIRLINE}; }}
        footer {{ visibility:hidden; }}
        h1,h2,h3,h5 {{ font-family:'{F_DISPLAY}',sans-serif; font-weight:600; letter-spacing:-0.01em; }}

        /* Botones: secundario = contorno, primario = relleno petrol */
        .stButton > button {{
            width:100%; background:transparent; color:{INK}; border:1px solid {LINE};
            border-radius:999px; padding:.42rem 1rem; font-family:'{F_DISPLAY}',sans-serif;
            font-weight:500; font-size:.92rem; transition:border-color .15s, color .15s, background .15s;
        }}
        .stButton > button:hover {{ border-color:{PETROL}; color:{PETROL}; background:transparent; }}
        .stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {{
            background:{PETROL}; color:{BG}; border-color:{PETROL};
        }}
        .stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {{
            background:#2A4C7A; color:{BG};
        }}

        /* Contenedores con borde = tarjetas */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background:{SURFACE}; border-color:{HAIRLINE}; border-radius:12px;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.is-pending) {{
            background:transparent; border-style:dashed; border-color:{LINE};
        }}

        .brand {{ font-family:'{F_DISPLAY}',sans-serif; font-weight:600; font-size:1.05rem; padding-top:.35rem; }}
        .hero {{ font-family:'{F_DISPLAY}',sans-serif; font-size:3.6rem; font-weight:700; line-height:1.04; letter-spacing:-0.025em; margin:3.2rem 0 1rem; max-width:760px; }}
        .hero-sub {{ color:{INK_MUTED}; font-size:1.08rem; line-height:1.55; max-width:600px; margin-bottom:2.4rem; }}
        .page-title {{ font-family:'{F_DISPLAY}',sans-serif; font-size:2.4rem; font-weight:700; letter-spacing:-0.02em; margin:2rem 0 .4rem; }}
        .page-sub {{ color:{INK_MUTED}; max-width:620px; margin-bottom:1.4rem; }}
        .group-title {{ font-family:'{F_DISPLAY}',sans-serif; font-size:1.15rem; font-weight:600; margin:2.6rem 0 .2rem; }}
        .group-sub {{ color:{INK_MUTED}; font-size:.92rem; margin-bottom:1rem; }}
        .kpi-value {{ font-family:'{F_DISPLAY}',sans-serif; font-size:2.4rem; font-weight:600; line-height:1.1; font-variant-numeric:tabular-nums; }}
        .kpi-label {{ color:{INK_MUTED}; font-size:.88rem; margin-top:.15rem; }}
        .kpi-petrol {{ color:{PETROL}; }} .kpi-ocre {{ color:{OCRE}; }}
        .card-title {{ font-family:'{F_DISPLAY}',sans-serif; font-size:1.3rem; font-weight:600; margin-bottom:.35rem; }}
        .card-text {{ color:{INK_MUTED}; font-size:.95rem; line-height:1.5; margin-bottom:1rem; min-height:3rem; }}
        .tag {{ font-family:'{F_BODY}',sans-serif; font-size:.74rem; font-weight:500; color:{OCRE}; border:1px solid {OCRE}; border-radius:999px; padding:.05rem .55rem; margin-left:.6rem; vertical-align:middle; }}
        .canvas-empty {{ min-height:440px; border:1.5px dashed {LINE}; border-radius:14px; display:flex; align-items:center; justify-content:center; color:{INK_MUTED}; font-size:.95rem; }}
        .rule {{ border:none; border-top:1px solid {HAIRLINE}; margin:1.2rem 0 1.4rem; }}
        .foot {{ color:{INK_MUTED}; font-size:.82rem; margin-top:3.5rem; }}
        .stTabs [data-baseweb="tab-list"] {{ gap:1.6rem; border-bottom:1px solid {HAIRLINE}; }}
        .stTabs [data-baseweb="tab"] {{ font-family:'{F_DISPLAY}',sans-serif; font-weight:500; color:{INK_MUTED}; padding-bottom:.6rem; }}
        .stTabs [aria-selected="true"] {{ color:{INK}; }}
        @media (max-width:700px) {{ .hero {{ font-size:2.4rem; }} }}
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
def barras(d, dim, series, titulo, horizontal, pct, apilado=False):
    fig = go.Figure()
    fmt, eje = (".0%" if pct else ",.0f"), ("x" if horizontal else "y")
    cat = d[dim].astype(str)
    for nombre, col, color in series:
        v = d[col]
        fig.add_bar(
            name=nombre, x=v if horizontal else cat, y=cat if horizontal else v,
            orientation="h" if horizontal else "v", marker_color=color,
            texttemplate=f"%{{{eje}:{fmt}}}", cliponaxis=False,
            textposition="inside" if apilado else "outside",
            textfont=dict(color="#FFFFFF" if apilado else INK_MUTED, size=11),
        )
    fig.update_layout(
        title=dict(text=titulo, font=dict(family=F_DISPLAY, size=15, color=INK), x=0, xanchor="left"),
        barmode="stack" if apilado else "group", bargap=0.35,
        font=dict(family=F_BODY, size=11, color=INK_MUTED),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.04, x=0, font=dict(size=12)),
        height=max(380, 30 * len(d) + 140) if horizontal else 380,
        margin=dict(t=70, b=20, l=10, r=10),
    )
    val = dict(showgrid=True, gridcolor=HAIRLINE, zeroline=False, tickformat=fmt)
    if pct:
        val["range"] = [0, 1]
    cats = dict(showgrid=False, zeroline=False, type="category", automargin=True)
    if horizontal:
        fig.update_xaxes(**val); fig.update_yaxes(**cats)
    else:
        fig.update_yaxes(**val); fig.update_xaxes(**cats)
    st.plotly_chart(fig, use_container_width=True)


def grafico_formalidad(df, dim, titulo, horizontal=False, por_n=True):
    d = agrupar(df, dim, "empleo_formal_pleno", ["mean"], por_n)
    d["no"] = 1 - d["mean"]
    if horizontal:
        d = d.sort_values("mean")
    barras(d, dim, [("Trabajo formal", "mean", PETROL), ("Trabajo no formal", "no", OCRE)],
           titulo, horizontal, pct=True, apilado=True)


def grafico_ingreso(df, dim, titulo, horizontal=False, por_n=True):
    d = agrupar(df, dim, "ingreso_laboral_total", ["mean", "median"], por_n)
    if horizontal:
        d = d.sort_values("mean")
    series = [("Promedio", "mean", PETROL)]
    if dim == "anio":  # igual que el reporte original: mediana solo por año
        series.append(("Mediana", "median", OCRE))
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
def kpi_block(value, label, color):
    st.markdown(f'<div class="kpi-value {color}">{value}</div><div class="kpi-label">{label}</div>',
                unsafe_allow_html=True)


def kpis_formalidad(df):
    pf, pnf = pct_formal_no_formal(df)
    c1, c2 = st.columns(2)
    with c1: kpi_block(f"{pf:.1%}", "Trabajo formal", "kpi-petrol")
    with c2: kpi_block(f"{pnf:.1%}", "Trabajo no formal", "kpi-ocre")


def kpis_ingreso(df):
    prom, med = promedio_mediana_ingreso(df)
    c1, c2 = st.columns(2)
    with c1: kpi_block(f"${prom:,.0f}", "Promedio de ingreso laboral", "kpi-petrol")
    with c2: kpi_block(f"${med:,.0f}", "Mediana", "kpi-ocre")


def ir(pagina):
    st.session_state.page = pagina


NAV = [("inicio", "Inicio"), ("formalidad", "Formalidad"), ("ingresos", "Ingresos"),
       ("salario", "Proyección salarial"), ("empleo", "Empleo formal")]


def barra_nav():
    marca, *botones = st.columns([1.4, 1, 1, 1, 1.4, 1.2], vertical_alignment="center")
    marca.markdown('<div class="brand">◆ Mercado laboral</div>', unsafe_allow_html=True)
    for col, (k, etiqueta) in zip(botones, NAV):
        col.button(etiqueta, key=f"nav_{k}", on_click=ir, args=(k,),
                   type="primary" if st.session_state.page == k else "secondary")
    st.markdown('<hr class="rule">', unsafe_allow_html=True)


def tarjeta(clave, titulo, texto, boton, destino, pendiente=False):
    with st.container(border=True):
        marca = '<span class="is-pending"></span>' if pendiente else ""
        tag = '<span class="tag">En desarrollo</span>' if pendiente else ""
        st.markdown(f'{marca}<div class="card-title">{titulo}{tag}</div><div class="card-text">{texto}</div>',
                    unsafe_allow_html=True)
        st.button(boton, key=f"card_{clave}", on_click=ir, args=(destino,))


def cabecera(titulo, subtitulo):
    st.markdown(f'<div class="page-title">{titulo}</div><div class="page-sub">{subtitulo}</div>',
                unsafe_allow_html=True)


def pagina_vacia(titulo, subtitulo):
    cabecera(titulo, subtitulo)
    st.markdown('<div class="canvas-empty">Esta sección está en desarrollo</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# PÁGINAS
# ---------------------------------------------------------------------------
def pagina_inicio(df, df_raw):
    a0, a1 = int(df_raw["anio"].min()), int(df_raw["anio"].max())
    st.markdown('<div class="hero">Cómo se reparten el empleo formal y los ingresos en Colombia</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">Estadística descriptiva de la población ocupada según la GEIH, '
                f'de {a0} a {a1}. Explora cada indicador por departamento, educación, sexo, '
                f'tipo de contrato, sector y más.</div>', unsafe_allow_html=True)

    pf, pnf = pct_formal_no_formal(df)
    prom, med = promedio_mediana_ingreso(df)
    with st.container(border=True):
        c = st.columns(4)
        with c[0]: kpi_block(f"{pf:.1%}", "Trabajo formal", "kpi-petrol")
        with c[1]: kpi_block(f"{pnf:.1%}", "Trabajo no formal", "kpi-ocre")
        with c[2]: kpi_block(f"${prom:,.0f}", "Promedio de ingreso laboral", "kpi-petrol")
        with c[3]: kpi_block(f"${med:,.0f}", "Mediana", "kpi-ocre")

    st.markdown('<div class="group-title">Análisis descriptivo</div>'
                '<div class="group-sub">Los dos tableros del reporte original.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        tarjeta("formalidad", "Formalidad laboral",
                "Porcentaje de trabajo formal y no formal por departamento, año, mes, educación, "
                "estado civil, etnia, sexo, contrato, posición, lugar, sector y oficio.",
                "Ver formalidad", "formalidad")
    with c2:
        tarjeta("ingresos", "Ingresos",
                "Promedio y mediana del ingreso laboral total con los mismos desgloses.",
                "Ver ingresos", "ingresos")

    st.markdown('<div class="group-title">Modelos</div>'
                '<div class="group-sub">Secciones nuevas, aún sin contenido.</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        tarjeta("salario", "Proyección de salario",
                "Estimar el ingreso esperado según el perfil de la persona.",
                "Abrir proyección salarial", "salario", pendiente=True)
    with c4:
        tarjeta("empleo", "Probabilidad de empleo formal",
                "Estimar la probabilidad de conseguir un empleo formal según el perfil.",
                "Abrir probabilidad de empleo formal", "empleo", pendiente=True)

    st.markdown('<div class="foot">Fuente: Gran Encuesta Integrada de Hogares (GEIH), DANE.</div>',
                unsafe_allow_html=True)


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

st.sidebar.markdown("**Filtros**")
anios = sorted(df_raw["anio"].unique())
anios_sel = st.sidebar.multiselect("Año", anios, default=anios)
meses_sel = st.sidebar.multiselect("Mes", MESES_ORDEN, default=MESES_ORDEN)
df = df_raw[df_raw["anio"].isin(anios_sel) & df_raw["Mes Letras"].isin(meses_sel)]
st.sidebar.caption(f"{len(df):,} registros de {len(df_raw):,}")

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
