import streamlit as st
from dashboard_campeonato import createDashboardCampeonato
from dashboard_time import createDashboardTime

def main() :
    tabs = ["Campeonato", "Time"]
    st.sidebar.title("Campeonato Brasileiro 2023 - Série A")
    selected = st.sidebar.selectbox("Selecione uma visualização", tabs)

    if selected == "Campeonato":
        createDashboardCampeonato()
    elif selected == "Time":
       createDashboardTime() 

if __name__ == "__main__":
    main()