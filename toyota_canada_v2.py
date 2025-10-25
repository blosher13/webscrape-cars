from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession

session = HTMLSession()
base_url = 'https://www.toyota.ca'
overview_url = session.get(f'{base_url}/en/build-price/')
overview_url.html.render(sleep=3)  # wait for JS to load
soup = BeautifulSoup(overview_url.html.html, 'html.parser')

model_details_urls = []
models = []
def get_make_model():

    models_tag = soup.find('div', class_='gridCardNormal')

    for ul in models_tag.find_all('ul'):
        anchor = ul.find('a', class_='anchor')
        # print(anchor)

        info_link = anchor.get('href')
        # print(info_link)
        model_details_urls.append(info_link)

        model = anchor.find('span', class_='title').get_text(strip=True)
        # print(model)
        models.append(model)
    return models, model_details_urls

x, y = get_make_model()
print(x)
print(y)
# prices = []
# def get_model_details(detail_urls_list):
#     for detail_url in detail_urls_list:
#         detail_request = session.get(f'{base_url}/{detail_url}')
#         detail_request.html.render(sleep=3)  # wait for JS to load
        
#         soup = BeautifulSoup(detail_request.html.html, 'html.parser')

#         trims = soup.find_all('div', class_='regularVehicleWrapper')
        
#         for trim in trims:
#             inner = trim.find('span', class_='dollarSign')
#             msrp_price = inner.find_parent('span').get_text(strip=True)
#             prices.append(msrp_price)






    

