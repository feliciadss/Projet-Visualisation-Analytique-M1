import plotly.express as px
from data.data_manager import DataManager
from static.enumerations import genre_colors  # Assurez-vous que le chemin est correct

def build_bubble_chart(genre):
    # Créer une instance de DataManager
    data_manager = DataManager()

    # Obtenir les sous-genres pour le genre sélectionné
    df_subgenres = data_manager.get_top_subgenres_per_genre(genre)
    
    if df_subgenres.empty:
        print("Aucune donnée disponible pour les sous-genres.")
        return None
    
    # Obtenir la couleur du genre depuis le dictionnaire genre_colors
    genre_color = genre_colors.get(genre.lower(), '#ffffff')  # Blanc par défaut si non trouvé

    # Créer un diagramme en bulles avec Plotly
    fig = px.scatter(df_subgenres, 
                     x='subgenre', 
                     y='count', 
                     size='count', 
                     color_discrete_sequence=[genre_color],  # Utiliser la couleur du genre sélectionné
                     hover_name='subgenre',
                     title=f'Diagramme en Bulles pour le genre {genre}',
                     labels={'subgenre': 'Sous-genres', 'count': 'Nombre d\'artistes'},
                     size_max=60)  # Taille max des bulles

    # Personnaliser la mise en page pour un fond noir
    fig.update_layout(
        plot_bgcolor='black',  # Fond noir pour le graphique
        paper_bgcolor='black',  # Fond noir pour l'ensemble de la figure
        font_color='white',  # Texte en blanc pour contraste
        title_font_color=genre_color,  # Titre en couleur du genre
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

    # Convertir la figure en HTML pour l'intégrer dans la page web
    return fig.to_html(full_html=False)
