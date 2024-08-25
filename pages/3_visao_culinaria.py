import pandas as pd
import streamlit as st
from PIL import Image
import plotly.express as px
import inflection

#--------- ETL PROCESS ------------------------------------

def extract_data(file_path: str) -> pd.DataFrame:
    """
    Função para extrair dados do arquivo CSV.
    Argumentos:
    - file_path: Caminho do arquivo CSV.
    
    Retorna:
    - DataFrame carregado com os dados extraídos.
    """
    return pd.read_csv(file_path)

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Função para transformar os dados extraídos.
    Realiza operações como renomear colunas, remover duplicatas, 
    eliminar colunas desnecessárias, ajustar espaços em branco e 
    criar novas colunas baseadas em regras específicas.
    
    Argumentos:
    - df: DataFrame extraído.
    
    Retorna:
    - DataFrame transformado e pronto para análise.
    """
    df = rename_columns(df)
    df.drop_duplicates(subset=['restaurant_id'], inplace=True)
    df.drop(columns=['switch_to_order_menu'], inplace=True)
    df = strip_columns(df)
    df['unique_cuisine'] = df['cuisines'].apply(lambda x: x.split(",")[0] if isinstance(x, str) else "")
    return df

def load_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Função para carregar os dados transformados.
    Neste exemplo, ela apenas retorna o DataFrame para ser usado 
    em outras partes da aplicação.
    
    Argumentos:
    - df: DataFrame transformado.
    
    Retorna:
    - DataFrame carregado.
    """
    return df

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renomeia as colunas do DataFrame para o formato snake_case.
    Também adiciona uma coluna 'country_name' baseada na coluna 'country_code'.
    
    Argumentos:
    - df: DataFrame com as colunas originais.
    
    Retorna:
    - DataFrame com as colunas renomeadas.
    """
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    
    df.columns = cols_new
    
    df['country_name'] = df['country_code'].apply(lambda x: COUNTRIES.get(x, "Unknown"))
    
    return df

def strip_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove espaços em branco do início e do final de valores de 
    colunas específicas para padronizar os dados.
    
    Argumentos:
    - df: DataFrame original.
    
    Retorna:
    - DataFrame com espaços em branco removidos nas colunas específicas.
    """
    df['restaurant_name'] = df['restaurant_name'].str.strip()
    df['city'] = df['city'].str.strip()
    df['locality'] = df['locality'].str.strip()
    df['locality_verbose'] = df['locality_verbose'].str.strip()
    return df

