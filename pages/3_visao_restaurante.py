#Libraries
from datetime import datetime
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
# bibliotecas
import plotly.graph_objects as go 
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static


st.set_page_config(page_title='Visão Restaurante', layout='wide')



#--------------------------------------------------
#                FUNÇÕES
#--------------------------------------------------
def avg_std_time_traffic(df1):
    df_aux=(df1.loc[:,['Time_taken(min)','City','Road_traffic_density']]
                .groupby(["City",'Road_traffic_density'])
                .agg({'Time_taken(min)' : ['mean','std']}))
    
    df_aux.columns = ['Tempo medio','desvio padrao']
    df_aux = df_aux.reset_index()
    #df_aux = df_aux.loc[df_aux['City'] != 'NaN ',:]
    fig = px.sunburst(df_aux, path=['City','Road_traffic_density'], values = "Tempo medio", color= 'desvio padrao',
                      color_continuous_scale = 'RdBu', color_continuous_midpoint = np.average(df_aux['desvio padrao']))
    return fig

def avg_std_time_graph(df1):
    st.markdown("# Tempo medio de entrega por cidade")
    df_aux=df1.loc[:,['Time_taken(min)','City']].groupby("City").agg({'Time_taken(min)' : ['mean','std']})
    df_aux.columns = ['Tempo medio','desvio padrao']
    df_aux = df_aux.reset_index()
    #df_aux = df_aux.loc[df_aux['City'] != 'NaN ',:]
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                   
                        x=df_aux['City'],
                        y=df_aux['Tempo medio'],
                        error_y = dict(type='data', array=df_aux['desvio padrao'])))
    fig.update_layout(barmode='group')
    return fig
                
def avg_std_delivery(df1,festival, op):
    """
        Está função calcula a media e desvio padrão do tempo de entrega
        Parâmetros:
            Input:
                - df1: Dataframe om os dados necessários para o cálculo
                - op: Tipo de operação que precisa ser calculada
                    'Tempo medio' : Calcula o tempo médio
                    'Desvio padrão': Calcula o desvio padrão
            Output:
                -df: Dataframe com 2 colunas e 1 linha                            
    """
    df_aux = df1.loc[:,['Festival','Time_taken(min)']].groupby("Festival").agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = (['Tempo medio','Desvio padrao'])
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op],2)
    return df_aux
                
def distance(df1, fig):
    if fig == False: 
        df_rest = (df1.loc[:,['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']].
                   mean().reset_index())
        orig = [df_rest.values[0,1],df_rest.values[1,1]] #lat, long
        dest = [df_rest.values[2,1],df_rest.values[3,1]]
        var = np.round(haversine(orig,dest),2)
        return var
    else:
        df1['Distance (Km)'] = (df1.loc[:,['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']]
                    .apply(lambda x: haversine( (x['Restaurant_latitude'],
                                                 x['Restaurant_longitude']), 
                                               (x['Delivery_location_latitude'], 
                                                x['Delivery_location_longitude'])), axis=1))

        avg_distance = df1.loc[:, ['City','Distance (Km)']].groupby("City").mean().reset_index()
        fig = go.Figure( data = [go.Pie(labels = avg_distance['City'], values = avg_distance['Distance (Km)'], pull = [0,0.1,0])])
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
    
#----------------------------------------------------
#            INICIO DA ESTRUTURA LÓGICA
#----------------------------------------------------
df = pd.read_csv("Documents/train.csv")
df1 = clean_code(df)

#===========================================#
#       BARRA LATERAL  STREAMLIT                      #
#============================================#
st.header("Visão - Resturante")

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

tab1,tab2,tab2 = st.tabs(['Visão Gerencial','-','-'])
with tab1:
    with st.container():
        st.title("Overall Metrics")
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            df2 = df1.loc[:,'Delivery_person_ID'].nunique()
            col1.metric("Entregadores únicos",df2)
            
        with col2:
            var = distance(df1,fig=False)
            col2.metric("A distancia média das entregas é:",var)

            
            
        with col3:
            df_aux = avg_std_delivery(df1,festival='Yes', op='Tempo medio')
            col3.metric('Tempo medio com Festival',df_aux)
            

                
            
        with col4:
            df_aux = avg_std_delivery(df1,festival='Yes', op='Desvio padrao')
            col4.metric('Desvio padrao com Festival',df_aux)


            
        with col5:
            df_aux = avg_std_delivery(df1,festival='No', op='Tempo medio')
            col5.metric('Tempo medio sem Festival',df_aux)

        with col6:
            df_aux = avg_std_delivery(df1,festival='No', op='Desvio padrao')
            col6.metric('Desvio padrao sem Festival',df_aux)


    with st.container():
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)


        with col2:
            st.markdown("# Distribuição da distância")
            df_aux=df1.loc[:,['Time_taken(min)','City','Type_of_order']].groupby(["City",'Type_of_order']).agg({'Time_taken(min)' : ['mean','std']})
            df_aux.columns = ['Tempo medio','desvio padrao']
            df_aux = df_aux.reset_index()
            #df_aux = df_aux.loc[df_aux['City'] != 'NaN ',:]
            st.dataframe(df_aux)

    with st.container():
        st.markdown("---")
        st.title("Distribuição do tempo")
        col1,col2 = st.columns(2)
        
        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig)

            
        with col2:
            fig = avg_std_time_traffic(df1)
            st.plotly_chart(fig)




