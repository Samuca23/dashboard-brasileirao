import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from dashboard_campeonato import createDashboardCampeonato
from dashboard_time import mainDashboardTime


with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

hashed_passwords = stauth.Hasher(['abc', 'def']).generate()
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authenticator_status, username = authenticator.login("Login", "main")

def main():
    st.set_page_config(layout="wide")
    tabs = ["Campeonato", "Time"]
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title("Campeonato Brasileiro 2023 - Série A")
    selected = st.sidebar.selectbox("Selecione uma visualização", tabs)

    if selected == "Campeonato":
        createDashboardCampeonato()
    elif selected == "Time":
        mainDashboardTime()

if authenticator_status == False:
    st.error("Username/password is incorrect")

if authenticator_status == None:
    st.warning("Please enter your username and password")

if authenticator_status:
    if __name__ == "__main__":
        main()




