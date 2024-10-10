import pandas as pd
import plotly.express as px
from data.data_manager import DataManager

def build_linear_chart(selected_genres):
    data_manager = DataManager()
    
    # Créer un DataFrame avec le nombre de tracks pour chaque genre
    genre_data = []
    for genre in selected_genres:
        df = data_manager.create_audiofeatures_dataframe([genre])
        count_tracks = len(df)
        genre_data.append({'genre': genre, 'track_count': count_tracks})
    
    genre_df = pd.DataFrame(genre_data)
    
    # Créer le graphique multilinéaire
    fig = px.line(genre_df, x='genre', y='track_count', title='Nombre de Tracks par Genre', markers=True)
    
    return fig
