from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd
from datetime import datetime, timezone
import os
from playwright.sync_api import sync_playwright

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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for detail_url in detail_urls_list:
            try:
                print(f'Scraping {detail_url}')
                page.goto(detail_url, timeout=6000)
                page.wait_for_timeout(3000)  # wait 3 sec for JS

                html = page.content()

                # detail_request = session.get(detail_url)
                # detail_request.html.render(timeout=20, sleep=3)  # wait for JS to load
                
                soup = BeautifulSoup(html, 'html.parser')

                trims = soup.find_all('div', class_='regularVehicleWrapper')
                
                for trim in trims:
                    # get title
                    model = trim.find('div', class_='titleTop subheading-1').get_text(strip=True)
                    trim_name = trim.find('div', class_='titleBottom heading-5 heading-5--bold').get_text(strip=True)

                    # get price
                    inner_price = trim.find('span', class_='dollarSign')
                    msrp_price = inner_price.find_parent('span').get_text(strip=True)
                    model_details.append(
                        {
                            'make': 'Toyota',
                            'model': model,
                            'trim': trim_name,
                            'msrp_price': msrp_price,
                            'as_of_datetime': datetime.now(timezone.utc)
                        })
            except Exception as e:
                print(f"Skipping {detail_url} due to error: {e}")
        browser.close()
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




# transform model details data into 2 datasets 

df_model_details[['year','model']] = df_model_details['model'].str.split(' ', n=1, expand=True)
df_model_details = df_model_details[['year','make', 'model', 'trim', 'msrp_price', 'as_of_datetime']]
df_model_details['msrp_price'] = df_model_details['msrp_price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
df_model_details['msrp_price'] = pd.to_numeric(df_model_details['msrp_price'])
df_model_details =df_model_details.where(pd.notnull(df_model_details), 'NA')
df_models = df_model_details[['make', 'model']].drop_duplicates().reset_index(drop=True)


df_models.to_csv('processed_data/toyota_make_model.csv', index=False, encoding='utf-8')
df_model_details.to_csv('processed_data/toyota_details.csv', index=False, encoding='utf-8')

print("Any NaN left in make_model:", df_model_details.isna().sum().sum())
print("Any NaN left in details:", df_models.isna().sum().sum())