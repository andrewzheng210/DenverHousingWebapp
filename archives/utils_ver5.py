import os
from itertools import product

try:
    import numpy as np
except:
    os.system("pip install numpy")
    import numpy as np
    
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


#############################################
####### xgboost model data structure ########
#dfx_lr = dfx[['AGE', 'AREA_ABG', 'AVG_HH_INC', 'BACHELORSO', 'BED_RMS', 
          #    'Colleges', 'Crimes', 'DrugDist', 
          #    'FoodStores', 'GRD_AREA', 'BATH_RMS', 'Intersects', 
          #    'K12s', 'LAND_SQFT', 'LESSTHANHS', 'Libraries', 'Malls', 'Marijuana', 
          #    'MaxPctRace', 'PCT_AGE65P', 'PCT_AGELES', 'PER_CAPITA', 'PCT_VAC', 'PER_COMM', 'ParkDist', 
          #    'Park_Coverage', 'SALE_MONTH', 'SALE_YEAR', 'STORY', 
          #    'StLights', 'StoreDist', 'TrAccident', 'Tree_Coverage']]
##############################################

def predict_house_xgb(neighbor, bed, bath, story, age, minarea, maxarea, minlot, maxlot, park, store, month, neighbor_stats, neighbor_demo):
    nbhd_name, beds, baths, storys, ages, parks, stores, months = '', [], [], [], [], [], [], []
    predict_tab=[]

    if neighbor is None:
        nbhd_name = 'Athmar Park'
    else:
        nbhd_name = neighbor

    if bed is None:
        beds = [2, 3]
    else:
        beds.append(bed)
    
    if bath is None:
        baths = [1, 2]
    else:
        baths.append(bath)
    
    if story is None:
        storys = [1, 2]
    else:
        storys.append(story)
    
    if age is None:
        ages = [0, 10]
    else:
        ages = [int(i) for i in age.split('-')]
    
    if minarea is None:
        minarea = 600
    if maxarea is None:
        maxarea = 10000
    if minlot is None:
        minlot = 600
    if maxlot is None:
        maxlot = 15000

    areas = [minarea, maxarea]
    lots = [minlot, maxlot]
    drugs = [2500]

    if park is None:
        parks = [500, 2500]
    else:
        parks.append(park)
    
    if store is None:
        stores = [500, 2500]
    else:
        stores.append(store)

    grns = [0, 500]
    year = [2020]

    if month is None:
        months = [6]
    else:
        months = [month]

    stats = neighbor_stats[neighbor_stats['NBRHD_NAME'] == nbhd_name]
    demo = neighbor_demo[neighbor_demo['NBHD_NAME'] == nbhd_name]

    avg_hh_inc, bachelorso, lessthanhs, maxpctrace, pctage65p, pctageless = demo['AVG_HH_INC'].values, demo['BACHELORSO'].values, demo['LESSTHANHS'].values, demo['MaxPctRace'].values, demo['PCT_AGE65P'].values, demo ['PCT_AGELES'].values
    per_capita, pct_vac, pct_comm = demo['PER_CAPITA'].values, demo['PCT_VAC'].values, demo['PER_COMM'].values

    colleges, crimes, foodstores, intersects, k12s, libraries = stats['Colleges'].values, stats['Crimes'].values, stats['FoodStores'].values, stats['Intersects'].values, stats['K12s'].values, stats['Libraries'].values
    malls, marijuana, stlights, traffic = stats['Malls'].values, stats['Marijuana'].values, stats['StLights'].values, stats['TrAccident'].values
    parkcover, treecover = stats['ParkA_SqM'].values, stats['TreesA_SqM'].values

    sel_columns = ['Story', 'Bedrooms', 'Bathrooms', 'Age of House (yrs)', 'Above Ground Area (sqft)', 'Lot Size (sqft)', 'Garden Area (sqft)' ,'Distance to Park (meters)', 'Distance to Food Stores (meters)', 'Predicted Price ($)']
    columns = ['AGE', 'AREA_ABG', 'AVG_HH_INC', 'BACHELORSO', 'BED_RMS', 
                'Colleges', 'Crimes', 'DrugDist', 
                'FoodStores', 'GRD_AREA', 'BATH_RMS', 'Intersects', 
                'K12s', 'LAND_SQFT', 'LESSTHANHS', 'Libraries', 'Malls', 'Marijuana', 
                'MaxPctRace', 'PCT_AGE65P', 'PCT_AGELES', 'PER_CAPITA', 'PCT_VAC', 'PER_COMM', 'ParkDist', 
                'Park_Coverage', 'SALE_MONTH', 'SALE_YEAR', 'STORY', 
                'StLights', 'StoreDist', 'TrAccident', 'Tree_Coverage']

    list_of_values = list(product(ages, areas, avg_hh_inc, bachelorso, beds, 
                                colleges, crimes, drugs, 
                                foodstores, grns, baths, intersects, 
                                k12s, lots, lessthanhs, libraries, malls, marijuana, 
                                maxpctrace, pctage65p, pctageless, per_capita, pct_vac, pct_comm, parks, 
                                parkcover, months, year, storys,
                                stlights, stores, traffic, treecover))

    x_pred = pd.DataFrame(list_of_values, columns = columns)
    xgb_model = xgb.Booster()
    xgb_model.load_model('models/model_xgb_regressor.model')
    y_pred = xgb_model.predict(xgb.DMatrix(x_pred.values))
    
    predict_df = x_pred.copy()
    predict_df['Predicted Price'] = np.round(y_pred)
    predict_df['Neighborhood'] = nbhd_name

    predict_tab = predict_df[['STORY', 'BED_RMS', 'BATH_RMS', 'AGE', 'AREA_ABG', 'LAND_SQFT', 'GRD_AREA', 'ParkDist', 'StoreDist', 'Predicted Price']]
    predict_tab.columns = sel_columns

    return predict_tab

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
        json_single_family = json.load(geojson_file)
    family_demo = pd.read_csv('CSVFiles/SingleFamilyDemo.csv')
    family_demo['AGE'] = family_demo['SALE_YEAR'] - family_demo['CCYRBLT']
    family_dist = pd.read_csv('CSVFiles/FamilyDistances.csv')
    neighbor_stats = pd.read_csv('CSVFiles/NeighborStatistics.csv')
    neighbor_stats = neighbor_stats.fillna(0)
    neighbor_demo = pd.read_csv('CSVFiles/NeighborDemo.csv')

    neighbor_centers = pd.read_csv('CSVFiles/NeighborhoodCenters.csv')
    neighbor_house_record = family_demo[['NBHD_ID', 'SALE_PRICE']].groupby(['NBHD_ID']).count().reset_index()
    neighbor_house_record = pd.merge(neighbor_house_record, neighbor_centers, left_on = 'NBHD_ID', right_on = 'NBHD_ID')

    metrics=np.append(metrics,["Seasonality of Median Price","Seasonality of Home Sold"])
    nbhd_stats = neighbor_stats.copy()
    nbhd_stats["Park Coverage"]=(nbhd_stats["ParkA_SqM"]/nbhd_stats["Area_SqM"]*100).round(2)
    nbhd_stats["Tree Coverage"]=(nbhd_stats["TreesA_SqM"]/nbhd_stats["Area_SqM"]*100).round(2)
    nbhd_stats=pd.concat([nbhd_stats.iloc[:,1], nbhd_stats.iloc[:,4:12],nbhd_stats.iloc[:,14:]],axis=1)
    nbhd_stats.rename(columns={"StLights":"Street Lights","NBRHD_NAME":"Neighborhood",
                                        "TrAccident":"Traffic Accidents"},inplace=True)

    house_sold=family_demo[['NBHD_ID','SALE_YEAR','SALE_PRICE']].groupby(['NBHD_ID','SALE_YEAR'],
                                    as_index=False).count().rename(columns={"SALE_PRICE":"Home Sold"})
    neighbor_prices=neighbor_prices.merge(house_sold,on=['NBHD_ID','SALE_YEAR'])

    sectors={
        "Education":["Neighborhood","Libraries","Colleges","K12s"],
        "Shopping":["Neighborhood","FoodStores","Malls","Marijuana"],
        "Safety":["Neighborhood","Crimes","Traffic Accidents"],
        "Environment":["Neighborhood","Street Lights","Park Coverage","Tree Coverage"]
    }

    return json_neighbor, neighbor_prices, json_neighbor_centers, json_single_family, neighbor_house_record, metrics, cities, city_data, family_dist, family_demo, city_seasonality, neighbor_demo, neighbor_stats, nbhd_stats, sectors

