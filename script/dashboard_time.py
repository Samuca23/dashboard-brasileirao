import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from dados import tabela, tabela_sort, df_chance_cluster, df_cluster_grupo, getAllTimes, getSiglaTimeFromNome, getNomeTimeFromSigla

def createSelecboxTime():
    times = getAllTimes()
    
    opcao_padrao = "Selecione um time..."
    times_lista = [opcao_padrao] + times["Time"].tolist()
    
    selected = st.selectbox("Escolha um time", times_lista)

    if selected != opcao_padrao:
        createDashboardTime(getSiglaTimeFromNome(selected))

# Método de criação do  Dashboard individual do time
def createDashboardTime(sigla):
    montaPainelTime(sigla)

# Método para montar o painel de métricar de status do time no campeonáto
def montaPainelTime(sigla): 
    df_chance_pred = df_chance_cluster().copy()
    index_of_sigla = df_chance_pred.index[df_chance_pred['Time'] == sigla].tolist()[0]
    nome_time = getNomeTimeFromSigla(df_chance_pred.loc[index_of_sigla, 'Time'])

    st.subheader(f"{nome_time} no Campeonato Brasileiro de Futebol")
    createPainelInfoTime()
    createPainelStatusCampeonato(index_of_sigla, df_chance_pred)
    style_metric_cards(
        border_left_color="#4fb342",
        background_color="#F0F2F6",
        border_size_px=3,
        border_color = "#CECED0",
        border_radius_px = 10,
        box_shadow=True
    )

def createPainelInfoTime():
    st.subheader('Status da classificação')
    card_classificacao, card_ponto, card_jogo, card_vitoria, card_empate, card_derrota, = st.columns(6)
    card_gol_pro, card_gol_con, card_saldo_gol = st.columns(3)
    card_classificacao.metric('Classificação', 1)
    card_ponto.metric('Pontos', 10)
    card_jogo.metric('Jogos', 10)
    card_vitoria.metric('Vitórias', 10)
    card_empate.metric('Empates', 10)
    card_derrota.metric('Derrotas', 10)
    card_gol_pro.metric('Gols Pró', 10)
    card_gol_con.metric('Gols Contra', 10)
    card_saldo_gol.metric('Saldo de Gols', 10)

def createPainelStatusCampeonato(index_of_sigla, df_chance_pred):
    st.subheader('Chances dentro do campeonato')
    libertadores = trataValorDashboardTime(df_chance_pred.loc[index_of_sigla, 'cl_o'])
    limbo = trataValorDashboardTime(df_chance_pred.loc[index_of_sigla, 'cl_1'])
    rebaixamento = trataValorDashboardTime(df_chance_pred.loc[index_of_sigla, 'cl_2'])
    titulo = trataValorDashboardTime(df_chance_pred.loc[index_of_sigla, 'cl_3'])
    sulAmericana = trataValorDashboardTime(df_chance_pred.loc[index_of_sigla, 'cl_4'])

    card_titulo, card_libertadores, card_sul_americada, card_limbo, card_rebaixamento = st.columns(5)
    card_titulo.metric('Título', f"{titulo}%")
    card_libertadores.metric('Libertadores', f"{libertadores}%")
    card_sul_americada.metric('Sul-Americana', f"{sulAmericana}%")
    card_limbo.metric('Limbo', f"{limbo}%")
    card_rebaixamento.metric('Rebaixamento', f"{rebaixamento}%")

# Método para realizar o tratamento dos valores do dashboard de status do time no campeonato
def trataValorDashboardTime(valor):
    retorno = valor * 100

    return round(retorno)

def mainDashboardTime():
    createSelecboxTime()