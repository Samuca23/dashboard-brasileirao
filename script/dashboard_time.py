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
    index_of_sigla = df_pred.index[df_pred['Time'] == sigla].tolist()[0]
    nome_time = getNomeTimeFromSigla(df_pred.loc[index_of_sigla, 'Time'])
    rebaixamento = df_pred.loc[index_of_sigla, 'cl_o']
    sulAmericana = df_pred.loc[index_of_sigla, 'cl_1']
    libertadores= df_pred.loc[index_of_sigla, 'cl_2']
    limbo = df_pred.loc[index_of_sigla, 'cl_3']
    titulo = df_pred.loc[index_of_sigla, 'cl_4']

    st.markdown(f"Status do **{nome_time}** no campeonato")
    st.markdown(f"**Título:** {titulo}")
    st.markdown(f"**Libertadores:** {libertadores}")
    st.markdown(f"**Sul-Americana:** {sulAmericana}")
    st.markdown(f"**Limbo:** {limbo}")
    st.markdown(f"**Rebaixamento:** {rebaixamento}")

def mainDashboardTime():
    createSelecboxTime()