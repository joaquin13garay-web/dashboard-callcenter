import pandas as pd
import streamlit as st
import plotly.express as px

# 1. Configuración de la página en modo ancho
st.set_page_config(
    page_title="Dashboard Operativo - Call Center",
    page_icon="📊",
    layout="wide"
)

# 2. Cargar y preparar los datos desde el archivo Excel
@st.cache_data
def cargar_datos():
    df = pd.read_excel("operacion.xlsx")
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"No se pudo cargar el archivo 'operacion.xlsx': {e}. Asegúrate de que esté en la misma carpeta.")
    st.stop()

# 3. Panel de Filtros en la barra lateral (Sidebar)
st.sidebar.header("🎛️ Panel de Filtros")

# Filtro por Campaña (Multiselect)
campañas_disponibles = sorted(df["Campaña"].unique().tolist())
seleccion_campañas = st.sidebar.multiselect(
    "Selecciona las Campañas:",
    options=campañas_disponibles,
    default=campañas_disponibles
)

# Filtro por Rango de Fechas
min_fecha = df["Fecha"].min().date()
max_fecha = df["Fecha"].max().date()
rango_fechas = st.sidebar.date_input(
    "Rango de Fechas:",
    value=(min_fecha, max_fecha),
    min_value=min_fecha,
    max_value=max_fecha
)

# Aplicar filtros al DataFrame
if len(rango_fechas) == 2:
    f_inicio, f_fin = rango_fechas
    df_filtrado = df[
        (df["Campaña"].isin(seleccion_campañas)) & 
        (df["Fecha"].dt.date >= f_inicio) & 
        (df["Fecha"].dt.date <= f_fin)
    ]
else:
    df_filtrado = df[df["Campaña"].isin(seleccion_campañas)]

# 4. Título Principal del Dashboard
st.title("📊 Dashboard Operativo de Call Center")
st.markdown("---")

if df_filtrado.empty:
    st.warning("⚠️ No hay datos disponibles para los filtros seleccionados.")
else:
    # 5. Tarjetas de Métricas Principales (KPIs)
    total_recibidas = int(df_filtrado["Llamadas Recibidas"].sum())
    total_atendidas = int(df_filtrado["Llamadas Atendidas"].sum())
    tasa_atencion = (total_atendidas / total_recibidas) * 100 if total_recibidas > 0 else 0
    nivel_servicio_prom = df_filtrado["Nivel de Servicio"].mean() * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📞 Llamadas Recibidas", f"{total_recibidas:,}")
    col2.metric("✅ Llamadas Atendidas", f"{total_atendidas:,}")
    col3.metric("📈 Tasa de Atención", f"{tasa_atencion:.2f}%")
    col4.metric("⭐ Nivel de Servicio Prom.", f"{nivel_servicio_prom:.2f}%")

    st.markdown("---")

    # 6. Gráficos distribuidos en dos columnas
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📞 Llamadas Recibidas vs Atendidas")
        resumen_campaña = df_filtrado.groupby("Campaña")[["Llamadas Recibidas", "Llamadas Atendidas"]].sum().reset_index()
        resumen_melted = resumen_campaña.melt(
            id_vars="Campaña", 
            value_vars=["Llamadas Recibidas", "Llamadas Atendidas"],
            var_name="Tipo", 
            value_name="Cantidad"
        )
        fig_bar = px.bar(
            resumen_melted, 
            x="Campaña", 
            y="Cantidad", 
            color="Tipo", 
            barmode="group",
            color_discrete_map={"Llamadas Recibidas": "#3366CC", "Llamadas Atendidas": "#109618"}
        )
        fig_bar.update_layout(xaxis_title="Campaña", yaxis_title="Total de Llamadas", legend_title="")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("⭐ Nivel de Servicio por Campaña")
        ns_campaña = df_filtrado.groupby("Campaña")["Nivel de Servicio"].mean().reset_index()
        ns_campaña["Nivel de Servicio (%)"] = ns_campaña["Nivel de Servicio"] * 100
        fig_ns = px.bar(
            ns_campaña, 
            x="Campaña", 
            y="Nivel de Servicio (%)", 
            color="Campaña", 
            text_auto=".2f%"
        )
        fig_ns.update_layout(xaxis_title="Campaña", yaxis_title="Nivel de Servicio (%)", showlegend=False)
        st.plotly_chart(fig_ns, use_container_width=True)

    # 7. Gráfico de Tendencia Temporal
    st.subheader("📈 Tendencia Temporal de Llamadas")
    df_tiempo = df_filtrado.groupby("Fecha")[["Llamadas Recibidas", "Llamadas Atendidas"]].sum().reset_index()
    fig_line = px.line(
        df_tiempo, 
        x="Fecha", 
        y=["Llamadas Recibidas", "Llamadas Atendidas"],
        labels={"value": "Cantidad de Llamadas", "variable": "Métrica"},
        color_discrete_map={"Llamadas Recibidas": "#3366CC", "Llamadas Atendidas": "#109618"}
    )
    fig_line.update_layout(xaxis_title="Fecha", yaxis_title="Total")
    st.plotly_chart(fig_line, use_container_width=True)

    # 8. Sección expandible para ver la tabla de datos
    with st.expander("📄 Ver tabla detallada de datos filtrados"):
        st.dataframe(df_filtrado, use_container_width=True)