"""
Dashboard de Estadística Descriptiva - Mercado Laboral (GEIH)
Replica en Streamlit del reporte de Power BI "Estadistica_descriptiva.pbix"

Ejecutar con:
    streamlit run app.py
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Estadística Descriptiva - Mercado Laboral",
    page_icon="◆",
    layout="wide",
)

DATA_PATH = "datos_reducidos.parquet"

MESES_ORDEN = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]

# ---------------------------------------------------------------------------
# TOKENS DE DISEÑO
# Dos acentos con significado fijo en todo el tablero: PETROL = métrica
# principal (formal / promedio), OCRE = métrica de comparación (no formal /
# mediana). El mismo par de colores se usa en ambos bloques para que el
# lenguaje visual se aprenda una sola vez.
# ---------------------------------------------------------------------------
BG_PAGE = "#F5F4F1"
INK = "#1B1F1D"
INK_MUTED = "#6B7570"
HAIRLINE = "#D9D6CD"
PETROL = "#1F3A5F"
OCRE = "#C98A2C"

FONT_DISPLAY = "Fraunces"
FONT_BODY = "IBM Plex Sans"


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

        html, body, [class*="css"] {{
            font-family: '{FONT_BODY}', sans-serif;
            color: {INK};
        }}
        .block-container {{
            padding-top: 2.5rem;
            max-width: 1200px;
        }}
        h1, h2, h3 {{
            font-family: '{FONT_BODY}', sans-serif;
            font-weight: 600;
            letter-spacing: -0.01em;
        }}
        .app-header {{
            font-family: '{FONT_DISPLAY}', serif;
            font-size: 2.4rem;
            font-weight: 600;
            line-height: 1.15;
            margin-bottom: 0.2rem;
        }}
        .app-subhead {{
            color: {INK_MUTED};
            font-size: 0.95rem;
            margin-bottom: 1.4rem;
        }}
        .app-rule {{
            border: none;
            border-top: 1px solid {HAIRLINE};
            margin: 0 0 1.6rem 0;
        }}
        .kpi-value {{
            font-family: '{FONT_DISPLAY}', serif;
            font-size: 2.6rem;
            font-weight: 600;
            line-height: 1.1;
        }}
        .kpi-label {{
            color: {INK_MUTED};
            font-size: 0.88rem;
            margin-top: 0.15rem;
        }}
        .kpi-petrol {{ color: {PETROL}; }}
        .kpi-ocre {{ color: {OCRE}; }}
        section[data-testid="stSidebar"] {{
            border-right: 1px solid {HAIRLINE};
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 1.6rem;
            border-bottom: 1px solid {HAIRLINE};
        }}
        .stTabs [data-baseweb="tab"] {{
            font-family: '{FONT_BODY}', sans-serif;
            font-weight: 500;
            color: {INK_MUTED};
            padding-bottom: 0.6rem;
        }}
        .stTabs [aria-selected="true"] {{
            color: {INK};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_block(value: str, label: str, color_class: str):
    st.markdown(
        f"""
        <div>
            <div class="kpi-value {color_class}">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_minimal_layout(fig: go.Figure, titulo: str, horizontal: bool, pct: bool):
    fig.update_layout(
        title=dict(text=titulo, font=dict(family=FONT_BODY, size=15, color=INK), x=0, xanchor="left"),
        barmode="group",
        bargap=0.35,
        font=dict(family=FONT_BODY, size=12, color=INK_MUTED),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.04, x=0,
            font=dict(size=12, color=INK_MUTED),
        ),
        height=380,
        margin=dict(t=70, b=20, l=10, r=10),
    )
    grid_kwargs = dict(showgrid=True, gridcolor=HAIRLINE, zeroline=False)
    no_grid_kwargs = dict(showgrid=False, zeroline=False)
    if horizontal:
        fig.update_xaxes(tickformat=".0%" if pct else ",.0f", **grid_kwargs)
        fig.update_yaxes(**no_grid_kwargs)
    else:
        fig.update_yaxes(tickformat=".0%" if pct else ",.0f", **grid_kwargs)
        fig.update_xaxes(**no_grid_kwargs)


# ---------------------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Cargando datos...")
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_parquet(path)

    df["Mes Letras"] = pd.Categorical(
        df["mes"].map(dict(zip(range(1, 13), MESES_ORDEN))),
        categories=MESES_ORDEN,
        ordered=True,
    )

    cat_cols = [
        "departamento", "sexo", "estado_civil", "etnia", "nivel_educativo",
        "tipo_contrato", "posicion_ocupacional", "lugar_trabajo",
        "sector_economico_seccion", "oficio_gran_grupo",
    ]
    for c in cat_cols:
        df[c] = df[c].astype("category")

    return df


# ---------------------------------------------------------------------------
# MEDIDAS (réplica exacta de las medidas DAX del .pbix)
# ---------------------------------------------------------------------------
def pct_formal_no_formal(df: pd.DataFrame) -> tuple[float, float]:
    total = len(df)
    if total == 0:
        return 0.0, 0.0
    formal = (df["empleo_formal_pleno"] == 1).sum()
    no_formal = (df["empleo_formal_pleno"] == 0).sum()
    return formal / total, no_formal / total


