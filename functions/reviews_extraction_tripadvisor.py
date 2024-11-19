import requests
import json
import pandas as pd

api_key = '64958C6CE3974BFA98E78B49E69F06B8'
lang = 'pt'
query = "Jardim Botânico de Curitiba"
query.replace(" ", "%20")  

url = f"https://api.content.tripadvisor.com/api/v1/location/search?key=64958C6CE3974BFA98E78B49E69F06B8&searchQuery={query}&language={lang}"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)

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

# Criando um DataFrame
df = pd.DataFrame({
    'Location Id': locationsIds,
    'Name': names,
    'City':cities,
    'State': states,
    'Country': countries,
    'Postal Code': postalCodes,
    'Address': addresses
})

#melhorar código para achar a localização correta
locationId = df.loc[df['Name'] == query, 'Location Id'].iloc[0]
locationId


url = f"https://api.content.tripadvisor.com/api/v1/location/{locationId}/reviews?language={lang}&key=64958C6CE3974BFA98E78B49E69F06B8"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)

# Parâmetros iniciais
limit = 5
offset = 0

headers = {
    'Accept': 'application/json'
}

url = f'https://api.content.tripadvisor.com/api/v1/location/{locationId}/reviews?language={lang}&key=64958C6CE3974BFA98E78B49E69F06B8'

all_reviews = []
i = 1

# pegar até 5 páginas de requisição
while i < 5:
    i= i + 1
    params = {
        'limit': limit,
        'offset': offset
    }

    response = requests.get(url, headers=headers, params=params)

    # Verificando se a resposta foi bem-sucedida
    if response.status_code == 200:
        data = response.json()

        # Adicionando reviews à lista
        all_reviews.extend(data.get('data', []))

        # Verifica se há mais reviews a serem obtidos
        if len(data.get('data', [])) < limit:
            break  # Sai do loop quando não houver mais reviews

        # Aumenta o offset para a próxima página
        offset += limit
    else:
        print(f"Erro na requisição: {response.status_code}")
        break

# Exibindo o total de reviews obtidos
print(f'Total de reviews obtidos: {len(all_reviews)}')


review_texts = []
review_titles = []

for review in all_reviews:
  review_texts.append(review.get('text', ''))
  review_titles.append(review.get('title', ''))


df_reviews = pd.DataFrame({'Review Text': review_texts, 'Review Title': review_titles})

df_reviews