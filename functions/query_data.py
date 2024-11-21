import pandas as pd
import psycopg2
from sqlalchemy import create_engine

def query(command):
    try:
        connection = psycopg2.connect(
            host="localhost",           # Host do banco de dados
            database="postgres",   # Nome do banco de dados
            user="postgres",         # Nome de usuário
            password="manager",       # Senha
            port="5432"                 # Porta padrão do PostgreSQL
        )

        cursor = connection.cursor()
        cursor.execute(command & ";")
        result = cursor.fetchall()

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        
    finally:
        # Fechar a conexão e o cursor
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return result

def insert_db(restaurants):
    rest_df = pd.DataFrame(restaurants)
    rest_df = rest_df.drop_duplicates(subset=['place_id'])
    engine = create_engine('postgresql://postgres:manager@localhost:5432/postgres')
    rest_df.to_sql('gmaps_restaurants', con=engine, if_exists='replace', index=False)