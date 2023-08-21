import streamlit as st
from dashboard_campeonato import createDashboardCampeonato
from dashboard_time import createDashboardTime

def main() :
    tabs = ["Campeonato", "Time"]
    st.sidebar.title("Campeonato Brasileiro 2023 - Série A")
    selected_tad = st.sidebar.selectbox("Selecione uma visualização", tabs)

    if selected_tad == "Campeonato":
        createDashboardCampeonato()
    elif selected_tad == "Time":
       createDashboardTime() 

if __name__ == "__main__":
    main()