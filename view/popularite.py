from dash import dcc, html, Input, Output
import plotly.express as px
import json
import pycountry
from static.enumerations import genres, genre_colors
from data.data_manager import DataManager

# Fonction pour convertir les codes ISO2 en ISO3
def convert_iso2_to_iso3(iso2_code):
    country = pycountry.countries.get(alpha_2=iso2_code)
    return country.alpha_3 if country else None

#chargment carte europe
geojson_path = "./static/custom.geo.json"
try:
    with open(geojson_path, "r", encoding="utf-8") as geojson_file:
        european_geojson = json.load(geojson_file)
except FileNotFoundError:
    european_geojson = None


layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1('Popularité des genres musicaux en Europe', style={'textAlign': 'center', 'color': 'white'}),
    
    # Conteneur général
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, children=[
        # Bouton pour revenir à l'accueil
        html.Div(style={'position': 'absolute','top': '30px','right': '30px','z-index': '1000','font-size': '40px'},children=[
            dcc.Link('🏠', href='/'),
        ]),
        # Sélection des genres à gauche
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.P("Sélectionnez un genre musical :", style={'fontWeight': 'bold', 'color': 'white'}),
            dcc.RadioItems(
                id='map-genre',
                options=[{'label': genre.title(), 'value': genre} for genre in genres],
                value="pop",
                inline=False,  
                style={'color': 'white'}
            ),
        ]),

        html.Div(style={'flex': '2', 'padding': '10px'}, children=[
            dcc.Graph(id="map-graph", style={'height': '500px'})
        ])
    ])
])

def register_callback(app):
    @app.callback(
        Output("map-graph", "figure"), 
        Input("map-genre", "value")
    )
    def display_choropleth(genre_filter):
        data_manager = DataManager()

        df = data_manager.create_genre_popularity_by_country(genre_filter)
        
        if df.empty:
            print(f"Aucune donnée disponible pour le genre {genre_filter}")
            return None

        # Conversion des codes ISO2 en ISO3
        df['country'] = df['country'].apply(convert_iso2_to_iso3)

        try:
            with open(geojson_path, "r", encoding="utf-8") as geojson_file:
                europe_geojson = json.load(geojson_file)
                print("GeoJSON chargé avec succès")
        except FileNotFoundError:
            print(f"Fichier non trouvé à l'emplacement : {geojson_path}")
            return None

        color_for_genre = genre_colors.get(genre_filter.lower(), '#ffffff')

        fig = px.choropleth(
            df,
            geojson=europe_geojson,
            locations="country",
            featureidkey="properties.ISO_A3",
            color="total_popularity",
            hover_name="country",
            color_continuous_scale=[[0, '#000000'], [1, color_for_genre]],  
            title=f"Popularité du genre '{genre_filter.title()}' par pays"
        )

        fig.update_geos(
            scope="europe",
            projection_type="equirectangular",
            showcoastlines=False,
            showland=True,
            landcolor="white",
            bgcolor="black",  #fond noir
            fitbounds="locations",
            visible=True
        )

        fig.update_layout(
            title_font_size=20,
            geo=dict(showframe=False, showcoastlines=False),
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white'),
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            width=800,
            height=500
        )

        return fig
