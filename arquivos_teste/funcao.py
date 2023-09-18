import pandas as pd
from sklearn.cluster import KMeans

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
