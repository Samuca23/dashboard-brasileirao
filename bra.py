import pandas as pd
import numpy as np

bra = pd.read_excel('brasileirao2023.xlsx')
bra

bra = bra[bra['Score_m'].notnull()]
bra

times = bra['Mandante'].unique()
tabela = pd.DataFrame()
for time in times:
    vit = emp = der = pro = con = jog = 0
    # emp = 0
    # der = 0
    # pro = 0
    # con = 0
    # jog = 0
    mandante = bra[bra['Mandante'] == time]
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
    visitante = bra[bra['Visitante'] == time]
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
    new_row = {
        '1-Time': time,
        '3-J': jog,
        '4-V': vit,
        '5-E' : emp,
        '6-D': der,
        '7-GP': pro,
        '8-GC': con
    }    
    tabela = tabela.append(
        new_row,
        ignore_index = True
    )
tabela['2-P'] = (tabela['4-V'] * 3) + tabela['5-E']
tabela['9-SG'] = tabela['7-GP'] - tabela['8-GC']   
tabela_sort = tabela.sort_values(by=['2-P','4-V','9-SG'], ascending=False)
tabela_sort

tabela

from sklearn.cluster import KMeans
df_data = tabela[[
    '2-P',              
    '4-V',
    '5-E',
    '6-D',
    '9-SG'
]]
kmeans = KMeans(n_clusters=5, random_state=0).fit(df_data)
tabela['cluster'] = kmeans.labels_
# tabela['c_p'] = kmeans.cluster_centers_[kmeans.labels_,0]
# tabela['c_v'] = kmeans.cluster_centers_[kmeans.labels_,1]
# tabela['c_e'] = kmeans.cluster_centers_[kmeans.labels_,2]
# tabela['c_d'] = kmeans.cluster_centers_[kmeans.labels_,3]
# tabela['c_sg'] = kmeans.cluster_centers_[kmeans.labels_,4]
tabela

print(kmeans.labels_)

kmeans.cluster_centers_

df_cluster = pd.DataFrame()
for cluster, colunas in enumerate(kmeans.cluster_centers_):
    print(cluster)
    print(colunas)
    new_row = {
        'cluster': cluster, 
        '2-P': colunas[0],              
        '4-V': colunas[1],
        '5-E': colunas[2],
        '6-D': colunas[3],
        '9-SG': colunas[4],
    }
    df_cluster = df_cluster.append(
        new_row,
        ignore_index=True
    )
df_cluster

df_cluster_sort = df_cluster.sort_values(by='2-P', ascending=False)
df_cluster_sort

df_cluster_sort['grupo'] = ['Titulo','Libertadores','Sul-Americana','limbo','Rebaixamento']
df_cluster_sort

df_cluster_grupo = df_cluster_sort[['cluster','grupo']]
df_cluster_grupo

tabela

tabela = tabela.merge(df_cluster_grupo, on='cluster', how='left')
tabela

tabela_sort = tabela.sort_values(by=['2-P','4-V','9-SG'], ascending=False)
tabela_sort.style.hide_index().background_gradient(cmap='Blues').set_precision(2)













#NORMALIZAR A TABELA E COLORIR...

#grafico com pontuacao original e dos cluster

#grafico dos cluster

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

