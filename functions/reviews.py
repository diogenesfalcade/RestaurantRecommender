import requests
import json
import pandas as pd
import Levenshtein

api_key = '64958C6CE3974BFA98E78B49E69F06B8'
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

    # Extraindo os dados dos reviews
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