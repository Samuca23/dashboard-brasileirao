import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def main():
    st.title("Exemplo de Gráfico de Dispersão com Streamlit")

    # Dados de exemplo
    data = {
        "Anos": [2010, 2012, 2014, 2016, 2018, 2020],
        "População": [100, 120, 150, 180, 200, 220]
    }
    df = pd.DataFrame(data)

    # Criando o gráfico de dispersão usando Matplotlib
    fig, ax = plt.subplots()
    ax.scatter(df["Anos"], df["População"])
    ax.set_xlabel("Anos")
    ax.set_ylabel("População")
    ax.set_title("Gráfico de Dispersão")
    st.pyplot(fig)

if __name__ == "__main__":
    main()