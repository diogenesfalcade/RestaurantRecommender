#api key AIzaSyAnarAqn6NUl3qScGwo1ZbVFzwvTDpcax4
#import googlemaps
import time

import requests

url = "https://api.content.tripadvisor.com/api/v1/location/search?key=64958C6CE3974BFA98E78B49E69F06B8&searchQuery=Curitiba&language=en"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)

# Sua chave de API do TripAdvisor
api_key = '64958C6CE3974BFA98E78B49E69F06B8'

# Endpoint base da API do TripAdvisor
url = 'https://api.tripadvisor.com/api/endpoint_que_você_deseja_utilizar'

# Cabeçalhos da requisição, incluindo a chave da API
headers = {
    'Accept': 'application/json',
    'X-TripAdvisor-API-Key': api_key  # Chave de API TripAdvisor
}

# Parâmetros da requisição (dependendo do endpoint)
params = {
    'location_id': '297704',  # ID de exemplo para Paris
    'lang': 'pt',             # Idioma dos resultados
    'currency': 'BRL',        # Moeda
    # Outros parâmetros que o endpoint exige
}

# Fazendo a requisição para a API do TripAdvisor
response = requests.get(url, headers=headers, params=params)

# Verificando se a requisição foi bem-sucedida
if response.status_code == 200:
    # Dados da API em formato JSON
    data = response.json()
    print(data)
else:
    print(f"Erro: {response.status_code} - {response.text}")


# # Substitua pela sua chave de API do Google Maps
# api_key = "AIzaSyAnarAqn6NUl3qScGwo1ZbVFzwvTDpcax4"
# gmaps = googlemaps.Client(key=api_key)

# # Obtenha o place_id do local
# lugar = 'Gianttura Ristorante'
# resultado = gmaps.places(query=lugar)

# # Pega o place_id do primeiro resultado
# if resultado['results']:
#     place_id = resultado['results'][0]['place_id']

# # Obtenha a primeira página de reviews
# detalhes_lugar = gmaps.place(place_id=place_id, fields=['name', 'rating', 'reviews'])

# # Armazena e exibe as reviews da primeira página
# if 'result' in detalhes_lugar:
#     lugar_info = detalhes_lugar['result']
#     print(f"Nome: {lugar_info.get('name')}")
    
#     # Itera sobre as reviews e armazena
#     all_reviews = lugar_info.get('reviews', [])
    
#     # Verifica se existe um token para a próxima página
#     next_page_token = detalhes_lugar.get('next_page_token')
    
#     # Se houver mais páginas, faz novas requisições
#     while next_page_token:
#         time.sleep(2)  # Aguarde um pouco antes de usar o token (isso é recomendado)
#         detalhes_lugar = gmaps.place(place_id=place_id, fields=['reviews'], page_token=next_page_token)
#         more_reviews = detalhes_lugar.get('result', {}).get('reviews', [])
#         all_reviews.extend(more_reviews)
#         next_page_token = detalhes_lugar.get('next_page_token')
    
#     # Exibe as reviews obtidas
#     for review in all_reviews:
#         print(f"Autor: {review['author_name']}, Nota: {review['rating']}, Comentário: {review['text']}\n")