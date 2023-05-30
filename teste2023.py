import pandas as pd
import numpy as np
import streamlit as st

brasileirao = pd.read_excel('brasileirao2023.xlsx')
brasileirao = brasileirao[brasileirao['Score_m'].notnull()]

times = brasileirao['Mandante'].unique()
tabela = pd.DataFrame()
for time in times:
    vit = emp = der = pro = con = jog = 0
    mandante = brasileirao[brasileirao['Mandante'] == time]
    for indice, partida in mandante.iterrows():
        if partida['Score_m'] > partida['Score_v']:
            vit += 1 
        elif partida['Score_m'] == partida['Score_v']:
            emp += 1
        else:
            der += 1
        pro += partida['Score_m']
        con += partida['Score_v']
        jog += 1
    visitante = brasileirao[brasileirao['Visitante'] == time]
    for indice, partida in visitante.iterrows():
        if partida['Score_v'] > partida['Score_m']:
            vit += 1
        elif partida['Score_v'] == partida['Score_m']:
            emp += 1
        else:
            der += 1
        pro += partida['Score_v']
        con += partida['Score_m']
        jog += 1
    new_row = pd.DataFrame({
        '1-Time': [time],
        '3-J': [jog],
        '4-V': [vit],
        '5-E' : [emp],
        '6-D': [der],
        '7-GP': [pro],
        '8-GC': [con]
    })   
    tabela = pd.concat([tabela, new_row], ignore_index = True)
    
tabela['2-P'] = (tabela['4-V'] * 3) + tabela['5-E']
tabela['9-SG'] = tabela['7-GP'] - tabela['8-GC']   
tabela_sort = tabela.sort_values(by=['2-P','4-V','9-SG'], ascending=False)

from sklearn.cluster import KMeans
df_data = tabela[[
    '2-P',              
    '4-V',
    '5-E',
    '6-D',
    '9-SG'
]]
kmeans = KMeans(n_clusters=5, random_state=0).fit(df_data)
tabela['cluster'] = kmeans.labels_

df_cluster = pd.DataFrame()
for cluster, colunas in enumerate(kmeans.cluster_centers_):
    print(cluster)
    print(colunas)
    new_row = pd.DataFrame({
        'cluster': [cluster], 
        '2-P': [colunas[0]],              
        '4-V': [colunas[1]],
        '5-E': [colunas[2]],
        '6-D': [colunas[3]],
        '9-SG': [colunas[4]],
    })
    df_cluster = pd.concat([df_cluster, new_row], ignore_index=True)

df_cluster_sort = df_cluster.sort_values(by='2-P', ascending=False)

df_cluster_sort['grupo'] = ['Título','Libertadores','Sul-Americana','Limbo','Rebaixamento']
df_cluster_grupo = df_cluster_sort[['cluster','grupo']]

tabela_sort = tabela.sort_values(by=['2-P','4-V','9-SG'], ascending=False)

# Método para retornar a tabela de Classificação.
def getTabelaClassificacao(bAddClomunCluster = False):
    classificacao = tabela_sort[['1-Time', '2-P', '3-J', '4-V', '5-E', '6-D', '7-GP', '8-GC', '9-SG']]
    classificacao['7-GP'] = classificacao['7-GP'].astype(int)
    classificacao['8-GC'] = classificacao['8-GC'].astype(int)
    classificacao['9-SG'] = classificacao['9-SG'].astype(int)
    if bAddClomunCluster:
        classificacao['Cluster'] = tabela_sort[['cluster']]

    return classificacao

# Método utilizado para criar a tabela de Classificação.
def createTabelaClassificacao():
    st.header('Classificação')
    st.subheader('Classificação Brasileirão 2023')
    st.table(getTabelaClassificacao())

# Método para retornar a Classificação com os Grupos.
def getClassificaoGrupo():
    classificacaoGrupo = getTabelaClassificacao(bAddClomunCluster=True)
    for index, row in classificacaoGrupo.iterrows():
        for _, cluster_grupo in df_cluster_grupo.iterrows():
            if row['Cluster'] == cluster_grupo['cluster']:
                classificacaoGrupo.loc[index, 'Grupo'] = cluster_grupo['grupo']

    return classificacaoGrupo

# Método utilizado para criar a tabela de Classificação com Grupo
def createTableClassificacaoGrupo():
    st.header('Classificação - Grupo')
    st.subheader('Classificação Brasileirão 2023 - Grupo')
    opcao = st.selectbox(
        'Escolha o Grupo',
        (df_cluster_grupo['grupo']))
    classificacaoGrupo = getClassificaoGrupo()
    st.table(classificacaoGrupo[classificacaoGrupo['Grupo'] == opcao])


createTabelaClassificacao()
createTableClassificacaoGrupo()