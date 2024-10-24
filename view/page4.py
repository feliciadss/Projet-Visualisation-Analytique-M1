import plotly.graph_objects as go
import pandas as pd
from data.data_manager import DataManager
from static.enumerations import genre_colors 

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
            name=f'Average Features for {genre}',
            line_color=genre_colors.get(genre, '#ffffff')  # Utilisation de la couleur du genre depuis le dictionnaire
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),  
        ),
        paper_bgcolor='black',  
        plot_bgcolor='black',  
        font=dict(color='white'),  
        showlegend=True,
        title='Radar Chart Comparing Audio Features by Genre',
        title_font=dict(color='white')
    )

    return fig