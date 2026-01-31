# importando as bibliotecas que serão utilizadas
import pandas as pd
import streamlit as st
import plotly.express as px

# Título da página do Dashboard
st.set_page_config(
    page_title='Dashboard de Salários na Área de Dados', # Titulo
    page_icon='📊', # Icone que aparece ao lado do titulo
    layout='wide', # wide = usa a tela inteira
)

# Importando a base de dados já tratada 
# df = pd.read_csv('https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv') -> DataFrame da Aula

# Meu DataFrame
df = pd.read_csv('dados-final.csv')


#------------------------------------------- Barra lateral (Filtros) ------------------------------------------------------
st.sidebar.header("Filtro") # Criando o titulo da barra lateral

# x_disponiveis
# Cria a variavel que vai armazenar as informações
# sorted = ordena
# df['ano'] = seleciona a coluna ano
# .unique = pega os valores unicos

# x_selecionados
# st.sidebar.multiselect = comando para dar a opção do usuario escolher quais dados vão aparecer
# ele vai receber o nome 'ano' e vai puxar os dados da variavel x_disponiveis

# FILTRO DE ANO
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect('ano', anos_disponiveis, default=anos_disponiveis)

# FILTRO DE SENIORIDADE
senioridades_disponieis = sorted(df['senioridade'].unique())
senioridades_selecionados = st.sidebar.multiselect('senioridade', senioridades_disponieis, default=senioridades_disponieis)

# FILTRO DE CONTRATO
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect('contrato', contratos_disponiveis, default=contratos_disponiveis)

# FILTRO DE TAMANHO DA EMPRESA
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect('tamanho_empresa', tamanhos_disponiveis, default=tamanhos_disponiveis)

#---------------------------------------------------- Aplicando a Filtragem dos dados ----------------------------------------------------------
#  O df principal é  filtrado baseado nas seleções feitas pelo usuario na barra lateral.

#.isin = seleciona apenas o que eu solicitei nos parenteses ao lado

df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionados)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]


#-------------------------------------------------------- Conteudo Principal -------------------------------------------------------------------
st.title('Dashboard Interativo da Análise de Salários na Área de Dados')
st.markdown('Explore os salários na área de dados nos últimos anos. Utilize os filtros a esquerda para selecionar dados específicos para a sua análise')


# Metricas Principais (KPIs)
st.subheader("Métricas gerais (Salario Anual em USD)") #subtitulo

# Se o DataFrame não estiver vazio, da para preencher tudo
# Senão retornará tudo vazio

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_freq = df_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_freq= 0, 0, 0, ""


col1, col2, col3, col4 = st.columns(4)
col1.metric("Média Salarial", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}") 
col3.metric("Total de Registros", f"${total_registros:,}")
col4.metric("Cargo Mais Frequente", cargo_freq)

st.markdown("---")



# Análises Visuais com Plotly 
st.subheader("Gráficos")

# Gráfico 1 - Barras
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'}) #(title_x=0.1, yaxis={'categoryorder':'total ascending'}) = move o titulo um pouco para a direita
        st.plotly_chart(grafico_cargos, use_container_width=True) #Exibe o Gráfico
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

# Gráfico 2 - Histograma
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")


# Gráfico 3 - Pizza/Rosca
col_graf3, col_graf4 = st.columns(2) #Define que os gráficos 3 e 4 fiquem juntos na linha de baixo

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['home_office'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")


# Gráfico 4 - Mapa
with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)

