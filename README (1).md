# Dashboard Estadística Descriptiva (réplica de Power BI en Streamlit)

## Instalación

```bash
pip install -r requirements.txt
```

## Preparar los datos

Coloca el archivo `datos_reducidos.parquet` en la **misma carpeta** que `app.py`
(o cambia la constante `DATA_PATH` al inicio de `app.py` si prefieres otra ruta).

Este parquet es una versión recortada de `df_ocupados_carac_2023_2025__2_.csv`: solo
tiene las 14 columnas que usa el dashboard. Pesa ~2.6 MB en vez de 370 MB, lo que lo
hace viable para subir a GitHub y desplegar en Streamlit Community Cloud. Si alguna
vez cambias el CSV fuente, puedes regenerarlo así:

```python
import pandas as pd
cols = ["departamento","anio","mes","sexo","estado_civil","etnia","nivel_educativo",
        "tipo_contrato","posicion_ocupacional","lugar_trabajo",
        "sector_economico_seccion","oficio_gran_grupo",
        "ingreso_laboral_total","empleo_formal_pleno"]
pd.read_csv("df_ocupados_carac_2023_2025__2_.csv", usecols=cols) \
  .to_parquet("datos_reducidos.parquet", index=False)
```

## Ejecutar

```bash
streamlit run app.py
```

Se abrirá en `http://localhost:8501`.

## Estructura del tablero

- **Sidebar**: filtros globales de Año y Mes (equivalentes a los slicers `anio` y
  `Mes Letras` del .pbix), y navegación entre secciones.
- **🏠 Inicio**: resumen general con los KPIs de ambos bloques (equivalente a la página "Menu").
- **🧑‍💼 Formalidad Laboral (TFNF)**: % Trabajo formal / % Trabajo no formal, con 5 pestañas
  que replican las páginas TFNF1-TFNF5 del reporte original (Departamento/Año/Mes,
  Educación/Estado civil/Etnia/Sexo, Contrato/Posición/Lugar, Sector económico, Oficio).
- **💰 Ingresos (ING)**: Promedio Ingreso Total y Mediana, con la misma estructura de
  pestañas (ING1-ING5).

## Medidas (réplica exacta de las fórmulas DAX)

```python
% Trabajo formal    = filas con empleo_formal_pleno == 1 / total filas
% Trabajo no formal = filas con empleo_formal_pleno == 0 / total filas
Promedio Ingreso Total = ingreso_laboral_total.mean()
Mediana                = ingreso_laboral_total.median()
```

Estas fórmulas están implementadas en `pct_formal_no_formal()` y
`promedio_mediana_ingreso()` dentro de `app.py`, y se aplican tanto al KPI global
como a cada desglose por dimensión (`formalidad_por_dimension()` /
`ingreso_por_dimension()`), agrupando con `groupby(...).mean()` en vez de filtrar
fila por fila — el resultado es idéntico al `CALCULATE(COUNTROWS(...), FILTER(...))`
de Power BI pero muchísimo más rápido en pandas.

## Notas y decisiones de diseño

- Se cargan solo las 14 columnas que usa el dashboard (`USE_COLS`), no las 65 del CSV
  original, para que la carga sea rápida. Los datos se cachean con `@st.cache_data`,
  así que solo se leen una vez por sesión aunque cambies los filtros.
- Los gráficos usan Plotly (`clusteredColumnChart`/`clusteredBarChart` → `go.Figure`
  con `barmode="group"`), igual que en Power BI. Las páginas TFNF4/TFNF5 e ING4/ING5
  usan barras horizontales porque las categorías (Sector económico, Oficio) tienen
  etiquetas largas, igual que en el original.
- No se aplica el factor de expansión (`factor_expansion`) porque tus medidas DAX
  originales tampoco lo usan (son conteos/promedios simples sobre las filas de la
  encuesta, no estimaciones poblacionales ponderadas). Si en algún momento quieres
  la versión ponderada, es un cambio pequeño en `pct_formal_no_formal` y
  `promedio_mediana_ingreso`.

## Próximos pasos sugeridos (no incluidos todavía)

- Botones de navegación tipo "menú" como en la página Menu original (aquí se resolvió
  con un `st.sidebar.radio`, que es el equivalente idiomático en Streamlit).
- Exportar a PDF/imagen los gráficos.
- Despliegue en Streamlit Community Cloud o similar.
