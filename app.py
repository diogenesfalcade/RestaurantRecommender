import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

df_orig = pd.read_csv("df_high.csv")
df_reviews = pd.read_csv("df_reviews.csv")
df_websites = pd.read_csv("df_websites.csv")

df_orig["price_level"] = df_orig["price_level"].fillna(2)
df_orig.dropna()
df_orig["price_level"] = pd.to_numeric(df_orig["price_level"])
# Criando a coluna de categoria de rating
def categorize_rating(rating):
    if rating < 4.0:
        return 'Baixo'
    elif rating < 4.5:
        return 'Médio'
    else:
        return 'Alto'

df_orig['rating_category'] = df_orig['rating'].apply(categorize_rating)

# Remove colunas com menos de 2 valores "1"
limiar = 2
colunas_binarias = [col for col in df_orig.columns if df_orig[col].nunique() <= 2 and df_orig[col].dtype in ['int64', 'float64']]
colunas_remover = [col for col in colunas_binarias if df_orig[col].sum() < limiar]

df = df_orig.drop(columns=colunas_remover)

# Remove colunas não numéricas
X = df.drop(columns=['name', 'rating_category', 'location_id'], errors='ignore')
X = X.select_dtypes(include=['int64', 'float64'])
X = X.fillna(X.mean())

# Normaliza os dados
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Aplica PCA mantendo componentes que explicam até 95% da variância
pca = PCA(n_components=0.95)
X_pca = pca.fit_transform(X_scaled)

# Filtra os restaurantes com categoria 'Alto' e 'Médio'
df_high = df[df['rating_category'] != 'Baixo'].reset_index(drop=True)
X_pca_high = X_pca[df['rating_category'] != 'Baixo']

# Mescla os websites com o dataframe df_high
df_high = df_high.merge(df_websites[['location_id', 'website']], on='location_id', how='left')

# Calcula a similaridade
similarity_matrix = cosine_similarity(X_pca_high)

# Função de recomendação
def calcular_recomendacoes(idx, df_high, df_reviews):

    similarities = list(enumerate(similarity_matrix[idx]))

    # Calcula proporções de sentimentos para cada restaurante
    df_sentiments = df_reviews.groupby('location_id')['sentiment_label'].value_counts(normalize=True).unstack().fillna(0)
    df_sentiments['sentiment_score'] = df_sentiments.get('positivo', 0) - df_sentiments.get('negativo', 0)

    # Junta esses scores ao df_high
    df_high = df_high.merge(df_sentiments['sentiment_score'], left_on='location_id', right_index=True, how='left').fillna(0)

    # Ordena pela similaridade e pega top 10
    pontuacoes_sim = sorted([(i, sim) for i, sim in similarities if i != idx], key=lambda x: x[1], reverse=True)
    top10 = pontuacoes_sim[:10]

    # Cria um dataframe com esses top 10
    df_top10 = df_high.iloc[[i for i, _ in top10]].copy()
    df_top10['similarity'] = [sim for _, sim in top10]

    # Normaliza rating e sentiment_score dentro do top10 (0-1)
    df_top10['rating_norm'] = (df_top10['rating'] - df_top10['rating'].min()) / (df_top10['rating'].max() - df_top10['rating'].min())
    df_top10['sentiment_norm'] = (df_top10['sentiment_score'] - df_top10['sentiment_score'].min()) / (df_top10['sentiment_score'].max() - df_top10['sentiment_score'].min())

    # Calcula pontuação final ponderada
    df_top10['final_score'] = (0.7 * df_top10['similarity'] +
                            0.1 * df_top10['sentiment_norm'] +
                            0.3 * df_top10['rating_norm'])

    # Filtra para incluir apenas restaurantes com pelo menos 5 reviews
    df_top10 = df_top10[df_top10['num_reviews'] >= 5]

    # Pega os top 5 da pontuação final
    df_top5 = df_top10.sort_values(by='final_score', ascending=False).head(5)

    # Adiciona diversidade/novidade: amostra de restaurantes com menos de 100 reviews e bom sentimento
    novidades = df_high[(df_high['num_reviews'] < 100) & 
                                (df_high['sentiment_score'] > 0) & 
                                (df_high.index != idx)].sample(n=2)

    return df_top5, novidades

def exibir_recomendacoes(top5_df, novidades_df):
    st.markdown("### ⭐ Top 5 semelhantes:")

    # Cria colunas para dispor os cartões
    cols = st.columns(len(top5_df))

    def format_price_level(level):
        if level == 1:
            return "$"
        elif level == 2:
            return "$$ - $$$"
        elif level == 3:
            return "$$$$"
        else:
            return "N/A"

    for col, (_, row) in zip(cols, top5_df.iterrows()):
        with col:
            price_level_str = format_price_level(row["price_level"])
            st.markdown(
                f"""
                <div style='background-color: #1f1f1f; padding: 10px; border-radius: 10px; text-align: center;'>
                    <h4 style='color: #f63366;'><a href="{row['website']}" target="_blank" style='color: #f63366; text-decoration: none;'>{row['name']}</a></h4>
                    <p>⭐ {row['rating']}</p>
                    <p>📈 Reviews: {row['num_reviews']}</p>
                    <p>💰 Preço: {price_level_str}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("### 🌟 Sugestões diferentes:")

    cols2 = st.columns(len(novidades_df))

    for col, (_, row) in zip(cols2, novidades_df.iterrows()):
        with col:
            price_level_str = format_price_level(row["price_level"])
            st.markdown(
                f"""
                <div style='background-color: #1f1f1f; padding: 5px; border-radius: 10px; text-align: center;'>
                    <h4 style='color: #f63366;'><a href="{row['website']}" target="_blank" style='color: #f63366; text-decoration: none;'>{row['name']}</a></h4>
                    <p>⭐ {row['rating']}</p>
                    <p>📈 Reviews: {row['num_reviews']}</p>
                    <p>💰 Preço: {price_level_str}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


# Streamlit Interface
st.title("Recomendador de restaurantes")
opcoes = df_high['name'].unique()
restaurante_base = st.selectbox("Escolha um restaurante que goste e conheça", opcoes)

if st.button("Recomendar"):
    idx = df_high[df_high['name'] == restaurante_base].index[0]
    top5, novidades = calcular_recomendacoes(idx, df_high, df_reviews)
    exibir_recomendacoes(top5, novidades)