def promedio_mediana_ingreso(df: pd.DataFrame) -> tuple[float, float]:
    if len(df) == 0:
        return 0.0, 0.0
    return df["ingreso_laboral_total"].mean(), df["ingreso_laboral_total"].median()


def formalidad_por_dimension(df: pd.DataFrame, dim: str) -> pd.DataFrame:
    out = (
        df.groupby(dim, observed=True)["empleo_formal_pleno"]
        .agg(["mean", "count"])
        .reset_index()
    )
    out.columns = [dim, "pct_formal", "n"]
    out["pct_no_formal"] = 1 - out["pct_formal"]
    return out.sort_values("n", ascending=False)


def ingreso_por_dimension(df: pd.DataFrame, dim: str) -> pd.DataFrame:
    out = (
        df.groupby(dim, observed=True)["ingreso_laboral_total"]
        .agg(["mean", "median", "count"])
        .reset_index()
    )
    out.columns = [dim, "promedio", "mediana", "n"]
    return out.sort_values("n", ascending=False)


# ---------------------------------------------------------------------------
# COMPONENTES VISUALES
# ---------------------------------------------------------------------------
def kpi_formalidad(df: pd.DataFrame):
    pf, pnf = pct_formal_no_formal(df)
    c1, c2 = st.columns(2)
    with c1:
        kpi_block(f"{pf:.1%}", "Trabajo formal", "kpi-petrol")
    with c2:
        kpi_block(f"{pnf:.1%}", "Trabajo no formal", "kpi-ocre")


def kpi_ingreso(df: pd.DataFrame):
    prom, med = promedio_mediana_ingreso(df)
    c1, c2 = st.columns(2)
    with c1:
        kpi_block(f"${prom:,.0f}", "Promedio ingreso total", "kpi-petrol")
    with c2:
        kpi_block(f"${med:,.0f}", "Mediana", "kpi-ocre")


def grafico_formalidad(df: pd.DataFrame, dim: str, titulo: str, top_n: int = 20, horizontal: bool = False):
    data = formalidad_por_dimension(df, dim).head(top_n)
    if horizontal:
        data = data.sort_values("pct_formal")
    fig = go.Figure()
    fig.add_bar(
        name="Trabajo formal",
        x=data["pct_formal"] if horizontal else data[dim],
        y=data[dim] if horizontal else data["pct_formal"],
        orientation="h" if horizontal else "v",
        marker_color=PETROL,
        texttemplate="%{x:.0%}" if horizontal else "%{y:.0%}",
        textposition="outside",
        textfont=dict(color=INK_MUTED, size=11),
    )
    fig.add_bar(
        name="Trabajo no formal",
        x=data["pct_no_formal"] if horizontal else data[dim],
        y=data[dim] if horizontal else data["pct_no_formal"],
        orientation="h" if horizontal else "v",
        marker_color=OCRE,
        texttemplate="%{x:.0%}" if horizontal else "%{y:.0%}",
        textposition="outside",
        textfont=dict(color=INK_MUTED, size=11),
    )
    apply_minimal_layout(fig, titulo, horizontal, pct=True)
    st.plotly_chart(fig, use_container_width=True)


def grafico_ingreso(df: pd.DataFrame, dim: str, titulo: str, top_n: int = 20, horizontal: bool = False, incluir_mediana: bool = True):
    data = ingreso_por_dimension(df, dim).head(top_n)
    if horizontal:
        data = data.sort_values("promedio")
    fig = go.Figure()
    fig.add_bar(
        name="Promedio",
        x=data["promedio"] if horizontal else data[dim],
        y=data[dim] if horizontal else data["promedio"],
        orientation="h" if horizontal else "v",
        marker_color=PETROL,
        texttemplate="%{x:,.0f}" if horizontal else "%{y:,.0f}",
        textposition="outside",
        textfont=dict(color=INK_MUTED, size=11),
    )
    if incluir_mediana:
        fig.add_bar(
            name="Mediana",
            x=data["mediana"] if horizontal else data[dim],
            y=data[dim] if horizontal else data["mediana"],
            orientation="h" if horizontal else "v",
            marker_color=OCRE,
            texttemplate="%{x:,.0f}" if horizontal else "%{y:,.0f}",
            textposition="outside",
            textfont=dict(color=INK_MUTED, size=11),
        )
    apply_minimal_layout(fig, titulo, horizontal, pct=False)
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# CARGA + FILTROS GLOBALES
# ---------------------------------------------------------------------------
inject_css()
df_raw = load_data(DATA_PATH)

st.sidebar.markdown("**Filtros**")
anios_sel = st.sidebar.multiselect(
    "Año", sorted(df_raw["anio"].unique()), default=sorted(df_raw["anio"].unique())
)
meses_sel = st.sidebar.multiselect(
    "Mes", MESES_ORDEN, default=MESES_ORDEN
)

