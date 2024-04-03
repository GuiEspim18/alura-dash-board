import streamlit as st
import requests
import pandas as pd
import plotly.exceptions as px

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

column1, column2 = st.columns(2)
with column1:
    st.metric("Receita", format(data['Preço'].sum(), "R$"))
with column2:
    st.metric("Quantidade de vendas", format(data.shape[0]))