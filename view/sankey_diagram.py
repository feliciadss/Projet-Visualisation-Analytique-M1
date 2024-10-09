from data.data_manager import DataManager
import plotly.graph_objects as go
import pandas as pd
from plotly.io import to_json
from static.enumerations import genre_colors  # Importer le dictionnaire des couleurs


def plot_sankey_diagram(selected_genres):
    data_manager = DataManager()
    
    # Créer la matrice des collaborations entre les genres sélectionnés
    all_genre_pairs = []
    
    for genre_selectionné in selected_genres:
        genre_matrix = data_manager.create_genre_collaboration_matrix(genre_selectionné)
        if not genre_matrix.empty:
            all_genre_pairs.append(genre_matrix)

    if not all_genre_pairs:
        return "Aucune collaboration trouvée pour les genres sélectionnés."
    
    # Fusionner toutes les matrices de collaboration et convertir en valeurs numériques
    combined_genre_matrix = pd.concat(all_genre_pairs).groupby(level=0).sum()
    
    # S'assurer que toutes les valeurs sont numériques
    combined_genre_matrix = combined_genre_matrix.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Genres (sources = genres sélectionnés, cibles = genres avec collaborations)
    selected_genres_list = selected_genres
    all_genres = combined_genre_matrix.columns.tolist()

    # Création des sources, cibles et valeurs pour le Sankey Diagram
    sources = []
    targets = []
    values = []
    colors = []

    for i, genre_selected in enumerate(selected_genres_list):
        for j, genre in enumerate(all_genres):
            if combined_genre_matrix.iloc[i, j] > 0:  # Seule comparaison avec des entiers/float
                sources.append(i)
                targets.append(len(selected_genres_list) + j)  # Indice pour le genre cible
                values.append(combined_genre_matrix.iloc[i, j])
                colors.append(genre_colors.get(genre_selected, 'grey'))  # Couleur du genre sélectionné

    # Noeuds (à gauche : genres sélectionnés, à droite : genres avec collaborations)
    labels = selected_genres_list + all_genres
    node_colors = [genre_colors.get(genre, 'grey') for genre in labels]

    # Créer le diagramme de Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=node_colors  # Couleurs des genres
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors  # Couleurs des liens correspondant aux genres sélectionnés
        )
    )])

    # Mise en page du diagramme
    fig.update_layout(
        title_text=f"Sankey Diagram des collaborations pour les genres sélectionnés",
        font=dict(size=14)
    )
    
    # Retourner le diagramme au format JSON pour l'affichage
    return to_json(fig)
