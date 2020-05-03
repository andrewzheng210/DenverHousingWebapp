from utils import (load_files, draw_base_map, grab_credentials,
                    draw_house_base_map, update_house_base_map, predict_house_xgb, 
                    draw_family_base_map, write_about, load_markdowns, 
                    load_app_header, family_demo_filter,load_neighbor_features,draw_store_map)

import os, json, urllib
import pandas as pd
import numpy as np

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
    import dash
except:
    os.system("pip install dash==1.9.1")
    import dash

try:
    import dash_table as dt
except:
    os.system("pip install dash-table==4.6.1")
    import dash_table as dt

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# responsive style sheet
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server

# load necessary files
json_neighbor, neighbor_prices, json_single_family, neighbor_house_record, metrics, cities, city_data, family_dist, family_demo, city_seasonality, neighbor_demo, neighbor_stats, nbhd_stats, sectors, cpi = load_files()
features, parks = load_neighbor_features()

app.index_string = load_app_header()
project_description, house_hunting_description = load_markdowns()

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

app.layout = html.Div([
    html.H4(children = 'Denver Single Family House Market Analytics', style = {
        'textAlign': 'middle',
    }),
    dcc.Markdown(children = project_description),

    # house hunting tab
    dcc.Tabs([
        dcc.Tab(
            label = 'Denver House',
            className = 'custom-tab', 
            selected_className = 'custom-tab--selected',
            children = [
                dcc.Markdown(children = house_hunting_description),

                html.Div([
                    
                   html.Div([
                        
                        html.Button('Check history', id = 'button-history', n_clicks = 0),
                        html.Button('See future', id = 'button-predict', n_clicks = 0),

						# side bar to check hisotry
                        dbc.Card([
                            dbc.CardHeader('Search (leave blank if you do not have any preference)'),
							
							dbc.CardBody([ # neighborhood selection
                                html.P('Neighborhood', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'history-house-neighbor',
                                            options = [{'label': nbhd_name, 'value': nbhd_name} for nbhd_name in neighbor_prices['NBHD_NAME'].unique()],
                                            placeholder = 'Select from list'
                                        ),
                                    ),
                                ]),
                            ]),


                            dbc.CardBody([ # Sale price min-max
                                html.P('Sale Price', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'sale-price-min',
                                            options = [{'label': '${:,.0f}'.format(price_min), 'value': price_min} for price_min in [100000, 200000, 300000, 400000]],
                                            value = 90000,
                                            placeholder = 'min (USD)'
                                        ),
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'sale-price-max',
                                            options = [{'label': '${:,.0f}'.format(price_max), 'value': price_max} for price_max in [600000, 700000, 800000, 900000]],
                                            value = 1500000,
                                            placeholder = 'max (USD)'
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # Sale price min-max
                                html.P('Sale Year', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'sale-year-min',
                                            options = [{'label': year_min, 'value': year_min} for year_min in range(2000, 2010)],
                                            value = 2010,
                                            placeholder = 'min (year)'
                                        ),
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'sale-year-max',
                                            options = [{'label': year_max, 'value': year_max} for year_max in range(2010, 2019)],
                                            value = 2019,
                                            placeholder = 'max (year)'
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # Sale price min-max
                                html.P('Bedroom', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'history-bedroom-min',
                                            options = [{'label': bed_min, 'value': bed_min} for bed_min in [0, 1, 2]],
                                            placeholder = 'min (number)'
                                        ),
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'history-bedroom-max',
                                            options = [{'label': bed_max, 'value': bed_max} for bed_max in [3, 4, 5]],
                                            placeholder = 'max (number)'
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # above ground area min-max
                                html.P('Above Ground Area', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'history-area-min',
                                            options = [{'label': '{:,.0f}'.format(area_min), 'value': area_min} for area_min in [800, 1200, 1600, 2000]],
                                            value = 1000,
                                            placeholder = 'min (sqft)'
                                        ),
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'history-area-max',
                                            options = [{'label': '{:,.0f}'.format(area_max), 'value': area_max} for area_max in [2400, 2800, 3200, 3600]],
                                            value = 5000,
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
                                            id = 'hisotry-lot-min',
                                            options = [{'label': '{:,.0f}'.format(lot_min), 'value': lot_min} for lot_min in [3000, 4000, 5000, 6000]],
                                            value = 2000,
                                            placeholder = 'min (sqft)'
                                        ),
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'hisotry-lot-max',
                                            options = [{'label': '{:,.0f}'.format(lot_max), 'value': lot_max} for lot_max in [7000, 8000, 9000, 10000]],
                                            value = 10400,
                                            placeholder = 'max (sqft)'
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # story
                                html.P('Story', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'history-story',
                                            options = [{'label': story, 'value': story} for story in [1, 2, 3]],
                                            placeholder = 'Story',
                                        ),
                                    ),
                                ]),
                            ]),

                            html.Button('Confirm', id = 'confirm-history', n_clicks = 0),
                            html.Button('Reset', id = 'button-reset-history', n_clicks = 0),

                        ], color='danger', outline = True, id = 'dropdown-history', style = {'display': 'none'}),						   
                        
                        # side bar to see future
                        dbc.Card([
                            dbc.CardHeader('Search (leave blank if you do not have any preference)'),
                            dbc.CardBody([ # neighborhood selection
                                html.P('Neighborhood', className = 'card-title'),
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
                                            options = [{'label': beds, 'value': beds} for beds in [0, 1, 2, 3, 4, 5]],
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
                                            options = [{'label': baths, 'value': baths} for baths in [1, 2, 3, 4]],
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
                                            options = [{'label': story, 'value': story} for story in [1, 2, 3]],
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
                                            options = [{'label': age, 'value': age} for age in ['0 - 5', '5 - 10', '10 - 20', '20 - 50', '50 - 100']],
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
                                            options = [{'label': '{:,.0f}'.format(area_min), 'value': area_min} for area_min in [800, 1200, 1600, 2000]],
                                            value = 1000,
                                            placeholder = 'min (sqft)'
                                        ),
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-area-max',
                                            options = [{'label': '{:,.0f}'.format(area_max), 'value': area_max} for area_max in [2400, 2800, 3200, 3600]],
                                            value = 5000,
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
                                            options = [{'label': '{:,.0f}'.format(lot_min), 'value': lot_min} for lot_min in [1000, 2000, 3000, 4000]],
                                            value = 1500,
                                            placeholder = 'min (sqft)'
                                        ),
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-lot-max',
                                            options = [{'label': '{:,.0f}'.format(lot_max), 'value': lot_max} for lot_max in [5000, 6000, 7000, 8000]],
                                            value = 10400,
                                            placeholder = 'max (sqft)'
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # dist to park
                                html.P('Desired distance to Park', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-park',
                                            options = [{'label': '{:,.0f}'.format(m), 'value': m} for m in [250, 500, 1000, 1500, 3000]],
                                            placeholder = 'Maximum Distance to Park (meters)'
                                        ),
                                    ),
                                ]),
                            ]),

                            dbc.CardBody([ # dist to food stores
                                html.P('Desired distance to Food Store', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-store',
                                            options = [{'label': '{:,.0f}'.format(m), 'value': m} for m in [250, 500, 1000, 1500, 3000]],
                                            placeholder = 'Maximum Distance to Food Store (meters)'
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
                                            options = [{'label': m, 'value': i+1} for i, m in enumerate(months)],
                                            placeholder = 'Month'
                                        ),
                                    ),
                                ]),
                            ]),

                            html.Button('Confirm', id = 'confirm-predict', n_clicks = 0),
                            html.Button('Reset', id = 'button-reset-predict', n_clicks = 0),

                        ], color='danger', outline = True, id = 'dropdown-predict', style = {'display': 'none'})
                    ], className = 'three columns', style = {'margin-left': 30, 'margin-bottom': 10, 'margin-right': 0}),

                    html.Div([
                        dcc.Graph(
                            id = 'denver-house-map',
                            figure = draw_house_base_map(json_neighbor, neighbor_house_record),
                            style = {'height': '800px'}
                        ),
                        html.A('Download Table', id = 'save-table', style = {'display': 'none'}),
                        html.Div([
                            dcc.Input(id = "price-min", placeholder = 'Min ($)'),
                            dcc.Input(id = "price-max", placeholder = 'Max ($)'),
                            html.Button('Filter Results', id = 'button-filter-record', n_clicks = 0),
                            dt.DataTable(id = 'pred-table', columns = [{"name": i, "id": i} for i in city_data.columns], data = city_data.to_dict("records"))
                        ], id = 'div-filter-table', style= {'display': 'none'}),

                    ], id = 'house-map-chart', className = 'eight columns', style = {'margin-top': 35, 'margin-right': 0}),
                    
                    html.Div(id = 'house-info', className = 'two columns', style = {'margin-top': 35, 'margin-right': 0}),

                    html.Div(id = 'predict-table', style = {'display': 'none'}),

                ], className = 'row')
            ]),  

        # neighborhood tab        
        dcc.Tab(
            label='Denver Neighborhood', 
            className='custom-tab', 
            selected_className='custom-tab--selected',
            children = [ 
                dcc.Markdown('''
                    > *This page hosts the details of **Neighborhood features** (Median sales prices and homes sold record between 2000 and 2020, Neighborhood Amenities).*
                    '''), 
            html.Div([
                 # time series chart (5 cols) -- city level housing market information
                html.Div([
                    dcc.Dropdown(
                        id = 'neighbor-price-chart-list',
                        options = [
                            {'label': nbhd_name, 'value': nbhd_name} for nbhd_name in neighbor_prices['NBHD_NAME'].unique()
                        ],
                        value = ['Washington Park'], # washington park
                        multi = True,
                        placeholder = 'Select A Neighborhood to See Details',
                        style = {'margin-top': 5, 'margin-right': 30}
                    ),
                    dcc.Dropdown(
                        id = 'nbhd-metrics',
                        options = [
                            {'label': metric, 'value': metric} for metric in ["Median Sale Price","Home Sold"]
                        ],
                        value = 'Median Sale Price',
                        multi = False,
                        placeholder = 'Select Metrics',
                        style = {'margin-top': 5, 'margin-right': 30}
                    ),
                    
                    dcc.Dropdown(
                        id = 'nbhd-info',
                        options = [
                            {'label': sector, 'value': sector} for sector in sectors
                        ],
                        multi = False,
                        placeholder = 'Select A Sector for More Info of Neighborhoods'
                    ),

                    html.Div(id = 'neighbor-table', style = {'margin-left': 20, 'margin-right': 40, 'margin-top': 35}),
                    
                    dcc.Graph(
                        id = 'neighbor-price-chart',
                        config = {'responsive': True, 'autosizable': True}
                    )
                ], className = 'four columns'),

                # neighborhood map (7 cols)
                html.Div([  
                    dcc.Graph(
                        id = 'denver-map',
                        figure = draw_base_map(json_neighbor, neighbor_prices,neighbor_house_record,[]),
                    ),
                ],
                className = 'eight columns',
                title = 'Select Neighborhoods to See Details'
                ),
            ],
            className = 'row', style = {'margin-right': 30, 'margin-top': 20, 'margin-left': 30}),
            html.Div([ 
                    dcc.Markdown('>*Neighborhood Amenities*', id = 'stores-map-header', style = {'display': 'none'}),
                    dcc.Graph(
                        id = 'stores-map'
                    ),
                ],
            id = "stores-div",
            className = 'seven columns'),
        ]),

        # city tab
        dcc.Tab(
            label = 'Denver City',  
            className = 'custom-tab', 
            selected_className = 'custom-tab--selected',
            children = [
                dcc.Markdown('> *This page hosts comparisons among similar cities with Denver.*'),

                html.Div([
                    html.Div([
                        html.Div(children=[
                            dcc.Markdown('''> *Comparison with National and State Levels*'''),
                            html.Label('Metrics Selection'),
                            dcc.Dropdown(
                                id="nsc_met",
                                options=[
                                    {'value': metric, 'label': metric} 
                                    for metric in metrics
                                ],
                                value='Median Sale Price',
                                multi=False
                            ),
                            ], id = 'multi-level-comp', style = {'margin-right': 50}
                        ),

                        html.Div([
                            dcc.Graph(id='nsc')
                            ], id = 'multi-level-comp-chart', style = {'margin-right': 10, 'margin-top': 50}), 
                        ], className = 'six columns', style = {'margin-right': 10, 'margin-left': 10},
                    ),

                    html.Div([
                        html.Div(children=[
                            dcc.Markdown('''> *Comparison between Different Cities*'''),
                            html.Label('City Selection'),
                            dcc.Dropdown(
                                id="cities",
                                options=[
                                    {'value': city, 'label': city} 
                                    for city in cities if (city!="National" and city!="Colorado")
                                ],
                                value=['Denver, CO',"Portland, OR","Salt Lake City, UT"],
                                multi=True
                            ),
                            html.Label('Metrics Selection'),
                            dcc.Dropdown(
                                id="ccc_met",
                                options=[
                                    {'value': metric, 'label': metric} 
                                    for metric in metrics
                                ],
                                value='Median Sale Price',
                                multi=False
                            ),
                        ], id = 'city-level-comp', style = {'margin-right': 50}),
                        
                        html.Div([
                            dcc.Graph(id='ccc')
                        ], id = 'city-level-comp-chart', style = {'margin-right': 10} )

                    ], className = 'six columns', style = {'margin-right': 10, 'margin-left': 10})
                ], className = 'row', style = {'margin-right': 30, 'margin-left': 30})
            ]),

        dcc.Tab(
            label = 'About',
            className = 'custom-tab',
            selected_className = 'custom-tab--selected',
            children = write_about()
        ),
     ]),
])

