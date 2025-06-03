import requests
import json
import pandas as pd
import Levenshtein
import os

api_key = os.environ.get('TRIPADVISOR_KEY')
lang = 'pt'

def locationId(name, lat, long):
    name.replace(" ", "%20")  
    url = f'https://api.content.tripadvisor.com/api/v1/location/search?key={api_key}&searchQuery=%7B{name}%7D&category=restaurants&latLong={lat}%2C{long}&language={lang}'
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    locationsIds = []
    names = []
    cities = []
    states = []
    countries = []
    postalCodes = []
    addresses = []

    for place in data['data']:
        locationsIds.append(place.get('location_id', 'N/A'))
        names.append(place.get('name', 'N/A'))
        cities.append(place['address_obj'].get('city', 'N/A'))
        states.append(place['address_obj'].get('state', 'N/A'))
        countries.append(place['address_obj'].get('country', 'N/A'))
        postalCodes.append(place['address_obj'].get('postalcode', 'N/A'))
        addresses.append(place['address_obj'].get('address_string', 'N/A'))

    df = pd.DataFrame({
        'location_id': locationsIds,
        'name': names,
        'city':cities,
        'state': states,
        'country': countries,
        'postal_code': postalCodes,
        'address': addresses
    })

    try:
        locationId = df.loc[df['name'] == name, 'location_id'].iloc[0]
    except:
        names = pd.Series(df['name'].values)
        ratio = 0.0
        for place in names:
            newRatio = Levenshtein.ratio(name,place, score_cutoff=0.9)
            if newRatio > ratio:
                ratio = newRatio
                mostRelevant = place
            
        if ratio != 0.0:
            locationId = df.loc[df['name'] == mostRelevant, 'location_id'].iloc[0]
        else:
            return 0, df

    return locationId, df

def getReviews(locationId):
    url = f"https://api.content.tripadvisor.com/api/v1/location/{locationId}/reviews?language={lang}&key={api_key}"
    headers = {"accept": "application/json"}
    
    # Parâmetros iniciais
    limit = 5
    offset = 0
    all_reviews = []
    max_pages = 100  # Máximo de páginas
    i = 1

    while i <= max_pages:
        params = {'limit': limit, 'offset': offset}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            # Adiciona reviews à lista
            reviews = data.get('data', [])
            all_reviews.extend(reviews)

            # Exibe logs para depuração
            print(f"Página: {i}, Offset: {offset}, Reviews retornados: {len(reviews)}")

            # Verifica se há mais reviews
            if len(reviews) < limit:
                print("Sem mais reviews disponíveis.")
                break

            # Incrementa offset e contador de páginas
            offset += limit
            i += 1
        else:
            print(f"Erro na requisição: {response.status_code}")
            break

    print(f"Total de reviews obtidos: {len(all_reviews)}")

    # Criando listas para cada coluna que será incluída no DataFrame
    ids = []
    lang_list = []
    location_id_list = []
    published_date = []
    rating = []
    review_texts = []
    review_titles = []
    trip_type = []
    travel_date = []
    usernames = []
    user_location_ids = []
    user_location_names = []
    subrating_cost = []
    subrating_service = []
    subrating_food = []

    # Extraindo os dados das reviews
    for review in all_reviews:
        ids.append(review.get('id', ''))
        lang_list.append(review.get('lang', ''))
        location_id_list.append(review.get('location_id', ''))
        published_date.append(review.get('published_date', ''))
        rating.append(review.get('rating', ''))
        review_texts.append(review.get('text', ''))
        review_titles.append(review.get('title', ''))
        trip_type.append(review.get('trip_type', ''))
        travel_date.append(review.get('travel_date', ''))
        usernames.append(review['user'].get('username', '') if review.get('user') else '')
        user_location_ids.append(review['user']['user_location'].get('id', '') if review.get('user', {}).get('user_location') else '')
        user_location_names.append(review['user']['user_location'].get('name', '') if review.get('user', {}).get('user_location') else '')

        # Subratings (avalições detalhadas)
        subratings = review.get('subratings', {})
        subrating_cost.append(subratings.get('0', {}).get('value', ''))
        subrating_service.append(subratings.get('1', {}).get('value', ''))
        subrating_food.append(subratings.get('2', {}).get('value', ''))

    # Criando o DataFrame com todas as colunas
    df_reviews = pd.DataFrame({
        'review_id': ids,
        'language': lang_list,
        'location_id': location_id_list,
        'published_date': published_date,
        'rating': rating,
        'review_text': review_texts,
        'review_title': review_titles,
        'trip_type': trip_type,
        'travel_date': travel_date,
        'username': usernames,
        'user_location_id': user_location_ids,
        'user_location_name': user_location_names,
        'subrating_cost': subrating_cost,
        'subrating_service': subrating_service,
        'subrating_food': subrating_food,
    })
                           
    return df_reviews


