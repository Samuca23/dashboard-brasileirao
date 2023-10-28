import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
from dados import (
    tabela_sort,
    df_cluster_grupo,
    getNomeTimeFromSigla,
    brasileirao,
    calcular_tabela,
    calcular_cluster,
    calcular_regressao,
    calcula_regressao_meio_campeonato,
    df_chance_cluster,
    brasileirao_all,
)


# Método para retornar a tabela de Classificação.
def getDadoTabelaClassificacao(bAddClomunCluster=False):
    classificacao = tabela_sort[["Time", "J", "P", "V", "E", "D", "GP", "GC", "SG"]]
    classificacao["GP"] = classificacao["GP"].astype(int)
    classificacao["GC"] = classificacao["GC"].astype(int)
    classificacao["SG"] = classificacao["SG"].astype(int)
    if bAddClomunCluster:
        classificacao["Cluster"] = tabela_sort[["cluster"]]

    return classificacao


# Método para retornar a Classificação com os Grupos.
def getClassificaoGrupo():
    classificacaoGrupo = getDadoTabelaClassificacao(bAddClomunCluster=True)
    for index, row in classificacaoGrupo.iterrows():
        for _, cluster_grupo in df_cluster_grupo.iterrows():
            if row["Cluster"] == cluster_grupo["cluster"]:
                classificacaoGrupo.loc[index, "Grupo"] = cluster_grupo["grupo"]

    return classificacaoGrupo


# Método para criar o painel de dados do campeonato
def createPainelCampeonato():
    st.subheader("Dados do campeonato.")
    card_total_jogo, card_total_gols, card_total_ponto, card_media_gol = st.columns(4)
    card_primeiro_colocado, card_time_mais_gol = st.columns(2)
    total_gol = int(brasileirao["Score_m"].sum() + brasileirao["Score_v"].sum())
    total_ponto = tabela_sort["P"].sum()
    time_mais_gol = getNomeTimeFromSigla(
        tabela_sort[tabela_sort["GP"].notnull().sort_values(ascending=False)][
            "Time"
        ].iloc[0]
    )
    primeiro_colocado = getDadoTabelaClassificacao().iloc[0]
    nome_primeiro_colocado = getNomeTimeFromSigla(primeiro_colocado["Time"])
    total_rodada_jogada = (
        brasileirao[brasileirao["Score_m"].notnull()]["Rodada"].unique().max()
    )
    media_gol_rodada = total_gol / total_rodada_jogada

    card_total_jogo.metric(
        "Total de jogos",
        brasileirao[brasileirao["Score_m"].notnull()]["Rodada"].count(),
    )
    card_total_gols.metric("Total de gols", total_gol)
    card_total_ponto.metric("Total de pontos", total_ponto)
    card_media_gol.metric("Média de gol por rodada", round(media_gol_rodada))
    card_primeiro_colocado.metric("Primeiro colocado", nome_primeiro_colocado)
    card_time_mais_gol.metric("Time com mais gols", time_mais_gol)
    style_metric_cards(
        border_left_color="#4fb342",
        background_color="#F0F2F6",
        border_size_px=3,
        border_color="#CECED0",
        border_radius_px=10,
        box_shadow=True,
    )


# Método utilizado para criar a tabela de Classificação
def createTabelaClassificacao():
    st.subheader("Classificação Brasileirão 2023.")
    progresso = st.toggle("Progresso dos dados 📈")
    dadoTabelaClassificacao = getDadoTabelaClassificacao()

    iClassificacao = 0
    for i in dadoTabelaClassificacao["Time"]:
        iClassificacao += 1
        dadoTabelaClassificacao.loc[
            dadoTabelaClassificacao["Time"] == i, "Classificação"
        ] = f"{iClassificacao}º"

    dadoTabelaClassificacao = dadoTabelaClassificacao[
        ["Classificação", "Time", "J", "P", "V", "E", "D", "GP", "GC", "SG"]
    ]

    if progresso:
        pon_max = int(dadoTabelaClassificacao["P"].max())
        vit_max = int(dadoTabelaClassificacao["V"].max())
        emp_max = int(dadoTabelaClassificacao["E"].max())
        der_max = int(dadoTabelaClassificacao["D"].max())
        gop_max = int(dadoTabelaClassificacao["GP"].max())
        goc_max = int(dadoTabelaClassificacao["GC"].max())
        sag_max = int(dadoTabelaClassificacao["SG"].max())
        st.dataframe(
            dadoTabelaClassificacao,
            height=750,
            hide_index=True,
            use_container_width=True,
            column_config={
                "P": st.column_config.ProgressColumn(
                    "P", format="%f", min_value=0, max_value=pon_max
                ),
                "V": st.column_config.ProgressColumn(
                    "V", format="%f", min_value=0, max_value=vit_max
                ),
                "E": st.column_config.ProgressColumn(
                    "E", format="%f", min_value=0, max_value=emp_max
                ),
                "D": st.column_config.ProgressColumn(
                    "D", format="%f", min_value=0, max_value=der_max
                ),
                "GP": st.column_config.ProgressColumn(
                    "GP", format="%f", min_value=0, max_value=gop_max
                ),
                "GC": st.column_config.ProgressColumn(
                    "GC", format="%f", min_value=0, max_value=goc_max
                ),
                "SG": st.column_config.ProgressColumn(
                    "SG", format="%f", min_value=0, max_value=sag_max
                ),
            },
        )
    else:
        st.dataframe(
            dadoTabelaClassificacao,
            height=750,
            hide_index=True,
            use_container_width=True,
        )


