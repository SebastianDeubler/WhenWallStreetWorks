import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from dash import Dash, dcc, html, Input, Output, State, callback_context
from sklearn.preprocessing import MinMaxScaler
from pymongo import MongoClient

# Initialize MongoDB client
client = MongoClient('mongodb+srv://WhenWallStreetWorksUser:NYMtzUpn98eVhnUP@sabbysmongodatabase.gfkwb.mongodb.net/?retryWrites=true&w=majority&appName=SabbysMongoDatabase')

# Access the database
db = client['WhenWallStreetWorks']

# Access the collection
collection = db['Limited_Data']

df_loaded = pd.DataFrame(list(collection.find({})))
df_stats_vis = df_loaded.drop('_id', axis=1)
df_stats_vis.index = df_loaded.set_index(['Indicator', 'Timeperiod']).index

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "23%",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-right": "18rem",
    "margin-left": "2rem",
    "padding": "2rem 1rem",
}

header_style = {
    "font-size": "2rem",
    "margin-left": "2rem",
    "padding": "1rem 0",
}

header = html.Div("WhenWallStreetWorks", style=header_style)

button_style = {'display': 'inline-block', 'width': '48%'}
button_color = 'secondary'
button_outline = True
button_active = True

indicator_buttons = html.Div([
    html.Div(
        dbc.Button("DEMA", id="button_dema", color=button_color, outline=button_outline, active=False, className="btn-block"),
        style=button_style
    ),
    html.Div(
        dbc.Button("EMA", id="button_ema", color=button_color, outline=button_outline, active=button_active, className="btn-block"),
        style=button_style
    ),
    html.Div(
        dbc.Button("KAMA", id="button_kama", color=button_color, outline=button_outline, active=False, className="btn-block"),
        style=button_style
    ),
    html.Div(
        dbc.Button("MA", id="button_ma", color=button_color, outline=button_outline, active=button_active, className="btn-block"),
        style=button_style
    ),
    html.Div(
        dbc.Button("SMA", id="button_sma", color=button_color, outline=button_outline, active=button_active, className="btn-block"),
        style=button_style
    ),
    html.Div(
        dbc.Button("TEMA", id="button_tema", color=button_color, outline=button_outline, active=False, className="btn-block"),
        style=button_style
    ),
    html.Div(
        dbc.Button("TRIMA", id="button_trima", color=button_color, outline=button_outline, active=False, className="btn-block"),
        style=button_style
    ),
    html.Div(
        dbc.Button("WMA", id="button_wma", color=button_color, outline=button_outline, active=button_active, className="btn-block"),
        style=button_style
    ),
    html.Div(id='output', style={'margin-top': '20px'})
])

button_row = dbc.Row(
    [dbc.Col(button, width="auto") for button in indicator_buttons.children[:-1]],  # Exclude the last output div
    justify="around",  # or use "between" or "evenly" for different spacing options
    style={"margin-top": "1rem"}
)

sidebar = html.Div(
    [
        html.P("The statistics of your favorite technical indicator", className="lead"),
        dbc.Container(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H6("Axis Features", className="card-title"),
                        html.Div(
                            style={'display': 'grid', 'gridTemplateColumns': 'auto 1fr', 'gap': '60px', 'alignItems': 'center'},
                            children=[
                                html.Div("X:", style={'gridColumn': '1'}),
                                dcc.Dropdown(
                                    id='x_axis_select',
                                    options=[{'label': col, 'value': col} for col in sorted(df_stats_vis.columns.drop('Indicator'))],
                                    value='Expectancy',
                                    clearable=False,
                                    style={'width': '100%'}
                                )
                            ]
                        ),
                        html.Div(
                            style={'display': 'grid', 'gridTemplateColumns': 'auto 1fr', 'gap': '60px', 'alignItems': 'center'},
                            children=[
                                html.Div("Y:", style={'gridColumn': '1'}),
                                dcc.Dropdown(
                                    id='y_axis_select',
                                    options=[{'label': col, 'value': col} for col in sorted(df_stats_vis.columns.drop('Indicator'))],
                                    value='Profit Factor',
                                    clearable=False,
                                    style={'width': '100%'}
                                )
                            ]
                        )
                    ]
                ),
                style={"width": "100%"}
            ),
            fluid=True
        ),
        dbc.Container(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H6("Axis Features", className="card-title"),
                        html.Div(
                            style={'display': 'grid', 'gridTemplateColumns': 'auto 1fr', 'gap': '40px', 'alignItems': 'center'},
                            children=[
                                html.Div("Size:", style={'gridColumn': '1'}),
                                dcc.Dropdown(
                                    id='size_select',
                                    options=[{'label': col, 'value': col} for col in ['None'] + sorted(df_stats_vis.columns.drop('Indicator'))],
                                    value='Total Return [%]',
                                    clearable=False,
                                    style={'width': '100%'}
                                )
                            ]
                        ),
                        html.Div(
                            style={'display': 'grid', 'gridTemplateColumns': 'auto 1fr', 'gap': '30px', 'alignItems': 'center'},
                            children=[
                                html.Div("Color:", style={'gridColumn': '1'}),
                                dcc.Dropdown(
                                    id='color_select',
                                    options=[{'label': col, 'value': col} for col in ['None'] + sorted(df_stats_vis.columns.drop('Indicator'))],
                                    value='Win Rate [%]',
                                    clearable=False,
                                    style={'width': '100%'}
                                )
                            ]
                        ),
                        html.Div(
                            style={'display': 'grid', 'gridTemplateColumns': 'auto 1fr', 'gap': '14px', 'alignItems': 'center'},
                            children=[
                                html.Div("Opacity:", style={'gridColumn': '1'}),
                                dcc.Dropdown(
                                    id='opacity_select',
                                    options=[{'label': col, 'value': col} for col in ['None'] + sorted(df_stats_vis.columns.drop('Indicator'))],
                                    value='Avg Winning Trade [%]',
                                    clearable=False,
                                    style={'width': '100%'}
                                )
                            ]
                        )
                    ]
                ),
                style={"width": "100%"}
            ),
            fluid=True
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

