import requests
import re
from bs4 import BeautifulSoup

def getSize (soup):
    tabSizeSoup = soup.find_all("option", {"data-pre-order": "0"})
    tabSize = []

    for elt in tabSizeSoup:
        elt = str(elt)
        if elt.find("data-sold-out=\"false\"") > 0:
            match = re.search(r'data-qualifier-value=\"\d*\.?\d*', elt)
            tabSize.append(match.group(0)[22:])
    return (tabSize)

def getImg (soup):
    imgSoup = soup.find_all("div", {"class": "product-gallery"})
    tabImgSoup = str(imgSoup).split("\n")
    tabImg = []

    for elt in tabImgSoup:
        elt = str(elt)
        match = re.search(r'src=\".*\"', elt)
        if match :
            tabImg.append(match.group(0)[5:len(match.group(0)) - 1])
    return (tabImg)

def getPrice (soup):
    priceSoup = soup.find("meta", itemprop="price")
    match = re.search(r'content=\"\d*\.?\d*\"', str(priceSoup))
    return(str(match.group(0))[9:len(match.group(0)) - 1])

def getDescription (soup):
    descrSoup = soup.find("p", itemprop="description")
    tmp = str(descrSoup)[26:len(str(descrSoup)) - 4]
    tmp = tmp.replace("<br/>", '')
    return (tmp)

def getProductID (soup):
    productIdSoup = soup.find("span", itemprop="productID")
    return (str(productIdSoup)[27:len(str(productIdSoup)) - 7])

def getName (soup):
    nameSoup = soup.find("h1", itemprop="name")
    return (str(nameSoup)[20:len(str(nameSoup)) - 5])

def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return (TAG_RE.sub('', text))

def getDetails(soup):
    detailsSoup = str(soup.find("div", {"id": "accordion_container"}))
    detailsTab = remove_tags(detailsSoup).split("\n\n")
    for i in range(len(detailsTab)):
        if detailsTab[i] == '':
            continue
        if detailsTab[i][0] == '\n':
            detailsTab[i] = detailsTab[i][1:]
        detailsTab[i] = detailsTab[i].replace('\xa0', '')
        detailsTab[i] = detailsTab[i].replace('\n', '')
    count = detailsTab.count('')
    while count > 0:
        detailsTab.remove('')
        count -= 1
    json = "{"
    title = True
    for elt in detailsTab:
        json += '"' + elt + '"'
        if title == True:
            json += ":"
            title = False
        else:
            json += ','
            title = True
    json = json[:len(json) - 1]
    json += "}"
    return (json)

def getNewItem (url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    listImg = getImg(soup)
    listImg.pop(0)
    # product_id | url | name | picture_url | alternate | price | price_old | description | sizes | details
    ret = getProductID(soup) + '|' + \
            url + '|' + \
            getName(soup) + '|' + \
            getImg(soup)[0] + '|' + \
            str(listImg) + '|' + \
            getPrice(soup) + '|' + \
            getDescription(soup) + '|' + \
            str(getSize(soup)) + '|' + \
            getDetails(soup) + '\n'
    return (ret)

def allURL (url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    urlSoup = soup.find_all("meta", {"itemprop": "url"})

    listUrl = []
    for elt in urlSoup:
        listUrl.append(str(elt)[15:len(str(elt)) - 18])
    return (listUrl)

def getCSV ():
    urls = ['https://www.fendi.com/fr/femme/sacs-femme', \
            'https://www.fendi.com/fr/femme/pret-a-porter-femme', \
            'https://www.fendi.com/fr/femme/chaussures-femme', \
            'https://www.fendi.com/fr/femme/women-039-s-accessories', \
            'https://www.fendi.com/fr/homme/sacs-homme', \
            'https://www.fendi.com/fr/homme/pret-a-porter-homme', \
            'https://www.fendi.com/fr/homme/chaussures-homme', \
            'https://www.fendi.com/fr/homme/men-039-s-accessories', \
            'https://www.fendi.com/fr/vetements-et-accessoires-de-luxe-enfants-fendi<br->/baby/baby-view-all', \
            'https://www.fendi.com/fr/kids/junior-boys/junior-boys-view-all', \
            'https://www.fendi.com/fr/kids/junior-girls/junior-girls-view-all']
    txt = ""
    for url in urls:
        listUrl = allURL(url)
        for elt in listUrl:
            txt += getNewItem(elt)
    with open('fendi.csv', 'w') as my_csv:
        my_csv.write(txt)

getCSV()