# Método utilizado para criar a tabela de Classificação com Grupo
def createTableClassificacaoGrupo():
    st.subheader("Classificação Brasileirão 2023 por Grupo.")
    opcao = st.selectbox("Escolha o Grupo", (df_cluster_grupo["grupo"]))
    classificacaoGrupo = getClassificaoGrupo()
    st.dataframe(
        classificacaoGrupo[classificacaoGrupo["Grupo"] == opcao],
        hide_index=True,
        use_container_width=True,
    )


# Método para criar os gráficos de desempenho dos time durante o campeonato
def createTableCluster():
    st.subheader("Gráficos de desempenho dos times durante o campeonato. 📉")
    rodada_inicial = st.slider("Rodada", min_value=2, max_value=38, value=10)
    clusters = []
    for rodada in range(
        rodada_inicial,
        brasileirao[brasileirao["Score_m"].notnull()]["Rodada"].max() + 1,
    ):
        bra_rodada = brasileirao[brasileirao["Rodada"] <= rodada].copy()
        bra_rodada = bra_rodada[bra_rodada["Score_m"].notnull()]
        tabela_rodada = calcular_tabela(bra_rodada)
        tabela_rodada_cluster = calcular_cluster(tabela_rodada)

        for index, row in tabela_rodada_cluster.iterrows():
            if row["Ranking"] == 1:
                tabela_rodada_cluster.loc[index, "Ranking"] = "Rebaixamento"
            elif row["Ranking"] == 2:
                tabela_rodada_cluster.loc[index, "Ranking"] = "Limbo"
            elif row["Ranking"] == 3:
                tabela_rodada_cluster.loc[index, "Ranking"] = "Sul-Americana"
            elif row["Ranking"] == 4:
                tabela_rodada_cluster.loc[index, "Ranking"] = "Libertadores"
            elif row["Ranking"] == 5:
                tabela_rodada_cluster.loc[index, "Ranking"] = "Título"

        for index, row in tabela_rodada_cluster.iterrows():
            clusters.insert(
                len(clusters),
                [rodada, row["Time"], row["Pontos"], row["Cluster"], row["Ranking"]],
            )
    clusters = pd.DataFrame(
        clusters, columns=["Rodada", "Time", "Pontos", "Cluster", "Grupo"]
    )
    tabela_atual = calcular_tabela(brasileirao[brasileirao["Score_m"].notnull()])
    tabela_atual = tabela_atual.sort_values(
        by=["Pontos", "Vit", "Saldo"], ascending=False
    )
    colocacao = list(tabela_atual["Time"])
    domain = ["Rebaixamento", "Limbo", "Sul-Americana", "Libertadores", "Título"]
    range_color = ["red", "orange", "yellow", "green", "blue"]
    opaco = ["#023999", "gray", "lightgray", "turquoise", "steelblue"]

    grafico_circle_1, grafico_circle_2 = st.columns(2)

    grafico_circle_1.altair_chart(
        alt.Chart(clusters, title="Brasileirao - Gráfico 1")
        .mark_circle(size=200)
        .encode(
            x="Rodada:O",
            y=alt.Y("Time:O", sort=colocacao),
            size=alt.Size("Grupo:O", scale=alt.Scale(domain=domain)),
            color=alt.Color(
                "Grupo:O", scale=alt.Scale(domain=domain, range=range_color)
            ),
            tooltip=[
                alt.Tooltip("Time", title="Time"),
                alt.Tooltip("sum(Pontos)", title="Pontos"),
            ],
        )
    )

    grafico_circle_2.altair_chart(
        alt.Chart(clusters, title="Brasileirao - Gráfico 2")
        .mark_circle(size=200)
        .encode(
            x="Rodada:O",
            y=alt.Y("Time:O", sort=colocacao),
            color=alt.Color(
                "Grupo:O", scale=alt.Scale(domain=domain, range=range_color)
            ),
            tooltip=[
                alt.Tooltip("Time", title="Time"),
                alt.Tooltip("sum(Pontos)", title="Pontos"),
            ],
        )
    )
    base = alt.Chart(clusters, title="Brasileirao - Heatmap ponto").encode(
        x="Rodada:O", y=alt.Y("Time:O", sort=colocacao)
    )
    heatmap = base.mark_rect().encode(
        color=alt.Color("Grupo:O", scale=alt.Scale(domain=domain, range=opaco)),
    )
    text = base.mark_text(baseline="middle").encode(
        text="Pontos",
        color=alt.condition(
            alt.datum.Grupo < 3, alt.value("white"), alt.value("black")
        ),
    )

    heatmap_no_ponit, heatmap_ponit = st.columns(2)

    heatmap_ponit.altair_chart(heatmap + text)

    heatmap_no_ponit.altair_chart(
        alt.Chart(clusters, title="Brasileirao - Heatmap")
        .mark_rect()
        .encode(
            x="Rodada:O",
            y=alt.Y("Time:O", sort=colocacao),
            color=alt.Color(
                "Grupo:O", scale=alt.Scale(domain=domain, range=range_color)
            ),
            tooltip=[
                alt.Tooltip("Time", title="Time"),
                alt.Tooltip("sum(Pontos)", title="Pontos"),
            ],
        )
        .configure_view(step=20, strokeWidth=1)
        .configure_axis(domain=False)
    )


