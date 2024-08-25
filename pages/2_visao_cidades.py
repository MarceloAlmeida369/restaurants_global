import pandas as pd
import streamlit as st
from PIL import Image
import plotly.express as px
import inflection

#--------- CLASSE: PÁGINA-2 'VISÃO CIDADES' -----------------------------------

class AppCidades:
    """
    Classe responsável pela interface da visão de cidades no aplicativo.
    Contém métodos para exibir a barra lateral e a página principal com gráficos e tabelas relacionadas às cidades.
    """
    
    def __init__(self) -> None:
        """
        Construtor da classe. Inicializa o DataFrame e a instância utilitária.
        """
        self.dfcidades: pd.DataFrame = None
        self.util: DBUtil = None

    def BarraLateral(self) -> None:
        """
        Método para construir a barra lateral do aplicativo.
        Adiciona filtros para seleção de países e define os critérios de visualização de dados.
        """
        # Icone e Título do App
        image_path = '/home/srm/PROJETOS_DS/Projeto_fomezero/Restaurant_Icon.png'
        image = Image.open(image_path)
        st.sidebar.image(image, width=60)

        # Filtros por países
        st.sidebar.markdown('## Filtros')
        st.sidebar.write('Escolha os **PAÍSES** cujas **CIDADES** deseja visualizar:')

        # Radio Button - Seleção de países
        the_countries = self.util.get_all_countries()
        default_countries = self.util.countries_with_more_restaurants(6)
        qty_countries = st.sidebar.radio("", ('Principais', 'Todos'), label_visibility="collapsed")
        if qty_countries == 'Todos':
            default_countries = the_countries

        # Multiselect para selecionar os países
        country_options = st.sidebar.multiselect(label='Seleção:', options=the_countries, default=default_countries)
        self.dfcidades = self.util.get_items_with_these_countries(country_options)

        # Assinatura do autor
        st.sidebar.markdown("""---""")
        st.sidebar.write('')
        st.sidebar.caption('Powered by Marcelo- 2024')
        st.sidebar.caption(':blue[servicoseletricosloiola@gmail.com]')
        st.sidebar.caption('[github](https://github.com/MarceloAlmeida369)')

    def MainPage(self):
        """
        Método para construir a página principal do aplicativo.
        Exibe gráficos e tabelas com base nas seleções feitas na barra lateral.
        """
        # Título da Página
        st.write('# Zomato Restaurants - Visão Cidades')

        # Gráfico 1: Top-10 cidades com mais restaurantes registrados
        st.divider()
        with st.container():
            st.write('### Top 10 cidades com mais restaurantes registrados')
            colunas = ['country_name', 'city', 'restaurant_id']
            df2 = (self.dfcidades.loc[:, colunas]
                   .groupby(['country_name', 'city']).count()
                   .sort_values(by=['country_name', 'city'])
                   .sort_values(by='restaurant_id', ascending=False)
                   .reset_index())
            df2.columns = ['País', 'Cidade', 'Qtd. Restaurantes']
            fig = px.bar(df2.head(10), x='Cidade', y='Qtd. Restaurantes', color='País', text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

        # Gráfico 2 e 3: Cidades com avaliações altas e baixas
        st.markdown("""---""")
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.write('### Qtd. Restaurantes avaliados acima de 4.0')
                colunas = ['country_name', 'city', 'aggregate_rating']
                linhas = self.dfcidades['aggregate_rating'] > 4.0
                df2 = self.dfcidades.loc[linhas, colunas].copy()
                df3 = (df2.loc[:, colunas]
                       .groupby(['country_name', 'city']).count()
                       .sort_values(by='aggregate_rating', ascending=False)
                       .reset_index())
                df3.columns = ['País', 'Cidade', 'Qtd. Restaurantes']
                fig = px.bar(df3.head(10), x='Cidade', y='Qtd. Restaurantes', color='País', text_auto=True)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.write('### Qtd. Restaurantes avaliados abaixo de 2.5')
                colunas = ['country_name', 'city', 'aggregate_rating']
                linhas = self.dfcidades['aggregate_rating'] < 2.5
                df2 = self.dfcidades.loc[linhas, colunas].copy()
                df3 = (df2.loc[:, colunas]
                       .groupby(['country_name', 'city']).count()
                       .sort_values(by='aggregate_rating', ascending=False)
                       .reset_index())
                df3.columns = ['País', 'Cidade', 'Qtd. Restaurantes']
                fig = px.bar(df3.head(10), x='Cidade', y='Qtd. Restaurantes', color='País', text_auto=True)
                st.plotly_chart(fig, use_container_width=True)

        # Gráfico 4: Top-10 cidades com mais restaurantes de tipos culinários distintos
        st.markdown("""---""")
        with st.container():
            st.write('### Top 10 Cidades com mais Restaurantes de tipos culinários distintos')
            colunas = ['country_name', 'city', 'unique_cuisine', 'restaurant_id']
            df2 = self.dfcidades.loc[:, colunas].groupby(['country_name', 'city', 'unique_cuisine']).count().reset_index()
            colunas = ['country_name', 'city', 'unique_cuisine']
            df3 = df2.loc[:, colunas].groupby(['country_name', 'city']).count().sort_values(by='unique_cuisine', ascending=False).reset_index()
            df3.columns = ['País', 'Cidade', 'Qtd. Tipos Culinários Únicos']
            fig = px.bar(df3.head(10), x='Cidade', y='Qtd. Tipos Culinários Únicos', color='País', text_auto=True)
            st.plotly_chart(fig, use_container_width=True)


#--------- CLASSE: FUNÇÕES DE APOIO PARA ACESSO AOS DADOS ---------------------
class DBUtil:
    """
    Classe utilitária para operações de dados.
    Contém métodos para manipular e recuperar informações específicas a partir do DataFrame transformado.
    """
    def __init__(self) -> None:
        """
        Construtor da classe. Inicializa as variáveis e carrega as referências de países e cores.
        """
        self.dtframe = None
        self.COUNTRIES = {
            1: "India",
            14: "Australia",
            30: "Brazil",
            37: "Canada",
            94: "Indonesia",
            148: "New Zealand",
            162: "Philippines",
            166: "Qatar",
            184: "Singapore",
            189: "South Africa",
            191: "Sri Lanka",
            208: "Turkey",
            214: "United Arab Emirates",
            215: "England",
            216: "United States of America",
        }
        self.COLORS = {
            "3F7E00": "darkgreen",
            "5BA829": "green",
            "9ACD32": "lightgreen",
            "CBCBC8": "darkred",
            "CDD614": "orange",
            "FFBA00": "red",
            "FF7800": "darkred",
        }

    def LoadDataframe(self, inCSVfile) -> None:
        """
        Carrega o DataFrame a partir de um arquivo CSV.
        
        Argumentos:
        - inCSVfile: Caminho do arquivo CSV.
        """
        self.dtframe = pd.read_csv(inCSVfile)

    def GeneralCleansing(self) -> pd.DataFrame:
        """
        Realiza as operações gerais de limpeza no DataFrame, como renomear colunas, 
        remover duplicatas, ajustar espaços em branco e criar novas colunas.
        
        Retorna:
        - DataFrame limpo e pronto para uso.
        """
        self.rename_columns()
        self.dtframe.drop_duplicates(subset=['restaurant_id'], inplace=True)
        self.dtframe.drop(columns=['switch_to_order_menu'], inplace=True)
        self.StripColumns()
        self.CreateUniqueCuisine()
        return self.dtframe

    def StripColumns(self) -> None:
        """
        Remove espaços em branco no início e fim de valores de colunas específicas.
        """
        self.dtframe['restaurant_name'] = self.dtframe['restaurant_name'].str.strip()
        self.dtframe['city'] = self.dtframe['city'].str.strip()
        self.dtframe['locality'] = self.dtframe['locality'].str.strip()
        self.dtframe['locality_verbose'] = self.dtframe['locality_verbose'].str.strip()

    def CreateUniqueCuisine(self) -> None:
        """
        Cria a coluna 'unique_cuisine' que contém o primeiro tipo de culinária listado na coluna 'cuisines'.
        """
        self.dtframe['unique_cuisine'] = (self.dtframe.loc[:, 'cuisines']
                                          .apply(lambda x: x.split(",")[0] if isinstance(x, str) else ""))

    def rename_columns(self) -> pd.DataFrame:
        """
        Renomeia as colunas do DataFrame para o formato snake_case.
        Também cria a coluna 'country_name' baseada na coluna 'country_code'.
        
        Retorna:
        - DataFrame com colunas renomeadas.
        """
        title = lambda x: inflection.titleize(x)
        snakecase = lambda x: inflection.underscore(x)
        spaces = lambda x: x.replace(" ", "")

        cols_old = list(self.dtframe.columns)
        cols_old = list(map(title, cols_old))
        cols_old = list(map(spaces, cols_old))
        cols_new = list(map(snakecase, cols_old))
        self.dtframe.columns = cols_new

        self.dtframe['country_name'] = (self.dtframe.loc[:, 'country_code']
                                        .apply(lambda x: self.country_name(x)))

        return self.dtframe

    def country_name(self, country_id):
        """
        Retorna o nome do país baseado em seu código.
        
        Argumentos:
        - country_id: Código do país.
        
        Retorna:
        - Nome do país correspondente.
        """
        return self.COUNTRIES[country_id]

    def get_all_countries(self) -> list:
        """
        Recupera a lista de todos os países disponíveis no DataFrame.
        
        Retorna:
        - Lista de nomes de países ordenados alfabeticamente.
        """
        all_countries = self.dtframe['country_name'].unique().tolist()
        return sorted(all_countries)

    def countries_with_more_restaurants(self, NumCountries: int) -> list:
        """
        Recupera uma lista dos países com maior quantidade de restaurantes.
        
        Argumentos:
        - NumCountries: Número máximo de países a serem retornados.
        
        Retorna:
        - Lista dos países com mais restaurantes, limitada ao número especificado.
        """
        if NumCountries < 1:
            return []

        colunas = ['country_name', 'restaurant_id']
        df1 = (self.dtframe.loc[:, colunas]
               .groupby('country_name').count()
               .sort_values(by=['restaurant_id'], ascending=False)
               .reset_index())
        aux = df1.loc[0:(NumCountries - 1), 'country_name']
        return aux.tolist()

    def get_items_with_these_countries(self, list_of_countries: list) -> pd.DataFrame:
        """
        Filtra o DataFrame para conter apenas registros dos países especificados.
        
        Argumentos:
        - list_of_countries: Lista de nomes de países para filtrar.
        
        Retorna:
        - DataFrame filtrado contendo apenas os países especificados.
        """
        lines = (self.dtframe.loc[:, 'country_name']
                 .apply(lambda x: any(country in x for country in list_of_countries)))
        return self.dtframe.loc[lines, :].copy().reset_index()

#--------- MAIN HOME PROCEDURE ------------------------------------------------
def main():
    """
    Função principal para configuração da aplicação Streamlit.
    Define a configuração da página e executa as funções de limpeza e transformação de dados,
    além de instanciar e executar a página de visão de cidades.
    """
    st.set_page_config(page_title="Cidades", page_icon="🏘️", layout='wide')

    MyCSV = '/home/srm/PROJETOS_DS/Projeto_fomezero/dataset/zomato.csv'
    util = DBUtil()
    util.LoadDataframe(MyCSV)
    util.GeneralCleansing()  # Limpa e ajusta os dados

    # Cria a Home e inclui BarraLateral e PáginaPrincipal
    HomePage = AppCidades()
    HomePage.util = util
    HomePage.BarraLateral()
    HomePage.MainPage()

#--------- START ME UP --------------------------------------------------------
if __name__ == "__main__":
    main()
