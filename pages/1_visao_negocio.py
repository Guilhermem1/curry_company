#Libraries
from datetime import datetime
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
# bibliotecas
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static


st.set_page_config(page_title='Visão Empresa', layout='wide')

#----------------------------------------------
#               FUNÇÕES
#----------------------------------------------
def country_maps(df1):
    map_ = folium.Map()
    df_auxx = df1.loc[: ,["City","Road_traffic_density","Delivery_location_latitude",
                          "Delivery_location_longitude"]].groupby(["City","Road_traffic_density"]).median().reset_index()

    for index, location_info in df_auxx.iterrows():
          folium.Marker( [location_info["Delivery_location_latitude"], location_info["Delivery_location_longitude"]], 
                        popup= location_info[["City","Road_traffic_density"]]).add_to( map_ )
    folium_static( map_ , width = 1024, height = 600)

    return None
    
def order_share_by_week(df1):
    #Quantidade de pedidos por semana / numero unico de entregadores por semana
    df_001 = df1.loc[:, ["ID","week_of_year"]].groupby("week_of_year").count().reset_index()
    df_002 = df1.loc[:, ["Delivery_person_ID","week_of_year"]].groupby("week_of_year").nunique().reset_index()
    
    # Juntando os dois dataframes
    df_aux = pd.merge(df_001, df_002, how='inner')
    df_aux['entrega_por_entregador'] = df_aux['ID']/ df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='entrega_por_entregador')
    return fig
            
def order_by_week(df1):     
    #criar columa semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( " %U ") # %U -> comeca no domingo / %W -> comeca na segunda
    df1_aux2 = df1.loc[: , ["ID","week_of_year"]].groupby("week_of_year").count().reset_index()
    fig = px.line(df1_aux2, x='week_of_year', y="ID")
    return fig
    
def traffic_order_city(df1):
    df_aux4 = df1.loc[:, ["ID","City","Road_traffic_density"]].groupby(["City","Road_traffic_density"]).count().reset_index()
    df_aux4 = df_aux4.loc[df_aux4['City'] != "NaN " , :]
    df_aux4 = df_aux4.loc[df_aux4['Road_traffic_density'] != "NaN " , :]
    fig = px.scatter(df_aux4, x='City', y="Road_traffic_density", size='ID', color='City')
    return fig
    
def traffic_order_share(df1):
    #st.markdown("# coluna 1")
    # Distribuição dos pedidos por tipo de tráfego
    df_aux3 = df1.loc[:, ["ID","Road_traffic_density"]].groupby("Road_traffic_density").count().reset_index()
    df_aux3 = df_aux3.loc[df_aux3["Road_traffic_density"] != "NaN ", :]
    df_aux3['entrega_porc'] = df_aux3['ID'] / df_aux3['ID'].sum()
    fig = px.pie(df_aux3, values='entrega_porc', names='Road_traffic_density')
    return fig

def order_metric(df1):
    # Seleção de linhas
    df_aux = df1.loc[:, ['ID','Order_Date']].groupby("Order_Date").count().reset_index()
    # desenhar gráfico de linhas
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig

def clean_code(df1):
    """ Esta função tem responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo de colunas de dados
        3. Remoção do espaço das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção da variável numérica [(min)] )

        Input: dataframe
        Output: dataframe
    
    """
    linhas_selecionadas = (df1['Delivery_person_Age'] != "NaN ")
    df1 = df1.loc[linhas_selecionadas,:].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != "NaN ")
    df1 = df1.loc[linhas_selecionadas,:].copy()
    
    linhas_selecionadas = (df1['City'] != "NaN ")
    df1 = df1.loc[linhas_selecionadas,:].copy()
    
    linhas_selecionadas = (df1['Festival'] != "NaN ")
    df1 = df1.loc[linhas_selecionadas,:].copy()
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format = '%d-%m-%Y')
    
    linhas_selecionadas = (df1['multiple_deliveries'] != "NaN ")
    df1 = df1.loc[linhas_selecionadas,:].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    df1.loc[:,"ID"] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,"Road_traffic_density"] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,"Type_of_order"] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,"Type_of_vehicle"] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,"City"] = df1.loc[:,'City'].str.strip()
    df1.loc[:,"Festival"] = df1.loc[:,'Festival'].str.strip()
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split("(min) ")[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

#---------------INICIO DA ESTRUTURA LÓGICA DO CÓDIGO---------------------
#=======================================================================
# Import dataset
df = pd.read_csv("Documents/train.csv")

#Limpando os dados
df1 = clean_code(df)


# Visao - Empresa

#===========================================#
#       BARRA LATERAL  STREAMLIT                      #
#============================================#
st.header("Visão - Cliente")

image_path = 'logo_raitec_transp.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Faster delivery in town")
st.sidebar.markdown("""---""")

st.sidebar.markdown("## Selecione uma data")
data_slider = st.sidebar.slider(
    'Até qual valor ?',
    value = datetime(2022,4,13), 
    min_value = datetime(2022,2,11),
    max_value= datetime(2022,4,6),
    format = 'DD-MM-YYYY')
st.header(data_slider)

st.sidebar.markdown("""---""")

traffic_option = st.sidebar.multiselect(
    'Quais as condições de trânsito ?',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Integrando o filtro slide data
linha_selecionada = df1['Order_Date'] <= data_slider
df1 = df1.loc[linha_selecionada,:]

# Integrando o filtro slide traffic
linha_selecionada = df1['Road_traffic_density'].isin(traffic_option)
df1 = df1.loc[linha_selecionada,:]
st.dataframe(df1)


#=======================================#
#         LAYOUT STREAMLIT              #
#=======================================#
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        fig = order_metric(df1)
        st.markdown("# Order by day")
        st.plotly_chart(fig, use_container_width=True) #use_container_width para nao invadir o espaço do sidebar

        

        

        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig = traffic_order_share(df1)
            st.header("Traffic Order Share")
            st.plotly_chart(fig, use_container_width = True)


  
    
        with col2:
            # Comparação do volume de pedidos por cidade e por tipo de tráfego
            st.header("Traffic Order City")
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width = True)






with tab2:
    with st.container():
        # Quantidade de pedidos por semana
        st.markdown("# Order by week")
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)




    
    with st.container():
        # Quantidade de pedidos por entregador por semana
        st.markdown("# Order share by week")
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)






with tab3:
    st.markdown("# Country Maps")
    country_maps(df1)












#st.dataframe(df1)
#print(df1.head())



