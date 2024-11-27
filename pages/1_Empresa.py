from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import folium
import pandas as pd
import streamlit as st 
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon=';)',layout= 'wide')






# Funções -----------------------------------------------------------------------------------------------
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

    df1['Order_Date'] = pd.to_datetime (df1['Order_Date'], format= "%d-%m-%Y")

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

def order_metric(df1):
    cols = ['ID','Order_Date']
    #Seleção de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    # desenhar o Gráfico de linhas
    fig = px.bar( df_aux, x = 'Order_Date', y='ID')
    return fig


def traffic_oder_share (df1):
    df_aux = (df1.loc[:,['ID','Road_traffic_density']]
                 .groupby( 'Road_traffic_density' )
                 .count()
                 .reset_index())
    
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN ", :]
    df_aux['entregas_perc'] = df_aux['ID']/ df_aux['ID'].sum()
          
    fig = px.pie (df_aux, values= 'entregas_perc', names = 'Road_traffic_density')
    return fig


def traffic_order_city( df1 ):
    df_aux = (df1.loc [:,['ID','City','Road_traffic_density']]
                 .groupby(['City','Road_traffic_density'])
                 .count()
                 .reset_index())
    
    fig = px.scatter( df_aux,x = 'City', y='Road_traffic_density', size='ID', color='City')
    return fig


def order_by_week ( df1 ):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    df_aux = (df1.loc[:,['ID','week_of_year']]
                 .groupby('week_of_year')
                 .count()
                 .reset_index())
    
    fig = px.line( df_aux, x= 'week_of_year', y= 'ID')
    return fig


def order_share_by_week ( df1 ):
    df_aux1 = (df1.loc[:,['ID','week_of_year']]
                  .groupby('week_of_year')
                  .count()
                  .reset_index())
    
    df_aux2 = (df1.loc[:,['Delivery_person_ID','week_of_year']]
                  .groupby('week_of_year')
                  .nunique()
                  .reset_index())
    
    df_aux = pd.merge(df_aux1, df_aux2, how= 'inner', on = 'week_of_year')
    df_aux ['Order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    
    fig= px.line(df_aux, x= 'week_of_year', y='Order_by_deliver')
    return fig


def country_maps ( df1 ):
    df_aux = (df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
                 .groupby(['City','Road_traffic_density'])
                 .median()
                 .reset_index())
    
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup= location_info[['City','Road_traffic_density']]).add_to( map )
        
    folium_static( map, width = 1024, height=600)


#-----------------------------------Inicio da estrutura lógica do código --------------------------------------
 


# import dataset
df = pd.read_csv('dataset/train.csv')



# Limpando os dados
df1 = clean_code ( df )


st.header( 'Marketplace - Visão Empresa')

image_path = 'img/ds.png'
image = Image.open( image_path)
st.logo( image)

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


# layout Streamlit
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática','Visão Geiográfica'])

with tab1:
    with st.container():
        fig = order_metric(df1)
        st.markdown( '# Order by Day')
        st.plotly_chart(fig, use_container_width=True)

        
    with st.container():
        col1, col2 = st.columns (2)
        
        with col1:
            fig = traffic_oder_share ( df1 )
            st.header( 'Traffic Order Share' )
            st.plotly_chart( fig, use_container_width=True)
            
        with col2:
            fig = traffic_order_city ( df1 )
            st.header ('Traffic Order City')
            st.plotly_chart (fig, use_container_width=True)
            
with tab2:
    with st.container():
        fig = order_by_week ( df1 )
        st.header( '# Order by Week' )
        st.plotly_chart (fig, use_container_width=True)
        
    with st.container():
        fig = order_share_by_week( df1 )
        st.header('# Order Share by Week')
        st.plotly_chart (fig, use_container_width= True)
        
with tab3:
    st.markdown ('# Country Maps')
    country_maps ( df1 )

