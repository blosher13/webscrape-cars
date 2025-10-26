from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
import pandas as pd
from datetime import date
import os
import time

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
    df_models = pd.read_csv(toyota_file_name)
else:
    print('Scraping fresh data')
    car_data = get_make_model()
    df_models = pd.DataFrame(car_data)
    df_models.to_csv(toyota_file_name, index=False, encoding='utf-8')
    print(f'Saved {len(df_models)} models to toyota_models.csv')

def get_model_details(detail_urls_list):
    model_details = []
    for detail_url in detail_urls_list:
        try:
            detail_request = session.get(detail_url)
            detail_request.html.render(timeout=20, sleep=3)  # wait for JS to load
            
            soup = BeautifulSoup(detail_request.html.html, 'html.parser')

            trims = soup.find_all('div', class_='regularVehicleWrapper')
            
            for trim in trims:
                # get title
                model = trim.find('div', class_='titleTop subheading-1').text(strip=True)
                trim = trim.find('div', class_='titleBottom heading-5 heading-5--bold').text(strip=True)

                # get price
                inner_price = trim.find('span', class_='dollarSign')
                msrp_price = inner_price.find_parent('span').get_text(strip=True)
                model_details.append(
                    {
                        'make': 'Toyota',
                        'model': model,
                        'trim': trim,
                        'msrp_price': msrp_price
                    })
                detail_request.close()
                time.sleep(2)
        except Exception as e:
            print(f"Skipping {detail_url} due to error: {e}")
    return model_details

toyota_details_file_name = 'toyota_model_details.csv'

if os.path.exists(toyota_details_file_name):
    print('loading cached csv file')
    df_model_details = pd.read_csv(toyota_details_file_name)
else:
    print('Scraping fresh model_details data')
    details_url_list = (list(df_models['url']))
    model_details = get_model_details(details_url_list)
    df_model_details = pd.DataFrame(model_details)
    df_model_details.to_csv(toyota_details_file_name, index=False, encoding='utf-8')
    print(f'Saved {len(df_model_details)} models to toyota_model_details.csv')




    

