from utils import *

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
    os.system("pip install dash-bootstrap-components")
    import dash_bootstrap_components as dbc
try:
    import dash_bio as dashbio
except:
    os.system("pip install dash-bio==0.4.8")
    import dash_bio as dashbio

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# responsive style sheet
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server

json_neighbor, neighbor_prices, json_neighbor_centers, single_family, neighbor_house_record, metrics, cities, city_data, family_dist, family_demo, city_seasonality = load_files()

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

app.layout = html.Div([
    html.H4(children = 'Denver House Price Record and Prediction', style = {
        'textAlign': 'middle',
    }),
    dcc.Markdown(children = project_description),

    # house hunting tab
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

                            html.Button('Check history', id = 'button-history', n_clicks = 0),
                            html.Button('See future', id = 'button-future', n_clicks = 0),
                            html.Button('Reset', id = 'button-reset', n_clicks = 0),

                        ], color='danger', outline = True)
                    ], className = 'three columns', style = {'margin-left': 30, 'margin-bottom': 10}),

                    html.Div([
                        dcc.Graph(
                            id = 'denver-house-map',
                            figure = draw_house_base_map(json_neighbor, neighbor_house_record),
                            style = {'height': '100%'}
                        )
                    ], id = 'house-map-chart', className = 'eight columns')

                ], className = 'row')
            ]),  

        # neighborhood tab        
        dcc.Tab(
            label='Neighborhood', 
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

        # city tab
        dcc.Tab(
            label = 'City', 
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
            children = ['This holds the explanation of our model...']
        ),
     ]),
])

# callback to predict house price
@app.callback(
    Output('house-map-chart', 'children'), # replace map with a prediction table
    [Input('house-neighbor', 'value'), # which neighborhood
     Input('house-bedroom', 'value'),  # how many bedrooms
     Input('house-bathroom', 'value'), # how may bathrooms
     Input('house-story', 'value'), # how many story
     Input('house-age', 'value'), # age of house
     Input('house-area-min', 'value'), # min above ground area
     Input('house-area-max', 'value'), # max above ground area
     Input('house-lot-min', 'value'), # min lot size
     Input('house-lot-max', 'value'), # max lot size
     Input('house-month', 'value'), # month of year buying
     Input('button-future', 'n_clicks')
    ]
)
def predict_house_price(neighbor, bed, bath, story, age, minarea, maxarea, minlot, maxlot, month, n_clicks):
    if n_clicks > 0:
        print(neighbor, bed, bath, story, age, minarea, maxarea, minlot, maxlot, month)
    elif neighbor is not None or bed is not None or bath is not None or story is not None or age is not None or month is not None:
        raise PreventUpdate
    else:
        return dcc.Graph(
            id = 'denver-house-map',
            figure = draw_house_base_map(json_neighbor, neighbor_house_record),
            style = {'height': '100%'}
        )

# callback to reset selection
@app.callback(
    [Output('button-history', 'n_clicks'),
     Output('button-future', 'n_clicks'),
     Output('house-neighbor', 'value'), # which neighborhood
     Output('house-bedroom', 'value'),  # how many bedrooms
     Output('house-bathroom', 'value'), # how may bathrooms
     Output('house-story', 'value'), # how many story
     Output('house-age', 'value'), # age of house
     Output('house-area-min', 'value'), # min above ground area
     Output('house-area-max', 'value'), # max above ground area
     Output('house-lot-min', 'value'), # min lot size
     Output('house-lot-max', 'value'), # max lot size
     Output('house-month', 'value'), ],# month of year buying
    [Input('button-reset', 'n_clicks')]
)
def reset_house_predict(n_clicks):
    if n_clicks > 0:
        return (0, 0, None, None, None, None, None, 
        family_demo['AREA_ABG'].min(), family_demo['AREA_ABG'].max(),
        family_demo['LAND_SQFT'].min(),family_demo['LAND_SQFT'].max(),None)
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


@app.callback(
    Output('nsc','figure'),
    [Input('nsc_met','value')]
)
def update_fig_nsc(sel_met):
    out_data=[]
    if sel_met in ["Seasonality of Median Price","Seasonality of Home Sold"]:
        met_temp="Avg_"+"_".join(sel_met.replace("of","").split())
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
                    "title":sel_met,
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
                    "title":sel_met,
                    'autosize': True,
                    "xaxis":xa,
                    "yaxis":ya
                }
            } 

if __name__ == '__main__':
    #pass
    app.run_server(debug=True)