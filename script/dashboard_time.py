import streamlit as st
from dados import tabela, tabela_sort, df_pred, df_cluster_grupo, getAllTimes, getSiglaTimeFromNome, getNomeTimeFromSigla

def createSelecboxTime():
    times = getAllTimes()
    
    opcao_padrao = "Selecione um time..."
    times_lista = [opcao_padrao] + times["Time"].tolist()
    
    selected = st.selectbox("Escolha um time", times_lista)

    if selected != opcao_padrao:
        createDashboardTime(getSiglaTimeFromNome(selected))

def createDashboardTime(sigla):
    montaPainelTime(sigla)

def montaPainelTime(sigla): 
    index_of_sigla = df_pred.index[df_pred['Time'] == sigla].tolist()[0]
    nome_time = getNomeTimeFromSigla(df_pred.loc[index_of_sigla, 'Time'])
    rebaixamento = trataValorDashboardTime(df_pred.loc[index_of_sigla, 'cl_o'])
    sulAmericana = trataValorDashboardTime(df_pred.loc[index_of_sigla, 'cl_1'])
    libertadores = trataValorDashboardTime(df_pred.loc[index_of_sigla, 'cl_2'])
    limbo = trataValorDashboardTime(df_pred.loc[index_of_sigla, 'cl_4'])
    titulo = trataValorDashboardTime(df_pred.loc[index_of_sigla, 'cl_3'])

    st.markdown(f"Status do **{nome_time}** no campeonato")
    st.markdown(f"**Título:** {titulo}%")
    st.markdown(f"**Libertadores:** {libertadores}%")
    st.markdown(f"**Sul-Americana:** {sulAmericana}%")
    st.markdown(f"**Limbo:** {limbo}%")
    st.markdown(f"**Rebaixamento:** {rebaixamento}%")

def trataValorDashboardTime(valor):
    retorno = valor * 100

    return round(retorno)

def mainDashboardTime():
    createSelecboxTime()