import pandas as pd
import googlemaps
import functions.locations_maps as maps
import functions.query_data as qry

if __name__ == "__main__":

    update = False

    if update:
        cidade = 'Curitiba'
        # bairros = ['Ahú', 'Alto da Glória', 'Alto da XV', 'Batel', 'Bigorrilho', 'Bom Retiro',
        #     'Cabral', 'Centro', 'Centro Cívico', 'Cristo Rei', 'Hugo Lange', 'Jardim Botânico',
        #     'Jardim Social', 'Juvevê', 'Mercês', 'Prado Velho', 'Rebouças', 'São Francisco']
        tipo_restaurante = ['tradicional', 'mexicana', 'latino', 'hamburger', 'pizzaria', 'alta gastronomia', 'americano', 'italiano', 
                        'turco', 'mediterraneano', 'chines', 'asiático', 'indiano', 'japones', 'brasileiro', 'árabe', 'vegetariano', 
                        'peruano', 'tailandês', 'pub', 'steakhouse', 'churrascaria', 'rodízio','fast food', 'yakisoba', 'ramem', 
                        'koren barbecue', 'izakaya', 'feijoada', 'risotto', 'focaccia', 'parmegiana', 'trattoria', 'ristorante']

        restaurants = maps.getRestaurantsByType(cidade, tipo_restaurante)
        qry.insert_db(restaurants)
    