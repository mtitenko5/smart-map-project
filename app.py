# import streamlit as st
# import pandas as pd
# import pydeck as pdk
# import sqlite3
#
# st.set_page_config(layout="wide")
#
# #UI-styles
# st.markdown("""
# <style>
# .stApp {
#     background: linear-gradient(180deg, #0F172A, #020617);
#     color: white;
# }
#
# h1, h2, h3 {
#     color: white;
# }
#
# .block-container {
#     padding-top: 1rem;
# }
#
# button {
#     border-radius: 12px !important;
#     height: 45px !important;
# }
#
# </style>
# """, unsafe_allow_html=True)
#
# #Download data
#
# @st.cache_data
# def load_csv():
#     return pd.read_csv("transactions.csv", encoding='cp1251')
#
# @st.cache_data
# def load_sql():
#     conn = sqlite3.connect("transactions.db")
#     df = pd.read_sql("SELECT * FROM transactions", conn)
#     conn.close()
#     return df
#
# data_source = st.sidebar.radio("Источник данных", ["CSV", "SQL"])
#
# if data_source == "CSV":
#     df = load_csv()
# else:
#     df = load_sql()
#
# #preparing data
# df = df.rename(columns={
#     "latitude": "lat",
#     "longitude": "lon"
# })
#
# df["amount"] = df["amount"].astype(float)
#
# # нормализация радиуса
# df["radius"] = df["amount"] / df["amount"].max() * 500
#
# #UI-filters
#
# st.title("📍 Карта трат")
# col1, col2 = st.columns([3,1])
# with col1:
#     category = st.selectbox(
#         "Категория",
#         ["Все"] + list(df["category"].unique())
#     )
# with col2:
#     mode = st.selectbox(
#         "Режим отображения",
#         ["Кружки", "Heatmap", "Кластеры"]
#     )
#
# if category != "Все":
#     df = df[df["category"] == category]
#
# #view SPb map
# view_state = pdk.ViewState(
#     latitude=59.9343,
#     longitude=30.3351,
#     zoom=11,
#     pitch=30
# )
#
# #set circles
# scatter_layer = pdk.Layer(
#     "ScatterplotLayer",
#     data=df,
#     get_position='[lon, lat]',
#     get_radius="radius",
#     get_fill_color=[255, 140, 0, 120],
#     pickable=True
# )
#
# #heatmap creation
# heatmap_layer = pdk.Layer(
#     "HeatmapLayer",
#     data=df,
#     get_position='[lon, lat]',
#     get_weight="amount",
#     radiusPixels=60
# )
#
# #make cluster (agregation)
#
# cluster_layer = pdk.Layer(
#     "HexagonLayer",
#     data=df,
#     get_position='[lon, lat]',
#     radius=200,
#     elevation_scale=4,
#     elevation_range=[0, 1000],
#     extruded=True,
#     pickable=True
# )
#
# #make decision about type of layer
# if mode == "Кружки":
#     layers = [scatter_layer]
#
# elif mode == "Heatmap":
#     layers = [heatmap_layer]
#
# else:
#     layers = [cluster_layer]
#
# #РЕНДЕР КАРТЫ
# st.pydeck_chart(pdk.Deck(
#     map_style="mapbox://styles/mapbox/dark-v10",
#     initial_view_state=view_state,
#     layers=layers,
#     tooltip={
#         "html": "<b>Траты:</b> {amount} ₽",
#         "style": {"color": "white"}
#     }
# ))
#
# #доп. аналитика
# st.subheader("📊 Сводка")
# col1, col2, col3 = st.columns(3)
# col1.metric("Всего трат", f"{int(df['amount'].sum())} ₽")
# col2.metric("Средняя трата", f"{int(df['amount'].mean())} ₽")
# col3.metric("Транзакций", len(df))

import streamlit as st
import pandas as pd
import pydeck as pdk
import sqlite3

st.set_page_config(layout="wide")

# UI-styles с новыми цветами
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


# Функция загрузки CSV (только этот источник)
@st.cache_data
def load_csv():
    try:
        # Пробуем UTF-8 сначала
        return pd.read_csv("transactions.csv", encoding='utf-8')
    except UnicodeDecodeError:
        try:
            # Если не получилось, пробуем Windows-1251
            return pd.read_csv("transactions.csv", encoding='cp1251')
        except Exception as e:
            st.error(f"Ошибка загрузки файла: {e}")
            # Создаем тестовые данные, если файл не найден
            return create_sample_data()


def create_sample_data():
    """Создает тестовые данные для демонстрации"""
    import numpy as np

    # Центр Петербурга с отклонениями
    n_points = 50
    np.random.seed(42)

    data = {
        'amount': np.random.randint(100, 5000, n_points),
        'category': np.random.choice(['Еда', 'Транспорт', 'Развлечения', 'Покупки'], n_points),
        'latitude': 59.9343 + np.random.normal(0, 0.02, n_points),
        'longitude': 30.3351 + np.random.normal(0, 0.03, n_points)
    }

    return pd.DataFrame(data)


