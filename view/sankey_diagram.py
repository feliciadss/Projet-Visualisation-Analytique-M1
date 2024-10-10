from data.data_manager import DataManager
import plotly.graph_objects as go
import pandas as pd
from plotly.io import to_json
from static.enumerations import genre_colors  # Importer le dictionnaire des couleurs


import pandas as pd
import plotly.graph_objects as go

# Fonction pour créer un diagramme de Sankey avec les collaborations entre plusieurs genres
def plot_genre_collab_sankey(self, selected_genres):
    genre_pairs = []

    # Récupérer les artistes appartenant à un ou plusieurs des genres sélectionnés depuis MongoDB
    genres_regex = '|'.join([f'({genre})' for genre in selected_genres])  # Construire une regex pour matcher plusieurs genres
    artists_in_genre = self.artists_collection.find({'genres': {'$regex': genres_regex, '$options': 'i'}})
    artist_ids = [artist['id'] for artist in artists_in_genre]  # Extraire les IDs des artistes trouvés

    if not artist_ids:
        print(f"Aucun artiste trouvé pour les genres {', '.join(selected_genres)}")
        return pd.DataFrame()  # Retourner un DataFrame vide si aucun artiste trouvé

    # Récupérer toutes les pistes avec les artistes trouvés
    tracks = self.tracks_collection.find({'artists.id': {'$in': artist_ids, '$exists': True}})

    # Parcourir les pistes pour identifier les collaborations entre genres
    for track in tracks:
        track_artists = track.get('artists', [])  # Liste des artistes sur la piste
        artist_genres = []

        # Récupérer les genres pour chaque artiste sur la piste
        for artist in track_artists:
            artist_data = self.artists_collection.find_one({'id': artist['id']})  # Chercher l'artiste dans la base
            if artist_data and artist_data.get('genres'):
                # Récupérer tous les genres de l'artiste et filtrer ceux en lien avec les genres sélectionnés
                relevant_genres = [genre for genre in artist_data['genres'] if any(selected_genre.lower() in genre.lower() for selected_genre in selected_genres)]
                if relevant_genres:
                    artist_genres.extend(relevant_genres)  # Ajouter les genres pertinents à la liste

        # Créer des paires de genres à partir des genres récupérés
        for i in range(len(artist_genres)):
            for j in range(i + 1, len(artist_genres)):
                genre1 = artist_genres[i]
                genre2 = artist_genres[j]
                genre_pairs.append((genre1, genre2))
                genre_pairs.append((genre2, genre1))  # Matrice symétrique

    # Si aucune paire n'a été trouvée, retourner un DataFrame vide
    if not genre_pairs:
        return pd.DataFrame()

    # Convertir les paires en DataFrame pour comptabiliser les occurrences
    df_collaborations = pd.DataFrame(genre_pairs, columns=['Genre1', 'Genre2'])

    # Compter le nombre de collaborations entre chaque paire de genres
    df_collaboration_count = df_collaborations.groupby(['Genre1', 'Genre2']).size().reset_index(name='count')

    # Créer une liste unique de genres pour les nœuds du diagramme Sankey
    genres = list(pd.unique(df_collaboration_count[['Genre1', 'Genre2']].values.ravel('K')))
    genre_index = {genre: i for i, genre in enumerate(genres)}  # Créer des indices pour chaque genre

    # Transformer les genres en indices pour le diagramme Sankey
    df_collaboration_count['source'] = df_collaboration_count['Genre1'].apply(lambda x: genre_index[x])
    df_collaboration_count['target'] = df_collaboration_count['Genre2'].apply(lambda x: genre_index[x])

    # Création du diagramme de Sankey
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=genres,  # Les noms des genres
        ),
        link=dict(
            source=df_collaboration_count['source'],  # Les indices des genres source
            target=df_collaboration_count['target'],  # Les indices des genres cible
            value=df_collaboration_count['count'],    # Le nombre de collaborations (poids des liens)
        )
    ))

    fig.update_layout(title_text=f"Collaborations entre genres pour {', '.join(selected_genres)}", font_size=10)
    fig.show()

    return fig


