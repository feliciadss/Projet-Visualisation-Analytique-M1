import plotly.graph_objects as go
import pandas as pd
from data.data_manager import DataManager

# Fonction pour normaliser chaque colonne manuellement entre 0 et 1
def normalize_column(col):
    return (col - col.min()) / (col.max() - col.min())  # Normalisation entre 0 et 1

# Fonction pour créer un radar chart avec normalisation manuelle
def build_radar(selected_genres):
    
    data_manager = DataManager()
    df = data_manager.create_radar_dataframe(selected_genres)

    # Vérifier que df n'est pas None et n'est pas vide
    if df is None or df.empty:
        print("Le DataFrame est vide ou None")
        return None  # Ou créer un radar chart fictif ici
    
    # Garder uniquement les colonnes des features audio
    features = ['tempo', 'energy', 'danceability', 'acousticness', 'valence', 'duration_ms']
    
    # Normalisation manuelle pour chaque colonne de features
    df[features] = df[features].apply(normalize_column)

    fig = go.Figure()

    # Boucle sur les genres sélectionnés
    for genre in selected_genres:
        # Vérifier que le genre est bien dans le DataFrame avant de filtrer
        if 'genre' not in df.columns:
            print(f"Le DataFrame ne contient pas la colonne 'genre' pour le genre {genre}")
            continue

        # Filtrer le DataFrame pour ne garder que les tracks dont un artiste est du genre en question
        df_genre = df[df['genre'] == genre]
        
        if df_genre.empty:
            print(f"Aucun track trouvé pour le genre {genre}")
            continue

        # Calculer la moyenne des features pour ce genre
        mean_features = df_genre[features].mean()

        # Ajouter une trace pour chaque genre dans le radar chart
        fig.add_trace(go.Scatterpolar(
            r=mean_features.values,  # Valeurs normalisées entre 0 et 1
            theta=features,
            fill='toself',
            name=f'Average Features for {genre}'
        ))

    # Mettre à jour le layout pour un visuel propre
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),  # Supprimer les unités affichées (0 à 1)
        ),
        paper_bgcolor='black',  # Fond noir de la charte
        plot_bgcolor='black',  # Fond noir pour la partie du graphique
        font=dict(color='white'),  # Couleur du texte en blanc
        showlegend=True,
        title='Radar Chart Comparing Audio Features by Genre',
        title_font=dict(color='white')  # Couleur du titre en blanc
    )

    return fig
