import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from dashboard_campeonato import createDashboardCampeonato
from dashboard_time import mainDashboardTime

st.set_page_config(
    page_title="Análise Campeonato Brasileiro 2023",
    page_icon="🏆",
    layout="wide",
   
)
st.markdown(
    """
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""",
    unsafe_allow_html=True,
)

st.title("Campeonato Brasileiro 2023 - Série A 🇧🇷⚽")

with open("./config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

hashed_passwords = stauth.Hasher(["admin"]).generate()
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

name, authenticator_status, username = authenticator.login("Login", "main")


def main():
    tabs = ["Campeonato", "Time"]
    selected = st.sidebar.selectbox("Selecione uma visualização 👓", tabs)
    authenticator.logout("Logout", "sidebar")

    if selected == "Campeonato":
        createDashboardCampeonato()
    elif selected == "Time":
        mainDashboardTime()


if authenticator_status == False:
    st.error("Username/password is incorrect")

if authenticator_status == None:
    st.warning("Please enter your username and password")

if authenticator_status == True:
    if __name__ == "__main__":
        main()
