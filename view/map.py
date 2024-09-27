import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import plotly_express as px


def build_map(df_genres):
    geojson_path = './utils/europe.geo.json'
    # Charger le fichier GeoJSON
    geojson_data = gpd.read_file(geojson_path)

    # Vérifier si le fichier GeoJSON est bien chargé
    if geojson_data is None or geojson_data.empty:
        print("Erreur lors du chargement du fichier GeoJSON.")
        return None

    # Créer la carte choropleth en utilisant le GeoJSON et les données
    fig = px.choropleth(df_genres,
                        geojson=geojson_path,  # Utiliser le fichier GeoJSON
                        locations="iso_a3",  # Associer les pays par leurs codes ISO
                        color="popularity",
                        hover_name="iso_a3",
                        color_continuous_scale=px.colors.sequential.OrRd,
                        title="Popularité fictive des genres musicaux en Europe")

    # Centrer la carte sur l'Europe
    fig.update_geos(fitbounds="locations", visible=False)
    
    return fig