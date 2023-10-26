import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

# Leitura dos dados do brasileirão
brasileirao = pd.read_excel("../data/brasileirao2023.xlsx")

# Limpeza dos dados Nulos
brasileirao = brasileirao[brasileirao["Score_m"].notnull()]

# Montagem dos primeiros dados necessários
times = brasileirao["Mandante"].unique()
tabela = pd.DataFrame()
for time in times:
    vit = emp = der = pro = con = jog = 0
    mandante = brasileirao[brasileirao["Mandante"] == time]
    for indice, partida in mandante.iterrows():
        if partida["Score_m"] > partida["Score_v"]:
            vit += 1
        elif partida["Score_m"] == partida["Score_v"]:
            emp += 1
        else:
            der += 1
        pro += partida["Score_m"]
        con += partida["Score_v"]
        jog += 1
    visitante = brasileirao[brasileirao["Visitante"] == time]
    for indice, partida in visitante.iterrows():
        if partida["Score_v"] > partida["Score_m"]:
            vit += 1
        elif partida["Score_v"] == partida["Score_m"]:
            emp += 1
        else:
            der += 1
        pro += partida["Score_v"]
        con += partida["Score_m"]
        jog += 1
    new_row = pd.DataFrame(
        {
            "Time": [time],
            "J": [jog],
            "V": [vit],
            "E": [emp],
            "D": [der],
            "GP": [pro],
            "GC": [con],
        }
    )
    tabela = pd.concat([tabela, new_row], ignore_index=True)

tabela["P"] = (tabela["V"] * 3) + tabela["E"]
tabela["SG"] = tabela["GP"] - tabela["GC"]
tabela_sort = tabela.sort_values(by=["P", "V", "SG"], ascending=False)

df_data = tabela[["P", "V", "E", "D", "SG"]]
kmeans = KMeans(n_clusters=5, random_state=0).fit(df_data)
tabela["cluster"] = kmeans.labels_

df_cluster = pd.DataFrame()
for cluster, colunas in enumerate(kmeans.cluster_centers_):
    new_row = pd.DataFrame(
        {
            "cluster": [cluster],
            "P": [colunas[0]],
            "V": [colunas[1]],
            "E": [colunas[2]],
            "D": [colunas[3]],
            "SG": [colunas[4]],
        }
    )
    df_cluster = pd.concat([df_cluster, new_row], ignore_index=True)

df_cluster_sort = df_cluster.sort_values(by="P", ascending=False)

df_cluster_sort["grupo"] = [
    "Título",
    "Libertadores",
    "Sul-Americana",
    "Limbo",
    "Rebaixamento",
]
df_cluster_grupo = df_cluster_sort[["cluster", "grupo"]]

tabela_sort = tabela.sort_values(by=["P", "V", "SG"], ascending=False)


df_data = tabela[["cluster", "P", "V", "E", "D", "SG"]]

X_Train = df_data.drop(columns=["cluster"], axis=1)
X_Test = df_data.drop(columns=["cluster"], axis=1)
y_Train = df_data["cluster"]
y_Test = df_data["cluster"]

sc_x = StandardScaler()
X_Train = sc_x.fit_transform(X_Train)
X_Test = sc_x.fit_transform(X_Test)

logreg = LogisticRegression(solver="lbfgs", max_iter=500)
logreg.fit(X_Train, y_Train)
pred_logreg = logreg.predict(X_Test)
pred_proba = logreg.predict_proba(X_Test)

tabela["cluster_pred"] = pred_logreg

lista_proba = pred_proba.tolist()

data = []  # Lista para armazenar os dicionários de dados

index = 0
for proba in lista_proba:
    for i in range(0, len(proba)):
        new_row = {"index": index, "prob": i, "valor": round(proba[i], 4)}
        data.append(new_row)
    index += 1

df_prob = pd.DataFrame(data)  # Cria o DataFrame a partir da lista de dicionários
df_prob = df_prob.pivot_table(
    index="index", columns="prob", values="valor", aggfunc="sum"
)
df_prob = df_prob.reset_index()
df_prob = df_prob.set_index("index")

