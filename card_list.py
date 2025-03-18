import asyncio
from pyppeteer import launch
from random import randint
from time import sleep
import re
import json
from bs4 import BeautifulSoup

async def setup_browser():
    browser = await launch({
        "headless": False,
         'defaultViewport' : { 'width' : 400, 'height' : 2000 }
        })
    page = await browser.newPage()
    page.setDefaultNavigationTimeout(10 * 60 * 1000)
    return(browser, page)

async def format_card(card):
    new_card = {}
    if "特殊ハート" in card:
        card.pop("特殊ハート")
    for key in card.keys():
        if key == "title":
            new_card["title"] = card[key]
        if key == "img":
            new_card["img"] = card[key]
        if key == "txt":
            new_card["txt"] = card[key]
        if key == "カードタイプ":
            new_card["type"] = card[key]
        if key == "コスト":
            new_card["cost"] = card[key]
        if key == "ブレード":
            new_card["blades"] = card[key]
        if key == "tokushu":
            new_card["tokushu"] = card[key]
        if key == "hearts":
            new_card["hearts"] = card[key]
        if key == "blade_h":
            new_card["blade_h"] = card[key]
        if key == "収録商品":
            new_card["origin"] = card[key]
        if key == "作品名":
            new_card["series"] = card[key]
        if key == "レアリティ":
            new_card["rarity"] = card[key]
        if key == "カード番号":
            new_card["code"] = card[key]
        if key == "参加ユニット":
            new_card["unit"] = card[key]
    return(new_card)

async def scrape():
    with open("card_codes.json") as file:
        data = json.load(file)

    browser, page = await setup_browser()
    url = "https://llofficial-cardgame.com/cardlist"

    card_list = []

    for category in data:
        for code in data[category]:
            card = {}

            await page.goto(f"{url}/searchresults/?cardno={code}")
            await page.waitForSelector(".info-Image")
            await asyncio.sleep(randint(3, 6))
            html = await page.content()

            soup = BeautifulSoup(html, 'html.parser') 
            soup = soup.find('div', class_='cardlist-Item cardlist-Info active')

            # attributes every card has
            card["title"] =  soup.find("p", class_="info-Heading").get_text()
            card["img"] = url + soup.find("div", class_="image").find("img")["src"]

            # these differ depending on card (special heart for live cards, no heart field on energy cards etc)
            txt = soup.find("p", class_="info-Text")
            
            if txt:
                formatted_txt = ""
                for e in txt:
                    if "alt=" in str(e):                 
                        alt = re.search('alt="(.*)" c', str(e)).group(1)  
                        formatted_txt += f"[{alt}] "
                    else:
                        formatted_txt += e.get_text()
                card["txt"] = formatted_txt

            info = soup.find("dl", class_="info-Dl").find_all("div")

            for dl in info:
                hearts = [0, 0, 0, 0, 0, 0, 0]
                blade_heart = [0, 0, 0, 0, 0, 0, 0]
                # only the tokushu heart field uses images
                if dl.find("img"):
                    card["tokushu"] = dl.find("img")["alt"]
                # for majority of info fields
                if len(dl.find_all("span")) == 1:
                    card[dl.find("span").get_text()] = dl.find("dd").get_text()
                # for hearts
                elif dl.find_all("span")[-1]["class"][-1][0] != 'b':
                    for heart in dl.find_all("span")[1:]:
                        hearts[int(heart["class"][-1][-1])] = int(heart.get_text())
                        card["hearts"] = hearts
                # for blade heart
                else:
                    if dl.find_all("span")[-1]["class"][-1][-1] != 'l':
                        blade_heart[int(dl.find_all("span")[-1]["class"][-1][-1])] = 1
                    else:
                        blade_heart[0] = 1
                    card["blade_h"] = blade_heart

            card = await format_card(card)
            card_list.append(card)

    await browser.close()
    with open("card_list.json", 'w') as file:
        json.dump(card_list, file)

asyncio.run(scrape())


            

    