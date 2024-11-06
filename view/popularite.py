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
    return country.alpha_3 if country else None

# Layout pour la page de popularité des genres musicaux
layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1('Popularité des genres musicaux en Europe', style={'textAlign': 'center', 'color': 'white'}),
    html.H3("Découvrez la popularité de chaque genre à travers les pays européens", style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal','paddingLeft': '50px', 'paddingRight': '50px'}),

    # Conteneur général
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, children=[
        html.Div(style={'position': 'absolute', 'top': '30px', 'right': '30px', 'z-index': '1000', 'font-size': '40px'}, children=[
            dcc.Link('🏠', href='/'),
        ]),
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[dcc.Graph(id="bubble-genre-chart", style={'height': '600px', 'width': '100%'})]),
        html.Div(style={'flex': '1.5', 'padding': '10px'}, children=[dcc.Graph(id="map-graph", style={'height': '500px'})])
    ]),
    
    # Section timeline
    html.Div(style={'padding': '20px'}, children=[
        html.H3("Timeline des festivals pour le genre sélectionné"),
        dcc.Graph(id="timeline-graph", style={'height': '400px', 'width': '100%'})
    ]),

    # Pied de page
    html.Footer(
        html.Small(
            ["Les données sont fournies par l'API Spotify"],
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
            featureidkey="properties.adm0_a3", color="total_popularity", 
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
