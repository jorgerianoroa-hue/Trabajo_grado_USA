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
    page_icon="📊",
    layout="wide",
)

DATA_PATH = "datos_reducidos.parquet"

MESES_ORDEN = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]

# Paleta consistente con las dos métricas del reporte original
COLOR_FORMAL = "#2E7D32"      # verde
COLOR_NO_FORMAL = "#C62828"   # rojo
COLOR_PROMEDIO = "#1565C0"    # azul
COLOR_MEDIANA = "#EF6C00"     # naranja


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

    # Tipos categóricos livianos para columnas de texto repetidas
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
    """
    % Trabajo formal = filas con empleo_formal_pleno=1 / total filas
    % Trabajo no formal = filas con empleo_formal_pleno=0 / total filas
    """
    total = len(df)
    if total == 0:
        return 0.0, 0.0
    formal = (df["empleo_formal_pleno"] == 1).sum()
    no_formal = (df["empleo_formal_pleno"] == 0).sum()
    return formal / total, no_formal / total


def promedio_mediana_ingreso(df: pd.DataFrame) -> tuple[float, float]:
    """
    Promedio Ingreso Total = AVERAGE(ingreso_laboral_total)
    Mediana = MEDIAN(ingreso_laboral_total)
    """
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
    c1.metric("% Trabajo formal", f"{pf:.1%}")
    c2.metric("% Trabajo no formal", f"{pnf:.1%}")


def kpi_ingreso(df: pd.DataFrame):
    prom, med = promedio_mediana_ingreso(df)
    c1, c2 = st.columns(2)
    c1.metric("Promedio Ingreso Total", f"${prom:,.0f}")
    c2.metric("Mediana", f"${med:,.0f}")


