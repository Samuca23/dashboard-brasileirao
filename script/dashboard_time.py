import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from dados import (
    brasileirao,
    tabela_sort,
    df_cluster_grupo,
    df_chance_cluster,
    getAllTimes,
    getSiglaTimeFromNome,
    getNomeTimeFromSigla,
    calcular_regressao,
    calcula_regressao_cluster
)


def createSelecboxTime():
    times = getAllTimes()
    st.header("Estatísticas do Time.")
    opcao_padrao = "Selecione um time..."
    times_lista = [opcao_padrao] + times["Time"].tolist()

    selected = st.selectbox("Escolha um time:", times_lista)

    if selected != opcao_padrao:
        createDashboardTime(getSiglaTimeFromNome(selected))


# Método de criação do  Dashboard individual do time
def createDashboardTime(sigla):
    montaPainelTime(sigla)


def getDadoTabelaClassificacao(bAddClomunCluster=False):
    iClassificacao = 0
    for i in tabela_sort["Time"]:
        iClassificacao += 1
        tabela_sort.loc[
            tabela_sort["Time"] == i, "Classificação"
        ] = f"{iClassificacao}º"

    classificacao = tabela_sort[
        ["Classificação", "Time", "P", "J", "V", "E", "D", "GP", "GC", "SG"]
    ]
    classificacao["GP"] = classificacao["GP"].astype(int)
    classificacao["GC"] = classificacao["GC"].astype(int)
    classificacao["SG"] = classificacao["SG"].astype(int)
    if bAddClomunCluster:
        classificacao["Cluster"] = tabela_sort[["cluster"]]

    return classificacao


# Método para montar o painel de métricar de status do time no campeonáto
def montaPainelTime(sigla):
    df_chance_pred = df_chance_cluster().copy()
    index_of_sigla_pred = df_chance_pred.index[
        df_chance_pred["Time"] == sigla
    ].tolist()[0]
    nome_time = getNomeTimeFromSigla(df_chance_pred.loc[index_of_sigla_pred, "Time"])

    st.subheader(f"{nome_time}")
    (
        painel_dado_campeonato,
        painel_status_campeonato,
        painel_chance_campeonato,
        painel_previsao_final,
    ) = st.tabs(
        [
            "Dados da Classificação",
            "Status Campeonado",
            "Chances no Campeonato",
            "Previsão final",
        ]
    )

    with painel_dado_campeonato:
        createPainelInfoTime(sigla)
    with painel_status_campeonato:
        createPainelStatusCampeonato(sigla)
    with painel_chance_campeonato:
        createPainelChancesCampeonato(index_of_sigla_pred, df_chance_pred)
    with painel_previsao_final:
        createPainelRegressaoTime(sigla)

    style_metric_cards(
        border_left_color="#4fb342",
        background_color="#F0F2F6",
        border_size_px=3,
        border_color="#CECED0",
        border_radius_px=10,
        box_shadow=True,
    )


def createPainelInfoTime(sigla):
    tabela = getDadoTabelaClassificacao()
    index_of_sigla = tabela.index[tabela["Time"] == sigla].tolist()[0]
    st.subheader("Status da classificação.")
    (
        card_classificacao,
        card_ponto,
        card_jogo,
        card_vitoria,
        card_empate,
        card_derrota,
    ) = st.columns(6)
    card_gol_pro, card_gol_con, card_saldo_gol = st.columns(3)
    card_classificacao.metric(
        "Classificação", f"{tabela.loc[index_of_sigla, 'Classificação']}"
    )
    card_ponto.metric("Pontos", tabela.loc[index_of_sigla, "P"])
    card_jogo.metric("Jogos", tabela.loc[index_of_sigla, "J"])
    card_vitoria.metric("Vitórias", tabela.loc[index_of_sigla, "V"])
    card_empate.metric("Empates", tabela.loc[index_of_sigla, "E"])
    card_derrota.metric("Derrotas", tabela.loc[index_of_sigla, "D"])
    card_gol_pro.metric("Gols Pró", tabela.loc[index_of_sigla, "GP"])
    card_gol_con.metric("Gols Contra", tabela.loc[index_of_sigla, "GC"])
    card_saldo_gol.metric("Saldo de Gols", tabela.loc[index_of_sigla, "SG"])


