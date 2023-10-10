import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from dados import tabela, tabela_sort, df_pred, df_cluster_grupo, getAllTimes, getSiglaTimeFromNome, getNomeTimeFromSigla

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
    index_of_sigla = df_pred.index[df_pred['Time'] == sigla].tolist()[0]
    nome_time = getNomeTimeFromSigla(df_pred.loc[index_of_sigla, 'Time'])

    st.subheader(f"Status do {nome_time} no campeonato")

    libertadores = trataValorDashboardTime(df_pred.loc[index_of_sigla, 'cl_o'])
    limbo = trataValorDashboardTime(df_pred.loc[index_of_sigla, 'cl_1'])
    rebaixamento = trataValorDashboardTime(df_pred.loc[index_of_sigla, 'cl_2'])
    sulAmericana = trataValorDashboardTime(df_pred.loc[index_of_sigla, 'cl_4'])
    titulo = trataValorDashboardTime(df_pred.loc[index_of_sigla, 'cl_3'])

    card_titulo, card_libertadores, card_sul_americada, card_limbo, card_rebaixamento = st.columns(5)
    card_titulo.metric('Título', f"{titulo}%")
    card_libertadores.metric('Libertadores', f"{libertadores}%")
    card_sul_americada.metric('Sul-Americana', f"{sulAmericana}%")
    card_limbo.metric('Limbo', f"{limbo}%")
    card_rebaixamento.metric('Rebaixamento', f"{rebaixamento}%")

    style_metric_cards(
        border_left_color="#4fb342",
        background_color="#F0F2F6",
        border_size_px=3,
        border_color = "#CECED0",
        border_radius_px = 10,
        box_shadow=True
    )

# Método para realizar o tratamento dos valores do dashboard de status do time no campeonato
def trataValorDashboardTime(valor):
    retorno = valor * 100

    return round(retorno)

def mainDashboardTime():
    createSelecboxTime()