def getLocationDetails(locationId):
    url = f"https://api.content.tripadvisor.com/api/v1/location/{locationId}/details?key={api_key}&language={lang}&currency=BRL"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida
        locationDetails = response.json()  # Converte diretamente para JSON 
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar detalhes da localização {locationId}: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro

    # Extraindo os dados com conversão de tipos
    location_id = int(locationDetails.get('location_id', 0))
    name = locationDetails.get('name', '')
    description = locationDetails.get('description', '')
    email = locationDetails.get('email', '')
    website = locationDetails.get('website', '')

    # Ranking
    ranking_data = locationDetails.get('ranking_data', {})
    ranking_position = int(ranking_data.get('ranking', 0)) if ranking_data.get('ranking') else None
    ranking_out_of = int(ranking_data.get('ranking_out_of', 0)) if ranking_data.get('ranking_out_of') else None

    # Avaliações
    rating = float(locationDetails.get('rating', 0.0))
    num_reviews = int(locationDetails.get('num_reviews', 0))

    # Contagem de avaliações por nota (1 a 5 estrelas)
    review_rating = locationDetails.get('review_rating_count', {})
    review_rating_1 = int(review_rating.get('1', 0))
    review_rating_2 = int(review_rating.get('2', 0))
    review_rating_3 = int(review_rating.get('3', 0))
    review_rating_4 = int(review_rating.get('4', 0))
    review_rating_5 = int(review_rating.get('5', 0))

    # Subratings
    subratings = locationDetails.get('subratings', {})
    food_rating = float(subratings.get("0", {}).get("value", 0.0))
    service_rating = float(subratings.get("1", {}).get("value", 0.0))
    value_rating = float(subratings.get("2", {}).get("value", 0.0))

    # Outras informações
    price_level = locationDetails.get('price_level', '')

    # Horários de funcionamento
    hours = locationDetails.get('hours', {})
    weekdays_opening_hours = hours.get('weekday_text', [])

    # Características, Culinárias, Categorias, Subcategorias, Tipos de Viagem
    features = locationDetails.get('features', [])
    cuisines = [cuisine.get('localized_name', '') for cuisine in locationDetails.get('cuisine', [])]
    category = locationDetails.get('category', {}).get('localized_name', '')
    subcategories = [subcategory.get('localized_name', '') for subcategory in locationDetails.get('subcategory', [])]
    trip_types = [tripType.get('localized_name', '') for tripType in locationDetails.get('trip_types', [])]

    # Convertendo as listas para o formato de array do PostgreSQL
    features = '{' + ','.join(features) + '}' if isinstance(features, list) else features
    cuisines = '{' + ','.join(cuisines) + '}' if isinstance(cuisines, list) else cuisines
    category = '{' + category + '}' if isinstance(category, str) else category
    subcategories = '{' + ','.join(subcategories) + '}' if isinstance(subcategories, list) else subcategories
    trip_types = '{' + ','.join(trip_types) + '}' if isinstance(trip_types, list) else trip_types

    # Criando o DataFrame
    df_location_details = pd.DataFrame([{
        'location_id': location_id,
        'name': name,
        'description': description,
        'email': email,
        'website': website,
        'ranking_position': ranking_position,
        'ranking_out_of': ranking_out_of,
        'rating': rating,
        'num_reviews': num_reviews,
        'review_rating_1': review_rating_1,
        'review_rating_2': review_rating_2,
        'review_rating_3': review_rating_3,
        'review_rating_4': review_rating_4,
        'review_rating_5': review_rating_5,
        'food_rating': food_rating,
        'service_rating': service_rating,
        'value_rating': value_rating,
        'price_level': price_level,
        'weekdays_opening_hours': weekdays_opening_hours,
        'features': features,
        'cuisines': cuisines,
        'categories': category,
        'subcategories': subcategories,
        'trip_types': trip_types
    }])

    return df_location_details