def createPainelStatusCampeonato(sigla):
    st.subheader("Status no campeonato.")

    dado_jogos = brasileirao.copy()
    dado_jogo_time_mandante = dado_jogos[dado_jogos["Mandante"] == sigla]
    dado_jogo_time_visitante = dado_jogos[dado_jogos["Visitante"] == sigla]

    dados_mandante = calculaVitoriaDerrotaEmpate(dado_jogo_time_mandante)
    dados_visitante = calculaVitoriaDerrotaEmpate(dado_jogo_time_visitante, True)

    st.text("Mandante")
    card_vitorias_mandante, card_derrota_mandante, card_empate_mandante = st.columns(3)
    card_vitorias_mandante.metric("Vitória", dados_mandante["vitoria"])
    card_derrota_mandante.metric("Derrota", dados_mandante["derrota"])
    card_empate_mandante.metric("Empate", dados_mandante["empate"])
    st.text("Visitante")
    card_vitoria_visitante, card_derrota_visitante, card_empate_visitante = st.columns(
        3
    )
    card_vitoria_visitante.metric("Vitória", dados_visitante["vitoria"])
    card_derrota_visitante.metric("Derrota", dados_visitante["derrota"])
    card_empate_visitante.metric("Empate", dados_visitante["empate"])


def calculaVitoriaDerrotaEmpate(dado_jogo, bVisitante=False):
    retorno = {}
    retorno["vitoria"] = 0
    retorno["derrota"] = 0
    retorno["empate"] = 0

    for index, row in dado_jogo.iterrows():
        if row["Score_m"] > row["Score_v"]:
            if bVisitante:
                retorno["derrota"] += 1
            else:
                retorno["vitoria"] += 1
        elif row["Score_m"] < row["Score_v"]:
            if bVisitante:
                retorno["vitoria"] += 1
            else:
                retorno["derrota"] += 1
        else:
            retorno["empate"] += 1

    return retorno


def createPainelChancesCampeonato(index_of_sigla, df_chance_pred):
    st.subheader("Chances dentro do campeonato.")
    libertadores = trataValorDashboardTime(df_chance_pred.loc[index_of_sigla, "cl_o"])
    limbo = trataValorDashboardTime(df_chance_pred.loc[index_of_sigla, "cl_1"])
    rebaixamento = trataValorDashboardTime(df_chance_pred.loc[index_of_sigla, "cl_2"])
    titulo = trataValorDashboardTime(df_chance_pred.loc[index_of_sigla, "cl_3"])
    sulAmericana = trataValorDashboardTime(df_chance_pred.loc[index_of_sigla, "cl_4"])

    (
        card_titulo,
        card_libertadores,
        card_sul_americada,
        card_limbo,
        card_rebaixamento,
    ) = st.columns(5)
    card_titulo.metric("Título", f"{titulo}%")
    card_libertadores.metric("Libertadores", f"{libertadores}%")
    card_sul_americada.metric("Sul-Americana", f"{sulAmericana}%")
    card_limbo.metric("Limbo", f"{limbo}%")
    card_rebaixamento.metric("Rebaixamento", f"{rebaixamento}%")


def createPainelRegressaoTime(sigla):
    dadoTabelaClassificacao = calcular_regressao()
    index_of_sigla = dadoTabelaClassificacao.index[
        dadoTabelaClassificacao["time"] == sigla
    ].tolist()[0]

    iClassificacao = 0
    for i in dadoTabelaClassificacao["time"]:
        iClassificacao += 1
        dadoTabelaClassificacao.loc[
            dadoTabelaClassificacao["time"] == i, "Classificação"
        ] = f"{iClassificacao}"

    dadoTabelaClassificacao = dadoTabelaClassificacao[
        ["Classificação", "time", "pontuacao_final", "intercept", "slope"]
    ]

    st.subheader("Previsão final do time no campeonato")
    card_classificacao, card_ponto, card_grupo = st.columns(3)
    card_classificacao.metric(
        "Classificação",
        f"{dadoTabelaClassificacao.loc[index_of_sigla, 'Classificação']}º",
    )
    card_ponto.metric(
        "Pontos", dadoTabelaClassificacao.loc[index_of_sigla, "pontuacao_final"]
    )
    tabela_regressao_cluster = calcula_regressao_cluster()
    index_of_sigla = tabela_regressao_cluster.index[tabela_regressao_cluster['Time'] == sigla].tolist()[0]
    iGrupo = tabela_regressao_cluster.loc[index_of_sigla, 'cluster_pred']
    linha_grupo = df_cluster_grupo.loc[df_cluster_grupo['cluster'] == iGrupo]
    sGrupo = linha_grupo['grupo'].values[0]
    card_grupo.metric("Grupo", sGrupo)


# Método para realizar o tratamento dos valores do dashboard de status do time no campeonato
def trataValorDashboardTime(valor):
    retorno = valor * 100

    return round(retorno)


def mainDashboardTime():
    createSelecboxTime()
