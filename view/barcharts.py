import plotly.graph_objects as go
from data.data_manager import DataManager
from static.enumerations import genre_colors 

# Fonction pour créer tous les bar charts pour les features
def build_barcharts(selected_genres):
    data_manager = DataManager()
    df = data_manager.create_audiofeatures_dataframe(selected_genres) 
    
    if df is None or df.empty:
        print("Le DataFrame est vide ou None")
        return []
    
    features = ['tempo', 'energy', 'danceability', 'acousticness', 'valence', 'duration_ms']
    bar_charts = []

    for feature in features:
        fig = go.Figure()

        df_avg = df.groupby('genre')[feature].mean().reset_index()
        colors = [genre_colors.get(genre, '#ffffff') for genre in df_avg['genre']]

        fig.add_trace(go.Bar(
            x=df_avg['genre'],
            y=df_avg[feature],
            text=df_avg[feature], 
            textposition='auto',
            marker_color=colors, 
        ))

        # Configuration du layout
        fig.update_layout(
            title=f'Comparaison des genres pour {feature}', 
            xaxis_title='Genres', 
            yaxis_title=feature, 
            paper_bgcolor='black',  # Fond noir
            plot_bgcolor='black',  # Fond noir 
            font=dict(color='white'),  # Texte en blanc
            showlegend=False
        )
        
        bar_charts.append(fig.to_html())

    return bar_charts
