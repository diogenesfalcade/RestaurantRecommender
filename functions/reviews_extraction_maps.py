import googlemaps
import time
import pandas as pd
from sqlalchemy import create_engine

# Localizar todos os restaurantes na região central de curitiba, ou seja, todos os bairros que fazem parte da Matriz

gmaps = googlemaps.Client(key='AIzaSyAnarAqn6NUl3qScGwo1ZbVFzwvTDpcax4')
restaurants = []
cidade = 'Curitiba'
bairros = ['Ahú', 'Alto da Glória', 'Alto da XV', 'Batel', 'Bigorrilho', 'Bom Retiro',
           'Cabral', 'Centro', 'Centro Cívico', 'Cristo Rei', 'Hugo Lange', 'Jardim Botânico',
           'Jardim Social', 'Juvevê', 'Mercês', 'Prado Velho', 'Rebouças', 'São Francisco']

tipo_restaurante = ['tradicional', 'mexicana', 'latino', 'hamburger', 'pizzaria', 'alta gastronomia', 'americano', 'italiano', 
                     'turco', 'mediterraneano', 'chines', 'asiático', 'indiano', 'japones', 'brasileiro', 'árabe', 'vegetariano', 
                     'peruano', 'tailandês', 'pub', 'steakhouse', 'churrascaria', 'rodízio','fast food', 'yakisoba', 'ramem', 
                     'koren barbecue', 'izakaya', 'feijoada', 'risotto', 'focaccia', 'parmegiana', 'trattoria', 'ristorante']

def restaurant_response(response_items, tag):
    restaurant_responses = []
    
    for item in response_items:
        item_dict = {
            'tag': tag,
            'name': item.get('name'),
            'place_id': item.get('place_id'),
            'price_level': item.get('price_level'),
            'rating': item.get('rating'),
            'user_ratings_total': item.get('user_ratings_total'),
            'business_status': item.get('business_status'),
            'address': item.get('formatted_address'),
            'latitude': item.get('geometry', {}).get('location', {}).get('lat'),
            'longitude': item.get('geometry', {}).get('location', {}).get('lng'),
            'compound_code': item.get('plus_code', {}).get('compound_code'),
            'types': item.get('types', []),
        }
        
        restaurant_responses.append(item_dict)
    return restaurant_responses

def get_neighborhood():

    for bairro in bairros:
        query_bairro = bairro + " curitiba"
        place = gmaps.geocode(query_bairro)
        place_info = place[0]
        geo_results = place_info['geometry']
        geo_coordinates = geo_results['location']
        lat = geo_coordinates['lat']
        lng = geo_coordinates['lng']
        flag = False
        counter = 0
        while flag == False:
            if counter == 0:
                results = gmaps.places(type="restaurant", location=[lat, lng], radius=3000)
                response_items = results['results']
                restaurants.extend(restaurant_response(response_items, bairro))
                counter += 1
            else:
                if results.get('next_page_token') is None:
                    flag = True
                else:
                    next_page = results.get('next_page_token')
                    time.sleep(2)
                    results = gmaps.places(type="restaurant", location=[lat, lng], radius=2000, page_token=next_page)
                    response_items = results['results']
                    restaurants.extend(restaurant_response(response_items, bairro))
                    counter += 1

def getRestaurantsByType(cidade):
    place = gmaps.geocode("Curitiba")
    place_info = place[0]
    geo_results = place_info['geometry']
    geo_coordinates = geo_results['location']
    lat = geo_coordinates['lat']
    lng = geo_coordinates['lng']
    for tipo in tipo_restaurante:
        print(len(restaurants))
        flag = False
        counter = 0
        while flag == False:
            if counter == 0:
                results = gmaps.places(query=(tipo, "restaurantes em ", cidade), type="restaurant", location=[lat, lng])
                response_items = results['results']
                restaurants.extend(restaurant_response(response_items, tipo))
                counter += 1
            else:
                if results.get('next_page_token') is None:
                    flag = True
                else:
                    next_page = results.get('next_page_token')
                    time.sleep(2)
                    results = gmaps.places(query=(tipo, "restaurantes em Curitiba"), type="restaurant", location=[lat, lng], page_token=next_page)
                    response_items = results['results']
                    restaurants.extend(restaurant_response(response_items, tipo))
                    counter += 1

def insert_db(restaurants):
    rest_df = pd.DataFrame(restaurants)
    rest_df = rest_df.drop_duplicates(subset=['place_id'])
    engine = create_engine('postgresql://postgres:manager@localhost:5432/postgres')
    rest_df.to_sql('gmaps_restaurants', con=engine, if_exists='replace', index=False)

# def restaurant_response(response_items, tag):
#     restaurant_responses = []
#     for item in response_items:
#         item_dict = {}
#         item_dict['tag'], item_dict['name'], item_dict['place_id'], item_dict['price_level'], item_dict['rating'], item_dict['user_ratings_total'] = tag, item.get('name'), item.get('place_id'), item.get('price_level'), item.get('rating'), item.get('user_ratings_total')
#         restaurant_responses.append(item_dict)
#     return restaurant_responses