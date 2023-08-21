import streamlit as st
from dados import tabela_sort, df_cluster_grupo, getNomeTimeFromSigla

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

# Método utilizado para criar um painel do possível campeão do campeonato
def createPainelPossivelCampeao():
    primeiro_colocado = getDadoTabelaClassificacao().iloc[0]
    nome_primeiro_colocado = getNomeTimeFromSigla(primeiro_colocado['Time'])
    st.title("Possível campeão ⭐")
    st.markdown(f"**Time:** {nome_primeiro_colocado}")
    st.markdown(f"**Pontuação: :green`{primeiro_colocado['P']}`**")

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

# Método utilizado para criar o Dashboard do campeonato
def createDashboardCampeonato():
    st.title("Dados do Campeonato Brasileiro 2023 ")
    createPainelPossivelCampeao()
    createTabelaClassificacao()
    createTableClassificacaoGrupo()