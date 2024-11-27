from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import folium
import pandas as pd
import streamlit as st 
from PIL import Image
import numpy as np

from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurantes', page_icon=';)',layout= 'wide')



# Funções -------------------------------------------------------------------------------------------------------------
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


def distance (df1, fig):
    if fig == False:
        cols = ['Restaurant_latitude','Restaurant_longitude',
                'Delivery_location_latitude','Delivery_location_longitude']

        df1['Distance'] = df1.loc[:,cols].apply(lambda x: 
                            haversine ((x['Restaurant_latitude'],
                            x['Restaurant_longitude']),
                            (x['Delivery_location_latitude'],
                            x['Delivery_location_longitude'])),axis=1)

        avg_distance = np.round( df1['Distance'].mean(),2 )
        return avg_distance
    else:
        cols = ['Restaurant_latitude','Restaurant_longitude',
                'Delivery_location_latitude','Delivery_location_longitude']

        df1['Distance'] = df1.loc[:,cols].apply(lambda x: 
                            haversine ((x['Restaurant_latitude'],
                            x['Restaurant_longitude']),
                            (x['Delivery_location_latitude'],
                            x['Delivery_location_longitude'])),axis=1)

        avg_distance = df1.loc[:, ['City', 'Distance']].groupby('City').mean().reset_index()
        fig = go.Figure ( data = [go.Pie (labels=avg_distance['City'], values = avg_distance['Distance'],pull=[0,0.1,0])])
        return fig


def avg_std_time_delivery (df1,festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
        Input: 
            - df: Dataframe com dados necessários para cálculo.
            - op: Tipo de operação que precisa ser calculado.
            'avg_time': Calcula o tempo médio
            'std_time': Calcula o desvio padrão do tempo
        Output:
            - df: Dataframe com 2 colunas 1 linha
    """
    df_aux = (df1.loc[:,['Time_taken(min)','Festival']]
                 .groupby('Festival')
                 .agg({'Time_taken(min)':['mean','std']}))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round (df_aux.loc[df_aux['Festival']== festival,op],2)
    return df_aux


def avg_std_time_graph ( df1 ):
    df_aux = df1.loc[:,['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
                                
    fig = go.Figure()
    fig.add_trace ( go.Bar ( name= 'Control', x= df_aux['City'], y= df_aux['avg_time'], error_y = dict (type='data', array=df_aux['std_time'],visible=True)))
    fig.update_layout (barmode = 'group')
    return fig


def avg_std_time_on_traffic( df1 ):
    df_aux = (df1.loc[:,['City', 'Time_taken(min)','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .agg({'Time_taken(min)':['mean','std']}))
    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    
    fig = px.sunburst (df_aux, path = ['City','Road_traffic_density'], values='avg_time',
                       color='std_time', color_continuous_scale= 'RdBu',
                       color_continuous_midpoint = np.average(df_aux['std_time']))
    return fig

#-----------------------------------Inicio da estrutura lógica do código --------------------------------------





# import dataset
df = pd.read_csv('dataset/train.csv')



# Limpando os dados
df1 = clean_code ( df )


st.header( 'Marketplace - Visão Entregadores')

image = Image.open( "img/DS.png" )
st.logo(image)

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
                col1, col2, col3, col4, col5, col6 = st.columns ( 6 )
                with col1:
                    delivery_unique = len(df1.Delivery_person_ID.unique())
                    col1.metric (' Entregadores', delivery_unique)
                
                with col2:
                    avg_distance = distance (df1, fig=False)
                    col2.metric ('A distância média ',avg_distance)
                    
                with col3:
                    df_aux = avg_std_time_delivery (df1,'Yes' ,'avg_time')
                    col3.metric('Tempo médio', df_aux)

                with col4:
                    df_aux = avg_std_time_delivery (df1,'Yes', 'std_time')
                    col4.metric('STD entrega', df_aux)
                
                with col5:
                    df_aux = avg_std_time_delivery (df1,'No' ,'avg_time')
                    col5.metric('Tempo médio', df_aux)
                
                with col6:
                    df_aux = avg_std_time_delivery (df1,'No', 'std_time')
                    col6.metric('STD entrega', df_aux)
                    
        with st.container():
                st.markdown ("""___""")
                
                col1, col2 = st.columns ( 2 )
                with col1:
                    fig = avg_std_time_graph (df1)
                    st.plotly_chart( fig )
                    
                with col2:
                    df_aux = (df1.loc[:,['City','Time_taken(min)','Type_of_order']]
                                 .groupby(['City','Type_of_order'])
                                 .agg({'Time_taken(min)':['mean','std']}))
                    
                    df_aux.columns = ['avg_time','std_time']
                    df_aux = df_aux.reset_index()
                    st.dataframe( df_aux )
                    
        with st.container():
                st.markdown ("""___""")
                st.title( 'Distribuição do Tempo' )
                
                col1, col2 = st.columns ( 2 )
                with col1:
                    fig = distance ( df1, fig=True)
                    st.plotly_chart (fig)
                    
                with col2:
                    fig = avg_std_time_on_traffic ( df1 )
                    st.plotly_chart (fig)
                    
                    
