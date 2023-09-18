import pandas as pd
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_vertical_slider import vertical_slider
from streamlit_card import card
import altair as alt
from funcao import calcular_tabela, calcular_cluster

st.set_page_config(layout="wide")
st.title('App - Brasileirão')

# Leitura dos banco de dados em cache
# @st.cache_data
def load_database():
    return pd.read_excel('../data/brasileirao2023.xlsx')

bra = load_database()

cla, rod, res, anl = st.tabs(['Classificação', 'Rodadas', 'Resultados', 'Análise'])

with cla:
    tabela_atual = calcular_tabela(bra[bra['Score_m'].notnull()])
    st.header('Classificação Atual', divider=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Numero de Jogos', bra[bra['Score_m'].notnull()]['Rodada'].unique().sum())
    # card('Brasileirão', 'Dados do Brasileirão')
    style_metric_cards(
        border_left_color="#3D5077",
        background_color="#F0F2F6",
        border_size_px=3,
        border_color = "#CECED0",
        border_radius_px = 10,
        box_shadow=True
    )
    grafico = st.toggle('Grafico')
    if grafico:
        vit_max = tabela_atual['Vit'].max()
        st.dataframe(
            tabela_atual.sort_values(by=['Pontos','Vit','Saldo'], ascending=False),
            height=750,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Vit": st.column_config.ProgressColumn(
                    "Vitórias",
                    format="%f",
                    min_value=0,
                    max_value=16,
                ),
            }
        )
    else:
        st.dataframe(
            tabela_atual.sort_values(by=['Pontos','Vit','Saldo'], ascending=False),
            height=750,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Vit": "Vitórias",
                "Emp": "Empates",
                "Der": "Derrotas",
                "GPro": "Gols Próprios",
                "GCon": "Gols Contra"
            }
        )
with rod:
    # rodada = st.slider('Rodada', min_value=1, max_value=38)
    c1, c2 = st.columns([1,7])
    with c1:
        rodd = vertical_slider(
            key="slider",
            default_value=22,
            step=1,
            min_value=1,
            max_value=38,
            track_color="gray",  # optional
            thumb_color="blue",  # optional
            slider_color="gray",  # optional
        )
    c2.dataframe(
        bra[bra['Rodada'] == rodd],
        column_config={
            "Score_m": st.column_config.ProgressColumn(
                "Placar Mandante",
                help="Gols marcados pelo Mandante",
                format="%f",
                min_value=0,
                max_value=5,
                width='medium'
            ),
            "Score_v": st.column_config.ProgressColumn(
                "Placar Visitante",
                help="Gols marcados pelo Visitante",
                format="%f",
                min_value=0,
                max_value=5,
                width='medium'
            ),
        },
        hide_index=True,
    )
with res:
    dados_editados = st.data_editor(
        bra,
        column_config={
            "Score_m": st.column_config.NumberColumn(
                "Placar Mandante",
                help="Gols marcados pelo Mandante",
                format="%f",
                min_value=0,
                max_value=5,
                width='medium'
            ),
            "Score_v": st.column_config.NumberColumn(
                "Placar Visitante",
                help="Gols marcados pelo Visitante",
                format="%f",
                min_value=0,
                max_value=5,
                width='medium'
            ),
        },
        disabled=["Temporada", "Rodada", "Mandante", "Visitante"],
        hide_index=True,
        key='data_editor'
    )
    if len(st.session_state["data_editor"]["edited_rows"]) > 0:
        if st.button('Salvar dados...'):
            dados_editados.to_excel('brasileirao2023.xlsx', index=False)
with anl:
    cluster, regressao = st.tabs(['Clusterização', 'Regressão'])
    with cluster:
        rodada_inicial = st.slider('Rodada', value = 10, min_value = 5, max_value = 20)
        clusters = []
        for rodada in range(rodada_inicial, bra[bra['Score_m'].notnull()]['Rodada'].max() + 1):
            bra_rodada = bra[bra['Rodada'] <= rodada].copy()
            bra_rodada = bra_rodada[bra_rodada['Score_m'].notnull()]
            tabela_rodada = calcular_tabela(bra_rodada)
            tabela_rodada_cluster = calcular_cluster(tabela_rodada)
            for index, row in tabela_rodada_cluster.iterrows():
                clusters.insert(len(clusters), [rodada, row['Time'], row['Pontos'], row['Cluster'], row['Ranking']])
        clusters = pd.DataFrame(clusters, columns = ['Rodada', 'Time', 'Pontos', 'Cluster', 'Grupo'])
        tabela_atual = calcular_tabela(bra[bra['Score_m'].notnull()])
        tabela_atual = tabela_atual.sort_values(by=['Pontos','Vit','Saldo'], ascending=False)
        colocacao = list(tabela_atual['Time'])
        htmp = st.toggle('Heatmap')
        domain = [1, 2, 3, 4, 5]
        range = ['red', 'orange', 'yellow', 'green', 'blue']
        opaco = ['black', 'gray', 'lightgray', 'turquoise', 'steelblue']
        if htmp:
            pontos = st.toggle('Pontos')
            if pontos:
                base = alt.Chart(clusters, title="Brasileirao").encode(
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
            else:
                st.altair_chart(
                    alt.Chart(clusters, title="Brasileirao").mark_rect().encode(
                        x = "Rodada:O",
                        y = alt.Y("Time:O", sort=colocacao),
                        color=alt.Color('Grupo:O', scale=alt.Scale(domain=domain, range=range)),
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
        else:
            c1, c2 = st.columns(2)
            c1.altair_chart(
                alt.Chart(clusters, title="Brasileirao").mark_circle(size=200).encode(
                    x='Rodada:O',
                    y = alt.Y("Time:O", sort=colocacao),
                    size='sum(Grupo):O',
                    color=alt.Color('Grupo:O', scale=alt.Scale(domain=domain, range=range)),
                    tooltip=[
                        alt.Tooltip("Time", title="Time"),
                        alt.Tooltip("sum(Pontos)", title="Pontos"),
                    ]
                )
            )
            c2.altair_chart(
                alt.Chart(clusters, title="Brasileirao").mark_circle(size=200).encode(
                    x='Rodada:O',
                    y = alt.Y("Time:O", sort=colocacao),
                    color=alt.Color('Grupo:O', scale=alt.Scale(domain=domain, range=range)),
                    tooltip=[
                        alt.Tooltip("Time", title="Time"),
                        alt.Tooltip("sum(Pontos)", title="Pontos"),
                    ]
                )
            )
