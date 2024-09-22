import pandas as pd
from data.get_data import get_data_from_mongodb  # Récupération des données brutes

import pandas as pd

def clean_genre(genre):
    """
    Simplifie les genres pour éviter les sous-genres ou des termes comme 'Albanian pop'.
    Par exemple, 'Albanian pop' deviendra 'pop'.
    """
    if isinstance(genre, list):
        return [g.split()[0].lower() for g in genre]  # Récupérer le mot principal du genre
    else:
        return genre.split()[0].lower() if isinstance(genre, str) else None

def get_genre_data_for_map():
    """
    Récupère et prépare les données pour la carte de chaleur des genres musicaux.
    """
    # Récupérer les données des morceaux et des artistes depuis MongoDB
    df_tracks = get_data_from_mongodb('tracks')  # DataFrame des morceaux
    df_artists = get_data_from_mongodb('artists')  # DataFrame des artistes

    # Associer les morceaux avec les artistes pour récupérer les genres et les marchés disponibles
    df_tracks = df_tracks.explode('artists')
    df_tracks['artist_id'] = df_tracks['artists'].apply(lambda x: x['id'] if isinstance(x, dict) and 'id' in x else None)
    df_tracks = df_tracks.merge(df_artists, left_on='artist_id', right_on='id', how='left')

    # Exploser les marchés disponibles (pays)
    df_tracks = df_tracks.explode('available_markets')
    df_tracks.rename(columns={'available_markets': 'country'}, inplace=True)

    # Nettoyer et simplifier les genres (par exemple, 'Albanian pop' -> 'pop')
    df_tracks['cleaned_genre'] = df_tracks['genres'].apply(clean_genre)

    # Exploser les genres si un artiste en a plusieurs
    df_tracks = df_tracks.explode('cleaned_genre')

    # Filtrer pour ne garder que les genres valides et les pays européens
    european_countries = [
        "AL", "AT", "BE", "BA", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", 
        "FR", "DE", "GR", "HU", "IS", "IE", "IT", "LV", "LI", "LT", "LU", "MT", 
        "ME", "NL", "MK", "NO", "PL", "PT", "RO", "RS", "SK", "SI", 
        "ES", "SE", "CH", "UA", "GB"
    ]
    
    df_tracks = df_tracks[df_tracks['country'].isin(european_countries)]

    # Créer un DataFrame pour compter les points des genres par pays
    genre_country_df = df_tracks.groupby(['country', 'cleaned_genre']).size().reset_index(name='points')

    # Vérifier le DataFrame final pour la heatmap
    print("DataFrame final pour la heatmap:")
    print(genre_country_df.head())

    return genre_country_df