df_prob = df_prob.rename(
    columns={0.0: "cl_o", 1.0: "cl_1", 2.0: "cl_2", 3.0: "cl_3", 4.0: "cl_4"}
)

tabela = pd.merge(tabela, df_prob, left_index=True, right_index=True)

df_pred = tabela[
    [
        "Time",
        "cl_o",
        "cl_1",
        "cl_2",
        "cl_3",
        "cl_4",
    ]
]
df_pred = df_pred.copy()


# Método para retornar a variável como uma cópia para que não sofra alterações
def df_chance_cluster():
    return df_pred


# Método para calcular a tabela
def calcular_tabela(df):
    times = df["Mandante"].unique()
    tabela = []
    for time in times:
        vit = emp = der = pro = con = jog = 0
        mandante = df[df["Mandante"] == time]
        for indice, partida in mandante.iterrows():
            if partida["Score_m"] > partida["Score_v"]:
                vit += 1
            elif partida["Score_m"] == partida["Score_v"]:
                emp += 1
            else:
                der += 1
            pro += partida["Score_m"]
            con += partida["Score_v"]
            jog += 1
        visitante = df[df["Visitante"] == time]
        for indice, partida in visitante.iterrows():
            if partida["Score_v"] > partida["Score_m"]:
                vit += 1
            elif partida["Score_v"] == partida["Score_m"]:
                emp += 1
            else:
                der += 1
            pro += partida["Score_v"]
            con += partida["Score_m"]
            jog += 1
        tabela.insert(0, [time, jog, vit, emp, der, pro, con])
    tabela = pd.DataFrame(
        tabela, columns=["Time", "Jogos", "Vit", "Emp", "Der", "GPro", "GCon"]
    )
    tabela["Pontos"] = (tabela["Vit"] * 3) + tabela["Emp"]
    tabela["Saldo"] = tabela["GPro"] - tabela["GCon"]

    return tabela


# Método para calcular os cluster
def calcular_cluster(df):
    df_data = df[["Pontos", "Vit", "Emp", "Der", "Saldo"]]
    kmeans = KMeans(n_clusters=5, random_state=0, n_init=5).fit(df_data)
    df["Cluster"] = kmeans.labels_
    cl = pd.DataFrame(kmeans.cluster_centers_[:, 0], columns=["Media"]).reset_index()
    cl["Ranking"] = cl["Media"].rank()
    cl = cl.rename(columns={"index": "Cluster"})
    df = df.merge(cl, on="Cluster", how="left")

    return df


# Método responsável por retornar todos os time do campeonato
def getAllTimes():
    times_brasileirao = pd.read_excel("../data/times_brasileirao_2023.xlsx")

    return times_brasileirao


# Método responsável por retornar o nome do time com base na sigla
def getNomeTimeFromSigla(sigla):
    times = getAllTimes()

    index_of_sigla = times.index[times["Sigla"] == sigla].tolist()[0]
    nome_time = times.loc[index_of_sigla, "Time"]

    return nome_time


# Método responsável por retornar a sigla do time com base no nome
def getSiglaTimeFromNome(nome):
    times = getAllTimes()

    index_of_sigla = times.index[times["Time"] == nome].tolist()[0]
    sgila_time = times.loc[index_of_sigla, "Sigla"]

    return sgila_time


# Método para retornar as rodadas do campeonato
def getAllRodadaCampeonato():
    rodada = brasileirao["Rodada"]


# Método para calcular a regressão
def calcula_pontuacao_regressao():
    rodadas = brasileirao["Rodada"].unique()
    times = brasileirao["Mandante"].unique()
    pontuacao = pd.DataFrame()
    data = []  # Lista para armazenar os dicionários de dados

    for rodada in rodadas:
        for time in times:
            resultado = brasileirao[
                (brasileirao["Rodada"] == rodada)
                & (
                    (brasileirao["Mandante"] == time)
                    | (brasileirao["Visitante"] == time)
                )
            ]
            if len(resultado) > 0:
                resultado = resultado.reset_index()
                if resultado["Mandante"][0] == time:
                    if resultado["Score_m"][0] > resultado["Score_v"][0]:
                        pontos = 3
                    elif resultado["Score_m"][0] == resultado["Score_v"][0]:
                        pontos = 1
                    else:
                        pontos = 0
                else:
                    if resultado["Score_v"][0] > resultado["Score_m"][0]:
                        pontos = 3
                    elif resultado["Score_v"][0] == resultado["Score_m"][0]:
                        pontos = 1
                    else:
                        pontos = 0
                new_row = {"time": time, "rodada": rodada, "pontos": pontos}
                data.append(new_row)  # Adiciona o dicionário à lista de dados

    pontuacao = pd.DataFrame(data)  # Cria o DataFrame a partir da lista de dicionários

    pt_pontuacao = pontuacao.pivot_table(
        index="rodada", columns="time", values="pontos", aggfunc="sum"
    )
    pt_pontuacao_cum = pt_pontuacao.cumsum()
    pt_pontuacao_cum = pt_pontuacao_cum.reset_index()

    return pt_pontuacao_cum


