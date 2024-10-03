import plotly.express as px
import json
from plotly.io import to_json
from data.data_manager import DataManager

def build_map(genre_filter):
    # Récupérer les données de popularité par genre et pays
    data_manager = DataManager()
    df = data_manager.create_genre_popularity_dataframe(genre_filter)
    
    if df.empty:
        print(f"Aucune donnée disponible pour le genre {genre_filter}")
        return None

    # Charger le fichier GeoJSON pour la carte de l'Europe
    geojson_path = "./static/custom.geo.json"
    print(f"Chemin vers le fichier GeoJSON: {geojson_path}")

    try:
        with open(geojson_path, "r", encoding="utf-8") as geojson_file:
            europe_geojson = json.load(geojson_file)
            print("GeoJSON chargé avec succès")
    except FileNotFoundError:
        print(f"Fichier non trouvé à l'emplacement : {geojson_path}")
        return None
    except UnicodeDecodeError as e:
        print(f"Erreur de décodage lors de la lecture du fichier GeoJSON : {e}")
        return None

    # Créer la carte Plotly en utilisant les pays et la popularité moyenne des artistes
    fig = px.choropleth(
        df,
        geojson=europe_geojson,
        locations="artist_market",  # Correspond aux codes ISO des pays
        featureidkey="properties.ISO_A3",  # Correspond au champ ISO-3 dans le fichier GeoJSON
        color="average_popularity",  # Utiliser la popularité moyenne pour la couleur
        hover_name="artist_market",  # Nom du pays affiché au survol
        color_continuous_scale="Blues",  # Palette de couleurs pour représenter la popularité
        title=f"Popularité moyenne des genres en Europe - {genre_filter.title()}"
    )

    # Ajuster la projection et limiter la carte à l'Europe
    fig.update_geos(
        scope="europe",  # Limiter l'affichage à l'Europe
        projection_type="equirectangular",  # Projection géographique pour l'Europe
        showcoastlines=False,  # Désactiver les côtes
        showland=True,  # Afficher les terres
        landcolor="white",  # Couleur des terres en blanc
        bgcolor="black",  # Fond noir pour les océans
        fitbounds="locations",  # Ajuster la carte aux données des pays
        visible=True  # Rendre la carte visible
    )

    # Ajuster l'apparence du graphique (fond noir, texte blanc, etc.)
    fig.update_layout(
        title_font_size=20,
        geo=dict(
            showframe=False,  # Désactiver le cadre autour de la carte
            showcoastlines=False,  # Pas de côtes visibles
            projection_type='equirectangular'  # Projection pour l'Europe
        ),
        paper_bgcolor='black',  # Fond noir pour la page
        plot_bgcolor='black',  # Fond noir pour la carte
        font=dict(color='white'),  # Texte en blanc
        margin={"r": 0, "t": 50, "l": 0, "b": 0},  # Ajuster les marges autour de la carte
        width=800,  # Largeur de la carte
        height=500  # Hauteur de la carte
    )

    print("Carte Plotly créée avec succès")

    # Retourner la figure sous forme de JSON pour l'afficher sur une page web
    return to_json(fig)
