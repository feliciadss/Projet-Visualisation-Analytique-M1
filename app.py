from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from data.data_manager import DataManager
from static.enumerations import genre_colors
import numpy as np

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
    
    html.H3("Nous avons catégorisé les genres en 14 grandes catégories, mais voici les sous-genres se cachant dans chacune :", style={'color': 'white', 'paddingTop': '40px'}),

    # Conteneur pour le bubble chart et l'histogramme
    html.Div(style={'display': 'flex', 'justifyContent': 'flex-start', 'alignItems': 'center', 'width': '100%', 'padding': '20px'}, children=[
        
        # Bubble chart à gauche
        html.Div(style={'flex': '0 0 40%', 'padding': '10px'}, children=[
            dcc.Graph(id="bubble-chart", style={'height': '600px', 'width': '100%'})
        ]),

        # Histogramme horizontal à droite
        html.Div(style={'flex': '1', 'padding': '10px', 'textAlign': 'left'}, children=[
            dcc.Graph(id="histogram-chart", style={'height': '600px', 'width': '100%'})
        ]),
    ])
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback pour la navigation entre les pages
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    return home_layout  # Page d'accueil par défaut

# Callback pour le bubble chart et l'histogramme
@app.callback(
    Output("bubble-chart", "figure"),
    Output("histogram-chart", "figure"),
    [Input("bubble-chart", "clickData")]
)
def update_charts(click_data):
    data_manager = DataManager()

    # Création du bubble chart
    genre_counts_df = data_manager.create_genre_count_dataframe()

    # Appliquer une transformation pour réduire l'écart (racine carrée)
    genre_counts_df['scaled_size'] = np.sqrt(genre_counts_df['total_count'])

    # Génération de positions X et Y avec une distribution plus régulière (grille + jitter)
    n_genres = len(genre_counts_df)
    grid_size = int(np.ceil(np.sqrt(n_genres)))  # Taille de la grille carrée
    genre_counts_df['x'] = np.tile(np.linspace(-1, 1, grid_size), grid_size)[:n_genres]
    genre_counts_df['y'] = np.repeat(np.linspace(-1, 1, grid_size), grid_size)[:n_genres]

    # Ajouter un léger jitter pour éviter les chevauchements exacts
    genre_counts_df['x'] += np.random.uniform(low=-0.05, high=0.05, size=n_genres)
    genre_counts_df['y'] += np.random.uniform(low=-0.05, high=0.05, size=n_genres)

    # Genre par défaut : 'indie' si aucun clic n'est fait
    selected_genre = "indie"
    if click_data:
        selected_genre = click_data['points'][0]['hovertext']
    
    # Bubble chart avec noms en noir dans chaque bulle
    fig_bubble = px.scatter(
        genre_counts_df,
        x='x',
        y='y',
        size='scaled_size',  # Utiliser la taille réduite avec racine carrée
        color='genre',
        hover_name='genre',
        size_max=100,  # Taille maximale plus grande pour agrandir les bulles
        text='genre',  # Afficher le nom du genre dans la bulle
        color_discrete_map=genre_colors
    )
    fig_bubble.update_traces(textposition='middle center', textfont=dict(color='black'))  # Nom du genre en noir au centre
    fig_bubble.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        title="Cliquez sur un genre pour voir les sous-genres"
    )

    # Si une bulle est cliquée, afficher l'histogramme des sous-genres
    df_subgenres = data_manager.get_top_subgenres_per_genre(selected_genre)
    
    # Retirer le nom du genre de la liste des sous-genres
    df_subgenres = df_subgenres[df_subgenres['subgenre'] != selected_genre]

    fig_histogram = go.Figure()
    fig_histogram.add_trace(
        go.Bar(
            x=df_subgenres['count'],
            y=df_subgenres['subgenre'],
            orientation='h',
            marker=dict(color=genre_colors.get(selected_genre.lower(), 'white'))  # Barres de la couleur du genre sélectionné
        )
    )
    fig_histogram.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white',
        title=f"Répartition des sous-genres pour {selected_genre}",
        xaxis=dict(title="Nombre d'artistes"),
        yaxis=dict(title=None)  # Supprimer le titre "Sous-genres" sur l'axe des ordonnées
    )

    return fig_bubble, fig_histogram

if __name__ == '__main__':
    app.run_server(debug=True)