def calcular_regressao():
    pt_pontuacao_cum = calcula_pontuacao_regressao()
    colunas = pt_pontuacao_cum.columns
    df_regressao = pd.DataFrame()
    data_regressao = (
        []
    )  # Lista para armazenar os dicionários de resultados de regressão

    for coluna in colunas:
        if coluna != "rodada":
            X = pt_pontuacao_cum["rodada"].values.reshape(-1, 1)
            y = pt_pontuacao_cum[coluna].values.reshape(-1, 1)
            regressor = LinearRegression()
            regressor.fit(X, y)
            A = regressor.intercept_[0]
            B = regressor.coef_[0][0]
            x = A + (B * 38)
            new_row_regressao = {
                "time": coluna,
                "pontuacao_final": round(x),
                "intercept": round(A, 2),
                "slope": round(B, 2),
            }
            data_regressao.append(new_row_regressao)
    df_regressao = pd.DataFrame(data_regressao)

    return df_regressao.sort_values(by="pontuacao_final", ascending=False)


# Método para calcular a regressão da metado do campeonato
def calcula_regressao_meio_campeonato(iRodada):
    pt_pontuacao_cum = calcula_pontuacao_regressao()
    pontuacao_2 = pt_pontuacao_cum[pt_pontuacao_cum["rodada"] > iRodada]
    colunas = pontuacao_2.columns
    df_regressao = pd.DataFrame()
    colunas = pontuacao_2.columns
    regressao_data = []

    for coluna in colunas:
        if coluna != "rodada":
            X = pontuacao_2["rodada"].values.reshape(-1, 1)
            y = pontuacao_2[coluna].values.reshape(-1, 1)
            regressor = LinearRegression()
            regressor.fit(X, y)
            A = regressor.intercept_[0]
            B = regressor.coef_[0][0]
            x = A + (B * 38)
            regressao_data.append(
                {
                    "time": coluna,
                    "intercept": round(A, 2),
                    "slope": round(B, 2),
                    "pontuacao_final": round(x),
                }
            )

    df_regressao = pd.DataFrame(regressao_data)

    return df_regressao.sort_values(by="pontuacao_final", ascending=False)


# Método para calcular a regressão do cluster
def calcula_regressao_cluster():
    df_regressao = calcular_regressao()
    tabela_teste = tabela.merge(
        df_regressao, left_on="Time", right_on="time", how="left"
    )
    df_data = tabela_teste[["P", "V", "E", "D", "SG", "slope"]]
    kmeans = KMeans(n_clusters=5, random_state=0).fit(df_data)
    tabela_teste["cluster"] = kmeans.labels_
    tabela_teste["c_p"] = kmeans.cluster_centers_[kmeans.labels_, 0]
    tabela_teste["c_v"] = kmeans.cluster_centers_[kmeans.labels_, 1]
    tabela_teste["c_e"] = kmeans.cluster_centers_[kmeans.labels_, 2]
    tabela_teste["c_d"] = kmeans.cluster_centers_[kmeans.labels_, 3]
    tabela_teste["c_sg"] = kmeans.cluster_centers_[kmeans.labels_, 4]
    tabela_teste["c_slope"] = kmeans.cluster_centers_[kmeans.labels_, 5]
    tabela_sort = tabela_teste.sort_values(by=["P", "V", "SG"], ascending=False)

    return tabela_sort