# Загружаем данные (только CSV)
df = load_csv()

# Подготовка данных
df = df.rename(columns={
    "latitude": "lat",
    "longitude": "lon"
})

# Проверяем, есть ли столбец amount, если нет - создаем
if 'amount' not in df.columns:
    df['amount'] = 1000

df["amount"] = df["amount"].astype(float)

# Нормализация радиуса (с защитой от деления на ноль)
if df['amount'].max() > 0:
    df["radius"] = df["amount"] / df["amount"].max() * 500
else:
    df["radius"] = 100

# UI-фильтры
st.title("📍 Карта трат Санкт-Петербурга")

col1, col2 = st.columns([3, 1])
with col1:
    categories = ["Все"] + list(df["category"].unique()) if "category" in df.columns else ["Все"]
    category = st.selectbox("Категория", categories)

with col2:
    mode = st.selectbox(
        "Режим отображения",
        ["Кружки", "Heatmap", "Кластеры"]
    )

if category != "Все" and "category" in df.columns:
    df_filtered = df[df["category"] == category]
else:
    df_filtered = df

# Состояние карты для Петербурга
view_state = pdk.ViewState(
    latitude=59.9343,  # Центр Петербурга
    longitude=30.3351,
    zoom=11,
    pitch=30,
    bearing=0
)

# Слои для отображения
layers = []

# Слой с кружками (всегда нужен для базового отображения)
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
    ]
)

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
    ]
)

# Выбор слоя в зависимости от режима
if mode == "Кружки":
    layers = [scatter_layer]
elif mode == "Heatmap":
    layers = [heatmap_layer]
else:  # Кластеры
    layers = [cluster_layer]

# Добавляем базовый слой с картой Петербурга (OpenStreetMap через Mapbox)
# Для корректного отображения карты нужно использовать Mapbox стиль
# Если нет ключа Mapbox, используем дефолтный стиль
# try:
#     # Пробуем использовать Mapbox стиль (может потребоваться ключ)
#     st.pydeck_chart(pdk.Deck(
#         map_style="mapbox://styles/mapbox/light-v10",  # Светлая карта
#         initial_view_state=view_state,
#         layers=layers,
#         tooltip={
#             "html": "<b>Сумма:</b> {amount} ₽<br/><b>Категория:</b> {category}",
#             "style": {"color": "#333333", "backgroundColor": "white", "padding": "10px"}
#         }
#     ))
# except:
#     # Если Mapbox не работает, используем встроенный стиль
#     st.pydeck_chart(pdk.Deck(
#         map_style="light",  # Встроенный светлый стиль
#         initial_view_state=view_state,
#         layers=layers,
#         tooltip={
#             "html": "<b>Сумма:</b> {amount} ₽<br/><b>Категория:</b> {category}",
#             "style": {"color": "#333333", "backgroundColor": "white", "padding": "10px"}
#         }
#     ))

st.pydeck_chart(pdk.Deck(
    map_style='light',  # Работает без ключа API
    initial_view_state=view_state,
    layers=layers,
    tooltip={
        "html": "<b>Сумма:</b> {amount} ₽<br/><b>Категория:</b> {category}",
        "style": {"color": "#333333", "backgroundColor": "white", "padding": "10px"}
    }
))

# Дополнительная информация о районе
st.subheader("📍 Информация о районе")
col_info1, col_info2 = st.columns(2)
with col_info1:
    st.info(f"**Центр карты:** {view_state.latitude:.4f}, {view_state.longitude:.4f}")
    st.info(f"**Масштаб:** {view_state.zoom}x")
with col_info2:
    st.info(f"**Наклон:** {view_state.pitch}°")
    st.info(f"**Поворот:** {view_state.bearing}°")

# Аналитика
st.subheader("📊 Сводка по тратам")

col1, col2, col3, col4 = st.columns(4)

total_amount = df_filtered['amount'].sum()
avg_amount = df_filtered['amount'].mean()
count_transactions = len(df_filtered)
max_amount = df_filtered['amount'].max()

col1.metric("Всего трат", f"{int(total_amount):,} ₽".replace(',', ' '))
col2.metric("Средняя трата", f"{int(avg_amount):,} ₽".replace(',', ' '))
col3.metric("Кол-во транзакций", count_transactions)
col4.metric("Макс. трата", f"{int(max_amount):,} ₽".replace(',', ' '))

# Дополнительная статистика по категориям (если есть категории)
if "category" in df_filtered.columns and len(df_filtered) > 0:
    st.subheader("📈 Траты по категориям")

    # Группировка по категориям
    category_stats = df_filtered.groupby('category')['amount'].agg(['sum', 'count', 'mean']).reset_index()
    category_stats.columns = ['Категория', 'Сумма', 'Кол-во', 'Среднее']
    category_stats['Сумма'] = category_stats['Сумма'].apply(lambda x: f"{int(x):,} ₽".replace(',', ' '))
    category_stats['Среднее'] = category_stats['Среднее'].apply(lambda x: f"{int(x):,} ₽".replace(',', ' '))

    st.dataframe(category_stats, use_container_width=True)
