import plotly.express as px
import json
from plotly.io import to_json
from data.data_manager import DataManager
from static.enumerations import genre_colors
import pycountry

def convert_iso2_to_iso3(iso2_code):
    country = pycountry.countries.get(alpha_2=iso2_code)
    return country.alpha_3 if country else None  

def build_map(genre_filter):
    data_manager = DataManager()
    df = data_manager.create_album_genre_popularity_dataframe(genre_filter)
    df['market'] = df['market'].apply(convert_iso2_to_iso3)

    if df.empty:
        print(f"Aucune donnée disponible pour le genre {genre_filter}")
        return None

    geojson_path = "./static/custom.geo.json"
    try:
        with open(geojson_path, "r", encoding="utf-8") as geojson_file:
            europe_geojson = json.load(geojson_file)
            print("GeoJSON chargé avec succès")
    except FileNotFoundError:
        print(f"Fichier non trouvé à l'emplacement : {geojson_path}")
        return None

    color_for_genre = genre_colors.get(genre_filter.lower(), '#ffffff')  # Défaut

    fig = px.choropleth(
        df,
        geojson=europe_geojson,
        locations="market",  # codes IOS pays
        featureidkey="properties.ISO_A3",  # champs ISO-3  GeoJSON
        color="popularity",
        hover_name="market",
        color_continuous_scale=[[0, '#000000'], [1, color_for_genre]],
        title=f"Popularité des genres par pays pour {genre_filter.title()}"
    )

    fig.update_geos(
        scope="europe", #focus
        projection_type="equirectangular", 
        showcoastlines=False, 
        showland=True, 
        landcolor="white",  
        bgcolor="black",  # Fond noir
        fitbounds="locations", 
        visible=True
    )

    # Ajuster l'apparence
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
