from dash import html, dcc, Output, Input
import plotly.graph_objects as go
from data.data_manager import DataManager
from static.enumerations import genre_colors


layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1('Collaboration entre genres', style={'textAlign': 'center', 'color': 'white'}),
    
    html.H3(
        "Sur cette page, des diagrammes de Sankey sont utilisés pour illustrer les collaborations entre un ou plusieurs genres sélectionnés et les autres.",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}
    ),
    
    # Conteneur général pour la sélection et le diagramme Sankey
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, children=[
        # Bouton pour revenir à l'accueil
        html.Div(style={'position': 'absolute','top': '30px','right': '30px','z-index': '1000','font-size': '40px'},children=[
            dcc.Link('🏠', href='/'),
        ]),
        # Sélection multiple des genres à gauche
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.P("Sélectionnez un ou plusieurs genres musicaux:", style={'fontWeight': 'bold', 'color': 'white'}),
            dcc.Checklist(
                id='sankey-genre-radio',
                options=[{'label': genre.title(), 'value': genre} for genre in genre_colors.keys()],
                value=[list(genre_colors.keys())[0]],  
                style={'color': 'white', 'backgroundColor': 'black'}
            ),
        ]),
        #centrer diagramme
        html.Div(style={'flex': '2', 'padding': '10px'}, children=[
            dcc.Graph(id='sankey-graph', style={'height': '500px'})
                ])
    ]),
    html.Div(style={'width': '100%', 'textAlign': 'center', 'marginTop': '30px'}, children=[
        html.P(
            "Le diagramme de Sankey illustre les collaborations musicales entre les différents genres sélectionnés. "
            "Chaque cercle représente un genre musical, et les tailles des cercles indiquent leur importance dans les collaborations. "
            "Les branches qui relient les cercles représentent les collaborations entre les genres, avec leur épaisseur reflétant "
            "le nombre de collaborations. Plus une branche est épaisse, plus les collaborations entre ces genres sont nombreuses.",
            style={'color': 'white', 'fontSize': '16px', 'maxWidth': '800px', 'margin': '0 auto', 'lineHeight': '1.5'}
        )
    ])
])

def register_callback(app):
    @app.callback(
        Output('sankey-graph', 'figure'),
        Input('sankey-genre-radio', 'value')
    )
    def display_sankey(selected_genres):
        datamanager = DataManager()
        
        genre_matrix = datamanager.create_genre_collaboration_matrix(selected_genres)
        
        if genre_matrix.empty:
            return go.Figure()

        all_genres = list(genre_matrix.columns.union(genre_matrix.index))
        genre_indices = {genre: i for i, genre in enumerate(all_genres)}

        source, target, value, link_colors = [], [], [], []
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
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white')
        )

        return fig
