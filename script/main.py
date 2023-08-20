import streamlit as st
from arquivo_oficial import getClassificaoGrupo, getDadoTabelaClassificacao, df_cluster_grupo

# Método utilizado para criar a tabela de Classificação.
def createTabelaClassificacao():
    st.subheader('Classificação Brasileirão 2023')
    st.table(getDadoTabelaClassificacao())

# Método utilizado para criar a tabela de Classificação com Grupo
def createTableClassificacaoGrupo():
    st.subheader('Classificação Brasileirão 2023 - Grupo')
    opcao = st.selectbox(
        'Escolha o Grupo',
        (df_cluster_grupo['grupo']))
    classificacaoGrupo = getClassificaoGrupo()
    st.table(classificacaoGrupo[classificacaoGrupo['Grupo'] == opcao])

def main() :
    createTabelaClassificacao()
    createTableClassificacaoGrupo()

main()