import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit.components.v1 as components
import io

# Adicione este código logo após os imports e antes da configuração da página
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
dados['Margem_Bruta'] = [(r - cf - cv) / r * 100 for r, cf, cv in zip(dados['Receita'], dados['Custos_Fixos'], dados['Custos_Variaveis'])]
dados['EBITDA'] = [r * 0.15 * (1 + np.random.normal(0, 0.03)) for r in dados['Receita']]

df = pd.DataFrame(dados)

# Configuração e estilo personalizado
st.set_page_config(page_title="Dashboard Financeiro", layout="wide", initial_sidebar_state="expanded")

# CSS personalizado
st.markdown("""
<style>
    /* Estilo do container principal */
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
    }
    
    /* Cards de métricas */
    div.css-1r6slb0.e1tzin5v2 {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    div.css-1r6slb0.e1tzin5v2:hover {
        transform: translateY(-5px);
    }
    
    /* Estilização dos títulos */
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .subtitle {
        font-size: 1.5rem;
        color: #374151;
        margin: 1.5rem 0;
        padding-left: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    
    /* Estilo para os gráficos */
    .plot-container {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Estilo para o sidebar */
    .css-1d391kg {
        background-color: #1f2937;
    }
    
    /* Estilo para tabela de dados */
    .dataframe {
        font-size: 12px !important;
    }
    
    /* Botões interativos */
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Título principal com HTML personalizado
st.markdown('<h1 class="main-title">📊 Dashboard Financeiro</h1>', unsafe_allow_html=True)

# Seletor de período interativo
col_date, col_metric = st.columns([2,1])
with col_date:
    periodo_analise = st.select_slider(
        "Período de Análise",
        options=periodos,
        value=(periodos[0], periodos[-1])
    )

with col_metric:
    metrica_principal = st.selectbox(
        "Métrica Principal",
        ["Receita", "EBITDA", "Margem Bruta", "Patrimônio Líquido"]
    )

# Cards de métricas com animação
col1, col2, col3, col4 = st.columns(4)
metricas = {
    "Receita Total": f"R$ {df['Receita'].sum():,.2f}k",
    "Ticket Médio": f"R$ {df['Ticket_Medio'].mean():,.2f}",
    "Margem Bruta": f"{df['Margem_Bruta'].mean():,.1f}%",
    "EBITDA": f"R$ {df['EBITDA'].sum():,.2f}k"
}

for col, (titulo, valor) in zip([col1, col2, col3, col4], metricas.items()):
    with col:
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; background-color: white; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);'>
            <h3 style='font-size: 0.9rem; color: #6b7280;'>{titulo}</h3>
            <p style='font-size: 1.5rem; font-weight: bold; color: #1f2937;'>{valor}</p>
        </div>
        """, unsafe_allow_html=True)

# Tabs para diferentes visualizações
tab1, tab2, tab3 = st.tabs(["📈 Desempenho", "💰 Financeiro", "📊 Análise"])

with tab1:
    st.markdown('<h2 class="subtitle">Fluxo de Caixa e Margens</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de Fluxo de Caixa interativo
        fig_fluxo = go.Figure()
        fig_fluxo.add_trace(go.Scatter(
            x=df['Período'], 
            y=df['Receita'],
            name='Receita',
            line=dict(color='#3b82f6', width=2),
            fill='tonexty'
        ))
        fig_fluxo.update_layout(
            title='Fluxo de Caixa Mensal',
            template='plotly_white',
            hovermode='x unified',
            hoverlabel=dict(bgcolor="white"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_fluxo, use_container_width=True, config={'displayModeBar': False})

with tab2:
    st.markdown('<h2 class="subtitle">💰 Custos e Patrimônio</h2>', unsafe_allow_html=True)
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

with tab3:
    st.markdown('<h2 class="subtitle">📋 Dados Detalhados</h2>', unsafe_allow_html=True)
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

# Sidebar aprimorado
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h2 style='color: white;'>Filtros Avançados</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros mais interativos
    ano_selecionado = st.multiselect(
        "Anos",
        options=anos,
        default=anos[-1]
    )
    
    indicadores = st.multiselect(
        "Indicadores",
        ["Receita", "Custos", "Margem", "EBITDA"],
        default=["Receita", "Margem"]
    )
    
    # Botões de ação
    if st.button("Aplicar Filtros", key="apply_filters"):
        st.success("Filtros aplicados com sucesso!")
    
    if st.button("Resetar Filtros", key="reset_filters"):
        st.info("Filtros resetados!")

# Download de dados
st.markdown('<h2 class="subtitle">Exportar Dados</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    if st.download_button(
        label="📥 Download CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='dados_financeiros.csv',
        mime='text/csv'
    ):
        st.success("Download iniciado!")

with col2:
    # Criar buffer para Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    
    if st.download_button(
        label="📥 Download Excel",
        data=buffer.getvalue(),
        file_name='dados_financeiros.xlsx',
        mime='application/vnd.ms-excel'
    ):
        st.success("Download iniciado!")

# Footer interativo
st.markdown("""
<footer style='text-align: center; padding: 2rem; margin-top: 3rem; background-color: white; border-radius: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);'>
    <p>Dashboard Financeiro © 2024</p>
    <p style='font-size: 0.8rem; color: #6b7280;'>Criado com Streamlit e Plotly</p>
</footer>
""", unsafe_allow_html=True)
