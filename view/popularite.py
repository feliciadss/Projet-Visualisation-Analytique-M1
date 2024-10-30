from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import json
import pycountry
from static.enumerations import genres, genre_colors
from data.data_manager import DataManager
import numpy as np

# Fonction pour convertir les codes ISO2 en ISO3
def convert_iso2_to_iso3(iso2_code):
    country = pycountry.countries.get(alpha_2=iso2_code)
    if country:
        return country.alpha_3
    else:
        print(f"Code ISO2 non trouvé : {iso2_code}")
        return None

# Chargement carte Europe
geojson_path = "./static/custom.geo.json"
try:
    with open(geojson_path, "r", encoding="utf-8") as geojson_file:
        european_geojson = json.load(geojson_file)
except FileNotFoundError:
    european_geojson = None

# Layout pour la page de popularité des genres musicaux
layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1('Popularité des genres musicaux en Europe', style={'textAlign': 'center', 'color': 'white'}),
    
    html.H3("Découvrez la popularité de chaque genre à travers les pays européens", style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}),
    
    # Conteneur général
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, children=[
        # Bouton pour revenir à l'accueil
        html.Div(style={'position': 'absolute', 'top': '30px', 'right': '30px', 'z-index': '1000', 'font-size': '40px'}, children=[
            dcc.Link('🏠', href='/'),
        ]),
        


        # Bubble chart à gauche
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            dcc.Graph(id="bubble-genre-chart", style={'height': '600px', 'width': '100%'})
        ]),

        # Carte choroplèthe à droite
        html.Div(style={'flex': '1.5', 'padding': '10px'}, children=[
            dcc.Graph(id="map-graph", style={'height': '500px'})
        ])
    ]),
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


def register_callback(app):
    @app.callback(
        Output("bubble-genre-chart", "figure"),
        Output("map-graph", "figure"),
        Input("bubble-genre-chart", "clickData")
    )
    def update_bubble_and_map(click_data):
        data_manager = DataManager()

        genre_counts_df = data_manager.create_genre_count_dataframe()
        genre_counts_df['scaled_size'] = np.sqrt(genre_counts_df['total_count'])

        n_genres = len(genre_counts_df)
        grid_size = int(np.ceil(np.sqrt(n_genres)))
        genre_counts_df['x'] = np.tile(np.linspace(-1, 1, grid_size), grid_size)[:n_genres]
        genre_counts_df['y'] = np.repeat(np.linspace(-1, 1, grid_size), grid_size)[:n_genres]
        genre_counts_df['x'] += np.random.uniform(low=-0.05, high=0.05, size=n_genres)
        genre_counts_df['y'] += np.random.uniform(low=-0.05, high=0.05, size=n_genres)

        selected_genre = "pop"
        if click_data:
            selected_genre = click_data['points'][0]['hovertext']

        fig_bubble = px.scatter(
            genre_counts_df,
            x='x',
            y='y',
            size='scaled_size',
            color='genre',
            hover_name='genre',
            size_max=100,
            text='genre',
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
        )

        # Génération de la carte en fonction du genre sélectionné
        df = data_manager.create_genre_popularity_by_country(selected_genre)
        df['total_popularity_percentile'] = df['total_popularity'].rank(pct=True)



        
        if df.empty:
            print(f"Aucune donnée disponible pour le genre {selected_genre}")
            return fig_bubble, go.Figure()

        # Conversion des codes ISO2 en ISO3
        df['country'] = df['country'].apply(convert_iso2_to_iso3)

        color_for_genre = genre_colors.get(selected_genre.lower(), '#ffffff')

        fig_map = px.choropleth(
            df,
            geojson=european_geojson,
            locations="country",
            featureidkey="properties.adm0_a3",
            color="total_popularity_percentile",
            hover_name="country",
            color_continuous_scale=[[0, '#000000'], [1, color_for_genre]],
            title=f"--> {selected_genre.title()}",
            labels={"total_popularity_percentile": "Popularité (%)"} 
        )

        fig_map.update_geos(
            scope="europe",
            projection_type="equirectangular",
            showcoastlines=False,
            showland=True,
            center=dict(lat=51.9194, lon=19.1451),  
            projection_scale=10,
            landcolor="white",
            bgcolor="black",
            fitbounds="locations",
            visible=True
        )

        fig_map.update_layout(
            title_font_size=20,
            geo=dict(showframe=False, showcoastlines=False),
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white'),
            margin={"r": 50, "t": 50, "l": 0, "b": 0},
            coloraxis_colorbar=dict(
        x=0.85,
        tickvals=[0.2, 0.4, 0.6, 0.8], 
        title="Popularité (%)"
    ),
            width=800,
            height=500
        )

        return fig_bubble, fig_map
