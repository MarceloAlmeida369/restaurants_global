import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
from locale import atof, setlocale, LC_NUMERIC
from dbutil import DbUtil  # Certifique-se de que o nome do arquivo é dbutil.py e o import está correto

#--------- CLASSE: PÁGINA 'HOME' ----------------------------------------------
class app_home():
    def __init__(self) -> None:
        self.dfhome: pd.core.frame.DataFrame = None
        self.util: DbUtil = None

    def BarraLateral(self) -> None:
        image_path = 'Restaurant_Icon.png'
        image = Image.open(image_path)
        st.sidebar.image(image, width=80)

        st.sidebar.markdown('# Zomato Restaurants')
        st.sidebar.markdown('## Filtros')
        st.sidebar.write('Escolha os **PAÍSES** cujas **INFORMAÇÕES** deseja visualizar:')

        the_countries = self.util.get_all_countries()
        default_countries = self.util.countries_with_more_restaurants(6)
        qty_countries = st.sidebar.radio("", ('Principais', 'Todos'), label_visibility="collapsed")
        if qty_countries == 'Todos':
            default_countries = the_countries

        country_options = st.sidebar.multiselect(
            label='Seleção:',
            options=the_countries,
            default=default_countries
        )

        self.dfhome = self.util.get_items_with_these_countries(country_options)

        st.sidebar.markdown("""---""")
        csv_file = self.dfhome.to_csv()
        txt = 'Dados tratados e com filtragem do usuário'
        if st.sidebar.download_button('Baixar dados', csv_file, None, 'text/csv', help=txt):
            st.sidebar.write('Download OK :thumbsup:')

        st.sidebar.markdown("""---""")
        st.sidebar.write('')
        st.sidebar.caption('Powered by Marcelo- 2024')
        st.sidebar.caption(':blue[servicoseletricosloiola@gmail.com]')
        st.sidebar.caption('[github](https://github.com/MarceloAlmeida369)')

    def MainPage(self):
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                image_path = 'Restaurant_Icon.png'
                image = Image.open(image_path)
                st.image(image, width=160)
            with col2:
                st.write('# Zomato Restaurants')

        st.write("### O melhor lugar para encontrar o seu mais novo restaurante favorito")
        st.markdown("""---""")
        st.write("### Nossa plataforma vem alcançando as seguintes marcas:")

        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.write('**Países selecionados**')
            with col2:
                st.write('**Cidades cadastradas**')
            with col3:
                st.write('**Restaurantes cadastrados**')
            with col4:
                st.write('**Avaliações feitas na plataforma**')
            with col5:
                st.write('**Tipos de culinárias ofertadas**')

        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                tot = len(self.dfhome['country_name'].unique())  # países
                st.markdown('## **' + str(tot) + '**')
            with col2:
                tot = len(self.dfhome['city'].unique())  # cidades
                st.markdown('## **' + str(tot) + '**')
            with col3:
                tot = len(self.dfhome['restaurant_name'].unique())  # restaurantes
                txt = self.num_to_str(tot)
                st.markdown('## **' + txt + '**')
            with col4:
                df1 = self.dfhome['votes']  # avaliações
                tot = df1.sum()
                txt = self.num_to_str(tot)
                st.markdown('## **' + txt + '**')
            with col5:
                tot = len(self.dfhome['unique_cuisine'].unique())  # culinárias
                st.markdown('## **' + str(tot) + '**')

        st.markdown("""---""")
        self.country_map()

    def country_map(self) -> None:
        colunas = ['city', 'aggregate_rating', 'rating_color', 'latitude', 'longitude']
        df2 = self.dfhome.loc[:, colunas]
        df3 = (df2.loc[:, :].groupby(['city', 'aggregate_rating', 'rating_color'])
              .median()
              .reset_index())

        CityMap = folium.Map(zoom_start=11)

        for _, location_info in df3.iterrows():
            folium.Marker(
                [location_info['latitude'], location_info['longitude']],
                popup=location_info[['city', 'aggregate_rating']],
                icon=folium.Icon(color=self.util.color_name(location_info['rating_color']))
            ).add_to(CityMap)
        folium_static(CityMap, width=1024, height=600)

    def num_to_str(self, inNUM: float) -> str:
        if inNUM < 10000:
            return '{:,.0f}'.format(inNUM)
        elif inNUM < 999999:
            return '{:,.1f}'.format(inNUM / 1000) + ' mil'
        elif inNUM < 999999999:
            return '{:,.2f}'.format(inNUM / 1000000) + ' mi'
        else:
            return '{:,.2f}'.format(inNUM / 1000000000) + ' bi'

def main():
    st.set_page_config(page_title="Home", page_icon="🍴", layout='wide')

    # Passe o caminho do arquivo diretamente
    csv_path = 'dataset/zomato.csv'

    util = DbUtil()
    util.LoadDataframe(csv_path)  # Passe o caminho do arquivo aqui
    util.GeneralCleansing()  # Limpar e ajustar os dados

    HomePage = app_home()
    HomePage.util = util
    HomePage.BarraLateral()
    HomePage.MainPage()



    st.markdown("""
    ## Descrição do Dataset

    O dataset contém dados detalhados sobre restaurantes, incluindo informações como:

    - **Nome do Restaurante**: O nome de cada restaurante listado.
    - **Cidade**: A cidade onde o restaurante está localizado.
    - **País**: O país onde o restaurante está localizado.
    - **Tipo de Culinária**: Os diferentes tipos de culinária que o restaurante oferece.
    - **Preço para Dois**: O custo médio para duas pessoas no restaurante.
    - **Avaliação Média**: A classificação média que os usuários deram ao restaurante.
    - **Número de Avaliações**: O número total de avaliações que o restaurante recebeu.
    - **Código de Cor de Avaliação**: Um código que indica a cor associada à avaliação do restaurante, que geralmente reflete a qualidade ou popularidade.

    ## Uso do Dataset

    Este dataset pode ser utilizado para análises como:

    - **Análise de Preços**: Comparar o custo médio de refeições em diferentes cidades ou países.
    - **Análise de Avaliações**: Identificar os restaurantes mais bem avaliados e os menos avaliados em diferentes regiões.
    - **Análise de Tipos de Culinária**: Entender a distribuição de diferentes tipos de culinária em várias regiões do mundo.
    - **Visualizações Geográficas**: Criar mapas que mostrem a localização de restaurantes com base em suas coordenadas, juntamente com informações sobre avaliação e preço.

    ## Possíveis Projetos com o Dataset

    - **Dashboard de Avaliação de Restaurantes**: Um painel interativo que permite ao usuário filtrar e explorar restaurantes com base em avaliações, preço, e tipo de culinária.
    - **Análise de Tendências de Culinária Global**: Identificação das culinárias mais populares em diferentes partes do mundo.
    - **Previsão de Popularidade de Restaurantes**: Modelos preditivos para prever quais restaurantes podem se tornar populares com base em características como preço e localização.

    ## Conclusão

    O "Zomato Restaurants - Autoupdated Dataset" é uma rica fonte de dados para quem está interessado em explorar o setor de restaurantes globalmente. Ele oferece diversas possibilidades para análises, visualizações e desenvolvimento de modelos preditivos focados no comportamento de consumo em restaurantes.
    """)

    return

#--------- START ME UP --------------------------------------------------------
main()
