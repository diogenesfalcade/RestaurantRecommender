import googlemaps
import time
import pandas as pd

gmaps = googlemaps.Client(key='AIzaSyAnarAqn6NUl3qScGwo1ZbVFzwvTDpcax4')
bairros = ['Ahú',
           'Alto da Glória',
           'Alto da XV',
           'Batel',
           'Bigorrilho',
           'Bom Retiro',
           'Cabral',
           'Centro',
           'Centro Cívico',
           'Cristo Rei',
           'Hugo Lange',
           'Jardim Botânico',
           'Jardim Social',
           'Juvevê',
           'Mercês',
           'Prado Velho',
           'Rebouças',
           'São Francisco']
restaurants = []

def restaurant_response(response_items, tag):
    restaurant_responses = []
    for item in response_items:
        item_dict = {}
        item_dict['tag'], item_dict['name'], item_dict['place_id'], item_dict['price_level'], item_dict['rating'], item_dict['user_ratings_total'] = tag, item.get('name'), item.get('place_id'), item.get('price_level'), item.get('rating'), item.get('user_ratings_total')
        restaurant_responses.append(item_dict)
    return restaurant_responses

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

tipo_restaurante = ['tradicional', 
                    'mexicana', 
                    'latino', 
                    'hamburger', 
                    'pizzaria', 
                    'alta gastronomia', 
                    'americano', 
                    'italiano', 
                    'turco', 
                    'mediterraneano', 
                    'chines', 
                    'asiático', 
                    'indiano', 
                    'japones']

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
            results = gmaps.places(query=(tipo, "restaurantes em Curitiba"), type="restaurant", location=[lat, lng])
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