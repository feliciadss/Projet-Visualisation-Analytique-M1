import plotly.graph_objects as go
from data.data_manager import DataManager


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

        fig.add_trace(go.Bar(
            x=df_avg['genre'],
            y=df_avg[feature],
            text=df_avg[feature], 
            textposition='auto',
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],  # Couleurs
        ))

        # Configuration du layout
        fig.update_layout(
            title=f'Comparaison des genres pour {feature}', 
            xaxis_title='Genres', 
            yaxis_title=feature, 
            paper_bgcolor='black',  
            plot_bgcolor='black',  # Fond noir 
            font=dict(color='white'),  # Texte en blanc
            showlegend=False
        )

        bar_charts.append(fig.to_html())

    return bar_charts