def draw_base_map(json_neighbor, neighbor_prices):
    return {
        'data': [{
            'type': "choroplethmapbox", 
            'geojson': json_neighbor,
            'locations': neighbor_prices[neighbor_prices['SALE_YEAR'] == 2019]['NBHD_NAME'].astype(str),
            'z': neighbor_prices[neighbor_prices['SALE_YEAR'] == 2019]['SALE_PRICE'],
            'name': '',
            'featureidkey': 'properties.NBHD_NAME',
            'marker': {'opacity': 1.0, 'line': {'color': 'lightgrey'}},
            'hovertemplate': "%{location} <br>Median Sale Price (2019): $%{z:,.f}",
            'colorbar':{
                'title': {'text': 'Neighborhood Median Sale Price 2019'}, 
                'x': 0},
            'colorscale': 'YlOrRd',
            'reversescale': True,
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
                'style': 'white-bg',  
                'layers': [
                    {
                        'source': ['https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg'],
                        'opacity': 0.3,
                        'sourcetype': 'raster',
                        'below': 'traces',
                    },
                    #{
                    #'source': json_neighbor,
                    #'below': 'traces',
                    #'type': "fill",     
                    #'color': 'grey',
                    #'opacity': 0.3,
                    #'paint': {'line': {'color': 'white'}}
                    #}
                ],                             
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
                'marker': {'opacity': 1.0, 'line': {'color': 'lightgrey'}},
                'hovertemplate': "%{location} <br>Annual Average Single Family House Sales: %{z:.0f}",   
                'showscale': False,   
                'colorscale': 'Blues',
            },

            {
                'type': "choroplethmapbox", 
                'geojson': json_neighbor,
                'locations': neighbor_house_record[neighbor_house_record['NBHD_NAME'] != sel_nbhd]['NBHD_NAME'].astype(str),
                'z': neighbor_house_record[neighbor_house_record['NBHD_NAME'] != sel_nbhd]['SALE_PRICE'] / 10.,
                'name': '',
                'featureidkey': 'properties.NBHD_NAME',
                'marker': {'opacity': 0.5, 'line': {'color': 'lightgrey'}},
                'hovertemplate': "%{location} <br>Annual Average Single Family Houses Sold: %{z:.0f}",
                'showscale': False,
                'colorscale': 'Reds',
            }],
        
        'layout': {
            'margin': {"r":10, "t": 0, "l":10,"b":10},
            'hovermode': 'closest',
            'autosize': True,
            'mapbox': {
                'center': {'lat': 39.7114, 'lon': -104.9360},
                'zoom': 11,
                'style': 'white-bg',                    
                'layers': [
                        {
                        'source': ['https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg'],
                        'opacity': 0.3,
                        'sourcetype': 'raster',
                        'below': 'traces',
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
                'colorscale': 'Reds',
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
                'style': 'white-bg', 
                'layers': [
                    {
                        'source': ['https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg'],
                        'opacity': 0.3,
                        'sourcetype': 'raster',
                        'below': 'traces',
                    },
                    #{
                    #    'source': json_neighbor,
                    #    'below': 'traces',
                    #    'type': "fill",     
                    #    'color': 'grey',
                    #    'opacity': 0.3,
                    #    'paint': {'line': {'color': 'white'}}
                    #}
                ],                 
            },
        }
    }
