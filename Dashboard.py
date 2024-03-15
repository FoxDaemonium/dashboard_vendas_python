import pandas as pd
import plotly.express as px 
import streamlit as st
import requests

st.set_page_config(layout='wide')

def formata_numero(valor,prefixo=''):
    for unidade in ['','mil']:
        if valor<1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor/=1000
    return f'{prefixo} {valor:.2f} milhões'
        

st.title('Dashboard de vendas :shopping_trolley:')

url = 'https://labdados.com/produtos'

regioes=['Brasil', 'centro-oeste','nordeste','norte','sul,sudeste']
st.sidebar.title('Filtros')
regiao=st.sidebar.selectbox('Região',regioes)
if regiao=='Brasil':
    regiao=''

todos_ano=st.sidebar.checkbox('Periodo de',value=True)
if todos_ano=='':
    ano=''
else:
    ano=st.sidebar.slider('Ano',2020,2023)

query_string={'regiao':regiao.lower(),'ano':ano}
response= requests.get(url,params=query_string)
dados=pd.DataFrame.from_dict(response.json())
dados['Data da Compra']= pd.to_datetime(dados['Data da Compra'],format='%d/%m/%Y')

filtro_vendedores=st.sidebar.multiselect('Vendedores',dados['Vendedor'].unique())
if filtro_vendedores:
    dados=dados[dados['Vendedor'].isin(filtro_vendedores)]

##tabela
##tabela vend
vendedores=pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))
##tabelas recei
rece_est=dados.groupby('Local da compra')[['Preço']].sum()
rece_est=dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat','lon']].merge(rece_est,left_on='Local da compra', right_index=True).sort_values('Preço',ascending = False)
##-----------------------------------------

rece_mens=dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
rece_mens['Ano']=rece_mens['Data da Compra'].dt.year
rece_mens['Mes']=rece_mens['Data da Compra'].dt.month_name()
##-----------------------------------------

rece_cate=dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço',ascending=False)


##grafi
fig_map_re=px.scatter_geo(rece_est,lat='lat', lon='lon',scope='south america', size='Preço', template='seaborn', hover_name='Local da compra',hover_data={'lat':False,'lon':False},title='Receita por estado')
##-----------------------------------------
fig_rece_men=px.line(rece_mens,x='Mes',y='Preço',markers=True,range_y=(0,rece_mens.max()),color='Ano',line_dash='Ano',title='Receita mensal')

fig_rece_men.update_layout(yaxis_title='Receita')
##-----------------------------------------
fig_rece_est=px.bar(rece_est.head(),x='Local da compra',y='Preço',text_auto=True,title='Top 5 estados(receita)')

fig_rece_est.update_layout(yaxis_title='Receita')
##-----------------------------------------
fig_rece_cate=px.bar(rece_cate,text_auto=True,title='Receita por cartegoria')
fig_rece_cate.update_layout(yaxis_title='Receita')

##visu

aba1,aba2,aba3=st.tabs(['Receita','Vendas feitas','Vendedores'])
with aba1:
    col1,col2=st.columns(2)
    with col1:
        st.metric('Receita',formata_numero( dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_map_re,use_container_width=True)
        st.plotly_chart(fig_rece_est,use_container_width=True)

    with col2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))
        st.plotly_chart(fig_rece_men,use_container_width=True)
        st.plotly_chart(fig_rece_cate,use_container_width=True)
##-----------------------------------------------------------------
with aba2:
    col1,col2=st.columns(2)
    with col1:
        st.metric('Receita',formata_numero( dados['Preço'].sum(), 'R$'))
        

    with col2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))
       
##----------------------------------------------------------------
with aba3:
    qtd_vend=st.number_input('Quantidade de vendedores',2,10,5)
    col1,col2=st.columns(2)
    with col1:
        st.metric('Receita',formata_numero( dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(
            vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vend),
            x='sum',
            y=vendedores[['sum']].sort_values(['sum'], ascending=False).head(qtd_vend).index,
            text_auto=True,
            title=f'Top {qtd_vend} vendedores (receita)'
        )
        st.plotly_chart(fig_receita_vendedores)

    with col2:
        st.metric('Quantidade de vendas',formata_numero(dados.shape[0]))

        fig_vend_vendedores = px.bar(
                    vendedores[['count']].sort_values('count', ascending=False).head(qtd_vend),
                    x='count',
                    y=vendedores[['count']].sort_values(['count'], ascending=False).head(qtd_vend).index,
                    text_auto=True,
                    title=f'Top {qtd_vend} vendedores (qtd vendas)'
                )
        st.plotly_chart(fig_vend_vendedores)