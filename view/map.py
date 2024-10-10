import plotly.express as px
import json
from plotly.io import to_json
from data.data_manager import DataManager
from static.enumerations import genre_colors
import pycountry

# Fonction pour convertir les codes ISO2 en ISO3
def convert_iso2_to_iso3(iso2_code):
    country = pycountry.countries.get(alpha_2=iso2_code)
    return country.alpha_3 if country else None

# Fonction pour créer une carte de popularité par genre avec une seule couleur
def build_map(genre_filter):
    data_manager = DataManager()
    
    # Utiliser la nouvelle fonction pour récupérer le top_market des albums par genre
    df = data_manager.create_album_top_market_dataframe(genre_filter)
    
    # Convertir les codes ISO2 des marchés en ISO3
    df['market'] = df['market'].apply(convert_iso2_to_iso3)
    
    if df.empty:
        print(f"Aucune donnée disponible pour le genre {genre_filter}")
        return None

    # Chemin vers le fichier GeoJSON personnalisé pour l'Europe
    geojson_path = "./static/custom.geo.json"
    try:
        with open(geojson_path, "r", encoding="utf-8") as geojson_file:
            europe_geojson = json.load(geojson_file)
            print("GeoJSON chargé avec succès")
    except FileNotFoundError:
        print(f"Fichier non trouvé à l'emplacement : {geojson_path}")
        return None

    # Couleur du genre sélectionné (une seule couleur dont l'intensité varie)
    color_for_genre = genre_colors.get(genre_filter.lower(), '#ffffff')  # Couleur associée au genre, blanc par défaut

    # Créer une carte choropleth avec une seule couleur dont l'intensité varie
    fig = px.choropleth(
        df,
        geojson=europe_geojson,
        locations="market",  # Codes ISO3 des pays
        featureidkey="properties.ISO_A3",  # Correspondance avec le GeoJSON
        color="album_id",  # On utilise la colonne pour l'intensité (nombre d'albums)
        hover_name="market",  # Nom du marché au survol
        color_continuous_scale=[[0, '#000000'], [1, color_for_genre]],  # Une seule couleur qui varie en intensité
        title=f"Popularité du genre '{genre_filter.title()}' par pays"
    )

    # Configuration de la carte (centrée sur l'Europe)
    fig.update_geos(
        scope="europe",
        projection_type="equirectangular", 
        showcoastlines=False, 
        showland=True, 
        landcolor="white",  # Couleur de la terre
        bgcolor="black",  # Fond noir
        fitbounds="locations",
        visible=True
    )

    # Mise à jour du layout pour ajuster l'apparence
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

    return to_json(fig)
