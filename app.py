from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from view.page1 import layout as map_layout, register_callback as register_map_callback
from view.page2 import layout as linear_layout, register_callback as register_linear_callback
from view.page3 import layout as sankey_layout, register_callback as register_sankey_callback
from view.page4 import layout as radar_layout, register_callback as register_radar_callback

app = Dash(__name__, suppress_callback_exceptions=True)

#Layout de la page d'accueil
home_layout = html.Div(style={'backgroundColor': 'black', 'height': '100vh', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center', 'color': 'white'}, children=[
    html.H1("Analyse des Genres Musicaux en Europe"),
    html.H2(
        "Ce site web vous fournit des informations clés sur la popularité des genres musicaux en Europe, "
        "l'évolution des tendances par pays, ainsi que les collaborations entre artistes de différents genres. "
        "En analysant les données des dernières années, vous pourrez suivre la croissance ou le déclin des genres, "
        "évaluer la diversité et l'influence des genres à travers les featurings, et ainsi identifier les meilleures "
        "opportunités d'investissement dans de nouveaux artistes et collaborations.",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}
    )
,
    html.P("Sélectionnez une analyse à explorer :"),
    html.Div([
        dcc.Link(
            html.Button('Popularité des genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/page1'
        ),
        dcc.Link(
            html.Button('Évolution des genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/page2'
        ),
        dcc.Link(
            html.Button('Collaborations entre genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/page3'
        ),
        dcc.Link(
            html.Button('Caractéristiques musicales', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/page4'
        ),
    ], style={'display': 'flex', 'justifyContent': 'center', 'flexDirection': 'row', 'gap': '20px'}) 
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback pour la navigation entre les pages
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page1':
        return map_layout
    elif pathname == '/page2':
        return linear_layout
    elif pathname == '/page3':
        return sankey_layout
    elif pathname == '/page4':
        return radar_layout
    else:
        return home_layout  # Page d'accueil par défaut

#Callbacks pour chaque page
register_map_callback(app)
register_linear_callback(app)
register_sankey_callback(app)
register_radar_callback(app)

if __name__ == '__main__':
    app.run_server(debug=True)

