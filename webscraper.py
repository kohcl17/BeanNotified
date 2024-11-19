import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import streamlit as st

# # OCR for tasting notes (if applicable)
# from PIL import Image
# import numpy as np
# from io import BytesIO
# import easyocr

# reader = easyocr.Reader(['en'])

from coffee_utils import *

####################
# Backend scraping #
####################

# Initial website list
SGcoffee = pd.read_csv("./sg_coffee_websites.txt", delimiter= "\t", index_col = 0)

# Parse shopify
shopify_sites = SGcoffee[SGcoffee.Platform == "Shopify"]

shopifyJsonLink = {}
shopifyJsonProducts = {}
for s in shopify_sites.index:
    parseLink = build_url(shopify_sites.loc[s, "Link"])
    shopifyJsonLink[s] = parseLink
    listing = get_products(parseLink)
    shopifyJsonProducts[s] = pd.DataFrame.from_dict(listing)

all_shopify_products = get_product_details(shopifyJsonProducts, platform="Shopify")

# Squarespace
sqspace_sites = SGcoffee[SGcoffee.Platform == "Squarespace"]

sqspaceJsonLink = {}
sqspaceJsonProducts = {}
for i in sqspace_sites.index:
    jlnk = build_url(sqspace_sites.loc[i, "Link"], platform="Squarespace")
    sqspaceJsonLink[i] = jlnk
    pdt = get_products(jlnk, platform="Squarespace")
    sqspaceJsonProducts[i] = pd.DataFrame.from_dict(pdt)

all_squarespace_products = get_product_details(sqspaceJsonProducts, platform="Squarespace")

all_data = pd.concat([all_shopify_products, all_squarespace_products], axis=0)
all_data = all_data.reset_index(drop=True)
all_data.description = all_data.description.str.replace("\n", "<br>")

####################
## USER INTERFACE ##
####################

st.header("BeanNotified")
# ask for user input
userFlavourInput = st.text_area("Enter comma-separated flavour notes here", 
                                help = "The results will contain any of the notes entered here"
                                )

matches_found = pd.DataFrame()
for i in all_data.index:
    text = all_data.loc[i, "description"]
    matches = extract_flavor_notes(text, parse_text_input(userFlavourInput))
    if len(matches) > 0:
        matches_found = pd.concat([matches_found, all_data.iloc[[i]]], axis = 0)

st.subheader("Here are your matches!")
st.markdown(matches_found.to_html(escape=False), unsafe_allow_html=True)