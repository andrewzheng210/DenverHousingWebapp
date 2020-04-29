import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_bio as dashbio

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import pandas as pd
import json
import xgboost as xgb

# responsive style sheet
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server

app.index_string = '''
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
neighbor_stats = pd.read_csv('CSVFiles/NeighborStatistics.csv').set_index('NBRHD_NAME')
neighbor_stats = neighbor_stats.fillna(0)

neighbor_centers = pd.read_csv('CSVFiles/NeighborhoodCenters.csv')
neighbor_house_record = family_demo[['NBHD_ID', 'SALE_PRICE']].groupby(['NBHD_ID']).count().reset_index()
neighbor_house_record = pd.merge(neighbor_house_record, neighbor_centers, left_on = 'NBHD_ID', right_on = 'NBHD_ID')

project_description = '''
> *This site showcases the product of our class project for CSE6242.*

> *In this project, we proposed a Machine Learning based 
house price prediction method with Denver data.*
'''

house_hunting_description = '''
> *This page hosts the single family house sale record and our prediction model.*

> *In the search box below, enter your choice of home features, we will show you the history and the future.*

> *Leave blank if you do not have any preference in the list below (except for neighborhood).*
'''

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

###############################
## model_xgb_regressor.model ##
## XGB regressor parameters  ##
# 'AREA_ABG', 'BATH_RMS', 'SALE_MONTH', 'AGE', 
# 'STORY', 'LAND_SQFT', 'BED_RMS', 'GRD_AREA', 
# 'ParkDist', 'DrugDist', 'StoreDist', 
# 'AVG_HH_INC', 'SALE_YEAR', 'PER_CAPITA', 
# 'LESSTHANHS', 'BACHELORSO',
# 'PCT_AGE65P', 'PER_COMM', 
# 'Tree_Coverage', 'K12s', 'Intersects', 
# 'PCT_VAC', 'Park_Coverage', 'Libraries', 
# 'FoodStores', 'Marijuana', 'Crimes', 'PCT_AGELES', 
# 'TrAccident', 'MaxPctRace', 'StLights', 'Colleges', 'Malls'
###############################


def draw_base_map():
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

def draw_house_base_map():
    return {
        'data': [{
            'type': "scattermapbox", 
            'lon': neighbor_house_record['Lon'],
            'lat': neighbor_house_record['Lat'],
            'text': neighbor_house_record['NBHD_NAME'] + '<br>' + 'Annual Average Houses Sold: ' + neighbor_house_record['SALE_PRICE'].apply(lambda x: round(x/10.)).astype(str),
            'hoverinfo': 'text',
            'mode': 'markers',
            'opacity': 0,
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
                    'opacity': 0.4,
                    'paint': {'line': {'color': 'white'}}
                }],                 
            },
        }
    }

app.layout = html.Div([
    html.H4(children = 'Denver House Price Record and Prediction', style = {
        'textAlign': 'middle',
    }),
    dcc.Markdown(children = project_description),

    dcc.Tabs([
        dcc.Tab(
            label = 'House Hunting', 
            className = 'custom-tab', 
            selected_className = 'custom-tab--selected',
            children = [
                dcc.Markdown(children = house_hunting_description),

                html.Div([
                    
                    html.Div([
                        # side bar
                        dbc.Card([
                            dbc.CardHeader('Search'),
                            dbc.CardBody([ # neighborhood selection
                                html.P('Neighborhood*', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-neighbor',
                                            options = [{'label': nbhd_name, 'value': nbhd_name} for nbhd_name in neighbor_prices['NBHD_NAME'].unique()],
                                            placeholder = 'Select from list'
                                        ), 
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # bedrooms
                                html.P('Bedroom', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-bedroom',
                                            options = [{'label': beds, 'value': beds} for beds in ['0', '1', '2', '3', '4', '5+']],
                                            placeholder = 'Number of Bedrooms',
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # bathrooms
                                html.P('Bathroom', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-bathroom',
                                            options = [{'label': baths, 'value': baths} for baths in ['1', '2', '3', '4', '5+']],
                                            placeholder = 'Number of Bathrooms',
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # story
                                html.P('Story', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-story',
                                            options = [{'label': story, 'value': story} for story in sorted(family_demo['STORY'].unique())],
                                            placeholder = 'Story',
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # age
                                html.P('Age of house', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-age',
                                            options = [{'label': age, 'value': age} for age in ['New Construction', '0 - 5', '5 - 10', '10 - 20', '20 - 50', '50 - 100']],
                                            placeholder = 'Age',
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # above ground area min-max
                                html.P('Above Ground Area', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-area-min',
                                            options = [{'label': area_min, 'value': area_min} for area_min in family_demo['AREA_ABG'].quantile([.1, .2, .3, .4, .5]) // 100 * 100],
                                            value = family_demo['AREA_ABG'].min(),
                                            placeholder = 'min (sqft)'
                                        ),
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-area-max',
                                            options = [{'label': area_max, 'value': area_max} for area_max in family_demo['AREA_ABG'].quantile([.6, .7, .8, .9, 1.]) // 100 * 100],
                                            value = family_demo['AREA_ABG'].max(),
                                            placeholder = 'max (sqft)'
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # lot size min-max
                                html.P('Lot Size', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-lot-min',
                                            options = [{'label': lot_min, 'value': lot_min} for lot_min in family_demo['LAND_SQFT'].quantile([.1, .2, .3, .4]) // 100 * 100],
                                            value = family_demo['LAND_SQFT'].min(),
                                            placeholder = 'min (sqft)'
                                        ),
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-lot-max',
                                            options = [{'label': lot_max, 'value': lot_max} for lot_max in family_demo['LAND_SQFT'].quantile([.6, .7, .8, .9]) // 100 * 100],
                                            value = family_demo['LAND_SQFT'].max(),
                                            placeholder = 'max (sqft)'
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # month
                                html.P('When would you like to buy', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-month',
                                            options = [{'label': m, 'value': i} for i, m in enumerate(months)],
                                            placeholder = 'Month'
                                        ),
                                    ),
                                ]),
                            ]),

                            html.Button('Check history', id = 'button-history'),
                            html.Button('See future', id = 'button-future'),

                        ], color='danger', outline = True)
                    ], className = 'three columns', style = {'margin-left': 30, 'margin-bottom': 10}),

                    html.Div([
                        dcc.Graph(
                            id = 'denver-house-map',
                            figure = draw_house_base_map(),
                            style = {'height': '100%'}
                        )
                    ], id = 'house-map-chart', className = 'eight columns')

                ], className = 'row')
            ]),      
        dcc.Tab(
            label='City', 
            className='custom-tab', 
            selected_className='custom-tab--selected',
            children = [ 
            html.Div([
                # neighborhood map (7 cols)
                html.Div([  
                    dcc.Graph(
                        id = 'denver-map',
                        figure = draw_base_map(),
                    ),
                ],
                className = 'seven columns',
                title = 'Select Neighborhoods to See Details'
                ),

                 # time series chart (5 cols) -- city level housing market information
                html.Div([
                    dcc.Dropdown(
                        id = 'neighbor-price-chart-list',
                        options = [
                            {'label': nbhd_name, 'value': nbhd_name} for nbhd_name in neighbor_prices['NBHD_NAME'].unique()
                        ],
                        value = ['Washington Park'], # washington park
                        multi = True,
                        placeholder = 'Select A Neighborhood for Detailed Price Trend',
                        style = {'margin-top': 10, 'margin-right': 30}
                    ),

                    dcc.Graph(
                        id = 'neighbor-price-chart',
                        config = {'responsive': True, 'autosizable': True}
                    ),
                ],
                className = 'five columns'
                ),
            ],
            className = 'row', style = {'margin-right': 30, 'margin-top': 10, 'margin-left': 30})
        ]),

        dcc.Tab(
            label = 'Neighborhoods', 
            className = 'custom-tab', 
            selected_className = 'custom-tab--selected',
            children = ['Under Development...']),

        dcc.Tab(
            label = 'About',
            className = 'custom-tab',
            selected_className = 'custom-tab--selected',
            children = ['This holds the explanation of our model...']
        ),
     ]),
])

# callback to select neighborhoods for comparison
@app.callback(
    Output('neighbor-price-chart-list', 'value'),
    [Input('denver-map', 'selectedData')]
)
def select_from_map(sel_nbhd):
    if sel_nbhd is None or sel_nbhd == []:
        return []
    else:
        nbhd_names = [i['location'] for i in sel_nbhd['points']]
        return nbhd_names

# callback to update maps from chart list value
@app.callback(
    Output('denver-map', 'figure'),
    [Input('neighbor-price-chart-list', 'value')]
)
def update_neighbor_map(sel_nbhd):
    if sel_nbhd is None or sel_nbhd == []:
        return draw_base_map()
    else:
        raise PreventUpdate

# callback to update neighbor price chart
@app.callback(
    Output('neighbor-price-chart', 'figure'),
    [Input('neighbor-price-chart-list', 'value')]
)
def update_neighbor_price_chart(sel_value):
    price_data = []
    frames = []
    steps = []

    years = neighbor_prices['SALE_YEAR'].unique()
    if sel_value is None or sel_value == []:
        for year in years:
            frames.append({
                'data': [{
                    'y': neighbor_prices[neighbor_prices['SALE_YEAR'] == year]['NBHD_NAME'].apply(lambda x: x.split('/')[0]),
                    'x': neighbor_prices[neighbor_prices['SALE_YEAR'] == year]['SALE_PRICE'],
                    'type': 'bar',
                    'orientation': 'h',
                    'name': year
                }],
                'name': year
            })
            steps.append({
                            "args": [
                                [year],
                                {"frame": {"duration": 500, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 300},
                                'visible': True}                               
                                ],
                            "label": year,
                            "method": "animate",
                })

        return {
            'data': [{
                'y': neighbor_prices[neighbor_prices['SALE_YEAR'] == 2000]['NBHD_NAME'].apply(lambda x: x.split('/')[0]),
                'x': neighbor_prices[neighbor_prices['SALE_YEAR'] == 2000]['SALE_PRICE'],
                'type': 'bar',
                'orientation': 'h',
                'name': 2000
            }],
            'frames': frames,
            'layout': {
                'title': 'Median Sale Price', 
                'hovermode': 'closest',
                'showlegend': True,
                'xaxis': {
                    'showline': True,
                    'linecolor': 'gray',
                    'mirror': True,
                    'showgrid': False,
                    'ticks': 'outside',
                    'range': [min(neighbor_prices['SALE_PRICE']), max(neighbor_prices['SALE_PRICE'])]
                    },
                'yaxis':{
                    'showline': True,
                    'linecolor': 'gray',
                    'mirror': True,
                    },
                'height': 600,
                'margin': {'l': 120, 'r': 70},
                'updatemenus':[{
                    "type": "buttons",
                    "buttons": [{
                            "args": [None, {"frame": {"duration": 500, "redraw": True},
                                            "fromcurrent": True, "transition": {"duration": 300,
                                                                                "easing": "quadratic-in-out"}}],
                            "label": "Play",
                            "method": "animate"
                            },
                            {
                            "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                            "mode": "immediate",
                                            "transition": {"duration": 0}}],
                            "label": "Pause",
                            "method": "animate"
                            }
                        ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 20},
                    "showactive": False,
                    "x": 0.1,
                    "xanchor": "right",
                    "y": -0.1,
                    "yanchor": "top"
                }],
                'sliders': [{
                    "active": 0,
                    "yanchor": "top",
                    "xanchor": "left",
                    "transition": {"duration": 300, "easing": "cubic-in-out"},
                    "pad": {"b": 10, "t": 30},
                    "len": 0.9,
                    "x": 0.1,
                    "y": -0.1,
                    "steps": steps,
                    "currentvalue": {"visible": False},
                    }],
            },
        }

    for val in sel_value:
        data = {
            'x': neighbor_prices[neighbor_prices['NBHD_NAME'] == val]['SALE_YEAR'],
            'y': neighbor_prices[neighbor_prices['NBHD_NAME'] == val]['SALE_PRICE'],
            'name': val,
            'mode': 'markers',
            'marker': {
                'size': neighbor_prices[neighbor_prices['NBHD_NAME'] == val]['SALE_PRICE'] / 20000,
            },
            'textposition': 'top center',
            'log_x': True,
        }
        price_data.append(data)
    return {
        'data': price_data,
        'layout': {
            'title': 'Median Sale Price', 
            'hovermode': 'closest',
            'xaxis': {
                'title': {'text': 'Year', 'standoff': 10},
                'showline': True,
                'linecolor': 'gray',
                'showgrid': True,
                'gridcolor': 'WhiteSmoke',
                'nticks': 10,
                'mirror': True,
                },
            'yaxis':{
                'title': {'text': 'Median Sale Price ($)', 'standoff': 40},
                'showline': True,
                'showgrid': True,
                'gridcolor': 'WhiteSmoke',
                'linecolor': 'gray',
                'mirror': True,
            },
            'height': 600,
            'margin': {'l': 60, 'r': 100}
        },
    }

if __name__ == '__main__':
    #pass
    app.run_server(debug=True)