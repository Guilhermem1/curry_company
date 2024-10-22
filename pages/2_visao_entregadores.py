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


st.set_page_config(page_title='Visão Entregadores', layout='wide')


#------------------------------------------------------------------
#-----------------------FUNÇÕES------------------------------------
#--------------------------------------------------------------
def top_less_deliverys(df1,top_asc):           
    dfaux = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
             .groupby(['City','Time_taken(min)']).max()
             .sort_values(['City','Time_taken(min)'],ascending=top_asc).reset_index())

    df_aux01 = dfaux.loc[dfaux['City']=='Metropolitian',:].head(10)
    df_aux02 = dfaux.loc[dfaux['City']=='Urban',:].head(10)
    df_aux03 = dfaux.loc[dfaux['City']=='Semi-Urban',:].head(10)
    
    df_new = pd.concat([df_aux01, df_aux02, df_aux03])
    return df_new


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


# Visao - entregadores

#===========================================#
#       BARRA LATERAL  STREAMLIT                      
#============================================#
st.header("Visão - Entregadores")

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

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
    with st.container():
        st.title("Overall Metrics")
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            #Maior idade dos entregadores
            max = df1.iloc[:,2].max()   
            col1.metric("Maior idade", max)

        with col2:
            #Menor idade dos entregadores
            min = df1.iloc[:,2].min()
            col2.metric("Menor idade",min)
            
        with col3:
            #Melhor condicao de veiculo
            max = df1.loc[:,'Vehicle_condition'].max()
            col3.metric("Melhor condição: ",max)
            
        with col4:
            #Pior condicao de veiculo
            min = df1.loc[:,'Vehicle_condition'].min()
            col4.metric("Pior condição: ",min)

    with st.container():
        st.markdown("---")
        st.title("Avaliações")
        col1,col2 = st.columns(2)

        with col1:
            st.markdown("##### Avaliação média por entregador")
            df_aux = df1.loc[:, ['Delivery_person_ID','Delivery_person_Ratings']].groupby("Delivery_person_ID").mean().reset_index()
            st.dataframe(df_aux)

        with col2:
            st.markdown("##### Avaliação média por trânsito")
            dfa = (df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                   .groupby('Road_traffic_density')
                   .agg({'Delivery_person_Ratings': ['mean','std']}))
            dfa.columns = ['Media','Desvio Padrão']
            st.dataframe(dfa.reset_index())

            st.markdown("##### Avaliação média por clima")
            df_mean_std_wc = (df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                              .groupby("Weatherconditions")
                              .agg({'Delivery_person_Ratings':['mean','std']}))
            df_mean_std_wc.columns = ['Média',"Desvio Padrão"]
            st.dataframe(df_mean_std_wc.reset_index())

    with st.container():
        st.markdown("---")
        st.title("Velocidade de entrega")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Entregadores mais rapidos")
            df_new = top_less_deliverys(df1, top_asc=True)
            st.dataframe(df_new.reset_index(drop=True))
            
        with col2:
            st.subheader("Entregadores mais lentos")
            df_new = top_less_deliverys(df1, top_asc=False)
            st.dataframe(df_new.reset_index(drop=True))




        