#--------- CONSTANTS ------------------------------------------------
COUNTRIES = {
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

#--------- CLASSE: PÁGINA-3 'VISÃO CULINÁRIA' ---------------------------------
class AppCulinarias:
    """
    Classe responsável pela interface de visão culinária do aplicativo.
    Contém métodos para exibir a barra lateral e a página principal com 
    gráficos e tabelas relacionadas às culinárias.
    """
    def __init__(self, df: pd.DataFrame):
        """
        Construtor da classe. Inicializa os dados e a quantidade padrão 
        de itens a serem exibidos.
        
        Argumentos:
        - df: DataFrame com os dados carregados e transformados.
        """
        self.dfculinarias = df
        self.util = DBUtil(self.dfculinarias)
        self.SliderQuantidade = 0

    def BarraLateral(self) -> None:
        """
        Método para construir a barra lateral do aplicativo.
        Adiciona filtros para seleção de países e culinárias, além 
        de controles de quantidade de restaurantes exibidos.
        """
        image_path = 'Restaurant_Icon.png'
        image = Image.open(image_path)
        st.sidebar.image(image, width=60)

        st.sidebar.markdown('## Filtros')
        st.sidebar.write('Escolha os **PAÍSES** cujas **CIDADES** deseja visualizar:')

        the_countries = self.util.get_all_countries()
        default_countries = self.util.countries_with_more_restaurants(6)
        qty_countries = st.sidebar.radio("", ('Principais', 'Todos'), label_visibility="collapsed")
        if qty_countries == 'Todos':
            default_countries = the_countries

        country_options = st.sidebar.multiselect('Seleção de países:', options=the_countries, default=default_countries)
        self.dfculinarias = self.util.get_items_with_these_countries(country_options)

        val_slider = st.sidebar.slider('## Selecione a quantidade de Restaurantes para tabelar:', value=10, min_value=1, max_value=20, format='%d')
        st.sidebar.markdown("""---""")
        self.SliderQuantidade = val_slider

        st.sidebar.write('Escolha as **CULINÁRIAS** que deseja visualizar:')
        the_cuisines = self.util.get_all_cuisines()
        default_cuisines = self.util.cuisines_with_more_restaurants(12, self.util.dtframe)
        qty_cuisines = st.sidebar.radio("", ('As principais', 'Todas'), label_visibility="collapsed")
        if qty_cuisines == 'Todas':
            default_cuisines = the_cuisines

        cuisine_options = st.sidebar.multiselect('Seleção de Culinárias:', options=the_cuisines, default=default_cuisines)
        self.dfculinarias = self.util.get_items_with_these_cuisines(self.dfculinarias, cuisine_options)

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
        st.markdown('# World Restaurants - Visão Culinária')

        st.divider()
        st.write('### Melhores Restaurantes por Tipo Culinário')

        cuisines = self.util.cuisines_with_more_restaurants(5, self.dfculinarias)
        dfs = [self.util.best_restaurants_from_cuisine(cuisine, self.dfculinarias) for cuisine in cuisines]

        with st.container():
            cols = st.columns(5)
            for i, col in enumerate(cols):
                col.write(f'Tipo: **{cuisines[i]}**')
                col.write(f'#### {dfs[i].loc[0,"restaurant_name"]}')

        with st.container():
            cols = st.columns(5)
            for i, col in enumerate(cols):
                col.write(f'#### :blue[{str(dfs[i].loc[0,"aggregate_rating"])}/5.0]')
                col.caption(f'Em: {dfs[i].loc[0,"country_name"]}')

        st.divider()
        with st.container():
            st.write('### Restaurantes Melhor Avaliados')
            df2 = self.util.best_restaurants(self.dfculinarias)
            st.write(df2.head(self.SliderQuantidade))

        st.divider()
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.write('### Melhores Culinárias')
                df2 = self.util.best_cuisines(False, self.dfculinarias)
                df2.columns = ['Tipo de Culinária', 'Avaliação Média']
                fig = px.bar(df2.head(self.SliderQuantidade), x='Tipo de Culinária', y='Avaliação Média', text_auto=True)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.write('### Piores Culinárias')
                df2 = self.util.best_cuisines(True, self.dfculinarias)
                df2.columns = ['Tipo de Culinária', 'Avaliação Média']
                fig = px.bar(df2.head(self.SliderQuantidade), x='Tipo de Culinária', y='Avaliação Média', text_auto=True)
                st.plotly_chart(fig, use_container_width=True)

#--------- CLASSE: FUNÇÕES DE APOIO PARA ACESSO AOS DADOS ---------------------
class DBUtil:
    """
    Classe utilitária para operações de dados.
    Contém métodos para manipular e recuperar informações específicas     a partir do DataFrame transformado.
    """
    def __init__(self, df: pd.DataFrame):
        """
        Construtor da classe. Recebe o DataFrame transformado e inicializa 
        a instância para manipulação dos dados.
        
        Argumentos:
        - df: DataFrame transformado com os dados.
        """
        self.dtframe = df

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
        Filtra o DataFrame original para conter apenas registros dos países especificados.
        
        Argumentos:
        - list_of_countries: Lista de nomes de países para filtrar.
        
        Retorna:
        - DataFrame filtrado contendo apenas os países especificados.
        """
        lines = (self.dtframe.loc[:, 'country_name']
                 .apply(lambda x: any(country in x for country in list_of_countries)))
        return self.dtframe.loc[lines, :].copy().reset_index(drop=True)

    def get_all_cuisines(self) -> list:
        """
        Recupera a lista de todas as culinárias disponíveis no DataFrame.
        
        Retorna:
        - Lista de tipos de culinárias ordenados alfabeticamente.
        """
        linhas = self.dtframe['unique_cuisine'] != ''
        df2 = self.dtframe.loc[linhas, :].copy()
        all_items = df2['unique_cuisine'].unique().tolist()
        return sorted(all_items)

    def cuisines_with_more_restaurants(self, NumCuisines: int, inDF: pd.DataFrame) -> list:
        """
        Recupera uma lista dos tipos de culinárias com maior quantidade de restaurantes.
        
        Argumentos:
        - NumCuisines: Número máximo de tipos de culinárias a serem retornados.
        - inDF: DataFrame filtrado onde a operação será realizada.
        
        Retorna:
        - Lista dos tipos de culinárias com mais restaurantes, limitada ao número especificado.
        """
        if NumCuisines < 1:
            return []

        colunas = ['unique_cuisine', 'restaurant_id']
        df1 = (inDF.loc[:, colunas]
               .groupby('unique_cuisine').count()
               .sort_values(by=['restaurant_id'], ascending=False)
               .reset_index())
        aux = df1.loc[0:(NumCuisines - 1), 'unique_cuisine']
        return aux.tolist()

    def get_items_with_these_cuisines(self, inDF: pd.DataFrame, list_of_cuisines: list) -> pd.DataFrame:
        """
        Filtra o DataFrame para conter apenas registros dos tipos de culinárias especificados.
        
        Argumentos:
        - inDF: DataFrame filtrado onde a operação será realizada.
        - list_of_cuisines: Lista de tipos de culinárias para filtrar.
        
        Retorna:
        - DataFrame filtrado contendo apenas os tipos de culinárias especificados.
        """
        lines = (inDF.loc[:, 'unique_cuisine']
                 .apply(lambda x: any(cuizn in x for cuizn in list_of_cuisines)))
        return inDF.loc[lines, :].copy().reset_index(drop=True)

    def best_restaurants_from_cuisine(self, cuisine: str, inDF: pd.DataFrame) -> pd.DataFrame:
        """
        Encontra os melhores restaurantes para um determinado tipo de culinária.
        
        Argumentos:
        - cuisine: Tipo de culinária para filtrar.
        - inDF: DataFrame filtrado onde a operação será realizada.
        
        Retorna:
        - DataFrame contendo os melhores restaurantes para o tipo de culinária especificado.
        """
        colunas = ['restaurant_id', 'restaurant_name', 'unique_cuisine', 'aggregate_rating', 'country_name']
        linhas = (inDF['unique_cuisine'] == cuisine)
        df2 = inDF.loc[linhas, colunas].copy()
        df3 = df2.sort_values(by='aggregate_rating', ascending=False).reset_index(drop=True)
        max_rating = df3.loc[0, 'aggregate_rating']
        linhas = df3['aggregate_rating'] == max_rating
        return df3.loc[linhas, :].sort_values(by='restaurant_id').reset_index(drop=True)

    def best_restaurants(self, inDF: pd.DataFrame) -> pd.DataFrame:
        """
        Encontra os melhores restaurantes no DataFrame.
        
        Argumentos:
        - inDF: DataFrame onde a operação será realizada.
        
        Retorna:
        - DataFrame contendo os melhores restaurantes ordenados por classificação.
        """
        colunas = ['restaurant_id', 'restaurant_name', 'country_name', 'city', 'unique_cuisine', 'aggregate_rating']
        df3 = inDF.loc[:, colunas].copy()
        df3['restaurant_id'] = -df3['restaurant_id']
        df4 = (df3.loc[:, :]
               .sort_values(by=['aggregate_rating', 'restaurant_id'], ascending=False)
               .reset_index(drop=True))
        df4['restaurant_id'] = -df4['restaurant_id']
        return df4

    def best_cuisines(self, ascending_order: bool, inDF: pd.DataFrame) -> pd.DataFrame:
        """
        Encontra os tipos de culinárias com melhores ou piores avaliações.
        
        Argumentos:
        - ascending_order: Booleano que define se as avaliações devem ser em ordem crescente ou decrescente.
        - inDF: DataFrame onde a operação será realizada.
        
        Retorna:
        - DataFrame contendo os tipos de culinárias ordenados por avaliação média.
        """
        colunas = ['unique_cuisine', 'aggregate_rating']
        df = (inDF.loc[:, colunas]
              .groupby('unique_cuisine').mean()
              .sort_values(by='aggregate_rating', ascending=ascending_order)
              .reset_index())
        df['aggregate_rating'] = df.loc[:, 'aggregate_rating'].apply(lambda x: round(x, 1))
        return df

#--------- MAIN HOME PROCEDURE ------------------------------------------------
def main():
    """
    Função principal para configuração da aplicação Streamlit.
    Define a configuração da página e executa as funções de ETL, 
    além de instanciar e executar a página de visão culinária.
    """
    st.set_page_config(page_title="Culinárias", page_icon="🫖", layout='wide')

    # Processo de ETL
    file_path = 'dataset/zomato.csv'
    df_raw = extract_data(file_path)
    df_transformed = transform_data(df_raw)
    df_loaded = load_data(df_transformed)

    # Instancia a classe e executa a interface do aplicativo
    app = AppCulinarias(df_loaded)
    app.BarraLateral()
    app.MainPage()

#--------- START ME UP --------------------------------------------------------
if __name__ == "__main__":
    main()
