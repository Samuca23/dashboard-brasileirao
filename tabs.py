import streamlit as st
import pandas as pd

# Criando um DataFrame de exemplo
data = {
    "Nome": ["João", "Maria", "Carlos"],
    "Idade": [25, 30, 22]
}
df = pd.DataFrame(data)

def main():
    st.title("Exemplo de Acesso a Dados de uma Tabela")

    # Acessando um dado específico
    nome_primeira_pessoa = df.loc[0, "Nome"]
    idade_segunda_pessoa = df.loc[1, "Idade"]

    # Escrevendo os dados usando Markdown
    st.markdown(f"Nome da primeira pessoa: **{nome_primeira_pessoa}**")
    st.markdown(f"Idade da segunda pessoa: *{idade_segunda_pessoa}*")

if __name__ == "__main__":
    main()