from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import folium
import pandas as pd
import streamlit as st 
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon=';)',layout= 'wide')




# Funções -----------------------------------------------------------------------------------------------------------------
def clean_code (df1):
    """
        Esta função deve limpar o dataframe
    
        Tipos de limpeza:
        1.Remoção de dados NaN
        2.Mudança do tipo de colunas de dados
        3.Remoção dos espaços da variável de texto
        4.formatação da coluna de datas
        5.Limpeza da coluna de tempo ( remoção do texto da variável numérica )
  
        Input: Dataframe
        Output: Dataframe
  
    """
    # convertendo os dados
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    df1['Order_Date'] = pd.to_datetime (df1['Order_Date'], format= '%d-%m-%Y' )

    linhas_selecionadas = (df1['multiple_deliveries']!= 'NaN ')
    df1 = df1.loc[linhas_selecionadas,:].copy()

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype (int)

    # removendo os espaços dentro da strings
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()

    # limnpando a coluna de time token
    df1.loc[:,'Time_taken(min)'] = df1.loc[:,'Time_taken(min)'].apply( lambda x: x.split ( '(min) ')[1] )
    df1.loc[:,'Time_taken(min)'] = df1.loc[:,'Time_taken(min)'].astype( int )
    
    return df1

def top_delivers ( df1, top_asc ):
        df2 = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
                  .groupby(['City','Delivery_person_ID'])
                  .mean()
                  .sort_values(['City','Time_taken(min)'], ascending = top_asc).reset_index() )
                
        df_aux01 = df2.loc[df2['City']== 'Metropolitan', :].head(10)
        df_aux02 = df2.loc[df2['City']== 'Urban', :].head(10)
        df_aux03 = df2.loc[df2['City']== 'Semi-Urban', :].head(10)
                
        df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index (drop =True)
        return df3



#-----------------------------------Inicio da estrutura lógica do código --------------------------------------





# import dataset
df = pd.read_csv('dataset/train.csv')



# Limpando os dados
df1 = clean_code ( df )


st.header( 'Marketplace - Visão Entregadores')

image_path = 'img/ds.png'
image = Image.open( image_path)
st.logo( image )
        
st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fatest Delivery in Town' )
st.sidebar.markdown( """___""" )

st.sidebar.markdown( '## Selecione uma data limite' )

value = pd.to_datetime("2022-04-13").to_pydatetime()
min_value = pd.to_datetime("2022-02-11").to_pydatetime()
max_value = pd.to_datetime("2022-04-06").to_pydatetime()

# Slider com datas
date_slider = st.sidebar.slider(
    'Até qual valor ?',
    value=value,  # Valor inicial
    min_value=min_value,  # Data mínima
    max_value=max_value,  # Data máxima
    format="YYYY-MM-DD"  # Formato da data
)
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low','Medium','High','Jam'],
    default = ['Low','Medium','High','Jam'])

st.sidebar.markdown("""___""")
st.sidebar.markdown("### Powered by Comunidade DS")

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

linhas_selecionadas = df1['Road_traffic_density'].isin ( traffic_options )
df1 = df1.loc[linhas_selecionadas,:]




#------------------------ Layout Streamlit -----------------------------------------------



tab1, tab2,tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
        with st.container():
                st.title( 'Overal Metrics')
                                
                col1, col2, col3, col4 = st.columns (4, gap= 'large')
                
                with col1:
                    maior_idade = df1.loc[:,['Delivery_person_Age']].max()
                    col1.metric ('Maior idade', maior_idade)
                
                with col2:
                    menor_idade = df1.loc[:,['Delivery_person_Age']].min()
                    col2.metric ('Menor idade', menor_idade)
                    
                with col3:
                    melhor_condicao = df1.loc[:,['Vehicle_condition']].max()
                    col3.metric ('Melhor condição', melhor_condicao)
                
                with col4:
                    pior_condicao = df1.loc[:,['Vehicle_condition']].min()
                    col4.metric ('Pior condição', pior_condicao)
                    
        with st.container():
                st.markdown ( """____""" )
                st.title ( 'Avaliações' )
                    
                col1, col2 = st.columns ( 2 )
                with col1:
                    st.markdown ( '##### Avaliação média por entregador' )
                    df_avg_ratings_per_delivery = (df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                                                      .groupby('Delivery_person_ID')
                                                      .mean()
                                                      .reset_index())
                    st.dataframe ( df_avg_ratings_per_delivery )
                     
                with col2:
                    st.markdown ('##### Avaliação média por trânsito')
                    df_avg_std_ratings_by_traffic = (df1.loc[:,['Road_traffic_density','Delivery_person_Ratings']]
                                                        .groupby('Road_traffic_density')
                                                        .agg({'Delivery_person_Ratings':['mean','std']}))

                    df_avg_std_ratings_by_traffic.columns = ['Delivery_mean','Delivery_std']
                     
                    df_avg_std_ratings_by_traffic = df_avg_std_ratings_by_traffic.reset_index()
                    st.dataframe(df_avg_std_ratings_by_traffic)
                     
                

                    st.markdown ('##### Avaliação média por clima')
                    df_avg_std_ratings_by_weather = (df1.loc[:,['Weatherconditions','Delivery_person_Ratings']]
                                                        .groupby('Weatherconditions')
                                                        .agg({'Delivery_person_Ratings':['mean','std']}))

                    df_avg_std_ratings_by_weather.columns = ['Delivery_mean','Delivery_std']
                     
                    df_avg_std_ratings_by_weather = df_avg_std_ratings_by_weather.reset_index()
                    st.dataframe(df_avg_std_ratings_by_weather)
  
        
        with st.container():
                st.markdown ( """____""" )
                st.title ( 'Velocidade de Entrega' )
                
                col1, col2 = st.columns ( 2 )
                with col1:
                    st.markdown ('##### Top entregadores mais rápidos')
                    df3 = top_delivers (df1, top_asc=True)
                    st.dataframe (df3)
                
                with col2:
                    st.markdown ('##### Top entregadores mais lentos')
                    df3 = top_delivers (df1, top_asc=False)
                    st.dataframe (df3)