import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título do Dashboard
st.title("Dashboard de Análise do Campeonato Brasileiro")

# Carregar múltiplos datasets
uploaded_files = st.file_uploader("Escolha os arquivos do campeonato", type=["csv"], accept_multiple_files=True)

# Concatenar todos os datasets em um único DataFrame
if uploaded_files:
    dataframes = []
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        dataframes.append(df)
        st.write(f"Dados do arquivo: {uploaded_file.name}")
        st.dataframe(df)

    # Concatenar todos os DataFrames
    data = pd.concat(dataframes, ignore_index=True)

    # Converter colunas de cartões para numérico
    if 'cartao_amarelo' in data.columns:
        data['cartao_amarelo'] = pd.to_numeric(data['cartao_amarelo'], errors='coerce')
    if 'cartao_vermelho' in data.columns:
        data['cartao_vermelho'] = pd.to_numeric(data['cartao_vermelho'], errors='coerce')

    # Exibir estatísticas básicas
    st.write("Estatísticas Básicas:")
    st.write(data.describe())

    # Filtros
    st.sidebar.header("Filtros")

    # Filtro por Clube
    if 'clube' in data.columns:
        unique_teams = data['clube'].unique()
        selected_team = st.sidebar.selectbox("Selecione um clube:", unique_teams)
    else:
        st.error("Coluna 'clube' não encontrada nos dados.")

    # Filtro por Data
    if 'rodata' in data.columns:
        unique_dates = data['rodata'].unique()
        selected_date = st.sidebar.selectbox("Selecione a data:", unique_dates)
    else:
        st.error("Coluna 'rodata' não encontrada nos dados.")

    # Filtrar dados com base na seleção
    filtered_data = data[(data['clube'] == selected_team) & (data['rodata'] == selected_date)]

    # Gráfico de Cartões por Clube
    if 'cartao_amarelo' in data.columns:
        st.write("Cartões por Clube:")
        cartoes_por_clube = data['cartao_amarelo'].value_counts()
        st.bar_chart(cartoes_por_clube)
    else:
        st.error("Coluna 'cartao_amarelo' não encontrada nos dados.")

    # Comparação de Jogadores
    st.write("Comparação de Desempenho de Jogadores:")
    if 'atleta' in data.columns:
        comparison_players = st.sidebar.multiselect("Selecione os jogadores para comparar:", data['atleta'].unique())
        
        if len(comparison_players) > 1:  # Certifica-se de que pelo menos 2 jogadores estão selecionados
            comparison_data = data[data['atleta'].isin(comparison_players)]
            metrics = ['chutes', 'chutes_no_alvo', 'posse_de_bola', 'passes', 'precisao_passes', 'faltas', 'cartao_amarelo', 'cartao_vermelho', 'impedimentos', 'escanteios']
            comparison_results = comparison_data.groupby('atleta')[metrics].sum().reset_index()
            
            st.write("Desempenho Comparativo:")
            st.dataframe(comparison_results)

            # Gráfico de Comparação
            comparison_results.set_index('atleta').plot(kind='bar', figsize=(12, 6))
            plt.title('Comparação de Desempenho entre Jogadores')
            plt.ylabel('Métricas')
            st.pyplot(plt)
        else:
            st.warning("Selecione pelo menos dois jogadores para comparar.")
    else:
        st.error("Coluna 'atleta' não encontrada nos dados.")

    # Comparação de Cartões
    st.write("Comparação de Cartões entre Jogadores:")
    if 'atleta' in data.columns:
        card_players = st.sidebar.multiselect("Selecione os jogadores para comparar cartões:", data['atleta'].unique())
        
        if len(card_players) > 1:  # Certifica-se de que pelo menos 2 jogadores estão selecionados
            card_data = data[data['atleta'].isin(card_players)]
            # Agrupar por jogador e somar os cartões
            card_comparison_results = card_data.groupby('atleta').agg({'cartao_amarelo': 'sum', 'cartao_vermelho': 'sum'}).reset_index()
            
            st.write("Comparação de Cartões:")
            st.dataframe(card_comparison_results)

            # Gráfico de Comparação de Cartões
            card_comparison_results.set_index('atleta').plot(kind='bar', figsize=(12, 6))
            plt.title('Comparação de Cartões entre Jogadores')
            plt.ylabel('Número de Cartões')
            st.pyplot(plt)
        else:
            st.warning("Selecione pelo menos dois jogadores para comparar cartões.")
    else:
        st.error("Coluna 'atleta' não encontrada nos dados.")

    # Tabela de Desempenho do Clube Selecionado
    st.write(f"Desempenho do {selected_team}:")
    st.dataframe(filtered_data)  # Mostra os dados filtrados

    # Gráfico de Distribuição de Cartões
    st.write("Distribuição de Cartões:")
    if 'cartao_amarelo' in data.columns:
        # Tentar converter a coluna cartao_amarelo para numérico
        data['cartao_amarelo'] = pd.to_numeric(data['cartao_amarelo'], errors='coerce')  # Converte strings para NaN onde não é possível

        # Remover NaN
        valid_cartoes = data['cartao_amarelo'].dropna()
        
        plt.figure(figsize=(10, 5))
        plt.hist(valid_cartoes, bins=30, color='red', alpha=0.7)
        plt.title('Distribuição de Cartões')
        plt.xlabel('Número de Cartões')
        plt.ylabel('Frequência')
        st.pyplot(plt)
    else:
        st.error("Coluna 'cartao_amarelo' não encontrada nos dados.")

    # Tabela de Melhores Jogadores por Cartões
    st.write("Jogadores com Mais Cartões:")
    if 'atleta' in data.columns:
        top_players = data['atleta'].value_counts().head(10)
        st.bar_chart(top_players)
    else:
        st.error("Coluna 'atleta' não encontrada nos dados.")

    # Tabela de Resultados
    st.write("Tabela de Resultados:")
    if all(col in data.columns for col in ['partida_id', 'rodata', 'clube', 'cartao_amarelo', 'atleta', 'num_camisa', 'posicao', 'minuto']):
        resultados = data[['partida_id', 'rodata', 'clube', 'cartao_amarelo', 'atleta', 'num_camisa', 'posicao', 'minuto']]
        st.dataframe(resultados)
    else:
        st.error("Uma ou mais colunas necessárias para a tabela de resultados não foram encontradas.")