# callback to show house information
@app.callback(
    [Output('house-info', 'children'),
     Output('house-map-chart', 'className')
    ],
    [Input('denver-house-map', 'selectedData'),
    Input('button-reset-history', 'n_clicks'),
    Input('button-predict', 'n_clicks')
    ]
)
def select_from_house_map(sel_house, n_clicks, button_predict_clicks):
    _, api_key = grab_credentials()
    pre_string = 'https://maps.googleapis.com/maps/api/streetview?size=200x200&location='
    aft_string = '&fov=40&key='+ api_key
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if sel_house is None or sel_house == [] or n_clicks > 0 or button_id == 'button-predict':
        return [[], 'eight columns']
    else:
        sel_house_df = [family_demo[family_demo['SCHEDNUM']==i['location']] for i in sel_house['points']]
        if api_key == '':
            text = [
                    '''
                    >Address: *[{}, Denver, CO {}]({})*

                    >Year Built: *{}*

                    >Year Sold: *{}*

                    >Sale Price: *${:,.0f}*

                    >Lot Size: *{:,.0f} sqft*

                    >Above Groud Area: *{:,.0f} sqft*

                    >Story: *{}*

                    >Bedrooms: *{}*

                    >Full Bathrooms: *{:,.0f}*

                    >Half Bathrooms: *{:,.0f}*

                    >Basement: *{:,.0f} sqft*

                    >Furnished Basement: *{:,.0f} sqft*

                    >Garden Area: *{:,.0f} sqft*

                    '''.format(row['SITUS_AD_1'].values[0], row['SITUS_ZIP'].values[0], 'https://www.google.com/maps/place/'+ '+'.join(row['SITUS_AD_1'].values[0].split()) + ',+Denver,+CO' + '+' + row['SITUS_ZIP'].values[0], row['CCYRBLT'].values[0], int(row['SALE_YEAR'].values[0]), int(row['SALE_PRICE'].values[0]), int(row['LAND'].values[0]), int(row['AREA_ABG'].values[0])
                    , row['STORY'].values[0], row['BED_RMS'].values[0], row['FULL_B'].values[0], row['HLF_B'].values[0], int(row['BSMT_AREA'].values[0]), int(row['FBSMT_SQFT'].values[0]), int(row['GRD_AREA'].values[0])
                    )
                for row in sel_house_df ]
        else:
            text = [
                '''
                >Address: *[{}, Denver, CO {}]({})*

                >Year Built: *{}*

                >Year Sold: *{}*

                >Sale Price: *${:,.0f}*

                >Lot Size: *{:,.0f} sqft*

                >Above Groud Area: *{:,.0f} sqft*

                >Story: *{}*

                >Bedrooms: *{}*

                >Full Bathrooms: *{:,.0f}*

                >Half Bathrooms: *{:,.0f}*

                >Basement: *{:,.0f} sqft*

                >Furnished Basement: *{:,.0f} sqft*

                >Garden Area: *{:,.0f} sqft*

                >Street View: 

                >![Street View]({} 'Street View')

                '''.format(row['SITUS_AD_1'].values[0], row['SITUS_ZIP'].values[0], 'https://www.google.com/maps/place/'+ '+'.join(row['SITUS_AD_1'].values[0].split()) + ',+Denver,+CO' + '+' + row['SITUS_ZIP'].values[0], row['CCYRBLT'].values[0], int(row['SALE_YEAR'].values[0]), int(row['SALE_PRICE'].values[0]), int(row['LAND'].values[0]), int(row['AREA_ABG'].values[0])
                , row['STORY'].values[0], row['BED_RMS'].values[0], row['FULL_B'].values[0], row['HLF_B'].values[0], int(row['BSMT_AREA'].values[0]), int(row['FBSMT_SQFT'].values[0]), int(row['GRD_AREA'].values[0]),
                pre_string+ '+'.join(row['SITUS_AD_1'].values[0].split()) + ',+Denver,+CO' + '+' + row['SITUS_ZIP'].values[0]+aft_string)
            for row in sel_house_df ]
        
        data = html.Div([
            dbc.CardHeader("Sale Record"),
            dbc.CardBody(
                [
                    dcc.Markdown("**Barnum West**", className="card-title"),
                    dcc.Markdown(children = text, className = 'card-text'),
                ]
            ),
        ])
        return [data, 'six columns']

