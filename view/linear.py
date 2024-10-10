import pandas as pd
from datetime import datetime
from data.data_manager import DataManager

def build_linear_chart(selected_genres):
    data_manager = DataManager()
    all_album_data = []
    
    # Récupérer la date actuelle
    current_year = datetime.now().year
    start_year = current_year - 3  # Trois dernières années

    for genre in selected_genres:
        albums = data_manager.create_album_dataframe([genre])  # Supposons que cette méthode renvoie les albums par genre
        print(albums.columns)  # Vérifiez les colonnes

        if not albums.empty:
            # Convertir release_date en datetime
            albums['release_date'] = pd.to_datetime(albums['release_date'], errors='coerce')

            # Filtrer pour les albums sortis dans les trois dernières années
            filtered_albums = albums[(albums['release_date'].dt.year >= start_year) & (albums['release_date'].dt.year <= current_year)]
            filtered_albums['semester'] = filtered_albums['release_date'].dt.to_period('Q').dt.qtr
            
            # Compter le nombre d'albums par semestre
            album_counts = filtered_albums.groupby(['semester']).size().reset_index(name='count')
            album_counts['genre'] = genre
            all_album_data.append(album_counts)

    # Combiner les données de tous les genres
    final_df = pd.concat(all_album_data, ignore_index=True) if all_album_data else pd.DataFrame()
    
    # Créer le pivot pour le graphique
    return final_df.pivot(index='semester', columns='genre', values='count').fillna(0)
