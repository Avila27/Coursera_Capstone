# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 12:21:27 2019
@author: H305128
References
----------
Data & The World: https://www.dataandtheworld.com/2017/06/20/scraping-wikipedia-tables-python-r/
"""

from bs4 import BeautifulSoup
import pandas as pd
import requests

pd.options.display.max_columns = 20

#WIKI_PAGE = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
WIKI_PAGE = 'https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'

# Grab the page HTML and get the list of rows for the table
req = requests.get(WIKI_PAGE)
page_html = BeautifulSoup(req.text, 'lxml')
wiki_table = page_html.find('table', attrs = {'class':'wikitable sortable'})
row_list = wiki_table.find_all('tr')

# First row in the table is the header, so extract that separately
header_row = row_list.pop(0)
header_th = header_row.find_all('th')
header = [el.text for el in header_th]

table_dict = {x:[] for x in header}

# Now for the rest of the table...
for row in row_list:
    row_td = row.find_all('td')
    for el,td in zip(header,row_td):
        table_dict[el].append(td.text)

df = pd.DataFrame(table_dict)
#print(df.head())

## Clean dataframe
df['Neighbourhood\n'] = df['Neighbourhood\n'].str.replace('\n','')

## Replaces \n's
df.columns = df.columns.str.replace('\n','')

## Filter Not assigned Boroughs
df2 = df[df['Borough'] != 'Not assigned']

## Group Neighbourhoods with same Postal Code
df3 = df2.groupby(['Postcode','Borough'])['Neighbourhood'].apply(', '.join).reset_index()

def CheckNeihgborhood(x):
    if x['Neighbourhood'] == 'Not assigned':
        x['Neighbourhood'] = x['Borough']
    else:
        x['Neighbourhood']
    return x['Neighbourhood']

## Assign Neighbourhood = Borough if Neighbourhood have Not assigned labels
df3['Neighbourhood'] = df3.apply(CheckNeihgborhood, axis=1)


print (df3.head())
### Add lattitde and longitude

import geocoder # import geocoder

#g = geocoder.arcgis('Scarborough, ON M1B')
#g.latlng

# Test to create Latitude and Longitude Columns

dfTest = df3.iloc[:10]

Borough = 'Etobicoke'
Postcode = 'M9W'


def GetCoord(Borough,Postcode):
    g = geocoder.arcgis('{}, ON {}'.format(Borough,Postcode))
    lat_long_coords = g.latlng
    return lat_long_coords

df3['LatLong'] = df3.apply(lambda x: GetCoord(x['Borough'],x['Postcode']), axis=1)
df3[['Lattitude','Longitude']] = pd.DataFrame(df3['LatLong'].values.tolist())
df3 = df3.drop('LatLong', 1)

print (df3.head(10))