def grafico_formalidad(df: pd.DataFrame, dim: str, titulo: str, top_n: int = 20, horizontal: bool = False):
    data = formalidad_por_dimension(df, dim).head(top_n)
    if horizontal:
        data = data.sort_values("pct_formal")
    fig = go.Figure()
    fig.add_bar(
        name="% Trabajo formal",
        x=data["pct_formal"] if horizontal else data[dim],
        y=data[dim] if horizontal else data["pct_formal"],
        orientation="h" if horizontal else "v",
        marker_color=COLOR_FORMAL,
        texttemplate="%{x:.0%}" if horizontal else "%{y:.0%}",
        textposition="outside",
    )
    fig.add_bar(
        name="% Trabajo no formal",
        x=data["pct_no_formal"] if horizontal else data[dim],
        y=data[dim] if horizontal else data["pct_no_formal"],
        orientation="h" if horizontal else "v",
        marker_color=COLOR_NO_FORMAL,
        texttemplate="%{x:.0%}" if horizontal else "%{y:.0%}",
        textposition="outside",
    )
    fig.update_layout(
        title=titulo,
        barmode="group",
        yaxis_tickformat=".0%" if not horizontal else None,
        xaxis_tickformat=".0%" if horizontal else None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        height=420,
        margin=dict(t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def grafico_ingreso(df: pd.DataFrame, dim: str, titulo: str, top_n: int = 20, horizontal: bool = False, incluir_mediana: bool = True):
    data = ingreso_por_dimension(df, dim).head(top_n)
    if horizontal:
        data = data.sort_values("promedio")
    fig = go.Figure()
    fig.add_bar(
        name="Promedio Ingreso Total",
        x=data["promedio"] if horizontal else data[dim],
        y=data[dim] if horizontal else data["promedio"],
        orientation="h" if horizontal else "v",
        marker_color=COLOR_PROMEDIO,
        texttemplate="%{x:,.0f}" if horizontal else "%{y:,.0f}",
        textposition="outside",
    )
    if incluir_mediana:
        fig.add_bar(
            name="Mediana",
            x=data["mediana"] if horizontal else data[dim],
            y=data[dim] if horizontal else data["mediana"],
            orientation="h" if horizontal else "v",
            marker_color=COLOR_MEDIANA,
            texttemplate="%{x:,.0f}" if horizontal else "%{y:,.0f}",
            textposition="outside",
        )
    fig.update_layout(
        title=titulo,
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        height=420,
        margin=dict(t=60, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# CARGA + FILTROS GLOBALES (equivalentes a los slicers de año / mes)
# ---------------------------------------------------------------------------
df_raw = load_data(DATA_PATH)

st.sidebar.title("📊 Filtros")
anios_sel = st.sidebar.multiselect(
    "Año", sorted(df_raw["anio"].unique()), default=sorted(df_raw["anio"].unique())
)
meses_sel = st.sidebar.multiselect(
    "Mes", MESES_ORDEN, default=MESES_ORDEN
)

df = df_raw[df_raw["anio"].isin(anios_sel) & df_raw["Mes Letras"].isin(meses_sel)]

st.sidebar.caption(f"{len(df):,} registros seleccionados de {len(df_raw):,}")

st.sidebar.divider()
seccion = st.sidebar.radio(
    "Navegación",
    ["🏠 Inicio", "🧑‍💼 Formalidad Laboral (TFNF)", "💰 Ingresos (ING)"],
)


# ---------------------------------------------------------------------------
# PÁGINA: INICIO (equivalente a "Menu")
# ---------------------------------------------------------------------------
if seccion == "🏠 Inicio":
    st.title("Estadística Descriptiva del Mercado Laboral")
    st.caption("GEIH · Personas ocupadas 2023-2025")
    st.write(
        "Este tablero replica el reporte de Power BI original, organizado en dos "
        "bloques: **Formalidad laboral** (% trabajo formal / no formal) e "
        "**Ingresos** (promedio y mediana), ambos desglosados por Departamento, "
        "Año, Mes, Educación, Estado civil, Etnia, Sexo, Tipo de contrato, "
        "Posición ocupacional, Lugar de trabajo, Sector económico y Oficio."
    )
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🧑‍💼 Formalidad Laboral")
        kpi_formalidad(df)
    with col2:
        st.subheader("💰 Ingresos")
        kpi_ingreso(df)

# ---------------------------------------------------------------------------
# BLOQUE TFNF: % Trabajo formal / no formal
# ---------------------------------------------------------------------------
elif seccion == "🧑‍💼 Formalidad Laboral (TFNF)":
    st.title("% Trabajo formal y % Trabajo no formal")
    kpi_formalidad(df)
    st.divider()

    tabs = st.tabs([
        "Departamento / Año / Mes",
        "Educación / Estado civil / Etnia / Sexo",
        "Contrato / Posición / Lugar",
        "Sector económico",
        "Oficio",
    ])

    with tabs[0]:  # TFNF1
        grafico_formalidad(df, "departamento", "% Trabajo formal y no formal por Departamento")
        c1, c2 = st.columns(2)
        with c1:
            grafico_formalidad(df, "anio", "% Trabajo formal y no formal por Año")
        with c2:
            grafico_formalidad(df, "Mes Letras", "% Trabajo formal y no formal por Mes")

    with tabs[1]:  # TFNF2
        grafico_formalidad(df, "nivel_educativo", "% Trabajo formal y no formal por Educación")
        grafico_formalidad(df, "estado_civil", "% Trabajo formal y no formal por Estado Civil")
        c1, c2 = st.columns(2)
        with c1:
            grafico_formalidad(df, "etnia", "% Trabajo formal y no formal por Etnia")
        with c2:
            grafico_formalidad(df, "sexo", "% Trabajo formal y no formal por Sexo")

    with tabs[2]:  # TFNF3
        grafico_formalidad(df, "tipo_contrato", "% Trabajo formal y no formal por Tipo de Contrato")
        grafico_formalidad(df, "posicion_ocupacional", "% Trabajo formal y no formal por Posición Ocupacional")
        grafico_formalidad(df, "lugar_trabajo", "% Trabajo formal y no formal por Lugar de Trabajo")

    with tabs[3]:  # TFNF4
        grafico_formalidad(
            df, "sector_economico_seccion",
            "% Trabajo formal y no formal por Sector Económico",
            horizontal=True,
        )

    with tabs[4]:  # TFNF5
        grafico_formalidad(
            df, "oficio_gran_grupo",
            "% Trabajo formal y no formal por Oficio",
            horizontal=True,
        )

# ---------------------------------------------------------------------------
# BLOQUE ING: Promedio Ingreso Total / Mediana
# ---------------------------------------------------------------------------
elif seccion == "💰 Ingresos (ING)":
    st.title("Promedio Ingreso Total y Mediana")
    kpi_ingreso(df)
    st.divider()

    tabs = st.tabs([
        "Departamento / Año / Mes",
        "Educación / Estado civil / Etnia / Sexo",
        "Contrato / Posición / Lugar",
        "Sector económico",
        "Oficio",
    ])

    with tabs[0]:  # ING1
        grafico_ingreso(df, "departamento", "Promedio Ingreso Total por Departamento", incluir_mediana=False)
        c1, c2 = st.columns(2)
        with c1:
            grafico_ingreso(df, "anio", "Promedio Ingreso Total por Año")
        with c2:
            grafico_ingreso(df, "Mes Letras", "Promedio Ingreso Total por Mes", incluir_mediana=False)

    with tabs[1]:  # ING2
        grafico_ingreso(df, "nivel_educativo", "Promedio Ingreso Total por Educación", incluir_mediana=False)
        grafico_ingreso(df, "estado_civil", "Promedio Ingreso Total por Estado Civil", incluir_mediana=False)
        c1, c2 = st.columns(2)
        with c1:
            grafico_ingreso(df, "etnia", "Promedio Ingreso Total por Etnia", incluir_mediana=False)
        with c2:
            grafico_ingreso(df, "sexo", "Promedio Ingreso Total por Sexo", incluir_mediana=False)

    with tabs[2]:  # ING3
        grafico_ingreso(df, "tipo_contrato", "Promedio Ingreso Total por Tipo de Contrato", incluir_mediana=False)
        grafico_ingreso(df, "posicion_ocupacional", "Promedio Ingreso Total por Posición Ocupacional", incluir_mediana=False)
        grafico_ingreso(df, "lugar_trabajo", "Promedio Ingreso Total por Lugar de Trabajo", incluir_mediana=False)

    with tabs[3]:  # ING4
        grafico_ingreso(
            df, "sector_economico_seccion",
            "Promedio Ingreso Total por Sector Económico",
            horizontal=True, incluir_mediana=False,
        )

    with tabs[4]:  # ING5
        grafico_ingreso(
            df, "oficio_gran_grupo",
            "Promedio Ingreso Total por Oficio",
            horizontal=True, incluir_mediana=False,
        )
