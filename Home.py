import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🎲"
)
#pwd no terminal
#image_path = "C:\Users\guilh" 
image = Image.open('logo_raitec_transp.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Faster delivery in town")
st.sidebar.markdown("""---""")

st.write("Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard ?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurate:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for help
    - Comunicate to @Guilherme
    """)


        