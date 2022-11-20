import click
import pandas as pd
import requests
from pathlib import Path as P

@click.command()
@click.option("--url", "url", type=str, required=True, help="URL scrapované stránky")
@click.option("--output", "out", type=str, required=True, help="Název výstupního souboru")
def app(url, out):
    r = requests.get(url, headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    data = pd.read_html(r.text)
    #print(data)
    #print(len(data)) # více tabulek potreba doimplementovat
    list_of_numbers = []
    list_of_cities = []
    list_of_parties = []
    list_of_votes = []
    for tabulka in range (0, len(data)):
        for i in data[tabulka]['Obec']['číslo']:
            list_of_numbers.append(i)
        for i in data[tabulka]['Obec']['název']:
            list_of_cities.append(i)
    list_of_cities = list_of_cities[:-2]
    list_of_numbers = list_of_numbers[:-2]
    #print(list_of_cities, list_of_numbers)
    res = {list_of_numbers[i] : list_of_cities[i] for i in range(len(list_of_numbers))}
    

    url2_link = f'https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xobec={list_of_numbers[0]}&xvyber=7103'
    r = requests.get(url2_link,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    data = pd.read_html(r.text, header=None)
    for iterace in range(1, len(data)):
        for nazev in data[iterace]['Strana']['název']:
            list_of_parties.append(nazev)
    list_of_parties = list_of_parties[:-1]

    for kod_obce in res:
        nazev = res[kod_obce]
        url2_link = f'https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xobec={kod_obce}&xvyber=7103'
        r = requests.get(url2_link,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        data = pd.read_html(r.text, header=None)
        volici = str(data[0]['Voliči v seznamu'].values[0][0])
        obalky = str(data[0]['Vydané obálky'].values[0][0])
        odevzdane = str(data[0]['Odevzdané obálky'].values[0][0])
        platne = str(data[0]['Platné hlasy'].values[0][0])
        procento = round(float(data[0]['% platných hlasů'].values[0]/100), 2)
        #print(nazev, kod_obce,"|", volici, obalky, odevzdane, platne, procento)
        for data_sub in range (1, len(data)):
            for hlasy in data[data_sub]['Platné hlasy']['celkem']:
                #print(hlasy)
                list_of_votes.append(hlasy)
    a = 0
    b = 25
    list_of_lists_of_votes = []
    for i in range(0, len(list_of_cities)):
        #print(len(list_of_votes[a:b]))
        #print(list_of_votes[a:b])
        list_of_lists_of_votes.append(list_of_votes[a:b])
        a+=26
        b+=26
    #print(list_of_lists_of_votes)
    
    
    data_for_output = {
        "code":list_of_numbers,
        "location":list_of_cities,
        "registered":volici,
        "envelopes":obalky,
        "valid":platne,
    }
                            #TO DO
                            #PRIRADIT K JEDNOTLIVYM STRANAM JEJICH HLASY TED JE TO BLBE

    for li in list_of_lists_of_votes: 
        parties = {list_of_parties[i] : list_of_lists_of_votes[i][li] for i in range(len(list_of_parties))}

    print(parties)

    data_for_output.update(parties)
    print(len(list_of_cities), len(list_of_lists_of_votes), len(list_of_numbers), len(list_of_parties))
    #print(pd.DataFrame(data_for_output))

    #filepath = P(f'output/{out}')
    #filepath.parent.mkdir(parents=True, exist_ok=True)
    #pd.DataFrame(data_for_output).to_csv(filepath, index=False, header=True)

if __name__ == '__main__':
    app()