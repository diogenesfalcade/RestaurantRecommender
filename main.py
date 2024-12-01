import pandas as pd
import googlemaps
import functions.locations_maps as maps
import functions.utilities as util
import functions.reviews as rev
from sqlalchemy import create_engine

update = False
engine = create_engine('postgresql://postgres:manager@localhost:5432/postgres')

if __name__ == "__main__":
    if update:
        cidade = 'Curitiba'
        # bairros = ['Ahú', 'Alto da Glória', 'Alto da XV', 'Batel', 'Bigorrilho', 'Bom Retiro',
        #     'Cabral', 'Centro', 'Centro Cívico', 'Cristo Rei', 'Hugo Lange', 'Jardim Botânico',
        #     'Jardim Social', 'Juvevê', 'Mercês', 'Prado Velho', 'Rebouças', 'São Francisco']
        tipo_restaurante = ['tradicional', 'mexicana', 'latino', 'hamburger', 'pizzaria', 'alta gastronomia', 'americano', 'italiano', 
                        'turco', 'mediterraneano', 'chines', 'asiático', 'indiano', 'japones', 'brasileiro', 'árabe', 'vegetariano', 
                        'peruano', 'tailandês', 'pub', 'steakhouse', 'churrascaria', 'carne', 'churrasco', 'rodízio','fast food', 'yakisoba', 'ramem', 
                        'koren barbecue', 'izakaya', 'feijoada', 'risotto', 'focaccia', 'parmegiana', 'trattoria', 'ristorante']

        restaurants = maps.getRestaurantsByType(cidade, tipo_restaurante)
        util.insertDb(restaurants)

    # Get all the restaurant names
    query = "SELECT name FROM gmaps_restaurants"
    df = pd.read_sql(query, con=engine)
    restaurants = pd.Series(df['name'].values)

    for restaurant in restaurants:
        locationId = rev.locationId(restaurant)
    

    

