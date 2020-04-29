from utils import load_files, draw_base_map, draw_house_base_map, update_house_base_map, predict_house_xgb, draw_family_base_map, write_about, load_markdowns, load_app_header

import os, json, urllib
import pandas as pd

try:
    import dash
except:
    os.system("pip install dash==1.9.1")
    import dash

import dash_core_components as dcc
import dash_html_components as html

try:
    import dash_bootstrap_components as dbc
except:
    os.system("pip install dash-bootstrap-components==1.1.1")
    import dash_bootstrap_components as dbc

try:
    import dash_table as dt
except:
    os.system("pip install dash-table==4.6.1")
    import dash_table as dt

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# responsive style sheet
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server

json_neighbor, neighbor_prices, json_neighbor_centers, json_single_family, neighbor_house_record, metrics, cities, city_data, family_dist, family_demo, city_seasonality, neighbor_demo, neighbor_stats, nbhd_stats, sectors, cpi= load_files()

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
    html.H4(children = 'Denver House Price Record and Prediction', style = {
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
                        html.Button('See future', id = 'button-future', n_clicks = 0),
                        html.Button('Reset', id = 'button-reset', n_clicks = 0),

                        # side bar
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
                                            options = [{'label': baths, 'value': baths} for baths in [1,2,3,4,5]],
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
                                            options = [{'label': area_min, 'value': area_min} for area_min in family_demo['AREA_ABG'].quantile([.1, .2, .3, .4, .5]) // 100 * 100],
                                            value = 600,
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

                            dbc.CardBody([ # dist to park
                                html.P('Desired distance to Park', className = 'card-title'),
                                dbc.Row([
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'house-park',
                                            options = [{'label': m, 'value': m} for m in [250, 500, 1000, 1500, 3000]],
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
                                            options = [{'label': m, 'value': m} for m in [250, 500, 1000, 1500, 3000]],
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

                            html.Button('Confirm', id = 'confirm-predict', n_clicks = 0)
                        ], color='danger', outline = True, id = 'dropdown-predict', style = {'display': 'none'})
                    ], className = 'three columns', style = {'margin-left': 30, 'margin-bottom': 10}),

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

                    ], id = 'house-map-chart', className = 'eight columns', style = {'margin-right': 30}),
                    
                    html.Div(id = 'predict-table', style = {'display': 'none'}),

                ], className = 'row')
            ]),  

        # neighborhood tab        
        dcc.Tab(
            label='Denver Neighborhood', 
            className='custom-tab', 
            selected_className='custom-tab--selected',
            children = [ 
            html.Div([
                # neighborhood map (7 cols)
                html.Div([  
                    dcc.Graph(
                        id = 'denver-map',
                        figure = draw_base_map(json_neighbor, neighbor_prices),
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
                        placeholder = 'Select A Neighborhood',
                        style = {'margin-top': 10, 'margin-right': 30}
                    ),

                    dcc.Dropdown(
                        id = 'nbhd-metrics',
                        options = [
                            {'label': metric, 'value': metric} for metric in ["Median Sale Price","Home Sold"]
                        ],
                        value = 'Median Sale Price',
                        multi = False,
                        placeholder = 'Select Metrics',
                        style = {'margin-top': 10, 'margin-right': 30}
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
                    ),
                ],
                className = 'five columns'
                ),
            ],
            className = 'row', style = {'margin-right': 30, 'margin-top': 10, 'margin-left': 30})
        ]),

        # city tab
        dcc.Tab(
            label = 'Denver City', 
            className = 'custom-tab', 
            selected_className = 'custom-tab--selected',
            children = [
                html.H6(children='City-Level Comparison'),

                html.Div([
                    html.Div(children=[
                        dcc.Markdown('''> *Comparison in National, State and City Levels*'''),
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
                ], className = 'six columns', style = {'margin-right': 20, 'margin-left': 30},
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
            ]),

        dcc.Tab(
            label = 'About',
            className = 'custom-tab',
            selected_className = 'custom-tab--selected',
            children = write_about()
        ),
     ]),
])

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
     Input('button-future', 'n_clicks'),
     Input('confirm-predict', 'n_clicks')
    ]
)
def predict_house_price(neighbor, bed, bath, story, age, minarea, maxarea, minlot, maxlot, park, store, month, n_clicks, confirm_sel):
    if n_clicks == 1 and confirm_sel == 0 and neighbor is None:
        return [
            [
                dcc.Graph(
                    id = 'denver-house-map',
                    figure = draw_house_base_map(json_neighbor, neighbor_house_record),
                    style = {'height': '1000px'}
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

    if confirm_sel > 0:
        predict_tab = predict_house_xgb(neighbor, bed, bath, story, age, minarea, maxarea, minlot, maxlot, park, store, month, neighbor_stats, neighbor_demo, cpi)
        max_price = predict_tab[predict_tab['Predicted Price ($)'] == max(predict_tab['Predicted Price ($)'])]
        min_price = predict_tab[predict_tab['Predicted Price ($)'] == min(predict_tab['Predicted Price ($)'])]

        year = 2020
        if month is None:
            month = 6
        if neighbor  is None:
            neighbor = 'Athmar Park'
        return [[
            dcc.Markdown('> *Predicted Single Family House Price*, **{0!s}**, **{2:0>2}/{1!s}**'.format(neighbor, year, month)),
            dcc.Markdown('*Highest* Predicted Price at **${:,.0f}** with *{}* stories, *{}* bedrooms, *{}* bathrooms, *{:,.0f}sqft* above ground area, *{:,.0f}sqft* lot zize, *{:,.0f}sqft* garden area, {:,.0f} meter to closest park, and {:,.0f} meter to closest food stores.'
            .format(max_price['Predicted Price ($)'].values[0], max_price['Story'].values[0], max_price['Bedrooms'].values[0], max_price['Bathrooms'].values[0], max_price['Above Ground Area (sqft)'].values[0], max_price['Lot Size (sqft)'].values[0], max_price['Garden Area (sqft)'].values[0], max_price['Distance to Park (meters)'].values[0], max_price['Distance to Food Stores (meters)'].values[0])),
            
            html.P(),

            dcc.Markdown('*Lowest* Predicted Price at **${:,.0f}** with *{}* stories, *{}* bedrooms, *{}* bathrooms, *{:,.0f}sqft* above ground area, *{:,.0f}sqft* lot zize, *{:,.0f}sqft* garden area, {:,.0f} meter to closest park, and {:,.0f} meter to closest food stores.'
            .format(min_price['Predicted Price ($)'].values[0], min_price['Story'].values[0], min_price['Bedrooms'].values[0], min_price['Bathrooms'].values[0], min_price['Above Ground Area (sqft)'].values[0], min_price['Lot Size (sqft)'].values[0], min_price['Garden Area (sqft)'].values[0], min_price['Distance to Park (meters)'].values[0], min_price['Distance to Food Stores (meters)'].values[0])),

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
    elif neighbor is not None or bed is not None or bath is not None or story is not None or age is not None or month is not None or park is not None or store is not None:
        raise PreventUpdate
    else:
        return [
            [
                dcc.Graph(
                    id = 'denver-house-map',
                    figure = draw_house_base_map(json_neighbor, neighbor_house_record),
                    style = {'height': '1000px'}
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

# callback to reset selection
@app.callback(
    [Output('button-history', 'n_clicks'),
     Output('button-future', 'n_clicks'),
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
     Output('house-month', 'value'), ],# month of year buying
    [Input('button-reset', 'n_clicks')]
)
def reset_house_predict(n_clicks):
    if n_clicks > 0:
        return (0, 0, 0, None, None, None, None, None, 
        family_demo['AREA_ABG'].min(), family_demo['AREA_ABG'].max(),
        family_demo['LAND_SQFT'].min(),family_demo['LAND_SQFT'].max(),
         None, None, None)
    else:
        raise PreventUpdate

# callback to update house hunting map to reflect neighborhood selection
@app.callback(
    Output('denver-house-map', 'figure'),
    [Input('house-neighbor', 'value')]
)
def update_house_map(sel_nbhd):
    if sel_nbhd is None:
        return draw_house_base_map(json_neighbor, neighbor_house_record)
    else:
        return update_house_base_map(sel_nbhd, json_neighbor, neighbor_house_record)

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
        return draw_base_map(json_neighbor, neighbor_prices)
    else:
        raise PreventUpdate

# create neighborhood quality dropdown list
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
        scale = 20000
    elif sel_met == "Median Sale Price":
        met = "SALE_PRICE"
        title = sel_met
        scale = 20000
    else:
        met = sel_met
        title = sel_met
        scale = 5

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
                'size': neighbor_prices[neighbor_prices['NBHD_NAME'] == val][met] / scale,
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
            'height': 500,
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
    app.run_server(debug=True)