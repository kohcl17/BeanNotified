import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st

@st.cache_data
def get_products(url, platform = "Shopify"):
    req = requests.get(url)
    req_status = req.status_code

    if req_status == 200:
        jsonReq = req.json()
        if platform == "Shopify":
            if "products" not in jsonReq.keys():
                products = {}
            else:
                products = jsonReq['products']
        elif platform == "Squarespace":
            if "items" not in jsonReq.keys():
                products = {}
            else:
                products = jsonReq['items']
    else:
        products = {}
    return products


# Wix and Woocommerce are special and needs its own method of scraping bc god knows
@st.cache_data
def build_url(link, platform = "Shopify"):
    if platform == "Shopify":
        productJson = link + "/products.json"
    elif platform == "Squarespace":
        productJson = link + "/?format=json"
    elif platform == "Wix":
        productJson = link
    else:
        productJson = link
    return productJson

def extract_flavor_notes(text, profile):
    # join the list of profiles to search for
    keywords = "|".join(profile)

    # Find all matches in the text
    matches = re.findall(keywords, text, re.IGNORECASE)
    return matches

@st.cache_data
def get_product_details(storeJsonProducts, platform = "Shopify"):
    all_products = pd.DataFrame()
    if platform == 'Shopify':
        for k,v in storeJsonProducts.items():
            if v.shape[0] != 0:
                title = v.title
                excerpt = v.body_html
                clean_excerpt = [BeautifulSoup(a, "html.parser").get_text() for a in excerpt]
                subdataset = pd.DataFrame(data = {"store": k,
                                                "product": title,
                                                "description": clean_excerpt
                                                })
            else:
                subdataset = pd.DataFrame()
            all_products = pd.concat([all_products, subdataset], axis = 0)
    
    elif platform == "Squarespace":
        for k,v in storeJsonProducts.items():
            if v.shape[0] != 0:
                title = v.title
                excerpt = v.excerpt
                clean_excerpt = [BeautifulSoup(a, "html.parser").get_text() for a in excerpt]
                subdataset = pd.DataFrame(data = {"store": k,
                                                "product": title,
                                                "description": clean_excerpt
                                                })
            else:
                subdataset = pd.DataFrame()
            all_products = pd.concat([all_products, subdataset], axis = 0)
    
    all_products = all_products.reset_index(drop = True)
    return all_products

def parse_image(url):
    response = requests.get(url)
    img = np.array(Image.open(BytesIO(response.content)).convert('L'))
    text = reader.readtext(img)
    text_confident = [t for bbox, t, prob in text if prob > 0.5]
    return text_confident

def parse_text_input(textIn):
    return textIn.strip().split(",")