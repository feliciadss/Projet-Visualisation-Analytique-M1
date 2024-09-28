import plotly.express as px
import json
from plotly.io import to_json
from data.data_manager import DataManager

def build_map(genre_filter):
    # Récupérer les données
    data_manager = DataManager()
    df = data_manager.create_tracks_artists_dataframe(genre_filter)

    # Vérifier si le DataFrame est correct
    print("DataFrame :")
    print(df.head())  # Imprimer les premières lignes du DataFrame

    if df.empty:
        print(f"Aucune donnée disponible pour le genre {genre_filter}")
        return None

    # Grouper par marché et compter le nombre d'artistes par pays
    df_market_count = df.groupby('artist_market').size().reset_index(name='artist_count')  # Créer 'artist_count'

    # Vérifier le DataFrame après regroupement
    print("DataFrame après regroupement par marché :")
    print(df_market_count)

    # Charger le fichier GeoJSON
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

    # Créer la carte Plotly avec les données des pays (sans normalisation)
    fig = px.choropleth(
        df_market_count,
        geojson=europe_geojson,
        locations="artist_market",  # Le marché artistique (pays) sous forme de codes ISO
        featureidkey="properties.ISO_A3",  # Correspond au champ ISO-3 dans le fichier GeoJSON
        color="artist_count",  # Utiliser les comptes d'artistes pour la couleur
        hover_name="artist_market",  # Nom du pays au survol
        color_continuous_scale="Blues",  # Palette de couleurs pour la heatmap
        title=f"Heatmap de l'Europe - Genre: {genre_filter}"
    )

    # Ajuster la projection et limiter la carte à l'Europe
    fig.update_geos(
        scope="europe",  # Limiter l'affichage à l'Europe
        projection_type="equirectangular",  # Projection géographique pour l'Europe
        showcoastlines=False,  # Désactiver les côtes
        showland=True,  # Afficher les terres
        landcolor="white",  # Couleur des pays (terres) en blanc
        bgcolor="black",  # Couleur de fond (océans) en noir
        fitbounds="locations",  # Adapter la carte aux données
        visible=True  # Rendre la carte visible
    )

    # Ajuster le layout (fond noir, etc.)
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
        width=600,  # Largeur de la carte
        height=300  # Hauteur de la carte
    )

    print("Plotly figure créée avec succès")

    return to_json(fig)
