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

    #Vycucnuti seznamu obci a jejich IDs
    for tabulka in range (0, len(data)):
        for i in data[tabulka]['Obec']['číslo']:
            if not i == '-':    #POKUD JE PRAZDNY RADEK V SENAMU OBCI TAK HO IGNOROVAT
                list_of_city_numbers.append(i)
        for i in data[tabulka]['Obec']['název']:
            if not i == '-':
                list_of_cities.append(i)
    
    cities = {list_of_city_numbers[i] : list_of_cities[i] for i in range(len(list_of_city_numbers))}

    #Priprava promennych do url
    kraj_no_f = url.split('kraj=')
    kraj_no = kraj_no_f[1].split('&xnu')[0]
    okrsek_no = url.split('&xnumnuts=')[1]

    url2_link = f'https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={kraj_no}&xobec={list_of_city_numbers[0]}&xvyber={okrsek_no}'
    r = requests.get(url2_link,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    data = pd.read_html(r.text, header=None)
    for iterace in range(1, len(data)):
        for nazev in data[iterace]['Strana']['název']:
            list_of_parties.append(nazev)

    for kod_obce in cities:
        nazev = cities[kod_obce]
        url3_link = f'https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={kraj_no}&xobec={kod_obce}&xvyber={okrsek_no}'
        r = requests.get(url3_link,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        data = pd.read_html(r.text, header=None)
        registered = str(data[0]['Voliči v seznamu'].values[0][0])
        list_of_registered.append((str(registered).encode("ascii", "ignore")).decode()) #odstraneni prasarnicek v datech
        envelopes = str(data[0]['Vydané obálky'].values[0][0])
        list_of_envelopes.append((str(envelopes).encode("ascii", "ignore")).decode())
        valid = str(data[0]['Platné hlasy'].values[0][0])
        list_of_valid_votes.append((str(valid).encode("ascii", "ignore")).decode())
        
        for data_sub in range (1, len(data)):
            for hlasy in data[data_sub]['Platné hlasy']['celkem']:
                list_of_votes.append((str(hlasy).encode("ascii", "ignore")).decode())
    #Rozsekani listu hlasu na list listu hlasu
    a = 0
    b = len(list_of_parties)
    list_of_lists_of_votes = []
    for i in range(0, len(list_of_cities)):
        list_of_lists_of_votes.append(list_of_votes[a:b])
        a += len(list_of_parties)
        b += len(list_of_parties)
    #preskladani listu listu hlasu do jednoho listu aby odpovidal stranam
    new_list=[]
    for i in range(0, len(list_of_parties)):
        for y in list_of_lists_of_votes:
            new_list.append(y[i])
    #vytvoreni listu listu hlasu podle stran
    a = 0
    b = len(list_of_cities)
    list_of_lists_of_votes_sorted = []
    for i in range(0, len(list_of_parties)):
        list_of_lists_of_votes_sorted.append(new_list[a:b])
        b += len(list_of_cities)
        a += len(list_of_cities)

    #Skladani vystupnich dat
    data_for_output = {
        "code":list_of_city_numbers,
        "location":list_of_cities,
        "registered":list_of_registered,
        "envelopes":list_of_envelopes,
        "valid":list_of_valid_votes,
    }

    parties = {list_of_parties[i] : list_of_lists_of_votes_sorted[i] for i in range(0, len(list_of_parties))}
    data_for_output.update(parties)

    #Vystup do souboru
    filepath = P(f'output/{out}.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(data_for_output).to_csv(filepath, index=False, header=True)

if __name__ == '__main__':
    app()