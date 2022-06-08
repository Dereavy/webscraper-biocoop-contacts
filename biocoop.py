# IMPORTS utiles
# La librairie BeautifulSoup sera reference par "bs" 
from bs4 import BeautifulSoup as bs

import datetime
import requests

import json

import csv

# Librairie pour faire des recherches par utilisation d'expression reguliere : "RegEx" (trouver le numero de tel ou mail dans une div)
import re

# Variables
regex_tel = re.compile("(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$")
regex_mail = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
url_biocoop="https://www.biocoop.fr/magasins-bio/Trouver-mon-magasin-Biocoop?postal_code=&region=&department=&page=1&ajax=1"
url_test_business = "https://www.biocoop.fr/magasins-bio/Trouver-mon-magasin-Biocoop/Pays-de-la-Loire/Sarthe/ALTERRE-NATIVE"

# Afficher la date du jour (optionelle)
today = datetime.date.today()
print("Date: "+str(today))

# Declaration de FONCTIONS
# Check pagination ajax pour trouver le nombre de pages maximum
def getPageAmount(url):
	print("Fetching page amount: "+ url)
	pages = []
	r = requests.get(url)
	soup = bs(r.text, 'html.parser')
	pagination = soup.find('div',class_="pagination").findChildren()
	for page in pagination:
		pages.append(page.text)
	return pages[-3]

# Recupere la liste des liens des differents biocoops sur une page
def getLinks(url):
	print("Fetching links in listing: "+ url)
	links = []
	r = requests.get(url)
	soup = bs(r.text, 'html.parser')
	results = soup.find_all('div',class_="result_row")
	for link in results:
		if link.a.has_attr('href'):
			# print(link.a['href'])
			links.append(link.a['href'])
	return links

# Fait un liste de toutes les pages
def getListings(amount):
	print("Fetching listings...")
	links = []
	for page in range(0,int(amount)):
		link = "https://www.biocoop.fr/magasins-bio/Trouver-mon-magasin-Biocoop?postal_code=&region=&department=&page={}&ajax=1".format(page)
		links.append(link)
	return links

# Recupere la liste de tout les urls des pages business en ligne 
def getFullList(url_biocoop):
	amount = getPageAmount(url_biocoop)
	listings = getListings(amount)
	full_list = []
	for listing in listings:
		links = getLinks(listing)
		full_list.extend(links)
	return full_list

# Sauvegarde de la liste, genere un document "liens.json" contenant tout les liens.
def saveFullList():
	liste = getFullList(url_biocoop)
	with open('liens.json', 'w') as outfile:
    		json.dump(liste, outfile)
    		
# Recupere la liste de tout les urls des pages business sauvegardees dans le json (nomme liens.json si aucun nom specifie)
def getFullListJson(full_list='liens.json'):
	with open(full_list) as json_file:
	    liste = json.load(json_file)
	    return liste

# Extraction des informations du lien business biocoop
def getBusinessInfo(url):
	print ("Scraping: "+url)
	business = {}
	r = requests.get(url)
	soup = bs(r.text, 'html.parser')
	store = soup.find('div',id="store_detail")
	# ".get_text(strip=True)" sur un element de beautifulsoup enleve les "\n\t"
	business['url'] = url
	try:
		business['name'] = store.find('h1',itemprop="name").get_text(strip=True)
	except:
		business['name'] = None;
		print("NO_NAME: "+url)
	try:
		business['adresse'] = store.find('p', class_="adresse").get_text(strip=True)
	
	except:
		business['adresse'] = None;
		print("NO_ADRESSE: "+url)
	try:
		business['tel'] = store.find('li',text=regex_tel).get_text(strip=True)
	except:
		business['tel'] = None;
		print("NO_TEL: "+url)
	try:
		business['mail'] = store.find('a',class_="ezemail-field").get_text(strip=True)                
	except:
		business['mail'] = None;
		print("NO_MAIL: "+url)
	return business

# Cree un json avec les informations des business biocoop
def getAllBusinesses():
	businesses = []
	business_list = getFullListJson()
	for business in business_list:
		data = getBusinessInfo(business)
		businesses.append(data)
	return businesses
	
# Mettre toutes les infos dans un JSON
def saveAllBusinessesJson():
	liste = getAllBusinesses()
	with open('biocoops.json', 'w') as outfile:
    		json.dump(liste, outfile)
    		
# Example d'extraction des informations dans le json :
def showAllBusinessesJson():
	with open('biocoops.json') as json_file:
	    biocoops = json.load(json_file)
	    for biocoop in biocoops:
	    	print("Nom: "+str(biocoop['name']))
	    	print("Tel: "+str(biocoop['tel']))
	    	print("Adr: "+str(biocoop['adresse']))
	    	print("Url: "+str(biocoop['url']))
	    	print("====")
 
def getAllBusinessesJson(full_list='biocoops.json'):
	with open(full_list) as json_file:
	    data = json.load(json_file)
	    return data
	
def createBiocoopsCSV():
	json_data = getAllBusinessesJson()
	
	# csv header
	fieldnames = ['name', 'adresse', 'tel', 'mail', 'url']

	# csv data
	rows = json_data

	with open('biocoops.csv', 'w', encoding='UTF8', newline='') as f:
	    writer = csv.DictWriter(f, fieldnames=fieldnames)
	    writer.writeheader()
	    writer.writerows(rows)


# TESTS
# Tester le scraper sur une url d'un business
#getBusinessInfo(url_test_business)
# Montrer le contenu du json dans la ligne de commande
#showAllBusinessesJson()

# INITIALISATION, creation des bases de donnees en JSON:
# 1. Lancer saveFullList()
# 2. Lancer saveAllBusinessesJson()
# 3. Lancer createBiocoopsCSV()

#saveFullList()
#saveAllBusinessesJson()
#createBiocoopsCSV()

