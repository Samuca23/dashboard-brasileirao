import streamlit as st
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards
from sklearn.cluster import KMeans
from dados import tabela_sort, tabela, df_cluster_grupo, getNomeTimeFromSigla, brasileirao

# Método para retornar a tabela de Classificação.
def getDadoTabelaClassificacao(bAddClomunCluster = False):
    classificacao = tabela_sort[['Time', 'P', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG']]
    classificacao['GP'] = classificacao['GP'].astype(int)
    classificacao['GC'] = classificacao['GC'].astype(int)
    classificacao['SG'] = classificacao['SG'].astype(int)
    if bAddClomunCluster:
        classificacao['Cluster'] = tabela_sort[['cluster']]

    return classificacao

# Método para retornar a Classificação com os Grupos.
def getClassificaoGrupo():
    classificacaoGrupo = getDadoTabelaClassificacao(bAddClomunCluster=True)
    for index, row in classificacaoGrupo.iterrows():
        for _, cluster_grupo in df_cluster_grupo.iterrows():
            if row['Cluster'] == cluster_grupo['cluster']:
                classificacaoGrupo.loc[index, 'Grupo'] = cluster_grupo['grupo']

    return classificacaoGrupo

# Método para criar o painel de dados do campeonato
def createPainelCampeonato():
    st.subheader("Dados do campeonato")
    card_total_jogo, card_total_gols= st.columns(2)
    card_total_jogo.metric('Total de Jogos', brasileirao[brasileirao['Score_m'].notnull()]['Rodada'].unique().sum())
    total_gol = int(brasileirao['Score_m'].sum() + brasileirao['Score_v'].sum())
    card_total_gols.metric('Total de Gols', total_gol)

# Método utilizado para criar um painel do possível campeão do campeonato
def createPainelPrimeiroColocado():
    primeiro_colocado = getDadoTabelaClassificacao().iloc[0]
    nome_primeiro_colocado = getNomeTimeFromSigla(primeiro_colocado['Time'])
    st.subheader("Primeiro colocado ⭐")
    card_time, card_ponto_time, card_jogo, card_vitoria = st.columns(4)
    card_time.metric('Time', nome_primeiro_colocado)
    card_ponto_time.metric('Pontuação', primeiro_colocado['P'])
    card_jogo.metric('Jogos', primeiro_colocado['J'])
    card_vitoria.metric('Vitórias', primeiro_colocado['V'])
    style_metric_cards(
        border_left_color="#15B000",
        background_color="#F0F2F6",
        border_size_px=3,
        border_color = "#CECED0",
        border_radius_px = 10,
        box_shadow=True
    )

# Método utilizado para criar a tabela de Classificação
def createTabelaClassificacao():
    st.subheader('Classificação Brasileirão 2023 - Série A 📜')
    st.table(getDadoTabelaClassificacao())

# Método utilizado para criar a tabela de Classificação com Grupo
def createTableClassificacaoGrupo():
    st.subheader('Classificação Brasileirão 2023 por Grupo - Série A 📜')
    opcao = st.selectbox(
        'Escolha o Grupo',
        (df_cluster_grupo['grupo']))
    classificacaoGrupo = getClassificaoGrupo()
    st.table(classificacaoGrupo[classificacaoGrupo['Grupo'] == opcao])

# Método utilizado para criar o Dashboard do campeonato
def createDashboardCampeonato():
    createPainelCampeonato()
    createPainelPrimeiroColocado()
    createTabelaClassificacao()
    createTableClassificacaoGrupo()