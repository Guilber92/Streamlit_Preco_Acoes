import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta
import io

# ============================
# Função para carregar dados via BRAPI
# ============================
def carregar_dados(empresas, intervalo):
    dados = pd.DataFrame()

    for acao in empresas:
        url = f"https://brapi.dev/api/quote/{acao}?range={intervalo}&interval=1d"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                prices = data["results"][0]["historicalDataPrice"]
                df = pd.DataFrame(prices)
                df["date"] = pd.to_datetime(df["date"], unit="s")
                df.set_index("date", inplace=True)
                df.rename(columns={"close": acao}, inplace=True)
                dados = pd.concat([dados, df[acao]], axis=1)
    return dados

# ============================
# Lista de ações da B3
# ============================
acoes = ["PETR4", "VALE3", "ITUB4", "ABEV3", "GGBR4", "MGLU3"]

# ============================
# Layout do App
# ============================
st.set_page_config(page_title="App - Preço de Ações", layout="wide")
st.title("📈 App - Preço de Ações (BRAPI)")
st.write("Visualize a variação das principais ações brasileiras, com filtros e exportação de dados.")

# Seleção de ações
empresas_selecionadas = st.multiselect(
    "Selecione as ações:",
    options=acoes,
    default=acoes
)

# Filtros de período rápido
periodos = {
    "1 mês": "1mo",
    "3 meses": "3mo",
    "6 meses": "6mo",
    "1 ano": "1y",
    "2 anos": "2y",
    "5 anos": "5y",
    "Máximo (10 anos)": "10y"
}

intervalo = st.selectbox("Selecione o período:", options=list(periodos.keys()), index=5)
mostrar_retorno = st.checkbox("Mostrar retorno percentual (%)", value=False)

# ============================
# Lógica principal
# ============================
if empresas_selecionadas:
    st.info("🔄 Buscando dados, aguarde alguns segundos...")
    dados = carregar_dados(empresas_selecionadas, periodos[intervalo])

    if not dados.empty:
        st.success("✅ Dados carregados com sucesso!")
        
        # Exibir gráfico
        if mostrar_retorno:
            dados = (dados / dados.iloc[0] - 1) * 100
            st.line_chart(dados)
            st.write("📊 Retorno percentual acumulado desde o início do período selecionado")
        else:
            st.line_chart(dados)
            st.write("💰 Preço de fechamento (R$)")
        
        # Mostrar últimas linhas
        st.dataframe(dados.tail())

        # Exportar dados
        buffer = io.BytesIO()
        dados.to_excel(buffer, index=True)
        st.download_button(
            label="💾 Baixar dados em Excel",
            data=buffer.getvalue(),
            file_name="dados_acoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("❌ Nenhum dado retornado pela API BRAPI.")
else:
    st.warning("⚠️ Selecione pelo menos uma ação para exibir o gráfico.")