figure = dcc.Graph(id='figure', figure={})

app.layout = html.Div([
    html.Div(
        [
            header,
            dbc.Container(button_row, style={"margin-right": "2rem"}),
            dbc.Container(dbc.Row([figure], justify='center'), style={"margin-right": "2rem"}),
        ], style={"width": "78%"}
    ),
    sidebar
])

@app.callback(
    Output('figure', 'figure'),
    Output('button_dema', 'active'),
    Output('button_ema', 'active'),
    Output('button_kama', 'active'),
    Output('button_ma', 'active'),
    Output('button_sma', 'active'),
    Output('button_tema', 'active'),
    Output('button_trima', 'active'),
    Output('button_wma', 'active'),
    Input('x_axis_select', 'value'),
    Input('y_axis_select', 'value'),
    Input('size_select', 'value'),
    Input('color_select', 'value'),
    Input('opacity_select', 'value'),
    Input('button_dema', 'n_clicks'),
    Input('button_ema', 'n_clicks'),
    Input('button_kama', 'n_clicks'),
    Input('button_ma', 'n_clicks'),
    Input('button_sma', 'n_clicks'),
    Input('button_tema', 'n_clicks'),
    Input('button_trima', 'n_clicks'),
    Input('button_wma', 'n_clicks'),
    State('button_dema', 'active'),
    State('button_ema', 'active'),
    State('button_kama', 'active'),
    State('button_ma', 'active'),
    State('button_sma', 'active'),
    State('button_tema', 'active'),
    State('button_trima', 'active'),
    State('button_wma', 'active')
)
def update(x_axis_selected, y_axis_selected, size_select, color_select, opacity_select, 
           n_dema, n_ema, n_kama, n_ma, n_sma, n_tema, n_trima, n_wma,
           active_dema, active_ema, active_kama, active_ma, active_sma, active_tema, active_trima, active_wma):
    
    ctx = callback_context

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "button_ema":
        active_ema = not active_emaa
    if button_id == "button_ma":
        active_ma = not active_ma
    if button_id == "button_sma":
        active_sma = not active_sma
    if button_id == "button_wma":
        active_wma = not active_wma
    
    filtered_df = df_stats_vis[
        ((df_stats_vis['Indicator'] == "EMA") & active_ema)  |
        ((df_stats_vis['Indicator'] == "MA") & active_ma) |
        ((df_stats_vis['Indicator'] == "SMA") & active_sma) |
        ((df_stats_vis['Indicator'] == "WMA") & active_wma)
    ]
    
    if color_select == 'None':
        color = '#0072b5'
        showscale = False
    else:
        color = filtered_df[color_select]
        showscale = True
        
    if size_select == 'None':
        size = 10
    else:
        size = pd.DataFrame(index=filtered_df[size_select].index, 
                            data=MinMaxScaler().fit_transform(filtered_df[size_select].values.reshape(-1, 1)).T[0]*25).apply(np.int8)
        
    if opacity_select == 'None':
        opacity = 1
    else:
        opacity = pd.DataFrame(index=filtered_df[opacity_select].index, 
                               data=MinMaxScaler().fit_transform(filtered_df[opacity_select].values.reshape(-1, 1)).T[0])
    
    fig = go.Figure(data=go.Scatter(
        x=filtered_df[x_axis_selected],
        y=filtered_df[y_axis_selected],
        mode='markers',
        marker=dict(color=color, size=size, opacity=opacity, showscale=showscale),
        hoverinfo='text',
        text=["<b>Indicator:</b> {}<br><b>Period:</b> {}".format(index, row['Timeperiod']) for index, row in filtered_df.iterrows()]
    ))
    return fig, active_dema, active_ema, active_kama, active_ma, active_sma, active_tema, active_trima, active_wma

if __name__ == "__main__":
    app.run_server(debug=False)