df_data = tabela[[
    'cluster',              
    '2-P',              
    '4-V',
    '5-E',
    '6-D',
    '9-SG'
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
df_prob_xy = pd.DataFrame()
index = 0
for proba in lista_proba:
    for i in range(0, len(proba)):
        new_row = {"index": index, "prob": i, "valor": round(proba[i], 4)}
        df_prob_xy = df_prob_xy.append(new_row, ignore_index=True)
    index += 1

df_prob = df_prob_xy.pivot_table(
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
tabela

df_pred = tabela[[
    '1-Time',
    'cl_o',
    'cl_1',
    'cl_2',
    'cl_3',
    'cl_4',
]]
df_pred = df_pred.copy()
df_pred

df_pred.style.hide_index().background_gradient(cmap='Blues', axis=1).set_precision(2)













rodadas = bra['Rodada'].unique()
times = bra['Mandante'].unique()
pontuacao = pd.DataFrame()
for rodada in rodadas:
    for time in times:
        resultado = bra[(bra['Rodada'] == rodada) & ((bra['Mandante'] == time) | (bra['Visitante'] == time))]
        if len(resultado) > 0:
            resultado = resultado.reset_index()
            if resultado['Mandante'][0] == time:
                if resultado['Score_m'][0] > resultado['Score_v'][0]:
                    pontos = 3
                elif resultado['Score_m'][0] == resultado['Score_v'][0]:
                    pontos = 1
                else:
                    pontos = 0
            else:                  
                if resultado['Score_v'][0] > resultado['Score_m'][0]:
                    pontos = 3
                elif resultado['Score_v'][0] == resultado['Score_m'][0]:
                    pontos = 1
                else:
                    pontos = 0
            new_row = {
                'time': time,
                'rodada': rodada,
                'pontos': pontos
            }        
            pontuacao = pontuacao.append(
                new_row,
                ignore_index = True
            )
pt_pontuacao = pontuacao.pivot_table(index='rodada', columns='time', values='pontos', aggfunc='sum')
pt_pontuacao_cum = pt_pontuacao.cumsum()
pt_pontuacao_cum

pt_pontuacao_cum = pt_pontuacao_cum.reset_index()
pt_pontuacao_cum

from sklearn.linear_model import LinearRegression

colunas = pt_pontuacao_cum.columns
df_regressao = pd.DataFrame()
for coluna in colunas:
    if coluna != 'rodada':
        X = pt_pontuacao_cum['rodada'].values.reshape(-1, 1)
        y = pt_pontuacao_cum[coluna].values.reshape(-1, 1)
        regressor = LinearRegression()
        regressor.fit(X, y)
        A = regressor.intercept_[0]
        B = regressor.coef_[0][0]
        x = A + (B * 38)
        new_row = {
            'time': coluna,
            'intercept': round(A,2),
            'slope': round(B,2),
            'pontuacao_final': round(x,2)
        }
        df_regressao = df_regressao.append(
            new_row,
            ignore_index=True
        )
df_regressao

df_regressao = df_regressao[['time','slope']]
df_regressao

tabela = tabela.merge(df_regressao, left_on='1-Time', right_on='time', how='left')
tabela

from sklearn.cluster import KMeans
df_data = tabela[[
    '2-P',              
    '4-V',
    '5-E',
    '6-D',
    '9-SG',
    'slope'
]]
kmeans = KMeans(n_clusters=5, random_state=0).fit(df_data)
tabela['cluster'] = kmeans.labels_
tabela['c_p'] = kmeans.cluster_centers_[kmeans.labels_,0]
tabela['c_v'] = kmeans.cluster_centers_[kmeans.labels_,1]
tabela['c_e'] = kmeans.cluster_centers_[kmeans.labels_,2]
tabela['c_d'] = kmeans.cluster_centers_[kmeans.labels_,3]
tabela['c_sg'] = kmeans.cluster_centers_[kmeans.labels_,4]
tabela['c_slope'] = kmeans.cluster_centers_[kmeans.labels_,5]
tabela_sort = tabela.sort_values(by=['2-P','4-V','9-SG'], ascending=False)
tabela_sort.style.hide_index().background_gradient(cmap='Blues').set_precision(2)





pontuacao_2 = pt_pontuacao_cum[pt_pontuacao_cum['rodada'] > 19]
pontuacao_2

colunas = pontuacao_2.columns
df_regressao = pd.DataFrame()
for coluna in colunas:
    if coluna != 'rodada':
        X = pontuacao_2['rodada'].values.reshape(-1, 1)
        y = pontuacao_2[coluna].values.reshape(-1, 1)
        regressor = LinearRegression()
        regressor.fit(X, y)
        A = regressor.intercept_[0]
        B = regressor.coef_[0][0]
        x = A + (B * 38)
        new_row = {
            'time': coluna,
            'intercept': round(A,2),
            'slope': round(B,2),
            'pontuacao_final': round(x,2)
        }
        df_regressao = df_regressao.append(
            new_row,
            ignore_index=True
        )
df_regressao

