from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from view.popularite import layout as map_layout, register_callback as register_map_callback
from view.evolution_genres import layout as linear_layout, register_callback as register_linear_callback
from view.collaborations import layout as sankey_layout, register_callback as register_sankey_callback
from view.caract_musicales import layout as radar_layout, register_callback as register_radar_callback

import plotly.graph_objects as go 
import plotly.express as px
from data.data_manager import DataManager
from static.enumerations import genres, genre_colors

app = Dash(__name__, suppress_callback_exceptions=True)

# Layout de la page d'accueil
home_layout = html.Div(style={'backgroundColor': 'black', 'minHeight': '100vh', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center', 'color': 'white'}, children=[
    html.H1("Analyse des Genres Musicaux en Europe"),
    html.H2(
        "Ce site web vous fournit des informations clés sur la popularité des genres musicaux en Europe, "
        "l'évolution des tendances par pays, ainsi que les collaborations entre artistes de différents genres. "
        "En analysant les données des dernières années, vous pourrez suivre la croissance ou le déclin des genres, "
        "évaluer la diversité et l'influence des genres à travers les featurings, et ainsi identifier les meilleures "
        "opportunités d'investissement dans de nouveaux artistes et collaborations.",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}
    ),
    html.P("Sélectionnez une analyse à explorer :"),
    html.Div([
        dcc.Link(
            html.Button('Popularité des genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/popularite'
        ),
        dcc.Link(
            html.Button('Évolution des genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/evolution_genres'
        ),
        dcc.Link(
            html.Button('Collaborations entre genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/collaborations'
        ),
        dcc.Link(
            html.Button('Caractéristiques musicales', style={'margin': '10px', 'color': 'black', 'backgroundColor': 'white', 'fontSize': '20px', 'padding': '15px 30px'}),
            href='/caract_musicales'
        ),
    ], style={'display': 'flex', 'justifyContent': 'center', 'flexDirection': 'row', 'gap': '20px'}),
    
    
    html.H3("Nous avons catégorisé les genres en 14 grandes catégories, mais voici les sous-genres se cachant dans chacune :",
            style={'color': 'white', 'paddingTop': '40px'}),

    # Conteneur général du bubble chart
    html.Div(style={'display': 'flex', 'justifyContent': 'flex-start', 'alignItems': 'center', 'width': '100%', 'padding': '20px'}, children=[
        # Sélection des genres à gauche
        html.Div(style={'flex': '0 0 20%', 'padding': '10px', 'textAlign': 'left'}, children=[
            html.P("Sélectionnez un genre musical :", style={'fontWeight': 'bold', 'color': 'white'}),
            dcc.RadioItems(
                id='map-genre',
                options=[{'label': genre.title(), 'value': genre} for genre in genres],
                value="pop",
                inline=False,  
                style={'color': 'white'}
            ),
        ]),

        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            dcc.Graph(id="bubble-chart", style={'height': '600px', 'width': '100%'})  # Augmenter la taille du graphique
        ])
    ])
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback pour la navigation entre les pages
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/accueil':
        return map_layout
    elif pathname == '/evolution_genres':
        return linear_layout
    elif pathname == '/collaborations':
        return sankey_layout
    elif pathname == '/caract_musicales':
        return radar_layout
    else:
        return home_layout  # Page d'accueil par défaut

# Callbacks pour chaque page
register_map_callback(app)
register_linear_callback(app)
register_sankey_callback(app)
register_radar_callback(app)

# Callback pour la bubble chart sur la page principale
@app.callback(
    Output("bubble-chart", "figure"),
    Input("map-genre", "value")
)
def update_bubble_chart(genre):
    data_manager = DataManager()
    df_subgenres = data_manager.get_top_subgenres_per_genre(genre)
    
    if df_subgenres.empty:
        print("Aucune donnée disponible pour les sous-genres.")
        return go.Figure()

    genre_color = genre_colors.get(genre.lower(), '#ffffff')  # Blanc par défaut

    fig = px.scatter(df_subgenres, 
                     x='subgenre', 
                     y='count', 
                     size='count', 
                     color_discrete_sequence=[genre_color],  
                     hover_name='subgenre',
                     title=f'Diagramme en Bulles pour le genre {genre}',
                     labels={'subgenre': 'Sous-genres', 'count': 'Nombre d\'artistes'},
                     size_max=60)

    fig.update_layout(
        plot_bgcolor='black',  
        paper_bgcolor='black',  # Fond noir 
        font_color='white',  # Texte en blanc 
        title_font_color='white',  # Titre blanc
        xaxis=dict(
            title_font=dict(color='white'), 
            tickfont=dict(color='white'),    
            showgrid=False, 
            zeroline=False
        ),
        yaxis=dict(
            title_font=dict(color='white'), 
            tickfont=dict(color='white'), 
            showgrid=False, 
            zeroline=False
        ),
        title=dict(
            font=dict(color='white') 
        )
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
