import os
from itertools import product
import time

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

try:
    import dash_core_components as dcc
except:
    os.system("pip install dash==1.9.1")
    import dash_core_components as dcc
import dash_html_components as html
try:
    import dash_bootstrap_components as dbc
except:
    os.system("pip install dash-bootstrap-components==1.1.1")
    import dash_bootstrap_components as dbc
try:
    import plotly.graph_objects as go
except:
    os.system("pip install plotly")
    import plotly.graph_objects as go

# grab mapbox token and street view api
def grab_credentials():
    with open('Credentials/mapbox_access_token.txt') as token_file:
        token = token_file.readline()
    with open('Credentials/google_street_view_api.txt') as api_file:
        api = api_file.readline()
    return token, api

# about tab
def write_about():
    about = html.Div([

        html.Div([ # data
            dbc.CardHeader("Data", style = {'background-color': 'white', 'font-weight': 'bold'}),
            dbc.CardBody(
                [
                    dcc.Markdown('''
                        > This project visualizes the analytics of Denver single family housing market, showing both historical and predicted house prices in Denver area. 
                        The key data is the historical house selling price associated with the property details, collected from [Denver open data website](https://www.denvergov.org/opendata). 
                        The original data contains ~200,000 house sales records dated from 1945 to 2020. Of these, single family house records between 2000 and 2020 were filtered for inclusion in this project.
                        
                        > To analyze housing market, we also collected Denver neighborhood-level features from [Redfin](https://www.redfin.com/blog/data-center/) and [Denver website](https://www.denvergov.org/opendata), for the showing of demographical, socio-economic, environmental differences among neighborhood.
                        The hypothesis was that the quality of neighborhood would have an impact on house prices.

                        > The final data set is the consumer price index report, collected from [Bureau of Labor Statistics](https://data.bls.gov/cgi-bin/srgate), for inflation adjustment over the year.
                    '''),
                ]
            ),
        ], id = 'data', className = 'eleven columns', style = {'margin-left': 15, 'margin-top': 15, 'margin-right': 30}),

        html.Div([ # model
             dbc.CardHeader("Analytics", style = {'background-color': 'white', 'font-weight': 'bold'}),
                dbc.CardBody(
                    [
                        dcc.Markdown('''
                            > Initial data process was done in QGIS environment, due to lack of common keys in different data sets.
                            To link single family house records and neighborhood features, their spatial relationship was applied such that each property was assigned a neighborhood id to extract neighborhood-level attrbutes.
                            Also based on spatial relationship, we have summarized key features in each neighborhood, such as number of crimes, traffic accidents, percentage of tree coverage.
                            Distance to nearest food stores, schools, and parks from each property was also calculated for model preparation.

                            > With the processed data, we built an XGBoost model and compared with a baseline Lasso regression model. 
                            The XGBoost model yielded a mean prediction error of $44K, and a median prediction error of $13K, compared to $73k mean error and $29K median error from the baseline model.

                            > [Code on Github](https://github.com/lzhao-byte/denver-housing)

                        '''),
                    ]
                ),
        ], id = 'model', className = 'eleven columns', style = {'margin-left': 15, 'margin-top': 15, 'margin-right': 30}),

        html.Div([ # visualization
             dbc.CardHeader("Visualization", style = {'background-color': 'white', 'font-weight': 'bold'}),
                dbc.CardBody(
                    [
                        dcc.Markdown('''
                            > The intent is to provide users with comprehensive knowledge and extensive information related to their househunting in Denver by 
                            integration of historical transaction data, neighborhood characteristics and price predicting model. 
                            
                            > Thus, the website mainly consists of three levels of data presentation: 
                            
                                * house price prediction
                                * neighborhood characteristics
                                * price comparison with different cities.
                            
                            > The website was created with [Plotly Dash](https://plotly.com/) and hosted in [heroku](https://www.heroku.com/). It contains four tabs: 

                                * Denver house: where the users see historical house records and house price prediction, such as neighborhood, number of bedrooms and bathrooms etc.
                                * Denver Neighborhood: where all neighborhood features and median sale prices can be queried, serving as a reference of house hunting
                                * Denver City: where we provide a comprehensive comparison on key housing market metrics with cities that are similar to Denver
                                * About: where a brief explanation on the project is provided
                        '''),
                    ]
                ),
        ], id = 'visual', className = 'eleven columns', style = {'margin-left': 15, 'margin-top': 15, 'margin-right': 30}),

        html.Div([ # about us
            dbc.CardHeader("About Us", style = {'background-color': 'white', 'font-weight': 'bold'}),
            dbc.CardBody(
                [ 
                    dcc.Markdown('''
                    > This website *Denver Single Family Housing Market* is created by *[Wentao Duan](https://www.linkedin.com/in/wentao-duan-b389861a/)*, *[Jingying Guan](/)*, 
                    *[Li Li](https://www.linkedin.com/in/li-li-69bb60128/)*, *[Liuhui Zhao](https://www.linkedin.com/in/lhzhao/)*, and *[Zehua Zheng](https://www.linkedin.com/in/zehuazheng/)*.
                    
                    > We came from different disciplines, formed *Team Flying Pig*, and accomplished this project for Denver housing market analytics and visualization in Spring, 2020.
                    '''),
                ]
            ),
        ], id = 'about-us', className = 'eleven columns', style = {'margin-left': 15, 'margin-top': 15, 'margin-bottom': 10, 'margin-right': 30}),

    ])
    return about

