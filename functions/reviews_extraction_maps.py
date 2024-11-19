import googlemaps
import time
import pandas as pd
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer

# API do Google Maps
api_key = "AIzaSyAnarAqn6NUl3qScGwo1ZbVFzwvTDpcax4"
gmaps = googlemaps.Client(key=api_key)

# Obter o place_id do local
lugar = 'Gianttura Ristorante'
resultado = gmaps.places(query=lugar)

# Pega o place_id do primeiro resultado
if resultado['results']:
    place_id = resultado['results'][0]['place_id']

# Obter a primeira página de reviews
detalhes_lugar = gmaps.place(place_id=place_id, fields=['name', 'rating', 'reviews'])


# Armazena e exibe as reviews da primeira página
if 'result' in detalhes_lugar:
    lugar_info = detalhes_lugar['result']
    print(f"Nome: {lugar_info.get('name')}")

    # Itera sobre as reviews e armazena
    all_reviews = lugar_info.get('reviews', [])

    # Força uma nova página
    next_page_token = detalhes_lugar.get('next_page_token')

    # Se houver mais páginas, faz novas requisições
    while next_page_token:
        time.sleep(2)  # Aguarde um pouco antes de usar o token (isso é recomendado)
        detalhes_lugar = gmaps.place(place_id=place_id, fields=['reviews'], page_token=next_page_token)
        more_reviews = detalhes_lugar.get('result', {}).get('reviews', [])
        all_reviews.extend(more_reviews)
        next_page_token = detalhes_lugar.get('next_page_token')

    # Exibe as reviews obtidas
    for review in all_reviews:
        print(f"Autor: {review['author_name']}, Nota: {review['rating']}, Comentário: {review['text']}\n")

def get_all_reviews(place_id, gmaps):
    all_reviews = []
    detalhes_lugar = gmaps.place(place_id=place_id, fields=['reviews', 'name'])

    if 'result' in detalhes_lugar:
        lugar_info = detalhes_lugar['result']
        print(f"Nome: {lugar_info.get('name')}")
        all_reviews.extend(lugar_info.get('reviews', []))

        # tenta pegar a próxima página
        next_page_token = detalhes_lugar.get('next_page_token')
        while next_page_token:
            time.sleep(3)  # Aguardar token

            # Faz a nova requisição para a próxima página
            detalhes_lugar = gmaps.place(place_id=place_id, fields=['reviews'], page_token=next_page_token)
            more_reviews = detalhes_lugar.get('result', {}).get('reviews', [])
            all_reviews.extend(more_reviews)
            next_page_token = detalhes_lugar.get('next_page_token')

    return all_reviews

def print_reviews(reviews):
    for review in reviews:
        print(f"Autor: {review.get('author_name')}, Nota: {review.get('rating')}, Comentário: {review.get('text')}\n")

reviews = get_all_reviews(place_id, gmaps)
print_reviews(reviews)