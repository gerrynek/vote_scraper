```
author: Jaroslav List 

email: jaroslav.list@kiwi.com 

discord: Jara#4939
```

Scraper for volby.cz that returns .csv file with results for the cities

How to start the script:
1) Install requirements:
```
pip install -r requirements.txt
```
2) Example:
```
python main.py --url 'https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2104' --output konecne_hotovo
```
```
The output .csv file will be generated to /output folder 

--url <URL of the site from volby.cz you want to scrape> | required

--output <name of the output file> | required
```