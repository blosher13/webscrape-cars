from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
import pandas as pd
from datetime import date
import os

session = HTMLSession()
base_url = 'https://www.toyota.ca'


def get_make_model():

    overview_url = session.get(f'{base_url}/en/build-price/')
    overview_url.html.render(sleep=3)  # wait for JS to load
    soup = BeautifulSoup(overview_url.html.html, 'html.parser')

    car_data = []
    models_tag = soup.find('div', class_='gridCardNormal')

    for ul in models_tag.find_all('ul'):
        anchor = ul.find('a', class_='anchor')

        info_link = anchor.get('href')
        model = anchor.find('span', class_='title').get_text(strip=True)

        car_data.append({
            'make': 'Toyota',
            'model': model,
            'url': f'{base_url}{info_link}'
        })
    return car_data

toyota_file_name = 'toyota_models.csv'

if os.path.exists(toyota_file_name):
    print('loading cached csv file')
    df = pd.read_csv(toyota_file_name)
else:
    print('Scraping fresh data')
    car_data = get_make_model()
    df = pd.DataFrame(car_data)
    df.to_csv(toyota_file_name, index=False, encoding='utf-8')
    print(f'Saved {len(df)} models to toyota_models.csv')

print(list(df['url']))
# prices = []
# def get_model_details(detail_urls_list):
#     for detail_url in detail_urls_list:
#         detail_request = session.get(f'{base_url}{detail_url}')
#         detail_request.html.render(sleep=3)  # wait for JS to load
        
#         soup = BeautifulSoup(detail_request.html.html, 'html.parser')

#         trims = soup.find_all('div', class_='regularVehicleWrapper')
        
#         for trim in trims:
#             inner = trim.find('span', class_='dollarSign')
#             msrp_price = inner.find_parent('span').get_text(strip=True)
#             prices.append(msrp_price)






    

