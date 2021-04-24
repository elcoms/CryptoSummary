from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import lxml.html as lxml
import requests
import pathlib
import json
import time
import os

currentFilePath = pathlib.Path(__file__).parent.absolute()

cmc = requests.get('https://coinmarketcap.com')
soup = BeautifulSoup(cmc.content, 'html.parser')

data = soup.find('script', id="__NEXT_DATA__", type="application/json")

coins = {}
 
# using data.contents[0] to remove script tags
coin_data = json.loads(data.contents[0])
listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']

with open('coins.txt', 'w') as f:
    for list in listings:
        coins[str(list['id'])] = list['slug']
        f.write(list['slug'] + "\n")

def GetCoinPageSource(coin):
    
    try:
        browser = webdriver.Chrome(executable_path= currentFilePath / "chromedriver")
        browser.get(f"https://coinmarketcap.com/currencies/{coin}/historical-data/")
        page = browser.page_source
    except:
        print("[CMCscraper] Unexpected error:", sys.exc_info()[0])
        page = None
    finally:
        browser.quit()
    
    return page

def ScrapePage(page_source):
    doc = lxml.fromstring(page_source)
    data = doc.xpath('//tr')

    dataList = []
    i=0

    for header in data[0]:
        i+=1
        name = header.text_content()
        # print('%d : %s' % (i,name))
        dataList.append((name, []))

    for i in range(1, len(data)):
        row = data[i]

        j=0
        for element in row:
            text = element.text_content()
            try:
                text = int(text)
            except:
                pass

            dataList[j][1].append(text)
            j+=1

    dataDict = {title:column for (title, column) in dataList}
    return dataDict

def ScrapeAll(folderpath=currentFilePath / "data"):
    
    browser = webdriver.Chrome(executable_path=currentFilePath / 'chromedriver')

    for coin in coins.values():
        # browser.get(f"https://coinmarketcap.com/currencies/{coin}/historical-data/")
        # data = ScrapePage(browser.page_source)
        # WriteToFile(data, folderpath, coin)
        print(coin)
    
    browser.quit()

def WriteToFile(data, folderpath, filename):
    df = pd.DataFrame(data)
    folderpath.mkdir(parents=True, exist_ok=True)
    filename += ".csv"
    df.to_csv(folderpath / filename, index=False)

# test case
# dataDict = ScrapePage(GetCoinPageSource("bitcoin"))
# WriteToFile(dataDict, pathlib.Path(__file__).parent.absolute() / "data", "sample")