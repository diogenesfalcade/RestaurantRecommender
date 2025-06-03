import googlemaps
import time
import os

api_key = os.environ.get('GMAPS_KEY')

gmaps = googlemaps.Client(key=api_key)


def restaurantResponse(responseItem, tag: str):
    ''' 
    Get only defined items from the request and trannform into a python dict
    
    responseItem: Dict
        dict from gmaps api with requests made
    tag: str 
        name related to the search 
    
    '''
    restaurantResponses = []

    # Get the dictionary resposeItem and extract the following values:
    #       tag, name, place_id, price_level, rating, user_ratings
    #       business_status, address, latitude
    #       longitude, compound_code, types
    for item in responseItem:
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
        # Insert the item_dict into a list of dictionaries 
        restaurantResponses.append(item_dict)

    return restaurantResponses

def getRestaurantsNeighborhood(neighborhoods: list, city: str):
    '''
    Uses the list of Neighborhoods from the city to search for restaurants

    neighborhoods: list
        user defined list of neighborhoods to search restaurants

    city: str
        string of the city to search for restaurants
        you may include the state or country acronym such as Curitiba - PR, Brasil
    '''
    restaurants = []

    for neighborhood in neighborhoods:

        # Set the neighborhood and city to search for
        query_neighborhood = neighborhood + city

        # Get info from neighborhood
        place = gmaps.geocode(query_neighborhood)
        place_info = place[0]
        geo_results = place_info['geometry']
        geo_coordinates = geo_results['location']
        lat = geo_coordinates['lat']
        lng = geo_coordinates['lng']

        # Initialize while loop variables
        flag = False
        counter = 0
        while flag == False:
            # Request for the neighborhood restaurants
            if counter == 0:
                results = gmaps.places(type="restaurant", location=[lat, lng], radius=3000)
                response_items = results['results']
                restaurants.extend(restaurantResponse(response_items, neighborhood))
                counter += 1
            else:
                # leave loop if there is no more pages to extract
                if results.get('next_page_token') is None:
                    flag = True
                # Get next pages from the neighborhood restaurants
                else:
                    next_page = results.get('next_page_token')
                    time.sleep(2)
                    results = gmaps.places(type="restaurant", location=[lat, lng], radius=2000, page_token=next_page)
                    response_items = results['results']
                    restaurants.extend(restaurantResponse(response_items, neighborhood))
                    counter += 1

def getRestaurantsByType(city, typesOfRestaurants):
    '''
    Uses the list of types of restaurants to search for places in the city

    typesOfRestaurants: list
        user defined list of types of restaurants

    city: str
        city to search for restaurants
        you may include the state or country acronym such as Curitiba - PR, Brasil
    '''

    restaurants = []
    place = gmaps.geocode(city)
    place_info = place[0]
    geo_results = place_info['geometry']
    geo_coordinates = geo_results['location']
    lat = geo_coordinates['lat']
    lng = geo_coordinates['lng']
    for type in typesOfRestaurants:
        print(len(restaurants))
        flag = False
        counter = 0
        while flag == False:
            if counter == 0:
                results = gmaps.places(query=(type, " restaurantes em ", city), type="restaurant", location=[lat, lng])
                response_items = results['results']
                restaurants.extend(restaurantResponse(response_items, type))
                counter += 1
            else:
                if results.get('next_page_token') is None:
                    flag = True
                else:
                    next_page = results.get('next_page_token')
                    time.sleep(2)
                    results = gmaps.places(query=(type, " restaurantes em ", city), type="restaurant", location=[lat, lng], page_token=next_page)
                    response_items = results['results']
                    restaurants.extend(restaurantResponse(response_items, type))
                    counter += 1
    return restaurants


def searchRestaurants(tripAdvRestName):
    '''
    
    '''
    place = gmaps.geocode(tripAdvRestName)
    place_info = place[0]
    geo_results = place_info['geometry']
    geo_coordinates = geo_results['location']
    lat = geo_coordinates['lat']
    lng = geo_coordinates['lng']

    return lat, lng