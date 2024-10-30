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

    # Encadré les liens des articles
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

        articles = []
        for genre in selected_genres:
            if genre == "rock":
                articles.append(html.A("L'histoire du rock", href="https://fr.wikipedia.org/wiki/Histoire_du_rock", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "pop":
                articles.append(html.A("L'histoire de la pop", href="https://fr.wikipedia.org/wiki/Pop_(musique)", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "latin":
                articles.append(html.A("L'histoire de la latino", href="https://fr.wikipedia.org/wiki/Musique_latine", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "jazz":
                articles.append(html.A("L'histoire du jazz", href="https://fr.wikipedia.org/wiki/Histoire_du_jazz", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "classical":
                articles.append(html.A("L'histoire de la classique", href="https://fr.wikipedia.org/wiki/Musique_classique", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "electronic":
                articles.append(html.A("L'histoire de l'électronique", href="https://fr.wikipedia.org/wiki/Musique_%C3%A9lectronique", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "indie":
                articles.append(html.A("L'histoire de l'indie", href="https://fr.wikipedia.org/wiki/Indie_pop", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "reggae":
                articles.append(html.A("L'histoire du reggae", href="https://fr.wikipedia.org/wiki/Reggae", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "blues":
                articles.append(html.A("L'histoire du blues", href="https://fr.wikipedia.org/wiki/Blues", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "metal":
                articles.append(html.A("L'histoire du metal", href="https://fr.wikipedia.org/wiki/Metal", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "folk":
                articles.append(html.A("L'histoire de la folk", href="https://fr.wikipedia.org/wiki/Musique_folk", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "country":
                articles.append(html.A("L'histoire de la country", href="https://fr.wikipedia.org/wiki/Musique_country", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "r&b":
                articles.append(html.A("L'histoire du r&b", href="https://fr.wikipedia.org/wiki/Rhythm_and_blues", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            elif genre == "soul":
                articles.append(html.A("L'histoire de la soul", href="https://fr.wikipedia.org/wiki/Musique_soul", target="_blank", style={'display': 'block', 'color': 'cyan'}))
            
        articles_section = html.Div(articles) if articles else "Sélectionnez un genre pour voir les articles."

        return fig, articles_section
