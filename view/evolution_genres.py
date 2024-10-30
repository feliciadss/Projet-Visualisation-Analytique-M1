from dash import html, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px
from static.enumerations import genres
from data.data_manager import DataManager

# Layout de la page
layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px', 'textAlign': 'center'}, children=[
    html.H1('Évolution de la popularité des genres', style={'color': 'white'}),
    html.H3("Découvrez l'évolution de leur popularité depuis 50 ans en sélectionnant un ou plusieurs genres.", 
            style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}),

    # Conteneur pour centrer la checklist et le graphique
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'flex-start'}, children=[
        # Bouton pour revenir à l'accueil
        html.Div(style={'position': 'absolute', 'top': '30px', 'right': '30px', 'z-index': '1000', 'font-size': '40px'}, children=[
            dcc.Link('🏠', href='/'),
        ]),
        
        # Liste des genres
        html.Div(style={'marginRight': '20px'}, children=[
            dcc.Checklist(
                id="linear-checklist",
                options=genres,
                value=["rock"],
                inline=False,
                style={'color': 'white'}
            )
        ]),

        html.Div(style={'width': '70%'}, children=[
            dcc.Graph(id="linear-graph", style={'backgroundColor': 'black'})
        ]),
    ]),

    # Encadré des liens des articles avec disposition en 3 lignes de 5 colonnes
    html.Div(id="articles-section", style={
        'marginTop': '20px',
        'padding': '10px',
        'backgroundColor': '#333',
        'borderRadius': '10px',
        'width': '80%',
        'margin': 'auto',
        'textAlign': 'left',
        'color': 'white'
    }),

    # Pied de page
    html.Footer(
        html.Small(
            [
                "Les données sont fournies par l' ",
                html.A("API Spotify", href="https://developer.spotify.com/documentation/web-api", target="_blank", style={'color': 'white'}),
            ]
        ),
        style={
            "textAlign": "center",
            "padding": "10px",
            "backgroundColor": "black",
            "width": "100%",
            "fontSize": "12px",
            "color": "#999",
            "position": "fixed",
            "bottom": "0",
        },
    ),
])

# Fonction pour enregistrer les callbacks
def register_callback(app):
    @app.callback(
        Output("linear-graph", "figure"),
        Output("articles-section", "children"),
        Input("linear-checklist", "value")
    )
    def update_content(selected_genres):
        data_manager = DataManager()
        df = data_manager.create_album_release_dataframe(selected_genres)
        df['release_date'] = pd.to_datetime(df['release_date'])
        df['year'] = df['release_date'].dt.year
        albums_per_year = df.groupby(['year', 'genre']).size().reset_index(name='album_count')
        
        fig = px.line(albums_per_year, x="year", y="album_count", color='genre')
        fig.update_layout(plot_bgcolor='black', paper_bgcolor='black', font_color='white')

        # Dictionnaire des genres avec leur article approprié
        genre_links = {
            "rock": ("du", "https://fr.wikipedia.org/wiki/Histoire_du_rock"),
            "pop": ("de la", "https://fr.wikipedia.org/wiki/Pop_(musique)"),
            "latin": ("de la", "https://fr.wikipedia.org/wiki/Musique_latine"),
            "jazz": ("du", "https://fr.wikipedia.org/wiki/Histoire_du_jazz"),
            "classical": ("de la", "https://fr.wikipedia.org/wiki/Musique_classique"),
            "electronic": ("de l'", "https://fr.wikipedia.org/wiki/Musique_%C3%A9lectronique"),
            "indie": ("de l'", "https://fr.wikipedia.org/wiki/Indie_pop"),
            "reggae": ("du", "https://fr.wikipedia.org/wiki/Reggae"),
            "blues": ("du", "https://fr.wikipedia.org/wiki/Blues"),
            "metal": ("du", "https://fr.wikipedia.org/wiki/Metal"),
            "folk": ("de la", "https://fr.wikipedia.org/wiki/Musique_folk"),
            "country": ("de la", "https://fr.wikipedia.org/wiki/Musique_country"),
            "r&b": ("du", "https://fr.wikipedia.org/wiki/Rhythm_and_blues"),
            "soul": ("de la", "https://fr.wikipedia.org/wiki/Musique_soul"),
            "musique": ("de la", "https://fr.wikipedia.org/wiki/Histoire_de_la_musique")
        }

        articles = []
        for genre, (article, link) in genre_links.items():
            img_src = f"/static/images/{genre}.jpg" 
            title = f"L'histoire {article} {genre.capitalize()}" 

            articles.append(
                html.Div(
                    children=[
                        html.Img(src=img_src, style={'width': '100%', 'border-radius': '5px'}),
                        html.H3(title, style={'text-align': 'center', 'color': 'white'}),
                        html.A("Lire plus", href=link, target="_blank", style={'display': 'block', 'text-align': 'center', 'color': 'cyan'})
                    ],
                    style={
                        'border': '1px solid #444',
                        'border-radius': '5px',
                        'padding': '10px',
                        'background-color': '#333',
                        'width': '100%',
                        'box-shadow': '2px 2px 5px rgba(0,0,0,0.5)'
                    }
                )
            )

        #  3 rangées de 5 colonnes
        articles_grid = html.Div(
            children=[
                html.Div(articles[i:i+5], style={'display': 'flex', 'justify-content': 'space-around', 'gap': '10px', 'margin-top': '10px'})
                for i in range(0, len(articles), 5)
            ]
        )

        articles_section = articles_grid
        return fig, articles_section