# Método utilizado para criar a tabela de chances do time em cada grupo (clustes)
def createTableChanceCluster():
    st.subheader("Chances de grupos.")
    df_chance_pred = df_chance_cluster().copy()
    df_chance_pred.rename(
        columns={
            "cl_o": "Rebaixamento",
            "cl_1": "Sul-Americana",
            "cl_2": "Libertadores",
            "cl_3": "Limbo",
            "cl_4": "Título",
        },
        inplace=True,
    )
    df_chance_pred["Título"] = trataValorPorcentagemTime(df_chance_pred["Título"])
    df_chance_pred["Libertadores"] = trataValorPorcentagemTime(
        df_chance_pred["Libertadores"]
    )
    df_chance_pred["Sul-Americana"] = trataValorPorcentagemTime(
        df_chance_pred["Sul-Americana"]
    )
    df_chance_pred["Limbo"] = trataValorPorcentagemTime(df_chance_pred["Limbo"])
    df_chance_pred["Rebaixamento"] = trataValorPorcentagemTime(
        df_chance_pred["Rebaixamento"]
    )
    df_chance_pred = df_chance_pred[
        ["Time", "Título", "Libertadores", "Sul-Americana", "Limbo", "Rebaixamento"]
    ]
    st.dataframe(
        df_chance_pred.sort_values(by="Título", ascending=False),
        hide_index=True,
        height=750,
        use_container_width=True,
        column_config={
            "Título": st.column_config.Column("Título %"),
            "Libertadores": st.column_config.Column("Libertadores %"),
            "Sul-Americana": st.column_config.Column("Sul-Americana %"),
            "Limbo": st.column_config.Column("Limbo %"),
            "Rebaixamento": st.column_config.Column("Rebaixamento %"),
        },
    )


# Método utilizado para a criação da tela de previsão dos dados (Regressão)
def createTabelaRegressao():
    dadoTabelaClassificacao = calcular_regressao()

    iClassificacao = 0
    for i in dadoTabelaClassificacao["time"]:
        iClassificacao += 1
        dadoTabelaClassificacao.loc[
            dadoTabelaClassificacao["time"] == i, "Classificação"
        ] = f"{iClassificacao}º"

    dadoTabelaClassificacao = dadoTabelaClassificacao[
        ["Classificação", "time", "pontuacao_final", "intercept", "slope"]
    ]
    st.dataframe(
        dadoTabelaClassificacao,
        height=750,
        hide_index=True,
        use_container_width=True,
        column_config={
            "time": st.column_config.Column("Time"),
            "pontuacao_final": st.column_config.Column("Pontuação"),
        },
    )


