from data.data_manager import DataManager
from static.enumerations import genre_colors
import plotly.graph_objects as go


def build_sankey_diagram(selected_genres):
    datamanager = DataManager()
    
    genre_matrix = datamanager.create_genre_collaboration_matrix(selected_genres)

    if genre_matrix.empty:
        print(f"Aucune collaboration trouvée pour les genres {', '.join(selected_genres)}")
        return None


    all_genres = list(genre_matrix.columns.union(genre_matrix.index)) 
    genre_indices = {genre: i for i, genre in enumerate(all_genres)} 

    source = []
    target = []
    value = []
    link_colors = []

    for genre1 in genre_matrix.index:
        for genre2 in genre_matrix.columns:
            collaborations = genre_matrix.loc[genre1, genre2]
            if collaborations > 0:
                source.append(genre_indices[genre1])
                target.append(genre_indices[genre2])
                value.append(collaborations)
                link_colors.append(genre_colors.get(genre1.lower(), '#CCCCCC'))

    node_colors = [genre_colors.get(genre.lower(), '#CCCCCC') for genre in all_genres]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_genres, 
            color=node_colors
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors  
        )
    )])

    fig.update_layout(
        title_text="Diagramme de Sankey des collaborations entre genres",
        font_size=10,
        paper_bgcolor='black',  # Fond noir
        plot_bgcolor='black',  
        font=dict(color='white')  
    )

    print("Diagramme de Sankey créé.") 

    return fig
