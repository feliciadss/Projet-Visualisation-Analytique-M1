from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
import pycountry
from static.enumerations import genres, genre_colors
from data.data_manager import DataManager

# Charger les données de festivals
festivals_df = pd.read_csv('./static/festivals_europe.csv')

# Fonction pour convertir les codes ISO2 en ISO3
def convert_iso2_to_iso3(iso2_code):
    country = pycountry.countries.get(alpha_2=iso2_code)
    if country:
        return country.alpha_3
    else:
        print(f"Code ISO2 non trouvé : {iso2_code}")
        return None


def register_callback(app):
    @app.callback(
        [Output("bubble-genre-chart", "figure"),
         Output("map-graph", "figure"),
         Output("timeline-graph", "figure")],
        [Input("bubble-genre-chart", "clickData")]
    )
    def update_charts(click_data):
        data_manager = DataManager()

        # Bubble chart
        genre_counts_df = data_manager.create_genre_count_dataframe()
        genre_counts_df['scaled_size'] = np.sqrt(genre_counts_df['total_count'] * 10)  # Ajustement pour la taille des bulles
        genre_counts_df['x'], genre_counts_df['y'] = np.linspace(-1, 1, len(genre_counts_df)), np.linspace(-1, 1, len(genre_counts_df))
        selected_genre = click_data['points'][0]['hovertext'] if click_data else "pop"

        fig_bubble = px.scatter(
            genre_counts_df,
            x='x', y='y', size='scaled_size', color='genre',
            hover_name='genre', text='genre', color_discrete_map=genre_colors
        )
        fig_bubble.update_traces(marker=dict(line=dict(width=2, color='white')))
        fig_bubble.update_layout(
            title="Popularité des genres musicaux en Europe",
            plot_bgcolor='black', paper_bgcolor='black', font_color='white', showlegend=False,
            xaxis=dict(visible=False), yaxis=dict(visible=False)
        )

        # Choropleth Map pour le genre sélectionné
        df = data_manager.create_genre_popularity_by_country(selected_genre)
        df['country'] = df['country'].apply(convert_iso2_to_iso3)
        fig_map = px.choropleth(
            df, geojson=json.load(open("./static/custom.geo.json")), locations="country", 
            featureidkey="properties.adm0_a3", color="total_popularity", zoom =3,
            title=f"Popularité du genre '{selected_genre.title()}' par pays en Europe"
        )
        fig_map.update_geos(scope="europe", projection_type="mercator", showcoastlines=False, lakecolor='black')
        fig_map.update_layout(
            plot_bgcolor='black', paper_bgcolor='black', font_color='white',
            geo=dict(bgcolor='rgba(0,0,0,0)')
        )

        # Timeline Graph pour les festivals du genre sélectionné
        filtered_festivals = festivals_df[festivals_df['Genres musicaux'].str.contains(selected_genre, case=False, na=False)]
        fig_timeline = px.scatter(
            filtered_festivals, x="Mois", y="Nom du festival", size="Participants (approx)", 
            color="Prix moyen (€)", hover_name="Nom du festival", 
            title=f"Festivals de {selected_genre.title()} en Europe (par Mois)"
        )
        fig_timeline.update_layout(
            plot_bgcolor='black', paper_bgcolor='black', font_color='white',
            xaxis_title="Mois", yaxis_title="Festivals", showlegend=False
        )

        return fig_bubble, fig_map, fig_timeline


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
        ]),
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
            "color": "#999"
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
            size_max=80,
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
            width=450,  # Augmenter ces valeurs pour forcer une taille de conteneur plus large
            height=600,
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
            title=f"→ {selected_genre.title()}",
            labels={"total_popularity_percentile": "Popularité (%)"} 
        )

        fig_map.update_geos(
            scope="europe",
            projection_type="equirectangular",
            showcoastlines=False,
            showland=True,
            center=dict(lat=51.9194, lon=19.1451),  
            projection_scale=1.1,
            landcolor="white",
            bgcolor="black",
            visible=True,
            lonaxis=dict(range=[-50, 60]),  # Ajustez pour exclure les îles
            lataxis=dict(range=[15, 85]) 
        )

        fig_map.update_layout(
            title_font_size=20,
            autosize = True,
            geo=dict(showframe=False, showcoastlines=False),
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white'),
            margin={"r": 10, "t": 50, "l": 0, "b": 0},
            width=610,  # Augmenter ces valeurs pour forcer une taille de conteneur plus large
            height=500,
            coloraxis_colorbar=dict(
        x=0.85,
        tickvals=[0.2, 0.4, 0.6, 0.8], 
        title="Popularité (%)"
    )
        )

        return fig_bubble, fig_map
