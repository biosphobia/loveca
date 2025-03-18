import asyncio 
from pyppeteer import launch 
from bs4 import BeautifulSoup
import json

async def setup_browser():
    browser = await launch({
        "headless": False,
         'defaultViewport' : { 'width' : 400, 'height' : 2000 }
        })
    page = await browser.newPage()
    page.setDefaultNavigationTimeout(10 * 60 * 1000)
    return(browser, page)

async def parse_html(page):
    html = await page.content()
    soup = BeautifulSoup(html, 'html.parser') 
    return soup

async def get_card_products():
    url = "https://llofficial-cardgame.com"
    links = []

    browser, page = await setup_browser()
    await page.goto(f"{url}/cardlist")
    html = await parse_html(page)
    for a in html.find_all("a", class_="productsList-Item"):
        links.append(url + a["href"])

    await browser.close()
    return links

async def get_card_codes():
    links = await get_card_products()
    codes = []
    categories = {}

    browser, page = await setup_browser()
    
    for url in links:
        await page.goto(url)
        html = await parse_html(page)
        title = html.find(class_="result-Heading").get_text()
        print(title)
        count = int(html.find(class_="search-Hits").find("span").get_text())

        cards = []
        while (len(cards) < count):
            await page.hover(".st-Footer")
            html = await parse_html(page)
            for c in html.find_all(class_="cardlist-Result_Item"):
                if c["card"] not in cards:
                    cards.append(c["card"])
            await page.hover(".search-Hits")
        categories[title] = cards
        print(categories)

    with open('card_codes.json', 'w') as fp:
        json.dump(categories, fp)

    await browser.close()
        

asyncio.run(get_card_codes())