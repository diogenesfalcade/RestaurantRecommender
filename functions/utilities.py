import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from deep_translator import GoogleTranslator
from nltk.tokenize import sent_tokenize
import sys

def translateText(paragraph):
    """Wrapper for Google Translate with upload workaround.
    
    Collects chuncks of senteces below limit to translate.
    """
    # Set-up and wrap translation client
    translate = GoogleTranslator(source='en', target='pt').translate

    # Split input text into a list of sentences
    sentences = sent_tokenize(paragraph)

    translated_text = ''
    source_text_chunk = ''

    # collect chuncks of sentences below limit and translate them individually
    for sentence in sentences:
        # if chunck together with current sentence is below limit, add the sentence
        if ((len(sentence.encode('utf-8')) + len(source_text_chunk.encode('utf-8')) < 5000)):
            source_text_chunk += ' ' + sentence
        
        # else translate chunck and start new one with current sentence
        else:
            translated_text += ' ' + translate(source_text_chunk)

            # if current sentence smaller than 5000 chars, start new chunck
            if (len(sentence.encode('utf-8')) < 5000):
                source_text_chunk = sentence

            # else, replace sentence with notification message
            else:    
                message = "<<Omitted Word longer than 5000bytes>>"
                translated_text += ' ' + translate(message)

                # Re-set text container to empty
                source_text_chunk = ''

    # Translate the final chunk of input text, if there is any valid text left to translate
    if translate(source_text_chunk) != None:
        translated_text += ' ' + translate(source_text_chunk)
    
    return translated_text

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

def insertDb(restaurants):
    rest_df = pd.DataFrame(restaurants)
    rest_df = rest_df.drop_duplicates(subset=['place_id'])
    engine = create_engine('postgresql://postgres:manager@localhost:5432/postgres')
    rest_df.to_sql('gmaps_restaurants', con=engine, if_exists='replace', index=False)