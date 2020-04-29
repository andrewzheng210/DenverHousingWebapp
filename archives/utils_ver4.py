import os

try:
    import pandas as pd
except:
    os.system("pip install pandas")
    import pandas as pd
import json
try:
    import xgboost as xgb
except:
    os.system("pip3 install xgboost")
    import xgboost as xgb
try:
    import numpy as np
except:
    os.system("pip install numpy")
    import numpy as np

def load_files():
    city_data=pd.read_csv(r"CSVFiles/CityComparison.csv")
    city_data["Region"]=city_data["Region"].str.strip()
    city_seasonality=pd.read_csv(r"CSVFiles/CitySeasonality.csv")
    city_seasonality["City"]=city_seasonality["City"].str.strip()
    city_seasonality=city_seasonality.dropna()
    cities=set(city_data["Region"].unique()) and set(city_seasonality["City"].unique())
    cities=cities - set(["National","Colorado"])
    metrics=city_data.columns[3:]

    # neighborhood price data for city/neighborhood tab
    with open('JsonFiles/Neighborhoods.geojson') as geojson_file:    
        json_neighbor = json.load(geojson_file)
    neighbor_prices = pd.read_csv('CSVFiles/NeighborPrices.csv')
    neighbors = pd.read_csv('CSVFiles/Neighborhoods.csv')
    neighbor_prices = pd.merge(neighbor_prices, neighbors, left_on = 'NBHD_ID', right_on = 'NBHD_ID')
    neighbor_prices['SALE_PRICE'] = neighbor_prices['SALE_PRICE'].astype(float)
    with open('JsonFiles/NeighborhoodCenters.geojson') as geojson_file:    
        json_neighbor_centers = json.load(geojson_file)

    # single family data for single family tab
    with open('JsonFiles/SingleFamilyHouses.geojson') as geojson_file:    
        single_family = json.load(geojson_file)
    family_demo = pd.read_csv('CSVFiles/SingleFamilyDemo.csv')
    family_demo['AGE'] = family_demo['SALE_YEAR'] - family_demo['CCYRBLT']
    family_dist = pd.read_csv('CSVFiles/FamilyDistances.csv')
    nbhd_stats = pd.read_csv('CSVFiles/NeighborStatistics.csv').set_index('NBRHD_NAME')
    nbhd_stats = nbhd_stats.fillna(0)

    neighbor_centers = pd.read_csv('CSVFiles/NeighborhoodCenters.csv')
    neighbor_house_record = family_demo[['NBHD_ID', 'SALE_PRICE']].groupby(['NBHD_ID']).count().reset_index()
    neighbor_house_record = pd.merge(neighbor_house_record, neighbor_centers, left_on = 'NBHD_ID', right_on = 'NBHD_ID')

    metrics=np.append(metrics,["Seasonality of Median Price","Seasonality of Home Sold"])
    nbhd_stats["Park Coverage"]=(nbhd_stats["ParkA_SqM"]/nbhd_stats["Area_SqM"]*100).round(2)
    nbhd_stats["Tree Coverage"]=(nbhd_stats["TreesA_SqM"]/nbhd_stats["Area_SqM"]*100).round(2)
    nbhd_stats=pd.concat([nbhd_stats.iloc[:,3:11],nbhd_stats.iloc[:,[13,15,16]]],axis=1)
    nbhd_stats.reset_index(inplace=True)
    nbhd_stats.rename(columns={"StLights":"Street Lights","NBRHD_NAME":"Neighborhood",
                                        "TrAccident":"Traffic Accidents"},inplace=True)

    house_sold=family_demo[['NBHD_ID','SALE_YEAR','SALE_PRICE']].groupby(['NBHD_ID','SALE_YEAR'],
                                    as_index=False).count().rename(columns={"SALE_PRICE":"Home Sold"})
    neighbor_prices=neighbor_prices.merge(house_sold,on=['NBHD_ID','SALE_YEAR'])

    sectors={
        "Education":["Neighborhood","Libraries","Colleges","K12s"],
        "Shopping":["Neighborhood","FoodStores","Malls","Marijuana"],
        "Safety":["Neighborhood","Crimes","Traffic Accidents"],
        "Walkability":["Neighborhood","Street Lights","Park Coverage","Tree Coverage"]
    }

    return json_neighbor, neighbor_prices, json_neighbor_centers, single_family, neighbor_house_record, metrics, cities, city_data, family_dist, family_demo, city_seasonality, nbhd_stats, sectors

