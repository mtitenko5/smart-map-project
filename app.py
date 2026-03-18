import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(layout="wide")
# UI-styles
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #009FDF, #428BCA);
    color: white;
}

h1, h2, h3 {
    color: #333333;
}

.block-container {
    padding-top: 1rem;
}

button {
    border-radius: 12px !important;
    height: 45px !important;
    background-color: #333333 !important;
    color: white !important;
}

/* Стили для карточек с метриками */
div[data-testid="metric-container"] {
    background-color: rgba(51, 51, 51, 0.1);
    border-radius: 10px;
    padding: 10px;
    border-left: 3px solid #333333;
}

/* Стили для селектов */
div[data-baseweb="select"] {
    background-color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_csv():
    try:
        return pd.read_csv("transactions.csv", encoding='utf-8')
    except UnicodeDecodeError:
        try:
            return pd.read_csv("transactions.csv", encoding='cp1251')
        except Exception as e:
            st.error(f"Ошибка загрузки файла: {e}")

df = load_csv()
df = df.rename(columns={
    "latitude": "lat",
    "longitude": "lon"
})
df["amount"] = df["amount"].astype(float)

if df['amount'].max() > 0:
    df["radius"] = df["amount"] / df["amount"].max() * 250
else:
    df["radius"] = 50

# UI-фильтры
st.title("Умная карта")
col1, col2 = st.columns([3, 1])
with col1:
    categories = ["Все"] + list(df["category"].unique()) if "category" in df.columns else ["Все"]
    category = st.selectbox("Категория", categories)
with col2:
    mode = st.selectbox("Режим отображения",["Кружки", "Heatmap", "Кластеры"])

if category != "Все" and "category" in df.columns:
    df_filtered = df[df["category"] == category]
else:
    df_filtered = df

# Центр Петербурга
view_state = pdk.ViewState(latitude=59.9343, longitude=30.3351, zoom=11, pitch=30, bearing=0)
layers = []
# Слой с кружками
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_filtered,
    get_position='[lon, lat]',
    get_radius="radius",
    get_fill_color=[0, 159, 223, 160],  # Cerulean с прозрачностью
    get_line_color=[51, 51, 51, 255],  # Mine Shaft
    line_width_min_pixels=1,
    pickable=True,
    auto_highlight=True
)

# Тепловая карта
heatmap_layer = pdk.Layer(
    "HeatmapLayer",
    data=df_filtered,
    get_position='[lon, lat]',
    get_weight="amount",
    radiusPixels=60,
    intensity=1,
    threshold=0.05,
    color_range=[
        [0, 159, 223, 100],  # Cerulean прозрачный
        [66, 139, 202, 150],  # Boston Blue
        [51, 51, 51, 200],  # Mine Shaft
        [0, 159, 223, 255],  # Cerulean
        [66, 139, 202, 255],  # Boston Blue
        [51, 51, 51, 255]  # Mine Shaft
    ])

# Кластерный слой (Hexagon)
cluster_layer = pdk.Layer(
    "HexagonLayer",
    data=df_filtered,
    get_position='[lon, lat]',
    radius=200,
    elevation_scale=4,
    elevation_range=[0, 1000],
    extruded=True,
    pickable=True,
    auto_highlight=True,
    get_fill_color=[0, 159, 223, 140],
    color_range=[
        [0, 159, 223, 100],
        [66, 139, 202, 150],
        [51, 51, 51, 200]
    ])

# Выбор слоя в зависимости от режима
if mode == "Кружки":
    layers = [scatter_layer]
elif mode == "Heatmap":
    layers = [heatmap_layer]
else:
    layers = [cluster_layer]

# Работает без ключа API
st.pydeck_chart(pdk.Deck(
    map_style='light',
    initial_view_state=view_state,
    layers=layers,
    tooltip={
        "html": "<b>Сумма:</b> {amount} ₽<br/><b>Категория:</b> {category}",
        "style": {"color": "#333333", "backgroundColor": "white", "padding": "10px"}
    }))

st.subheader("Информация о районе")
col_info1, col_info2 = st.columns(2)
with col_info1:
    st.info(f"**Центр карты:** {view_state.latitude:.4f}, {view_state.longitude:.4f}")
    st.info(f"**Масштаб:** {view_state.zoom}x")
with col_info2:
    st.info(f"**Наклон:** {view_state.pitch}°")
    st.info(f"**Поворот:** {view_state.bearing}°")

st.subheader("Сводка по тратам")
col1, col2, col3, col4 = st.columns(4)

total_amount = df_filtered['amount'].sum()
avg_amount = df_filtered['amount'].mean()
count_transactions = len(df_filtered)
max_amount = df_filtered['amount'].max()

col1.metric("Всего трат", f"{int(total_amount):,} ₽".replace(',', ' '))
col2.metric("Средняя трата", f"{int(avg_amount):,} ₽".replace(',', ' '))
col3.metric("Кол-во транзакций", count_transactions)
col4.metric("Макс. трата", f"{int(max_amount):,} ₽".replace(',', ' '))

if "category" in df_filtered.columns and len(df_filtered) > 0:
    st.subheader("Траты по категориям")
    # Группировка по категориям
    category_stats = df_filtered.groupby('category')['amount'].agg(['sum', 'count', 'mean']).reset_index()
    category_stats.columns = ['Категория', 'Сумма', 'Кол-во', 'Среднее']
    category_stats['Сумма'] = category_stats['Сумма'].apply(lambda x: f"{int(x):,} ₽".replace(',', ' '))
    category_stats['Среднее'] = category_stats['Среднее'].apply(lambda x: f"{int(x):,} ₽".replace(',', ' '))

    st.dataframe(category_stats, use_container_width=True)
