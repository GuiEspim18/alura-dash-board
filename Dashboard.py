import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

def format(value, prefix = ""):
    for unit in ["", "mil"]:
        if value < 1000:
            return f"{prefix} {value:.2f} {unit}"
        else:
            value /= 1000
    return f"{prefix} {value:.2f} milhões"

st.title("DASHBOARD DE VENDAS :shopping_trolley:")

url = "https://labdados.com/produtos"
response = requests.get(url)
data = pd.DataFrame.from_dict(response.json())
data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format="%d/%m/%Y")

## Tables

### Revenue
states = data.groupby("Local da compra")[['Preço']].sum()
states = data.drop_duplicates(subset="Local da compra")[['Local da compra', 'lat', 'lon']].merge(states, left_on="Local da compra", right_index=True).sort_values("Preço", ascending=False)

monthly = data.set_index('Data da Compra').groupby(pd.Grouper(freq="M"))['Preço'].sum().reset_index()
monthly['Ano'] = monthly['Data da Compra'].dt.year
monthly['Mes'] = monthly['Data da Compra'].dt.month_name()

categories = data.groupby("Categoria do Produto")[['Preço']].sum().sort_values('Preço', ascending=False)

### Sell

sell_by_states = pd.DataFrame(data.groupby("Local da compra")[['Preço']].count())
sell_by_states = data.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(sell_by_states, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

sell_by_month = pd.DataFrame(data.set_index("Data da Compra").groupby(pd.Grouper(freq= "M"))['Preço'].count()).reset_index()
sell_by_month['Ano'] = sell_by_month['Data da Compra'].dt.year
sell_by_month['Mes'] = monthly['Data da Compra'].dt.month_name()

sell_by_category = pd.DataFrame(data.groupby("Categoria do Produto")['Preço'].count().sort_values(ascending=False))



### Sellers
sellers = pd.DataFrame(data.groupby("Vendedor")['Preço'].agg(['sum', 'count']))


## Charts

### Revenue
fig_map = px.scatter_geo(states, lat = "lat", lon = "lon", scope = "south america", size = "Preço", template = "seaborn", hover_name = "Local da compra", hover_data = {'lat':False,'lon':False}, title = "Receita por Estado")

fig_monthly = px.line(monthly, x="Mes", y="Preço", markers=True, range_y=(0, monthly.max()), color = "Ano", line_dash="Ano", title="Receita mensal")
fig_monthly.update_layout(yaxis_title="Receita")

fig_states = px.bar(states.head(), x = "Local da compra", y = "Preço", text_auto=True, title="Top estados (receita)")
fig_states.update_layout(yaxis_title="Receita")

fig_categories = px.bar(categories, text_auto=True, title="Receita por categoria")
fig_categories.update_layout(yaxis_title="Receita")

### Selles
fig_sell_map = px.scatter_geo(sell_by_states, lat="lat", lon="lon", scope="south america", size="Preço", template="seaborn", hover_name="Local da compra", hover_data={'lat': False, 'lon': False}, title = "Venda por Estado")

fig_sell_by_month = px.line(sell_by_month, x="Mes", y="Preço", markers=True, range_y=(0, sell_by_month.max()), color = "Ano", line_dash="Ano", title="Quantidade de vendas mensal")
fig_sell_by_month.update_layout(yaxis_title="Quantidade de vendas")

fig_sell_by_state = px.bar(sell_by_states.head(), x="Local da compra", y="Preço", text_auto=True, title="Top 5 estados")
fig_sell_by_state.update_layout(showlegend=False, yaxis_title="Quantidade de vendas")

fig_sell_by_category = px.bar(sell_by_category, text_auto=True, title="Vendas por categoria")
fig_sell_by_category.update_layout(showlegend=False, yaxis_title="Quantidade de vendas")


## View streamlit
tab1, tab2, tab3 = st.tabs(["Receita", "Quantidade de vendas", "Vendedores"])

with tab1:
    column1, column2 = st.columns([3, 3])
    with column1:
        st.metric("Receita", format(data['Preço'].sum(), "R$"))
        st.plotly_chart(fig_map, use_container_width=True)
        st.plotly_chart(fig_states, use_container_width=True)
    with column2:
        st.metric("Quantidade de vendas", format(data.shape[0]))
        st.plotly_chart(fig_monthly, use_container_width=True)
        st.plotly_chart(fig_categories, use_container_width=True)

with tab2:
    column1, column2 = st.columns([3, 3])
    with column1:
        st.metric("Receita", format(data['Preço'].sum(), "R$"))
        st.plotly_chart(fig_sell_map, use_container_width=True)
        st.plotly_chart(fig_sell_by_state, use_container_width=True)
    with column2:
        st.metric("Quantidade de vendas", format(data.shape[0]))
        st.plotly_chart(fig_sell_by_month, use_container_width=True)
        st.plotly_chart(fig_sell_by_category, use_container_width=True)


with tab3:
    qtd_sellers = st.number_input("Quantidade de vendedores", 2, 10, 5)
    column1, column2 = st.columns([3, 3])
    

    with column1:
        st.metric("Receita", format(data['Preço'].sum(), "R$"))
        fig_sellers = px.bar(sellers['sum'].sort_values(ascending=False).head(qtd_sellers), x="sum", y=sellers['sum'].sort_values(ascending=False).head(qtd_sellers).index, text_auto=True, title=f"Top {qtd_sellers} vendedores (receita)")
        st.plotly_chart(fig_sellers)

    with column2:
        st.metric("Quantidade de vendas", format(data.shape[0]))
        fig_sell_sellers = px.bar(sellers['count'].sort_values(ascending=False).head(qtd_sellers), x="count", y=sellers['count'].sort_values(ascending=False).head(qtd_sellers).index, text_auto=True, title=f"Top {qtd_sellers} vendedores (quantidade vendas)")
        st.plotly_chart(fig_sell_sellers)
