import streamlit as st
from dados import tabela_sort, df_cluster_grupo, getAllTimes, getNomeTimeFromSigla, getDadoTime

def createSelecboxTime():
    times = getAllTimes()
    
    opcao_padrao = "Selecione um time..."
    times_lista = [opcao_padrao] + times["Time"].tolist()
    
    selected = st.selectbox("Escolha um time", times_lista)

    if selected != opcao_padrao:
        dadotime = getDadoTime(getNomeTimeFromSigla(selected))

def createDashboardTime():
    createSelecboxTime()