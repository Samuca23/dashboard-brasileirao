import streamlit as st
import pandas as pd
import altair as alt
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_vertical_slider import vertical_slider
from streamlit_card import card
from sklearn.cluster import KMeans
from dados import tabela_sort, tabela, df_cluster_grupo, getNomeTimeFromSigla, brasileirao, calcular_tabela, calcular_cluster

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
    card_total_jogo, card_total_gols, card_media_gol, card_total_ponto = st.columns(4)
    card_primeiro_colocado, card_time_mais_gol = st.columns(2)
    total_gol = int(brasileirao['Score_m'].sum() + brasileirao['Score_v'].sum())
    total_ponto = tabela_sort['P'].sum()
    time_mais_gol = getNomeTimeFromSigla(tabela_sort[tabela_sort['GP'].notnull().sort_values(ascending=False)]['Time'].iloc[0])
    primeiro_colocado = getDadoTabelaClassificacao().iloc[0]
    nome_primeiro_colocado = getNomeTimeFromSigla(primeiro_colocado['Time'])
    total_rodada_jogada = brasileirao[brasileirao['Score_m'].notnull()]['Rodada'].unique().max()
    media_gol_rodada = total_gol / total_rodada_jogada

    card_total_jogo.metric('Total de jogos', brasileirao[brasileirao['Score_m'].notnull()]['Rodada'].count())
    card_total_gols.metric('Total de gols', total_gol)
    card_media_gol.metric('Média de gol por rodada', round(media_gol_rodada))
    card_total_ponto.metric('Total de pontos', total_ponto)
    card_primeiro_colocado.metric('Primeiro colocado', nome_primeiro_colocado)
    card_time_mais_gol.metric('Time com mais gols', time_mais_gol)
    style_metric_cards(
        border_left_color="#4fb342",
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

# Método para criar os gráficos de desempenho dos time durante o campeonato
def createTableCluster() :
    st.subheader('Gráficos de desempenho dos times durante o campeonato')
    rodada_inicial = st.slider('Rodada', min_value = 2, max_value = 38)
    clusters = []
    for rodada in range(rodada_inicial, brasileirao[brasileirao['Score_m'].notnull()]['Rodada'].max() + 1):
        bra_rodada = brasileirao[brasileirao['Rodada'] <= rodada].copy()
        bra_rodada = bra_rodada[bra_rodada['Score_m'].notnull()]
        tabela_rodada = calcular_tabela(bra_rodada)
        tabela_rodada_cluster = calcular_cluster(tabela_rodada)
        for index, row in tabela_rodada_cluster.iterrows():
            clusters.insert(len(clusters), [rodada, row['Time'], row['Pontos'], row['Cluster'], row['Ranking']])
    clusters = pd.DataFrame(clusters, columns = ['Rodada', 'Time', 'Pontos', 'Cluster', 'Grupo'])
    tabela_atual = calcular_tabela(brasileirao[brasileirao['Score_m'].notnull()])
    tabela_atual = tabela_atual.sort_values(by=['Pontos','Vit','Saldo'], ascending=False)
    colocacao = list(tabela_atual['Time'])
    domain = [1, 2, 3, 4, 5]
    range_color = ['red', 'orange', 'yellow', 'green', 'blue']
    opaco = ['black', 'gray', 'lightgray', 'turquoise', 'steelblue']

    st.altair_chart(
        alt.Chart(clusters, title="Brasileirao - Gráfico 1").mark_circle(size=200).encode(
            x='Rodada:O',
            y = alt.Y("Time:O", sort=colocacao),
            size='sum(Grupo):O',
            color=alt.Color('Grupo:O', scale=alt.Scale(domain=domain, range=range_color)),
            tooltip=[
                alt.Tooltip("Time", title="Time"),
                alt.Tooltip("sum(Pontos)", title="Pontos"),
            ]
        )
    )

    st.altair_chart(
        alt.Chart(clusters, title="Brasileirao - Gráfico 2").mark_circle(size=200).encode(
            x='Rodada:O',
            y = alt.Y("Time:O", sort=colocacao),
            color=alt.Color('Grupo:O', scale=alt.Scale(domain=domain, range=range_color)),
            tooltip=[
                alt.Tooltip("Time", title="Time"),
                alt.Tooltip("sum(Pontos)", title="Pontos"),
            ]
        )
    )
    base = alt.Chart(clusters, title="Brasileirao - Heatmap ponto").encode(
        x = "Rodada:O", y = alt.Y("Time:O", sort=colocacao)
    )
    heatmap = base.mark_rect().encode(
        color=alt.Color('Grupo:O', scale=alt.Scale(domain=domain, range=opaco)),
    )
    text = base.mark_text(baseline='middle').encode(
        text = 'Pontos',
        color=alt.condition(
            alt.datum.Grupo < 3,
            alt.value('white'),
            alt.value('black')
        )
    )
    st.altair_chart(heatmap + text)
    st.altair_chart(
        alt.Chart(clusters, title="Brasileirao - Heatmap").mark_rect().encode(
            x = "Rodada:O",
            y = alt.Y("Time:O", sort=colocacao),
            color=alt.Color('Grupo:O', scale=alt.Scale(domain=domain, range=range_color)),
            tooltip=[
                alt.Tooltip("Time", title="Time"),
                alt.Tooltip("sum(Pontos)", title="Pontos"),
            ]
            ).configure_view(
                step=20,
                strokeWidth=1
            ).configure_axis(
                domain=False
            )
        )
    
# Método utilizado para criar o Dashboard do campeonato
def createDashboardCampeonato():
    createPainelCampeonato()
    createTabelaClassificacao()
    createTableClassificacaoGrupo()
    createTableCluster()