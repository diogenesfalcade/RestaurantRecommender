import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_parquet("recommendations.parquet")

df_ready = load_data()

def format_price_level(level):
    if level == 1:
        return "$"
    elif level == 2:
        return "$$ - $$$"
    elif level == 3:
        return "$$$$"
    else:
        return "N/A"

def exibir_recomendacoes(top5_df, novidades_df=None):
    st.markdown("### ⭐ Top 5 semelhantes:")

    cols = st.columns(len(top5_df))
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

    if novidades_df is not None and not novidades_df.empty:
        st.markdown("### 🌟 Sugestões que podem te agradar:")

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

opcoes = df_ready['name'].unique()
restaurante_base = st.selectbox("Escolha um restaurante que goste e conheça", opcoes)

if st.button("Recomendar"):
    linha = df_ready[df_ready['name'] == restaurante_base].iloc[0]
    nomes_recomendados = [linha[f"recom_{i}"] for i in range(1, 6)]
    df_top5 = df_ready[df_ready['name'].isin(nomes_recomendados)]

    # Sugestões adicionais
    top100 = df_ready[df_ready['ranking'] <= 100]
    top100 = top100[~top100['name'].isin(nomes_recomendados)]
    novidades_top100 = top100.sample(n=2, random_state=None)

    excluidos = nomes_recomendados + novidades_top100['name'].tolist()
    novidade_extra = df_ready[
        (df_ready['num_reviews'] < 100) &
        (~df_ready['name'].isin(excluidos))
        ].sample(n=1, random_state=None)

    novidades_df = pd.concat([novidades_top100, novidade_extra])
    exibir_recomendacoes(df_top5, novidades_df)
