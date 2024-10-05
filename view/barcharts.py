import plotly.graph_objects as go
from data.data_manager import DataManager

# Fonction pour créer tous les bar charts pour les features
def build_barcharts(selected_genres):
    data_manager = DataManager()
    df = data_manager.create_audiofeatures_dataframe(selected_genres)  # Réutilisation du DataFrame
    
    if df is None or df.empty:
        print("Le DataFrame est vide ou None")
        return []  # Renvoie une liste vide si aucun genre n'est trouvé
    
    features = ['tempo', 'energy', 'danceability', 'acousticness', 'valence', 'duration_ms']
    bar_charts = []

    # Créer un bar chart pour chaque feature
    for feature in features:
        fig = go.Figure()

        # Filtrer le DataFrame pour les genres sélectionnés
        df_filtered = df[df['genre'].isin(selected_genres)]

        # Ajouter une barre pour chaque genre pour la feature sélectionnée
        fig.add_trace(go.Bar(
            x=df_filtered['genre'],
            y=df_filtered[feature],
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],  # Utiliser les mêmes couleurs que le radar
        ))

        # Configuration du layout
        fig.update_layout(
            title=f'Comparaison des genres pour {feature}',
            xaxis_title='Genres',
            yaxis_title=feature,
            paper_bgcolor='black',  # Fond noir pour uniformité
            plot_bgcolor='black',
            font=dict(color='white'),  # Texte en blanc
            showlegend=False
        )

        # Convertir le graphique en HTML et l'ajouter à la liste
        bar_charts.append(fig.to_html())

    return bar_charts
