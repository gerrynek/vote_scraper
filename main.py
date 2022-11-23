import click
import pandas as pd
import requests
from pathlib import Path as P

@click.command()
@click.option("--url", "url", type=str, required=True, help="URL scrapované stránky")
@click.option("--output", "out", type=str, required=False, help="Název výstupního souboru")
def app(url, out):
    r = requests.get(url, headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    data = pd.read_html(r.text)
    list_of_votes = []
    list_of_cities = []
    list_of_city_numbers = []
    list_of_parties = []
    list_of_envelopes = []
    list_of_registered = []
    list_of_valid_votes = []

    for tabulka in range (0, len(data)):
        for i in data[tabulka]['Obec']['číslo']:
            list_of_city_numbers.append(i)
        for i in data[tabulka]['Obec']['název']:
            list_of_cities.append(i)
    list_of_cities = list_of_cities[:-2]
    list_of_city_numbers = list_of_city_numbers[:-2]
    cities = {list_of_city_numbers[i] : list_of_cities[i] for i in range(len(list_of_city_numbers))}
    
    kraj_no_f = url.split('kraj=')
    kraj_no = kraj_no_f[1].split('&xnu')[0]
    okrsek_no = url.split('&xnumnuts=')[1]

    url2_link = f'https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={kraj_no}&xobec={list_of_city_numbers[0]}&xvyber={okrsek_no}'
    r = requests.get(url2_link,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    data = pd.read_html(r.text, header=None)
    for iterace in range(1, len(data)):
        for nazev in data[iterace]['Strana']['název']:
            list_of_parties.append(nazev)
    list_of_parties = list_of_parties[:-1]

    for kod_obce in cities:
        nazev = cities[kod_obce]
        url2_link = f'https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={kraj_no}&xobec={kod_obce}&xvyber={okrsek_no}'
        r = requests.get(url2_link,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        data = pd.read_html(r.text, header=None)
        registered = str(data[0]['Voliči v seznamu'].values[0][0])
        list_of_registered.append((str(registered).encode("ascii", "ignore")).decode())
        envelopes = str(data[0]['Vydané obálky'].values[0][0])
        list_of_envelopes.append((str(envelopes).encode("ascii", "ignore")).decode())
        valid = str(data[0]['Platné hlasy'].values[0][0])
        list_of_valid_votes.append((str(valid).encode("ascii", "ignore")).decode())
        
        for data_sub in range (1, len(data)):
            for hlasy in data[data_sub]['Platné hlasy']['celkem']:
               # import code; code.interact(local=locals())
                list_of_votes.append((str(hlasy).encode("ascii", "ignore")).decode())

    a = 0
    b = len(list_of_parties)
    list_of_lists_of_votes = []
    for i in range(0, len(list_of_cities)):
        if list_of_votes[a:b]:
            list_of_lists_of_votes.append(list_of_votes[a:b])
        a += len(list_of_parties)+1
        b += len(list_of_parties)+1
#––––––––––––––––––––––––––––––––––––––––––
#OUTPUT data
    data_for_output = {
        "code":list_of_city_numbers,
        "location":list_of_cities,
        "registered":list_of_registered,
        "envelopes":list_of_envelopes,
        "valid":list_of_valid_votes,
    }
                    #TO DO
                    #PRIRADIT K JEDNOTLIVYM STRANAM JEJICH HLASY TED JE TO BLBE
    new_list=[]
    for i in range(0, len(list_of_parties)):
        for y in list_of_lists_of_votes:
            new_list.append(y[i])
    print(new_list)

    a = 0
    b = 25
    list_of_lists_of_votes_sorted = []
    for i in range(0, len(list_of_parties)):
        list_of_lists_of_votes_sorted.append(new_list[a:b])
        b+=25
        a+=25
    print(list_of_lists_of_votes_sorted)

    #for li in list_of_lists_of_votes: 
    #    parties = {list_of_parties[i] : list_of_lists_of_votes[i][li] for i in range(len(list_of_parties))}

    #print(list_of_parties)
    #print(list_of_lists_of_votes)

    #data_for_output.update(parties)
    #print(len(list_of_cities), len(list_of_lists_of_votes), len(list_of_city_numbers), len(list_of_parties))
    #print(pd.DataFrame(data_for_output))
    #filepath = P(f'output/{out}.csv')
    #filepath.parent.mkdir(parents=True, exist_ok=True)
    #pd.DataFrame(data_for_output).to_csv(filepath, index=False, header=True)

if __name__ == '__main__':
    app()