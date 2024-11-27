import streamlit as st
from PIL import Image



st.set_page_config(
    page_title='Home',
)

image = Image.open( "../img/ds.png" )
st.logo( image)

st.sidebar.markdown( """___""" )
st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fatest Delivery in Town' )
st.sidebar.markdown( """___""" )
st.sidebar.markdown( '###### Auno Comunidade DS - Fabio R Silva' )


st.write (' # Cury Company Growth Dashboard')

st.markdown(
    """
    Growth Daschboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes
    #### Como utilizar o Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores Semanais de Crescimento.
        - Visão Geográfica: Insigths de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    #### ASK for Help.
        - Time de Data Science do Discord
        @fabio
    """
)
