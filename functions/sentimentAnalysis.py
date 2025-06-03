import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm
import requests
import json

conn_string = "postgresql://postgres:manager@localhost:5432/postgres"
db = create_engine(conn_string)

# Configuração do servidor Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"


# Função de classificação via Ollama
def classify_with_ollama(text):
    prompt = f"""Classifique o sentimento do texto abaixo e retorne APENAS um JSON com a chave "sentimento" e o valor: 'positivo', 'negativo' ou 'neutro'. Sem texto extra.

    Exemplo de saída: {{"sentimento": "positivo"}}

    Texto:
    {text[:512]}
    """
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False  # retorna a resposta completa
    }
    response = requests.post(OLLAMA_URL, json=data)
    response.raise_for_status()  # Lança exceção se der erro
    generated_text = response.json()['response']

    # Tenta encontrar o JSON e parsear
    try:
        # Às vezes o modelo coloca \n ou outros caracteres antes/depois – tentar extrair só o JSON
        start_idx = generated_text.find('{')
        end_idx = generated_text.rfind('}') + 1
        json_str = generated_text[start_idx:end_idx]
        sentiment_data = json.loads(json_str)
        return sentiment_data['sentimento'].strip()
    except Exception as e:
        print("Erro ao extrair JSON:", e)
        print("Texto recebido:", generated_text)
        return "neutro"  # Valor default ou pode lançar exceção, como preferir

# Ler todos os reviews
query = """
SELECT review_id, review_text FROM ta_reviews r
inner join ta_features_expanded f on r.location_id = f.location_id
"""
reviews_df = pd.read_sql(query, db)

# Classificar e atualizar em lote
with db.begin() as conn:
    for idx, row in tqdm(reviews_df.iterrows(), total=len(reviews_df)):
        sentiment_label = classify_with_ollama(row['review_text'])
        conn.execute(
            text("""
                UPDATE ta_reviews
                SET sentiment_label = :label
                WHERE review_id = :review_id
            """),
            {"label": sentiment_label, "review_id": row['review_id']}
        )