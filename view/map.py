from dash import dcc, html, Input, Output
import plotly.express as px
from static.enumerations import genres
from data.data_manager import DataManager
import json
import pycountry

def convert_iso2_to_iso3(iso2_code):
    country = pycountry.countries.get(alpha_2=iso2_code)
    return country.alpha_3 if country else None

geojson_path = "./static/custom.geo.json"
try:
    with open(geojson_path, "r", encoding="utf-8") as geojson_file:
        european_geojson = json.load(geojson_file)
except FileNotFoundError:
    european_geojson = None

layout = html.Div([
    html.H1('Popularité des genres', style={'textAlign': 'center', 'color': 'white'}),
    html.H3(
        "Cette page illustre la popularité des genres",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}
    ),
    html.P("Sélectionnez un genre musical pour afficher sa répartition en Europe:", style={'color': 'white', 'fontWeight': 'bold'}),
    dcc.RadioItems(
        id='map-genre',
        options=[{'label': genre.title(), 'value': genre} for genre in genres],
        value="pop",
        inline=False,  
        style={'color': 'white'} 
    ),
    dcc.Graph(id="map-graph") 
], style={'backgroundColor': 'black', 'padding': '20px'})  

def register_callback(app):
    @app.callback(
        Output("map-graph", "figure"), 
        Input("map-genre", "value"))
    def display_choropleth(genre):
        data_manager = DataManager()
        df = data_manager.create_album_top_market_dataframe(genre)
        df['market'] = df['market'].apply(convert_iso2_to_iso3)
        
        if df.empty:
            return px.choropleth() 
        
        albums_per_country = df.groupby('market').size().reset_index(name='album_count')
        
        fig = px.choropleth(
            albums_per_country,
            geojson=european_geojson,
            locations="market",
            featureidkey="properties.ISO_A3", 
            color="album_count",  
            hover_name="market",  
            color_continuous_scale="Viridis", 
            title=f"Popularité du genre '{genre.title()}' par pays"
        )

        fig.update_geos(
            scope="europe",
            projection="mercator",
            showcoastlines=False,
            showland=True,
            landcolor="white",
            fitbounds="locations",
            visible=True
        )

        fig.update_layout(
            title_font_size=20,
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            width=800,
            height=500,
            paper_bgcolor='black',  
            plot_bgcolor='black',  
            font=dict(color='white') 
        )

        return fig
