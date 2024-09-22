import plotly.express as px
import pandas as pd

def build_map(data):
    """
    Génère une carte de chaleur (heatmap) affichant la popularité des genres musicaux en Europe.
    
    :param data: Un DataFrame contenant les colonnes 'country', 'cleaned_genre', et 'points'
    :return: Une figure Plotly
    """
    # Générer une carte de chaleur basée sur les points par genre et par pays
    fig = px.choropleth(
        data,
        locations="country",
        locationmode='country names',
        color="points",
        hover_name="cleaned_genre",  # Utiliser 'cleaned_genre' au lieu de 'genre'
        title="Popularité des genres musicaux en Europe",
        color_continuous_scale="Viridis"
    )
    
    fig.update_geos(
        showcoastlines=True, coastlinecolor="Black",
        showland=True, landcolor="white",
        showocean=True, oceancolor="LightBlue"
    )
    
    return fig
