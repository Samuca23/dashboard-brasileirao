import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans

brasileirao = pd.read_excel('../data/brasileirao2023.xlsx')
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
        'Time': [time],
        'J' : [jog],
        'V' : [vit],
        'E' : [emp],
        'D' : [der],
        'GP': [pro],
        'GC': [con]
    })   
    tabela = pd.concat([tabela, new_row], ignore_index = True)
    
tabela['P'] = (tabela['V'] * 3) + tabela['E']
tabela['SG'] = tabela['GP'] - tabela['GC']   
tabela_sort = tabela.sort_values(by=['P','V','SG'], ascending=False)

from sklearn.cluster import KMeans
df_data = tabela[[
    'P',              
    'V',
    'E',
    'D',
    'SG'
]]
kmeans = KMeans(n_clusters=5, random_state=0).fit(df_data)
tabela['cluster'] = kmeans.labels_

df_cluster = pd.DataFrame()
for cluster, colunas in enumerate(kmeans.cluster_centers_):
    new_row = pd.DataFrame({
        'cluster': [cluster], 
        'P': [colunas[0]],              
        'V': [colunas[1]],
        'E': [colunas[2]],
        'D': [colunas[3]],
        'SG': [colunas[4]],
    })
    df_cluster = pd.concat([df_cluster, new_row], ignore_index=True)

df_cluster_sort = df_cluster.sort_values(by='P', ascending=False)

df_cluster_sort['grupo'] = ['Título','Libertadores','Sul-Americana','Limbo','Rebaixamento']
df_cluster_grupo = df_cluster_sort[['cluster','grupo']]

tabela_sort = tabela.sort_values(by=['P','V','SG'], ascending=False)


df_data = tabela[[
    'cluster',              
    'P',              
    'V',
    'E',
    'D',
    'SG'
]]

X_Train = df_data.drop(columns=['cluster'], axis=1)
X_Test = df_data.drop(columns=['cluster'], axis=1)
y_Train = df_data['cluster']
y_Test = df_data['cluster']

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

df_prob = df_prob.rename(columns={
    0.0: 'cl_o',
    1.0: 'cl_1',
    2.0: 'cl_2',
    3.0: 'cl_3',
    4.0: 'cl_4'
})

tabela = pd.merge(tabela, df_prob, left_index=True, right_index=True)

################################################
df_data = tabela[[
    'cluster',              
    'P',              
    'V',
    'E',
    'D',
    'SG'
]]

X_Train = df_data.drop(columns=['cluster'], axis=1)
X_Test = df_data.drop(columns=['cluster'], axis=1)
y_Train = df_data['cluster']
y_Test = df_data['cluster']

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

df_prob = df_prob.rename(columns={
    0.0: 'cl_o',
    1.0: 'cl_1',
    2.0: 'cl_2',
    3.0: 'cl_3',
    4.0: 'cl_4'
})

tabela_clutabelaster_pred = pd.merge(tabela, df_prob, left_index=True, right_index=True)

df_pred = tabela[[
    'Time',
    'cl_o',
    'cl_1',
    'cl_2',
    'cl_3',
    'cl_4',
]]
df_pred = df_pred.copy()

##########################################################

def calcular_tabela(df):
  times = df['Mandante'].unique()
  tabela = []
  for time in times:
      vit = emp = der = pro = con = jog = 0
      mandante = df[df['Mandante'] == time]
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
      visitante = df[df['Visitante'] == time]
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
      tabela.insert(0, [time, jog, vit, emp, der, pro, con])
  tabela = pd.DataFrame(tabela, columns = ['Time', 'Jogos', 'Vit', 'Emp', 'Der', 'GPro', 'GCon'])
  tabela['Pontos'] = (tabela['Vit'] * 3) + tabela['Emp']
  tabela['Saldo'] = tabela['GPro'] - tabela['GCon']
  return tabela

def calcular_cluster(df):
  df_data = df[['Pontos', 'Vit', 'Emp', 'Der', 'Saldo']]
  kmeans = KMeans(n_clusters=5, random_state=0, n_init=5).fit(df_data)
  df['Cluster'] = kmeans.labels_
  cl = pd.DataFrame(kmeans.cluster_centers_[:,0], columns =['Media']).reset_index()
  cl['Ranking'] = cl['Media'].rank()
  cl = cl.rename(columns = {'index': 'Cluster'})
  df = df.merge(cl, on='Cluster', how='left')
  return df


# Método responsável por retornar todos os time do campeonato
def getAllTimes():
    times_brasileirao = pd.read_excel('../data/times_brasileirao_2023.xlsx')

    return times_brasileirao

# Método responsável por retornar o nome do time com base na sigla
def getNomeTimeFromSigla(sigla):
    times = getAllTimes()
    
    index_of_sigla = times.index[times['Sigla'] == sigla].tolist()[0]
    nome_time = times.loc[index_of_sigla, 'Time']
    
    return nome_time

# Método responsável por retornar a sigla do time com base no nome
def getSiglaTimeFromNome(nome):
    times = getAllTimes()
    
    index_of_sigla = times.index[times['Time'] == nome].tolist()[0]
    sgila_time = times.loc[index_of_sigla, 'Sigla']
    
    return sgila_time

def getAllRodadaCampeonato():
    rodada = brasileirao["Rodada"] 

def calcular_tabela(df):
  times = df['Mandante'].unique()
  tabela = []
  for time in times:
      vit = emp = der = pro = con = jog = 0
      mandante = df[df['Mandante'] == time]
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
      visitante = df[df['Visitante'] == time]
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
      tabela.insert(0, [time, jog, vit, emp, der, pro, con])
  tabela = pd.DataFrame(tabela, columns = ['Time', 'Jogos', 'Vit', 'Emp', 'Der', 'GPro', 'GCon'])
  tabela['Pontos'] = (tabela['Vit'] * 3) + tabela['Emp']
  tabela['Saldo'] = tabela['GPro'] - tabela['GCon']

  return tabela

def calcular_cluster(df):
  df_data = df[['Pontos', 'Vit', 'Emp', 'Der', 'Saldo']]
  kmeans = KMeans(n_clusters=5, random_state=0, n_init=5).fit(df_data)
  df['Cluster'] = kmeans.labels_
  cl = pd.DataFrame(kmeans.cluster_centers_[:,0], columns =['Media']).reset_index()
  cl['Ranking'] = cl['Media'].rank()
  cl = cl.rename(columns = {'index': 'Cluster'})
  df = df.merge(cl, on='Cluster', how='left')

  return df