# Callback to update house hunting map to reflect history
@app.callback(
    [Output('denver-house-map', 'figure'),
    Output('denver-house-map', 'style'),
    Output('dropdown-history', 'style')],
    [Input('sale-price-min', 'value'),
     Input('sale-price-max', 'value'),
     Input('sale-year-min', 'value'),
     Input('sale-year-max', 'value'),
     Input('history-bedroom-min', 'value'),
     Input('history-bedroom-max', 'value'),
     Input('history-area-min', 'value'),
     Input('history-area-max', 'value'),
     Input('hisotry-lot-min', 'value'),
     Input('hisotry-lot-max', 'value'),
     Input('history-house-neighbor', 'value'),
     Input('history-story', 'value'),
     Input('button-history', 'n_clicks'),
     Input('confirm-history', 'n_clicks'),
     Input('button-predict', 'n_clicks'),
    ]
)
def update_house_map(min_price, max_price, min_year, max_year, min_bed, max_bed, minarea, maxarea, minlot, maxlot, neighbor, story, nclicks, confirm_sel, button_predict_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if nclicks == 0 or button_id == 'button-predict':
        return [draw_house_base_map(json_neighbor, neighbor_house_record), {'height': '100%'}, {'display': 'none'}]  
    elif nclicks > 0 and confirm_sel > 0:
        json_filtered, family_demo_filtered = family_demo_filter(min_price, max_price, min_year, max_year, min_bed, max_bed, minarea, maxarea, minlot, maxlot, neighbor, story, family_demo, json_single_family)
        if neighbor is None:
            neighbor = 'Athmar Park'
        return [update_house_base_map(json_filtered, family_demo_filtered, json_neighbor, neighbor_house_record, neighbor), {'height': '100%'}, {'display': 'block'}]
    elif nclicks > 0 and confirm_sel == 0 and neighbor is None:
        return [draw_house_base_map(json_neighbor, neighbor_house_record), {'height': '100%'}, {'display': 'block'}] 
    else:
        raise PreventUpdate

# callback to filter prediction table
@app.callback(
    Output('pred-table', 'data'),
    [Input('price-min', 'value'),
     Input('price-max', 'value'),
     Input('button-filter-record', 'n_clicks'),
     Input('predict-table', 'children')
    ]
)
def filter_predict_table(minprice, maxprice, n_clicks, values):
    if n_clicks == 0:
        raise PreventUpdate
    else:
        df = pd.read_json(values)
        max_price = df[df['Predicted Price ($)'] == max(df['Predicted Price ($)'])]['Predicted Price ($)'].values[0]
        min_price = df[df['Predicted Price ($)'] == min(df['Predicted Price ($)'])]['Predicted Price ($)'].values[0]
        if minprice is None:
            minprice = min_price
        if maxprice is None:
            maxprice = max_price

        try:
            minprice = float(minprice)
        except ValueError:
            minprice = min_price
        
        try:
            maxprice = float(maxprice)
        except ValueError:
            maxprice = max_price

        if minprice < min_price:
            minprice = min_price
        if maxprice > max_price:
            maxprice = max_price

        return df[(df['Predicted Price ($)'] >= minprice) & (df['Predicted Price ($)'] <= maxprice)].to_dict('records')

# callback to predict house price
@app.callback(
    [Output('house-map-chart', 'children'),
    Output('predict-table', 'children'),
    Output('dropdown-predict', 'style')
    ],     # replace map with a prediction table
    [Input('house-neighbor', 'value'), # which neighborhood
     Input('house-bedroom', 'value'),  # how many bedrooms
     Input('house-bathroom', 'value'), # how may bathrooms
     Input('house-story', 'value'), # how many story
     Input('house-age', 'value'), # age of house
     Input('house-area-min', 'value'), # min above ground area
     Input('house-area-max', 'value'), # max above ground area
     Input('house-lot-min', 'value'), # min lot size
     Input('house-lot-max', 'value'), # max lot size
     Input('house-park', 'value'), # distance to park
     Input('house-store', 'value'), # distance to store
     Input('house-month', 'value'), # month of year buying
     Input('button-predict', 'n_clicks'),
     Input('confirm-predict', 'n_clicks'),
     Input('button-history', 'n_clicks'),
    ]
)
def predict_house_price(neighbor, bed, bath, story, age, minarea, maxarea, minlot, maxlot, park, store, month, n_clicks, confirm_sel, button_history_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = ''
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if n_clicks == 0 or button_id == 'button-history':
        return [
            [
                dcc.Graph(
                    id = 'denver-house-map',
                    figure = draw_house_base_map(json_neighbor, neighbor_house_record),
                    style = {'height': '700px'}
                ),
                html.A('Download Table', id = 'save-table', style = {'display': 'none'}),
                html.Div([
                            dcc.Input(id = "price-min", placeholder = 'Min ($)'),
                            dcc.Input(id = "price-max", placeholder = 'Max ($)'),
                            html.Button('Filter Results', id = 'button-filter-record', n_clicks = 0),
                            dt.DataTable(id = 'pred-table', columns = [{"name": i, "id": i} for i in city_data.columns], data = city_data.to_dict("records")),
                        ], id = 'div-filter-table', style= {'display': 'none'}),
                
            ],'', {'display': 'none'}
        ]
    elif n_clicks == 1 and confirm_sel == 0:
        if neighbor is None:
            return [
                [
                    dcc.Graph(
                        id = 'denver-house-map',
                        figure = draw_house_base_map(json_neighbor, neighbor_house_record),
                        style = {'height': '100%'}
                    ), 
                    html.A('Download Table', id = 'save-table', style = {'display': 'none'}),
                    html.Div([
                        dcc.Input(id = "price-min", placeholder = 'Min ($)'),
                        dcc.Input(id = "price-max", placeholder = 'Max ($)'),
                        html.Button('Filter Results', id = 'button-filter-record', n_clicks = 0),
                        dt.DataTable(id = 'pred-table', columns = [{"name": i, "id": i} for i in city_data.columns], data = city_data.to_dict("records")),
                    ], id = 'div-filter-table', style= {'display': 'none'}),
                ]
            ,'', {'display': 'block'}
            ]
        else:
            raise PreventUpdate
    elif confirm_sel > 0 and n_clicks >= 1:
        predict_tab = predict_house_xgb(neighbor, bed, bath, story, age, minarea, maxarea, minlot, maxlot, park, store, month, neighbor_stats, neighbor_demo, cpi)
        max_price = predict_tab[predict_tab['Predicted Price ($)'] == max(predict_tab['Predicted Price ($)'])]
        min_price = predict_tab[predict_tab['Predicted Price ($)'] == min(predict_tab['Predicted Price ($)'])]

        year = 2020
        if month is None:
            month = 6
        if neighbor is None:
            neighbor = 'Athmar Park'
        return [[
            dcc.Markdown('> *Predicted Single Family House Price*, **{0!s}**, **{2:0>2}/{1!s}**'.format(neighbor, year, month)),
            dcc.Markdown('*Highest* Predicted Price at **${:,.0f}** with *{}* stories, *{}* bedrooms, *{}* bathrooms, *{:,.0f}sqft* above ground area, *{:,.0f}sqft* lot zize, {:,.0f} meter to closest park, and {:,.0f} meter to closest food stores.'
            .format(max_price['Predicted Price ($)'].values[0], max_price['Story'].values[0], max_price['Bedrooms'].values[0], max_price['Bathrooms'].values[0], max_price['Above Ground Area (sqft)'].values[0], max_price['Lot Size (sqft)'].values[0], max_price['Distance to Park (meters)'].values[0], max_price['Distance to Food Stores (meters)'].values[0])),
            
            html.P(),

            dcc.Markdown('*Lowest* Predicted Price at **${:,.0f}** with *{}* stories, *{}* bedrooms, *{}* bathrooms, *{:,.0f}sqft* above ground area, *{:,.0f}sqft* lot zize, {:,.0f} meter to closest park, and {:,.0f} meter to closest food stores.'
            .format(min_price['Predicted Price ($)'].values[0], min_price['Story'].values[0], min_price['Bedrooms'].values[0], min_price['Bathrooms'].values[0], min_price['Above Ground Area (sqft)'].values[0], min_price['Lot Size (sqft)'].values[0], min_price['Distance to Park (meters)'].values[0], min_price['Distance to Food Stores (meters)'].values[0])),

            html.Code('Show results only for price ranged: '),
            dcc.Input(id = "price-min", placeholder = 'Min ($)'),
            dcc.Input(id = "price-max", placeholder = 'Max ($)'),
            html.Button('Filter Results', id = 'button-filter-record', n_clicks = 0),
            
            html.P(),

            dt.DataTable(
                id = 'pred-table',
                columns = [{'name': i, 'id': i} for i in predict_tab.columns],
                data = predict_tab.to_dict('records'),
                style_header={
                    'fontWeight': 'bold',
                },
                style_table={
                    'maxHeight': '800px',
                },
                style_cell={
                    'height': 'auto',
                    'minWidth': '0px', 'width': '100px', 'maxWidth': '180px',
                    'whiteSpace': 'normal'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ],
                fixed_rows = { 'headers': True, 'data': 0 },
                page_current = 0,
                page_size = 100,
                sort_action = "native",
                sort_mode = "multi",
                page_action = "native",
            ),
            html.A('Download Table', id = 'save-table', download = "denver-house-price-prediction.csv", target = '_blank', style = {'margin-top': 20}),
            ], json.dumps(predict_tab.to_dict('records'), indent = 2), {'display': 'block'}]
    else:
        raise PreventUpdate

# callback to save data
@app.callback(
    Output('save-table', 'href'),
    [Input('save-table', 'style'),
    Input('predict-table', 'children')]
)
def save_predict_table(style, values):
    if 'display' not in style:
        df = pd.read_json(values)
        dfcsv = df.to_csv(index=False, encoding='utf-8')
        dfcsv = "data:text/csv;charset=utf-8," + urllib.parse.quote(dfcsv)
        return dfcsv

# callback to reset prediction selection
@app.callback(
    [Output('button-predict', 'n_clicks'),
     Output('confirm-predict', 'n_clicks'),
     Output('house-neighbor', 'value'), # which neighborhood
     Output('house-bedroom', 'value'),  # how many bedrooms
     Output('house-bathroom', 'value'), # how may bathrooms
     Output('house-story', 'value'), # how many story
     Output('house-age', 'value'), # age of house
     Output('house-area-min', 'value'), # min above ground area
     Output('house-area-max', 'value'), # max above ground area
     Output('house-lot-min', 'value'), # min lot size
     Output('house-lot-max', 'value'), # max lot size
     Output('house-park', 'value'), # park
     Output('house-store', 'value'), # store
     Output('house-month', 'value'), # month of year buying
     ],
    [Input('button-reset-predict', 'n_clicks')]
)
def reset_house_predict(n_clicks):
    if n_clicks > 0:
        return (0, 0,
        None, None, None, None, None, 1000, 5000, 1500, 10400, None, None, None
        )
    else:
        raise PreventUpdate

# callback to reset history selection
@app.callback(
    [Output('button-history', 'n_clicks'),
     Output('confirm-history', 'n_clicks'),
     Output('sale-price-min', 'value'),# check history
     Output('sale-price-max', 'value'),
     Output('sale-year-min', 'value'),
     Output('sale-year-max', 'value'),
     Output('history-bedroom-min', 'value'),
     Output('history-bedroom-max', 'value'),
     Output('history-area-min', 'value'),
     Output('history-area-max', 'value'),
     Output('hisotry-lot-min', 'value'),
     Output('hisotry-lot-max', 'value'),
     Output('history-house-neighbor', 'value'),
     Output('history-story', 'value'),
     ],
    [Input('button-reset-history', 'n_clicks')]
)
def reset_house_history(n_clicks):
    if n_clicks > 0:
        return (0, 0,
        150000, 1000000, 2010, 2019, None, None, 1000, 5000, 2000, 10400, None, None
        )
    else:
        raise PreventUpdate

# callback to select neighborhoods for comparison
@app.callback(
    Output('neighbor-price-chart-list', 'value'),
    [Input('denver-map', 'selectedData'),
    Input('denver-map', 'clickData')],
    [State('neighbor-price-chart-list', 'value')]
)
def select_from_map(sel_nbhd,curr_sel,curr_nbhd):
    if sel_nbhd is None or sel_nbhd == []:
        return []
    elif len(sel_nbhd['points'])==1:
        return [i['location'] for i in sel_nbhd['points']]
    else:
        sel_names = set([i['location'] for i in sel_nbhd['points']])
        curr_names = set([i['location'] for i in curr_sel['points']])
        nbhd_names = sel_names.intersection(curr_nbhd).union(curr_names)
        nbhd_names = list(nbhd_names.union(set(curr_nbhd)))
        nbhd_names = list(sorted(nbhd_names))
        return nbhd_names


# callback to update maps from chart list value
@app.callback(
    Output('denver-map', 'figure'),
    [Input('neighbor-price-chart-list', 'value'),
    Input('denver-map', 'clickData')]
)
def update_neighbor_map(sel_nbhd,sel_cli):
    ctx = dash.callback_context
    if len(sel_nbhd)==0 and sel_cli=={} and ctx=={}:
		 
        raise PreventUpdate
    return draw_base_map(json_neighbor, neighbor_prices,neighbor_house_record,sel_nbhd)

# create neighborhood quality dropdown list

# callbacks to display map of stores in nbhd
@app.callback(
    Output('stores-div', 'style'),
    [Input('neighbor-price-chart-list', 'value')]
)
def map_display(sel_val):
    if sel_val==None or len(sel_val)==0:
        return {"display":"none"}
    return {"display":"contents"}

@app.callback(
    [Output('stores-map','figure'),
    Output('stores-map-header', 'style')
    ],
    [Input('neighbor-price-chart-list', 'value')]
)
def update_stores_map(sel_val):
    if sel_val is None or len(sel_val) == 0:
        raise PreventUpdate
    return [draw_store_map(sel_val, features, parks, json_neighbor, neighbor_house_record), {'display': 'block'}]

# callback to update neighbor price chart
@app.callback(
    Output('nbhd-info', 'style'),
    [Input('neighbor-price-chart-list', 'value')]
)
def show_choice(sel_val):
    if sel_val is None or len(sel_val) == 0:
        return {'margin-top': 0, 'margin-right': 30,"display":"none"}
    return {'margin-top': 0, 'margin-right': 30}

# create table for neighborhood statistics
@app.callback(
    Output('neighbor-table', 'children'),
    [Input('neighbor-price-chart-list', 'value'),
    Input('nbhd-info','value')]
)
def print_neighbor_table(sel_val1,sel_val2): # Inspired by https://dash.plotly.com/datatable
    if sel_val1 is None or len(sel_val1) == 0:
        return []
    if sel_val2 is None or len(sel_val2) == 0:
        raise PreventUpdate
    df = nbhd_stats.loc[nbhd_stats["Neighborhood"].isin(sel_val1),sectors[sel_val2]]
    return [
        dt.DataTable(
            id = 'nbhd-table',
            columns = [{"name": i, "id": i} for i in df.columns],
            data = df.to_dict("records"),
        ),
    ]
    
# callback to update neighbor price chart
@app.callback(
    Output('neighbor-price-chart', 'figure'),
    [Input('neighbor-price-chart-list', 'value'),
    Input('nbhd-metrics','value')]
)
def update_neighbor_price_chart(sel_value,sel_met):
    price_data = []
    frames = []
    steps = []
    if sel_met==None or len(sel_met)==0:
        title = "Median Sale Price"
        met = "SALE_PRICE"
        scale = 50
    elif sel_met == "Median Sale Price":
        met = "SALE_PRICE"
        title = sel_met
        scale = 50
    else:
        met = sel_met
        title = sel_met
        scale = 0.5


    years = neighbor_prices['SALE_YEAR'].unique()
    if sel_value is None or sel_value == []:
        for year in years:
            frames.append({
                'data': [{
                    'y': neighbor_prices[neighbor_prices['SALE_YEAR'] == year]['NBHD_NAME'].apply(lambda x: x.split('/')[0]),
                    'x': neighbor_prices[neighbor_prices['SALE_YEAR'] == year][met],
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
                'x': neighbor_prices[neighbor_prices['SALE_YEAR'] == 2000][met],
                'type': 'bar',
                'orientation': 'h',
                'name': 2000
            }],
            'frames': frames,
            'layout': {
                'title': title, 
                'hovermode': 'closest',
                'showlegend': True,
                'xaxis': {
                    'showline': True,
                    'linecolor': 'gray',
                    'mirror': True,
                    'showgrid': False,
                    'ticks': 'outside',
                    'range': [min(neighbor_prices[met]), max(neighbor_prices[met]) + min(neighbor_prices[met])]
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
    temp = ""
    if len(sel_value)==1:
        temp=" of "+sel_value[0]
    for val in sel_value:
        data = {
            'x': neighbor_prices[neighbor_prices['NBHD_NAME'] == val]['SALE_YEAR'],
            'y': neighbor_prices[neighbor_prices['NBHD_NAME'] == val][met],
            'name': val,
            'mode': 'markers',
            'marker': {
                'size': np.sqrt(neighbor_prices[neighbor_prices['NBHD_NAME'] == val][met]) / scale,
            },
            'textposition': 'top center',
            'log_x': True,
        }
        price_data.append(data)
    return {
        'data': price_data,
        'layout': {
            'title': title+temp, 
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
                'title': {'text': title, 'standoff': 40},
                'showline': True,
                'showgrid': True,
                'gridcolor': 'WhiteSmoke',
                'linecolor': 'gray',
                'mirror': True,
            },
            'height': 400,
            'margin': {'l': 50, 'r': 40},
            'legend':{'x': 0, 'y': 1},
        },
    }


@app.callback(
    Output('nsc','figure'),
    [Input('nsc_met','value')]
)
def update_fig_nsc(sel_met):
    if sel_met == None or len(sel_met)==0:
        met="Median Sale Price"
    else:
        met=sel_met

    out_data=[]
    if met in ["Seasonality of Median Price","Seasonality of Home Sold"]:
        met_temp="Avg_"+"_".join(met.replace("of","").split())
        for city in ["National","Colorado","Denver, CO"]:
            out_data.append({
                            "x" : [mo[:3] for mo in months],
                            "y" : city_seasonality.loc[city_seasonality["City"]==city,met_temp],
                            "type" : "bar",
                            "name" : city 
                            })
            xa = {'title':'Month of the Year'}
            ya = {'title':"Normalized Pct",'type':'log'}
    else:
        xa = {'title':'Time'}
        for city in ["National","Colorado","Denver, CO"]:
            out_data.append({
                            "x" : city_data.loc[city_data["Region"]==city,"Month of Period End"],
                            "y" : city_data.loc[city_data["Region"]==city,met],
                            "mode" : "markers+lines",
                            "name" : city 
                            })
        if met == "Median Sale Price":
            ya= {'title':'House Sales Prices (K$)'}
        elif met in ["Homes Sold","New Listings","Inventory","Average Sale To List"]:
            ya = {'title':met,'type':'log'}
        else:
            ya = {'title':met}
    return {
                'data': out_data,
                'layout': {
                    "title":met,
                    'autosize': True,
                    "xaxis":xa,
                    "yaxis":ya
                }
            }

@app.callback(
    Output('ccc','figure'),
    [Input('cities','value'), Input('ccc_met','value')]
)

def update_city_fig_ccc(sel_city,sel_met):
    temp=""
    if sel_city == None or len(sel_city)==0:
        sel_city=["Denver, CO"]
        temp=" of "+sel_city[0]
    if len(sel_city)==1:
        temp=" of "+sel_city[0]
    if sel_met == None or len(sel_met)==0:
        sel_met="Median Sale Price"
    out_data=[]
    if sel_met in ["Seasonality of Median Price","Seasonality of Home Sold"]:
        met_temp="Avg_"+"_".join(sel_met.replace("of","").split())
        for city in sel_city:
            out_data.append({
                            "x" : [mo[:3] for mo in months],
                            "y" : city_seasonality.loc[city_seasonality["City"]==city,met_temp],
                            "type" : "bar",
                            "name" : city 
                            })
            xa = {'title':'Month of the Year'}
            ya = {'title':"Normalized Pct",'type':'log'}
    else:
        xa = {'title':'Time'}
        for city in sel_city:
            out_data.append({
                            "x" : city_data.loc[city_data["Region"]==city,"Month of Period End"],
                            "y" : city_data.loc[city_data["Region"]==city,sel_met],
                            "mode" : "markers+lines",
                            "name" : city 
                            })
        if sel_met == "Median Sale Price":
            ya= {'title':'House Sales Prices (K$)'}
        elif sel_met in ["Homes Sold","New Listings","Inventory","Average Sale To List"]:
            ya = {'title':sel_met,'type':'log'}
        else:
            ya = {'title':sel_met}
    return {
                'data': out_data,
                'layout': {
                    "title":sel_met+temp,
                    'autosize': True,
                    "xaxis":xa,
                    "yaxis":ya
                }
            } 

if __name__ == '__main__':
    #pass
    app.run_server(debug = True)