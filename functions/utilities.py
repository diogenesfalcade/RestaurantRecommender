import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from deep_translator import GoogleTranslator
from nltk.tokenize import sent_tokenize
import logging

logging.basicConfig(level=logging.INFO)

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

# def insertDb(tableName, data, dropDuplicatesBy=None, method='append'):
#     rest_df = pd.DataFrame(data)

#     if dropDuplicatesBy and dropDuplicatesBy not in rest_df.columns:
#         raise ValueError(f"Coluna '{dropDuplicatesBy}' não encontrada no DataFrame.")

#     if dropDuplicatesBy:
#         rest_df = rest_df.drop_duplicates(subset=[dropDuplicatesBy])

#     engine = create_engine('postgresql://postgres:manager@localhost:5432/postgres')
#     rest_df.to_sql(tableName, con=engine, if_exists = method, index=False)

def insertDb(tableName, data, dropDuplicatesBy=None, primaryKey=None):
    """
    Insere dados no banco de dados PostgreSQL com controle de duplicatas.

    Args:
        tableName (str): Nome da tabela no banco de dados.
        data (list[dict] | DataFrame): Dados a serem inseridos.
        dropDuplicatesBy (str): Coluna para eliminar duplicatas antes da inserção (opcional).
        primaryKey (str): Nome da chave primária para gerenciar duplicatas (obrigatório para evitar conflitos).
    """
    rest_df = pd.DataFrame(data)

    if dropDuplicatesBy and dropDuplicatesBy not in rest_df.columns:
        raise ValueError(f"Coluna '{dropDuplicatesBy}' não encontrada no DataFrame.")

    if dropDuplicatesBy:
        rest_df = rest_df.drop_duplicates(subset=[dropDuplicatesBy])

    if primaryKey is None:
        raise ValueError("A chave primária (primaryKey) deve ser especificada para gerenciar duplicatas.")

    temp_table = f"{tableName}_temp"
    engine = create_engine('postgresql://postgres:manager@localhost:5432/postgres')

    with engine.connect() as connection:
        try:
            # Inserir dados na tabela temporária
            rest_df.to_sql(temp_table, con=connection, if_exists='replace', index=False)
            logging.info(f"Dados inseridos na tabela temporária '{temp_table}' com sucesso.")

            # Inserir na tabela final
            insert_query = f"""
            INSERT INTO {tableName} ({', '.join(rest_df.columns)})
            SELECT {', '.join(rest_df.columns)}
            FROM {temp_table}
            ON CONFLICT ({primaryKey}) DO NOTHING;
            """
            logging.info(f"Executando o comando: {insert_query}")
            result = connection.execute(text(insert_query))
            logging.info(f"Linhas afetadas: {result.rowcount}")

            # Confirmar transação
            connection.commit()
            logging.info("Transação confirmada com sucesso.")

        except Exception as e:
            logging.error(f"Erro durante a inserção: {e}")
            connection.rollback()  # Reverter alterações em caso de erro
        finally:
            # Limpar tabela temporária
            connection.execute(text(f"DROP TABLE IF EXISTS {temp_table}"))
            logging.info(f"Tabela temporária '{temp_table}' descartada com sucesso.")