# meta
def load_app_header():
    text =  '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>Denver Single Family Housing Market</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
            <div>
                <code style = 'font-family: monospace'>Copyright &copy; 2020 Team Flying Pig.</code>
            </div>
        </body>
    </html>
    '''
    return text

# descriptions
def load_markdowns():
    project_description = '''
    > *This site showcases the product of our class project for CSE6242.*
    '''

    house_hunting_description = '''
    > *This page hosts the single family house sale record and our prediction model.*

    > *Click **see future** to check predicted house prices of your choice. Click **check history** to see recent sold houses.*
    '''
    return project_description, house_hunting_description

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

# prediction model (see future)
def predict_house_xgb(neighbor, bed, bath, story, age, minarea, maxarea, minlot, maxlot, park, store, month, neighbor_stats, neighbor_demo, cpi):
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

    grns = [0]
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

    sel_columns = ['Story', 'Bedrooms', 'Bathrooms', 'Age of House (yrs)', 'Above Ground Area (sqft)', 'Lot Size (sqft)', 'Distance to Park (meters)', 'Distance to Food Stores (meters)', 'Predicted Price ($)']
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
    xgb_model.load_model('Models/model_xgb_regressor.model')
    y_pred = xgb_model.predict(xgb.DMatrix(x_pred.values))
    y_cpi = cpi[cpi['month'] == months[0]]['cpi'].values[0]

    predict_df = x_pred.copy()
    predict_df['Predicted Price'] = np.round(y_pred * y_cpi / 100)
    predict_df['Neighborhood'] = nbhd_name

    predict_tab = predict_df[['STORY', 'BED_RMS', 'BATH_RMS', 'AGE', 'AREA_ABG', 'LAND_SQFT', 'ParkDist', 'StoreDist', 'Predicted Price']]
    predict_tab.columns = sel_columns

    return predict_tab

# load necessary files
def load_files():
    city_data=pd.read_csv(r"CSVFiles/CityComparison.csv")
    city_data["Region"]=city_data["Region"].str.strip()
    city_seasonality=pd.read_csv(r"CSVFiles/CitySeasonality.csv")
    city_seasonality["City"]=city_seasonality["City"].str.strip()
    city_seasonality=city_seasonality.dropna()
    cities=set(city_data["Region"].unique()) and set(city_seasonality["City"].unique())
    cities=cities - set(["National","Colorado"])
    metrics=city_data.columns[3:]

    cpi = pd.read_csv('CSVFiles/cpi.csv')

    # neighborhood price data for city/neighborhood tab
    with open('JsonFiles/Neighborhoods.geojson') as geojson_file:    
        json_neighbor = json.load(geojson_file)
    neighbor_prices = pd.read_csv('CSVFiles/NeighborPrices.csv')
    neighbors = pd.read_csv('CSVFiles/Neighborhoods.csv')
    neighbor_prices = pd.merge(neighbor_prices, neighbors, left_on = 'NBHD_ID', right_on = 'NBHD_ID')
    neighbor_prices['SALE_PRICE'] = neighbor_prices['SALE_PRICE'].astype(float)
 
    # single family data for single family tab
    with open('JsonFiles/SingleFamilyHouses.geojson') as geojson_file:    
        json_single_family = json.load(geojson_file)
    family_demo = pd.read_csv('CSVFiles/SingleFamilyDemo.csv', dtype = {'SCHEDNUM':'str'})
    family_dist = pd.read_csv('CSVFiles/FamilyDistances.csv', dtype = {'SCHEDNUM_STR':'str'})
    neighbor_stats = pd.read_csv('CSVFiles/NeighborStatistics.csv')
    neighbor_stats = neighbor_stats.fillna(0)
    neighbor_demo = pd.read_csv('CSVFiles/NeighborDemo.csv')

    neighbor_centers = pd.read_csv('CSVFiles/NeighborhoodCenters.csv')
    neighbor_house_record = family_demo[['NBHD_ID', 'SALE_PRICE']].groupby(['NBHD_ID']).count().reset_index()
    neighbor_house_record = pd.merge(neighbor_house_record, neighbor_centers, left_on = 'NBHD_ID', right_on = 'NBHD_ID')

    metrics=np.append(metrics,["Seasonality of Median Price","Seasonality of Home Sold"])
    nbhd_stats = neighbor_stats.copy()
    nbhd_stats["Park Coverage(%)"]=(nbhd_stats["ParkA_SqM"]/nbhd_stats["Area_SqM"]*100).round(2)
    nbhd_stats["Tree Coverage(%)"]=(nbhd_stats["TreesA_SqM"]/nbhd_stats["Area_SqM"]*100).round(2)
    nbhd_stats=pd.concat([nbhd_stats.iloc[:,1], nbhd_stats.iloc[:,4:12],nbhd_stats.iloc[:,14:]],axis=1)
    nbhd_stats.rename(columns={"StLights":"Street Lights","NBRHD_NAME":"Neighborhood",
                        "Marijuana":"Marijuana Business","Crimes":"Annual Crimes", 
                        "TrAccident":"Annual Traffic Accidents"},inplace=True)
    nbhd_stats["Annual Crimes"]=(nbhd_stats["Annual Crimes"]/4).astype(int)
    nbhd_stats["Annual Traffic Accidents"]=(nbhd_stats["Annual Traffic Accidents"]/4).astype(int)

    house_sold=family_demo[['NBHD_ID','SALE_YEAR','SALE_PRICE']].groupby(['NBHD_ID','SALE_YEAR'],
                                    as_index=False).count().rename(columns={"SALE_PRICE":"Home Sold"})
    neighbor_prices=neighbor_prices.merge(house_sold,on=['NBHD_ID','SALE_YEAR'])

    sectors={
        "Education":["Neighborhood","Libraries","Colleges","K12s"],
        "Shopping":["Neighborhood","FoodStores","Malls","Marijuana Business"],
        "Safety":["Neighborhood","Annual Crimes","Annual Traffic Accidents"],
        "Environment":["Neighborhood","Street Lights","Park Coverage(%)","Tree Coverage(%)"]
    }

    return json_neighbor, neighbor_prices, json_single_family, neighbor_house_record, metrics, cities, city_data, family_dist, family_demo, city_seasonality, neighbor_demo, neighbor_stats, nbhd_stats, sectors, cpi

def draw_family_base_map(json_single_family, family_demo, family_dist):
    return {
        'data': [{
            'type': "choroplethmapbox", 
            'geojson': json_single_family,
            'locations': family_dist['SCHEDNUM_STR'],
            'z': family_dist['StoreDist'],
            'name': '',
            'featureidkey': 'properties.SCHEDNUM',
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
                ],                             
            },
        }
    }

def draw_base_map(json_neighbor, neighbor_prices, neighbor_house_record, sel_nbhd):			
    data=[{
            'type': "choroplethmapbox", 
            'geojson': json_neighbor,
            'locations': neighbor_prices[neighbor_prices['SALE_YEAR'] == 2019]['NBHD_NAME'].astype(str),
            'z': neighbor_prices[neighbor_prices['SALE_YEAR'] == 2019]['SALE_PRICE'],
            'name': '',
            'featureidkey': 'properties.NBHD_NAME',
            'marker': {'opacity': 0.5, 'line': {'color': 'lightgrey'}},
            'hovertemplate': "%{location} <br>Median Sale Price (2019): $%{z:,.f}",
            'colorbar':{
                'title': {'text': 'Neighborhood Median Sale Price 2019'}, 
                'x': 0},
            'colorscale': 'YlOrRd',
            'reversescale': True,
            'unselected': {
                'marker': {'opacity': 0.5, 'line': {'color': 'lightgrey'}},
            }
            }
        ]
    json_sel_nbhd=json_neighbor.copy()
    json_sel_nbhd["features"]=[feature for feature in json_neighbor["features"] if feature["properties"]["NBHD_NAME"] in sel_nbhd]
    layout = {
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
                {
                    'source': json_sel_nbhd,
                    'below': 'traces',
                    'opacity': 1.0,
                    'type' : 'fill',
                    'color': 'grey',
                    'fill': {'outlinecolor': 'red'}
                }
            ],                             
        },
    }
    return {
        'data': data,  
        'layout': layout
    }

# update house hunting map
def update_house_base_map(json_single_family, family_demo, json_neighbor, neighbor_house_record, sel_nbhd):
    access_token, _ = grab_credentials()
    if access_token == '':
        style = 'stamen-terrain'
    else:
        style = 'light'
    return {
        'data': [
            {
                'type': "choroplethmapbox",
                'geojson': json_single_family,
                'locations': family_demo['SCHEDNUM'],
                'z': family_demo['SALE_PRICE'],
                'text': family_demo['SALE_YEAR'],
                'featureidkey': 'properties.SCHEDNUM',
                'marker': {'opacity': 1.0, 'line': {'color': 'lightgrey'}},
                'name': '',
                'hovertemplate': "Sales Price: %{z:,.0f} <br>Sale Year: %{text:.0f} ",
                'colorscale': 'Reds',
                'showlegend': False,
                'colorbar':{
                    'title': {'text': 'Sale Price ($)'}, 
                    'x': 0},
            }           
            ],

        'layout': {
            'clickmode': 'event+select',
            'margin': {"r":10, "t": 0, "l":10,"b":10},
            'hovermode': 'closest',
            'autosize': True,
            'mapbox': {
                'center': {'lat': neighbor_house_record[neighbor_house_record['NBHD_NAME'] == sel_nbhd]['Lat'].values[0], 'lon': neighbor_house_record[neighbor_house_record['NBHD_NAME'] == sel_nbhd]['Lon'].values[0]},
                'zoom': 14,
                'style': style,
                'accesstoken': access_token,
                'layers': [
                    {
                        'source': json_neighbor,
                        'below': 'traces',
                        'type': "fill",     
                        'color': 'yellow',
                        'opacity': 0.05,
                        'fill': {'outlinecolor': 'red', 'outlinewidth': 2}
                    }
                ],
            },
        }
    }

# update house hunting map  
def update_house_base_map_origin(sel_nbhd, json_neighbor, neighbor_house_record):
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

def family_demo_filter(min_price, max_price, min_year, max_year, min_bed, max_bed, minarea, maxarea, minlot, maxlot, neighbor, story, family_demo, json_single_family):
    if min_price is None:
        min_price = 100000
    if max_price is None:
        max_price = 1500000
    if min_year is None:
        min_year = 2010
    if max_year is None:
        max_year = 2019
    if min_bed is None:
        min_bed = 1
    if max_bed is None:
        max_bed = 3
    if minarea is None:
        minarea = 1800
    if maxarea is None:
        maxarea = 7500
    if minlot is None:
        minlot = 1000
    if maxlot is None:
        maxlot_filter = 7500
    if neighbor is None:
        neighbor = 'Athmar Park'
    if story is None:
        story = 1

    min_price_filter = family_demo['SALE_PRICE'] >= min_price
    max_price_filter = family_demo['SALE_PRICE'] <= max_price
    min_year_filter = family_demo['SALE_YEAR'] >= min_year
    max_year_filter = family_demo['SALE_YEAR'] <= max_year
    min_bed_filter = family_demo['BED_RMS'] >= min_bed
    max_bed_filter = family_demo['BED_RMS'] <= max_bed
    minarea_filter = family_demo['AREA_ABG'] >= minarea
    maxarea_filter = family_demo['AREA_ABG'] <= maxarea
    minlot_filter = family_demo['LAND_SQFT'] >= minlot
    maxlot_filter = family_demo['LAND_SQFT'] <= maxlot
    neighbor_filter = family_demo['NBRHD_NAME'] == neighbor
    story_filter = family_demo['STORY'] == story

    sel_df = family_demo[min_price_filter & max_price_filter & min_year_filter & max_year_filter & min_bed_filter & max_bed_filter & minarea_filter & maxarea_filter & minlot_filter & maxlot_filter & neighbor_filter & story_filter]

    # filter geojson
    geodf = [f for f in json_single_family['features'] if f['properties']['NBRHD_NAME'] == neighbor]
    geodf = {"type": "FeatureCollection", "name": "SingleFamilyHouses", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } }, "features": geodf}

    return geodf, sel_df    

def load_neighbor_features():
    with open('JsonFiles/NeighborParks.geojson') as json_file:
        parks = json.load(json_file)
    features = pd.read_csv('CSVFiles/NeighborFeatures.csv')
    return features, parks

def draw_store_map(sel_nbhd, features, parks, json_neighbor, neighbor_centers):
    sel_features = features[features['NBRHD_NAME'].isin(sel_nbhd)]
    sel_nbhds = neighbor_centers[neighbor_centers['NBHD_NAME'].isin(sel_nbhd)]
    types = sel_features['Type'].unique()
    data = []
    zoom = 11 if len(sel_nbhd) > 1 else 13

    access_token,_ = grab_credentials()

    for tp in types:
        if tp == 'College':
            symbol = 'college'
        elif tp == 'K-12':
            symbol = 'school'
        elif tp == 'Marijuana':
            symbol = 'commercial'
        elif tp == 'Library':
            symbol = 'library'
        elif tp == 'Food Store':
            symbol = 'grocery'
        elif tp == 'Shopping Center':
            symbol = 'shop'
        
        if access_token == '':
            marker = {'size': 16},
            style = 'stamen-terrain'
            legend = True
        else:
            marker = {'size': 14, 'symbol': symbol}
            style = 'light'
            legend = False

        data_dict = {
            'type': "scattermapbox", 
            'lon': sel_features[sel_features['Type'] == tp]['Lon'].values,
            'lat': sel_features[sel_features['Type'] == tp]['Lat'].values,
            'text': sel_features[sel_features['Type'] == tp]['Name'].values + '__' + sel_features[sel_features['Type'] == tp]['NBRHD_NAME'].values[0],
            'hoverinfo': 'text',
            'mode': 'markers',
            'opacity': 0.8,
            'marker': marker,
            'name': tp,
            'showlegend': legend
        }
        data.append(data_dict)

    return {
        'data': data,
    
        'layout': {
            'title': "Points of Interests",
            'height': 600,
            'margin': {"r":10, "t": 0, "l":10,"b":20},
            'hovermode': 'closest',
            'autosize': True,
            'legend':{'x': 0, 'y': 1},
            'mapbox': {
                'center': {'lat': np.mean(sel_nbhds['Lat'].values), 'lon': np.mean(sel_nbhds['Lon'].values)},
                'zoom': zoom,
                'style': style,
                'accesstoken': access_token,
                'layers': [                 
                    {
                        'source': json_neighbor,
                        'below': 'traces',
                        'type': "fill",     
                        'color': 'yellow',
                        'opacity': 0.1,
                        'fill': {'outlinecolor': 'red'}
                    },
                    {
                        'source': parks,
                        'below': 'traces',
                        'type': "fill",     
                        'color': 'green',
                        'opacity': 0.2,
                        'fill': {'outlinecolor': 'white'}
                    },
                ],                  
            },
        }
    }