df = df_raw[df_raw["anio"].isin(anios_sel) & df_raw["Mes Letras"].isin(meses_sel)]

st.sidebar.markdown(
    f'<span style="color:{INK_MUTED}; font-size:0.85rem;">'
    f'{len(df):,} registros de {len(df_raw):,}</span>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------------------------
st.markdown('<div class="app-header">Estadística descriptiva del mercado laboral</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subhead">GEIH · Personas ocupadas, 2023–2025</div>', unsafe_allow_html=True)
st.markdown('<hr class="app-rule">', unsafe_allow_html=True)

tab_inicio, tab_formalidad, tab_ingresos = st.tabs(["Inicio", "Formalidad laboral", "Ingresos"])

# ---------------------------------------------------------------------------
# INICIO
# ---------------------------------------------------------------------------
with tab_inicio:
    st.write(
        "Formalidad laboral e ingresos, desglosados por Departamento, Año, Mes, "
        "Educación, Estado civil, Etnia, Sexo, Tipo de contrato, Posición "
        "ocupacional, Lugar de trabajo, Sector económico y Oficio."
    )
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Formalidad laboral")
        kpi_formalidad(df)
    with col2:
        st.markdown("##### Ingresos")
        kpi_ingreso(df)

# ---------------------------------------------------------------------------
# BLOQUE TFNF: % Trabajo formal / no formal
# ---------------------------------------------------------------------------
with tab_formalidad:
    kpi_formalidad(df)
    st.markdown('<hr class="app-rule">', unsafe_allow_html=True)

    subtabs = st.tabs([
        "Departamento / Año / Mes",
        "Educación / Estado civil / Etnia / Sexo",
        "Contrato / Posición / Lugar",
        "Sector económico",
        "Oficio",
    ])

    with subtabs[0]:
        grafico_formalidad(df, "departamento", "Por Departamento")
        c1, c2 = st.columns(2)
        with c1:
            grafico_formalidad(df, "anio", "Por Año")
        with c2:
            grafico_formalidad(df, "Mes Letras", "Por Mes")

    with subtabs[1]:
        grafico_formalidad(df, "nivel_educativo", "Por Educación")
        grafico_formalidad(df, "estado_civil", "Por Estado Civil")
        c1, c2 = st.columns(2)
        with c1:
            grafico_formalidad(df, "etnia", "Por Etnia")
        with c2:
            grafico_formalidad(df, "sexo", "Por Sexo")

    with subtabs[2]:
        grafico_formalidad(df, "tipo_contrato", "Por Tipo de Contrato")
        grafico_formalidad(df, "posicion_ocupacional", "Por Posición Ocupacional")
        grafico_formalidad(df, "lugar_trabajo", "Por Lugar de Trabajo")

    with subtabs[3]:
        grafico_formalidad(df, "sector_economico_seccion", "Por Sector Económico", horizontal=True)

    with subtabs[4]:
        grafico_formalidad(df, "oficio_gran_grupo", "Por Oficio", horizontal=True)

# ---------------------------------------------------------------------------
# BLOQUE ING: Promedio Ingreso Total / Mediana
# ---------------------------------------------------------------------------
with tab_ingresos:
    kpi_ingreso(df)
    st.markdown('<hr class="app-rule">', unsafe_allow_html=True)

    subtabs = st.tabs([
        "Departamento / Año / Mes",
        "Educación / Estado civil / Etnia / Sexo",
        "Contrato / Posición / Lugar",
        "Sector económico",
        "Oficio",
    ])

    with subtabs[0]:
        grafico_ingreso(df, "departamento", "Por Departamento", incluir_mediana=False)
        c1, c2 = st.columns(2)
        with c1:
            grafico_ingreso(df, "anio", "Por Año")
        with c2:
            grafico_ingreso(df, "Mes Letras", "Por Mes", incluir_mediana=False)

    with subtabs[1]:
        grafico_ingreso(df, "nivel_educativo", "Por Educación", incluir_mediana=False)
        grafico_ingreso(df, "estado_civil", "Por Estado Civil", incluir_mediana=False)
        c1, c2 = st.columns(2)
        with c1:
            grafico_ingreso(df, "etnia", "Por Etnia", incluir_mediana=False)
        with c2:
            grafico_ingreso(df, "sexo", "Por Sexo", incluir_mediana=False)

    with subtabs[2]:
        grafico_ingreso(df, "tipo_contrato", "Por Tipo de Contrato", incluir_mediana=False)
        grafico_ingreso(df, "posicion_ocupacional", "Por Posición Ocupacional", incluir_mediana=False)
        grafico_ingreso(df, "lugar_trabajo", "Por Lugar de Trabajo", incluir_mediana=False)

    with subtabs[3]:
        grafico_ingreso(df, "sector_economico_seccion", "Por Sector Económico", horizontal=True, incluir_mediana=False)

    with subtabs[4]:
        grafico_ingreso(df, "oficio_gran_grupo", "Por Oficio", horizontal=True, incluir_mediana=False)