# Método utilizado para a criação da tela de previsão dos dados do meio do campeonato em diante (Regressão)
def createTabelaRegressaoMeioCampeonato():
    rodada_inicial = st.slider("Rodada", min_value=1, max_value=38, value=19)
    dadoTabelaClassificacao = calcula_regressao_meio_campeonato(rodada_inicial)

    iClassificacao = 0
    for i in dadoTabelaClassificacao["time"]:
        iClassificacao += 1
        dadoTabelaClassificacao.loc[
            dadoTabelaClassificacao["time"] == i, "Classificação"
        ] = f"{iClassificacao}º"

    dadoTabelaClassificacao = dadoTabelaClassificacao[
        ["Classificação", "time", "pontuacao_final", "intercept", "slope"]
    ]
    st.dataframe(
        dadoTabelaClassificacao,
        height=750,
        hide_index=True,
        use_container_width=True,
        column_config={
            "time": st.column_config.Column("Time"),
            "pontuacao_final": st.column_config.Column("Pontuação"),
        },
    )


# Método utilizado para centralizar a criação das tabelas de previsão de dados (Regressão)
def createAreaRegressao():
    st.subheader("Tabela de possíveis pontos finais. 🏆")
    createTabelaRegressao()
    st.subheader("Tabela com possibilidade de mudança das rodadas")
    createTabelaRegressaoMeioCampeonato()

# Método criado para exibir os jogos
def createTableJogos():
    selecao = st.radio(
        "Filtros", ["Por rodada", "Disputados", "Todos jogos"], horizontal=True
    )

    if selecao == "Todos jogos":
        brasileirao_all_copy = brasileirao_all.copy()
        brasileirao_all_copy = brasileirao_all_copy.drop("Temporada", axis=1)
        rodada = 0
        for index, row in brasileirao_all.iterrows():
            if np.isnan(row['Score_m']):
                score_m = 'null'
                score_v = 'null'
            else:
                score_m = int(row['Score_m'])
                score_v = int(row['Score_v'])
            if rodada == 0 | rodada != row["Rodada"]:
                rodada = row["Rodada"]
                st.subheader(f"")
                st.divider()
                st.subheader(f"Rodada: {row['Rodada']}")
            st.markdown(f"{row['Mandante']}  {score_m}  x  {score_v}  {row['Visitante']}")
    elif selecao == "Disputados":
        brasileirao_copy = brasileirao.copy()
        rodada = 0
        for index, row in brasileirao_copy.iterrows():
            if np.isnan(row['Score_m']):
                score_m = 'null'
                score_v = 'null'
            else:
                score_m = int(row['Score_m'])
                score_v = int(row['Score_v'])
            if rodada == 0 | rodada != row["Rodada"]:
                rodada = row["Rodada"]
                st.subheader(f"")
                st.divider()
                st.subheader(f"Rodada: {row['Rodada']}")
            st.markdown(f"{row['Mandante']}  {score_m}  x  {score_v}  {row['Visitante']}")
    elif selecao == "Por rodada":
        rodada = st.slider(
            "Rodada", min_value=1, max_value=brasileirao["Rodada"].max(), value=1
        )

        if selecao == "Por rodada" and rodada:
            brasileirao_all_copy = brasileirao_all.copy()
            brasileirao_all_copy = brasileirao_all_copy.drop("Temporada", axis=1)
            st.subheader(f"Rodada: {rodada}")
            for index, row in brasileirao_all_copy[brasileirao_all_copy["Rodada"] == rodada].iterrows():
                score_m = int(row['Score_m'])
                score_v = int(row['Score_v'])                               
                st.markdown(f"{row['Mandante']}  {score_m}  x  {score_v}  {row['Visitante']}")

# Método para criar a tabela de alteração de resultados
def createEditResultado():
    st.text("Essa ação é disponível somente para Administradores.")
    dados_editados = st.data_editor(
        brasileirao_all,
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
            dados_editados.to_excel('../data/brasileirao2023.xlsx', index=False)

# Método utilizado para tratando dos valores para porcentagem
def trataValorPorcentagemTime(valor):
    retorno = valor * 100

    return round(retorno)


# Método utilizado para criar o Dashboard do campeonato
def createDashboardCampeonato():
    (
        painel_campeonato,
        classificao_grupo,
        classificacao_regressao,
        chances_campeonato,
        jogos,
        resultados
    ) = st.tabs(
        [
            "Campeonato e Classificação",
            "Classificação - Grupo",
            "Classificação - Previsão",
            "Chances de Grupos",
            "Jogos",
            "Resultados"
        ]
    )

    with painel_campeonato:
        createPainelCampeonato()
        createTabelaClassificacao()
    with classificao_grupo:
        createTableClassificacaoGrupo()
        createTableCluster()
    with classificacao_regressao:
        createAreaRegressao()
    with chances_campeonato:
        createTableChanceCluster()
    with jogos:
        createTableJogos()
    with resultados:
        createEditResultado()
