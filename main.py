import pandas as pd
import functions.locations_maps as maps
import functions.utilities as util
import functions.reviews as rev
from sqlalchemy import create_engine

update = False
engine = create_engine('postgresql://postgres:manager@localhost:5432/postgres')

if __name__ == "__main__":

    # Get locations from gmaps api -> Around 900 restaurants
    if update:
        cidade = 'Curitiba'
        tipo_restaurante = ['tradicional', 'mexicana', 'latino', 'hamburger', 'pizzaria', 'alta gastronomia', 'americano', 'italiano', 
                        'turco', 'mediterraneano', 'chines', 'asiático', 'indiano', 'japones', 'brasileiro', 'árabe', 'vegetariano', 
                        'peruano', 'tailandês', 'pub', 'steakhouse', 'churrascaria', 'carne', 'churrasco', 'rodízio','fast food', 'yakisoba', 'ramem', 
                        'koren barbecue', 'izakaya', 'feijoada', 'risotto', 'focaccia', 'parmegiana', 'trattoria', 'ristorante']

        restaurants = maps.getRestaurantsByType(cidade, tipo_restaurante)
        util.insertDb(tableName='gmaps_restaurants', data=restaurants, dropDuplicatesBy = 'place_id')
    
    # Get all the restaurant from TripAdvisor based on gmaps first search
    if update:
        query = "SELECT name, latitude, longitude FROM gmaps_restaurants"
        df = pd.read_sql(query, con=engine)
        for row in df.itertuples():
            locationId, dfplaces = rev.locationId(row.name, row.latitude, row.longitude)
            util.insertDb('ta_location', dfplaces, dropDuplicatesBy='location_id', primaryKey='location_id')
            if locationId != 0:
                reviews = rev.getReviews(locationId)
                util.insertDb('ta_reviews', reviews, primaryKey='review_id')
    
    # Get all the reviews from TripAdvisor based on the location_id
    if update:
        query = """select distinct l.location_id from ta_location l
                left join ta_reviews r on l.location_id = r.location_id
                where r.review_id IS NULL 
                limit 50
                """
        df = pd.read_sql(query, con=engine)
        for row in df.itertuples():
            reviews = rev.getReviews(row.location_id)
            util.insertDb('ta_reviews', reviews, primaryKey='review_id')

    # Get location details from TripAdvisor based on the location_id
    query = "select location_id from ta_location limit 100 "
    df = pd.read_sql(query, con=engine)
    for row in df.itertuples():
        locationDetails = rev.getLocationDetails(row.location_id)
        util.insertDb('ta_location_details', locationDetails, primaryKey='location_id')

    