def draw_base_map(json_neighbor, neighbor_prices):
    return {
        'data': [{
            'type': "choroplethmapbox", 
            'geojson': json_neighbor,
            'locations': neighbor_prices[neighbor_prices['SALE_YEAR'] == 2019]['NBHD_NAME'].astype(str),
            'z': neighbor_prices[neighbor_prices['SALE_YEAR'] == 2019]['SALE_PRICE'],
            'name': '',
            'featureidkey': 'properties.NBHD_NAME',
            'marker': {'opacity': 0.8, 'line': {'color': 'white'}},
            'hovertemplate': "%{location} <br>Median Sale Price (2019): $%{z:,.f}",
            'colorbar':{
                'title': {'text': 'Neighborhood Median Sale Price 2019'}, 
                'x': 0}
            }],
    
        'layout': {
            'clickmode': 'event+select',
            'margin': {"r":10,"t":10,"l":10,"b":10},
            'height': 700,
            'hovermode': 'closest',
            'autosize': True,
            'mapbox': {
                'center': {'lat': 39.7114, 'lon': -104.9360},
                'zoom': 10.5,
                'style': 'carto-positron',                              
            },
        }
    }
# update house hunting map  
def update_house_base_map(sel_nbhd, json_neighbor, neighbor_house_record):
    return {
            'data': [{
                'type': "choroplethmapbox", 
                'geojson': json_neighbor,
                'locations': neighbor_house_record[neighbor_house_record['NBHD_NAME'] == sel_nbhd]['NBHD_NAME'].astype(str),
                'z': neighbor_house_record[neighbor_house_record['NBHD_NAME'] == sel_nbhd]['SALE_PRICE'] / 10.,
                'name': '',
                'featureidkey': 'properties.NBHD_NAME',
                'marker': {'opacity': 1.0, 'line': {'color': 'white'}},
                'hovertemplate': "%{location} <br>Annual Average Single Family House Sales: %{z:.0f}",   
                'showscale':False,   
                },

                {
                'type': "choroplethmapbox", 
                'geojson': json_neighbor,
                'locations': neighbor_house_record[neighbor_house_record['NBHD_NAME'] != sel_nbhd]['NBHD_NAME'].astype(str),
                'z': neighbor_house_record[neighbor_house_record['NBHD_NAME'] != sel_nbhd]['SALE_PRICE'] / 10.,
                'name': '',
                'featureidkey': 'properties.NBHD_NAME',
                'marker': {'opacity': 0.3, 'line': {'color': 'white'}},
                'hovertemplate': "%{location} <br>Annual Average Single Family Houses Sold: %{z:.0f}",
                'showscale': False,
                }],
        
            'layout': {
                'margin': {"r":10, "t": 0, "l":10,"b":10},
                'hovermode': 'closest',
                'autosize': True,
                'mapbox': {
                    'center': {'lat': 39.7114, 'lon': -104.9360},
                    'zoom': 11,
                    'style': 'carto-positron', 
                    'layers': [{
                        'source': json_neighbor,
                        'below': 'traces',
                        'type': "fill",     
                        'color': 'lightslategrey',
                        'opacity': 0.3,
                        'paint': {'line': {'color': 'white'}}
                    }],                              
                },
            }
        }

# initial house hunting map
def draw_house_base_map(json_neighbor, neighbor_house_record):
    return {
        'data': [
                {
                'type': "choroplethmapbox", 
                'geojson': json_neighbor,
                'locations': neighbor_house_record['NBHD_NAME'].astype(str),
                'z': neighbor_house_record['SALE_PRICE'] / 10.,
                'name': '',
                'featureidkey': 'properties.NBHD_NAME',
                'marker': {'opacity': 0.8, 'line': {'color': 'white'}},
                'hovertemplate': "%{location} <br>Annual Average Single Family Houses Sold: %{z:.0f}",
                'showscale': False,
                }
            #{
            #'type': "scattermapbox", 
            #'lon': neighbor_house_record['Lon'],
            #'lat': neighbor_house_record['Lat'],
            #'text': neighbor_house_record['NBHD_NAME'] + '<br>' + 'Annual Average Houses Sold: ' + neighbor_house_record['SALE_PRICE'].apply(lambda x: round(x/10.)).astype(str),
            #'hoverinfo': 'text',
            #'mode': 'markers',
            #'opacity': 0,
            #}
            ],
    
        'layout': {
            'margin': {"r":10, "t": 0, "l":10,"b":10},
            'hovermode': 'closest',
            'autosize': True,
            'mapbox': {
                'center': {'lat': 39.7114, 'lon': -104.9360},
                'zoom': 11,
                'style': 'carto-positron',      
                'layers': [{
                    'source': json_neighbor,
                    'below': 'traces',
                    'type': "fill",     
                    'color': 'lightslategrey',
                    'opacity': 0.4,
                    'paint': {'line': {'color': 'white'}}
                }],                 
            },
        }
    }
