import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import pandas as pd
from os import listdir
from datetime import datetime as dt


def get_page_content(soup, url):
    if 'olx.pl' in url:
        title = soup.find('div', 'offer-titlebox').h1.text.strip()
        data = {
            x.find('th').text: x.find('strong').text.strip()
            for x in 
            soup\
                .find('table', 'details fixed marginbott20 margintop5 full')\
                .find_all('table')
        }
        desc = soup.find('div', id = 'textContent').text.strip()
        imgs = [
            x['src']
            for x in 
            soup\
                .find('div', id = 'offerdescription')\
                .find_all('img')
        ]
        
    elif 'otodom.pl' in url:    
        soup = soup.find('article')
        title = soup.find('h1').text.strip()
        data = dict([
            [x.strip() for x in x.text.split(':')]
            for x in
            soup\
                .find('section', 'section-overview')\
                .find_all('li')
        ])
        desc = " ".join([
            x.text.replace('\xa0', '')
            for x in 
            soup\
                .find('section', 'section-description')\
                .find_all('p')
            if x.text != ''
        ])
        imgs = list(set([
            x['srcset']
            for x in 
            soup\
                .find('div', 'slick-list')\
                .find_all('source')
        ]))
    return title, data, desc, imgs


opt = Options()
opt.add_argument('--headless')
driver = Chrome(options = opt)


driver.get("""
https://www.olx.pl/nieruchomosci/domy/sprzedaz/otrebusy/?
search%5Bfilter_enum_builttype%5D%5B0%5D=wolnostojacy&search%5B\
filter_enum_builttype%5D%5B1%5D=gospodarstwo&search%5Bdist%5D=5&page=1
""")
soup = BeautifulSoup(
    driver.find_element_by_xpath("//*").get_attribute('innerHTML'), 
    features = "html.parser"
)


urls = set([
    x['href']
    for x in 
    soup\
        .find('table', id = 'offers_table')\
        .find_all('a', attrs = {'class': 'detailsLink'})
])


offers = []
for url in urls:
    page = requests.get(url).text
    soup = BeautifulSoup(page, features = "html.parser")
    
    try:
        title, data, desc, imgs = get_page_content(soup, url)
    except Exception as e:
        print(e)
        print(url)
        print('---')
        continue
        
    offers.append({
        'url'  : url,
        'title': title,
        'data' : data,
        'desc' : desc,
        'imgs' : imgs
    })


data_list = [
    [
        offer['title'],
        offer['url'],
        offer['desc'],
        "-@@@-".join(offer['imgs']),

        offer['data']['Rynek'],
        offer['data']['Powierzchnia'],
        offer['data']['Powierzchnia działki'],
        offer['data']['Rodzaj zabudowy'],
        offer['data']['Liczba pięter'],
        
        offer['data'].get('Rok budowy', ""),
        offer['data'].get("Poddasze", ""),
        offer['data'].get("Dach", ""),
        offer['data'].get("Pokrycie dachu", ""),
        offer['data'].get("Stan wykończenia", ""),
        offer['data'].get("Okna", ""),
        offer['data'].get("Położenie", ""),
    ]
    for offer in
    offers
]


results = pd.DataFrame(
    data_list,
    columns = ['tytul', 'url', 'opis', 'zdj', 'rynek', 'pow', 'pow_dzialki', 'rodzaj_zab',
               'pietra', 'rok_budowy', 'poddasze', 'dach', 'pokrycie_dach', 'stan_wyk',
               'okna', 'polozenie']
)

results.to_csv('data/'+str(len(listdir('data/'))+1).zfill(5)+"_"+str(dt.now().date()))




