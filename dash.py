import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(page_title="Dashboard Financeiro", layout="wide")

# Título principal
st.title("📊 Dashboard Financeiro")

# Criando dados fictícios para 5 anos
anos = list(range(2019, 2024))
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
periodos = [f"{mes}-{ano}" for ano in anos for mes in meses]

# Gerando dados com tendência crescente e sazonalidade
np.random.seed(42)  # Para reprodutibilidade

# Dados financeiros com tendência e sazonalidade
base_receita = 150
dados = {
    'Período': periodos,
    'Receita': [
        base_receita * (1 + 0.1 * (i // 12)) * (1 + 0.1 * np.sin(i * np.pi / 6)) * (1 + np.random.normal(0, 0.05))
        for i in range(len(periodos))
    ]
}

# Calculando outros indicadores baseados na receita
dados['Custos_Fixos'] = [r * 0.3 * (1 + np.random.normal(0, 0.02)) for r in dados['Receita']]
dados['Custos_Variaveis'] = [r * 0.25 * (1 + np.random.normal(0, 0.03)) for r in dados['Receita']]
dados['Patrimonio_Liquido'] = [500 * (1 + 0.05 * (i // 12)) for i in range(len(periodos))]
dados['Ticket_Medio'] = [120 * (1 + 0.03 * (i // 12)) * (1 + np.random.normal(0, 0.02)) for i in range(len(periodos))]

df = pd.DataFrame(dados)

# Cálculos financeiros
df['Lucro_Bruto'] = df['Receita'] - (df['Custos_Fixos'] + df['Custos_Variaveis'])
df['Margem_Bruta'] = (df['Lucro_Bruto'] / df['Receita']) * 100
df['EBITDA'] = df['Lucro_Bruto'] - (df['Custos_Fixos'] * 0.2)
df['Margem_Liquida'] = (df['EBITDA'] / df['Receita']) * 100

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Receita Total", f"R$ {df['Receita'].sum():,.2f}k")
with col2:
    st.metric("Ticket Médio", f"R$ {df['Ticket_Medio'].mean():,.2f}")
with col3:
    st.metric("Margem Bruta Média", f"{df['Margem_Bruta'].mean():,.1f}%")
with col4:
    st.metric("EBITDA Total", f"R$ {df['EBITDA'].sum():,.2f}k")

# Criando as visualizações
st.subheader("📈 Fluxo de Caixa e Margens")
col1, col2 = st.columns(2)

with col1:
    # Gráfico de Fluxo de Caixa
    fig_fluxo = go.Figure()
    fig_fluxo.add_trace(go.Scatter(x=df['Período'], y=df['Receita'], 
                                  name='Receita', line=dict(color='green')))
    fig_fluxo.update_layout(title='Fluxo de Caixa Mensal',
                           xaxis_title='Mês',
                           yaxis_title='Valor (R$ mil)')
    st.plotly_chart(fig_fluxo, use_container_width=True)

with col2:
    # Gráfico de Margens
    fig_margens = go.Figure()
    fig_margens.add_trace(go.Scatter(x=df['Período'], y=df['Margem_Bruta'], 
                                    name='Margem Bruta', line=dict(color='blue')))
    fig_margens.add_trace(go.Scatter(x=df['Período'], y=df['Margem_Liquida'], 
                                    name='Margem Líquida', line=dict(color='red')))
    fig_margens.update_layout(title='Margens (%)',
                             xaxis_title='Mês',
                             yaxis_title='Percentual (%)')
    st.plotly_chart(fig_margens, use_container_width=True)

st.subheader("💰 Custos e Patrimônio")
col1, col2 = st.columns(2)

with col1:
    # Gráfico de Custos
    fig_custos = go.Figure()
    fig_custos.add_trace(go.Bar(x=df['Período'], y=df['Custos_Fixos'], 
                               name='Custos Fixos', marker_color='red'))
    fig_custos.add_trace(go.Bar(x=df['Período'], y=df['Custos_Variaveis'], 
                               name='Custos Variáveis', marker_color='orange'))
    fig_custos.update_layout(title='Custos Mensais',
                            xaxis_title='Mês',
                            yaxis_title='Valor (R$ mil)',
                            barmode='group')
    st.plotly_chart(fig_custos, use_container_width=True)

with col2:
    # Gráfico de Patrimônio Líquido
    fig_pl = go.Figure()
    fig_pl.add_trace(go.Bar(x=df['Período'], y=df['Patrimonio_Liquido'], 
                           name='Patrimônio Líquido', marker_color='blue'))
    fig_pl.update_layout(title='Patrimônio Líquido',
                        xaxis_title='Mês',
                        yaxis_title='Valor (R$ mil)')
    st.plotly_chart(fig_pl, use_container_width=True)

# Tabela de dados
st.subheader("📋 Dados Detalhados")
st.dataframe(df.style.format({
    'Receita': 'R$ {:,.2f}k',
    'Custos_Fixos': 'R$ {:,.2f}k',
    'Custos_Variaveis': 'R$ {:,.2f}k',
    'Patrimonio_Liquido': 'R$ {:,.2f}k',
    'Ticket_Medio': 'R$ {:,.2f}',
    'Lucro_Bruto': 'R$ {:,.2f}k',
    'Margem_Bruta': '{:,.1f}%',
    'EBITDA': 'R$ {:,.2f}k',
    'Margem_Liquida': '{:,.1f}%'
}))

# Sidebar com filtros
st.sidebar.header("Filtros")
periodo_selecionado = st.sidebar.multiselect(
    "Selecione os períodos:",
    options=periodos,
    default=periodos[-12:]  # Últimos 12 meses como padrão
)

# Adicione um footer
st.markdown("---")
st.markdown("Dashboard criado com Streamlit e Plotly")
