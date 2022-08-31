from bs4 import BeautifulSoup
from matplotlib.pyplot import text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from msedge.selenium_tools import EdgeOptions, Edge
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import folium
import requests
from folium.plugins import MarkerCluster
import pandas as pd
from lxml import etree
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import numpy as np
from branca.element import Figure
start = time.time()
dep = 44
url = f"http://annuairesante.ameli.fr/trouver-un-professionnel-de-sante/chirurgiens-dentistes/{dep}-loire-atlantique"
base_url = "http://annuairesante.ameli.fr"

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
a_href = soup.findAll('a')

list_url_ville = []
list_ville = []
a_href = a_href[3:-6]
for link in a_href:
    if link.has_attr('href'):
        list_url_ville.append(link['href'])
        list_ville.append(link.text)


def get_liste_detail_praticiens(details_praticiens):
    for i in range(len(list_url_ville)):
        response_name = requests.get(base_url + list_url_ville[i])
        soup_name = BeautifulSoup(response_name.text, 'html.parser')
        a = soup_name.find('h2').find('a', href=True)
        details_praticiens.append(a['href'])
        
details_praticiens=[]
get_liste_detail_praticiens(details_praticiens)   

def get_actes_tarifications(details_praticiens):
    listes_tarif_actes=[]
    url = base_url + details_praticiens
    options = EdgeOptions()
    options.use_chromium = True
    options.add_argument("--headless")
    options.add_argument("disable-gpu")

    browser = webdriver.Chrome(
        executable_path="msedgedriver.exe",options=options)
    browser.get(url)
    actes=WebDriverWait(browser, 10).until(EC.visibility_of_all_elements_located(
        (By.XPATH, "//div[@class='bloc-gris-inner']/h3")))
    tarif=WebDriverWait(browser, 10).until(EC.visibility_of_all_elements_located(
        (By.XPATH, "//div[@class='valeur']/strong")))
    #horraire=WebDriverWait(browser, 10).until(EC.visibility_of_all_elements_located(
      # (By.XPATH, "//table[@class='tableau-cabinet']/tbody/tr")))
    for i in range(len(actes)):
        actes_tarifs = {}
        actes_tarifs['actes'] = actes[i].text
        actes_tarifs['prix'] = tarif[i].text
        listes_tarif_actes.append(actes_tarifs)
    
    return listes_tarif_actes
    
  
def get_praticien_ville(ville, url):
    k=0
    l=0
    for i in range(len(details_praticiens)):
        response_name = requests.get(base_url + url[i])
        soup_name = BeautifulSoup(response_name.text, 'html.parser')
        name = soup_name.findAll('a')
        adress = soup_name.findAll(class_='item left adresse')#soup_name.findAll(class_="item left adresse")
        
        # contient le nom et le prenom de tous les praticiens de la ville
        name_clean = [] 
        for n in name:
            if n.strong:
                name_clean.append(n)
                
        # liste des informations des praticiens de la ville: nom, adresse et ville
        list_info_praticiens = []
        liste_adresse=[]
        for line_break in adress:
                    words = line_break.getText(
                        separator='|br|', strip=True).split('|br|')
                    words = words[1:]
                    str1 = ','.join(words)
                    liste_adresse.append(str1)
        #print(liste_adresse)
       
        for j in range(len(name_clean)):
            
            info_praticiens = {}        
            info_praticiens['nom'] = name_clean[j].text
            info_praticiens['adress'] =liste_adresse[j]
            info_praticiens['ville'] = ville[3]
            info_praticiens['actes_et_prix']=get_actes_tarifications(details_praticiens[l+j])
            list_info_praticiens.append(info_praticiens)
            k=j
        l=l+k
    return list_info_praticiens


all_praticiens = [] 
praticiens = get_praticien_ville(list_ville, list_url_ville)
all_praticiens.extend(praticiens)
#print("all_praticiens",all_praticiens)
df = pd.DataFrame(all_praticiens)
end = time.time()
print(df)
print("time= ", format(end-start))