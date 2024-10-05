import plotly.graph_objects as go
import pandas as pd
from data.data_manager import DataManager

# Fonction pour normaliser chaque colonne manuellement entre 0 et 1
def normalize_column(col):
    return (col - col.min()) / (col.max() - col.min())  


def build_radar(selected_genres):
    
    data_manager = DataManager()
    df = data_manager.create_audiofeatures_dataframe(selected_genres)
    
    if df is None or df.empty:
        print("Le DataFrame est vide ou None")
        return None 
    
    features = ['tempo', 'energy', 'danceability', 'acousticness', 'valence', 'duration_ms']
    
    df[features] = df[features].apply(normalize_column)

    fig = go.Figure()

    for genre in selected_genres:
        if 'genre' not in df.columns:
            print(f"Le DataFrame ne contient pas la colonne 'genre' pour le genre {genre}")
            continue

        df_genre = df[df['genre'] == genre]
        
        if df_genre.empty:
            print(f"Aucun track trouvé pour le genre {genre}")
            continue

        mean_features = df_genre[features].mean()

        fig.add_trace(go.Scatterpolar(
            r=mean_features.values, 
            theta=features,
            fill='toself',
            name=f'Average Features for {genre}'
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),  # Supprimer unités
        ),
        paper_bgcolor='black',  # Fond noir de la chart
        plot_bgcolor='black',  # Fond noir pour la partie du graphique
        font=dict(color='white'),  # Couleur du texte en blanc
        showlegend=True,
        title='Radar Chart Comparing Audio Features by Genre',
        title_font=dict(color='white')  # Couleur du titre en blanc
    )

    return fig
