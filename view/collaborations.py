from dash import html, dcc, Output, Input, ALL, callback_context, dash_table
from dash.dependencies import State
import plotly.graph_objects as go
from data.data_manager import DataManager
from static.enumerations import genre_colors, genres

layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1('Collaboration entre genres', style={'textAlign': 'center', 'color': 'white'}),
    
    html.H3(
        "Analyser la diversité des genres au sein des featurings entre artistes de différents genres. Cette page montre comment les genres se mélangent et s’influencent mutuellement. Cliquez sur le lien entre deux genre pour afficher le top 10 des titres en collaboration associés à ces deux genres",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal', 'paddingLeft': '50px', 'paddingRight': '50px'}
    ),
    html.P(
        "Le diagramme de Sankey illustre les collaborations musicales entre les différents genres sélectionnés. "
        "Chaque cercle représente un genre musical, et les tailles des cercles indiquent leur importance dans les collaborations. "
        "Les branches qui relient les cercles représentent les collaborations entre les genres, avec leur épaisseur reflétant "
        "le nombre de collaborations. Plus une branche est épaisse, plus les collaborations entre ces genres sont nombreuses.",
        style={'color': 'white', 'fontSize': '12px', 'textAlign': 'center', 'marginTop': '10px','paddingLeft': '60px', 'paddingRight': '60px'}
    ),
    
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, children=[
        # Bouton pour revenir à l'accueil
        html.Div(style={'position': 'absolute','top': '30px','right': '30px','z-index': '1000','font-size': '40px'},children=[
            dcc.Link('🏠', href='/'),
        ]),
        
        
        # Sélection multiple des genres sous forme de boutons colorés à gauche
        html.Div(id='genre-colored-button', style={'flex': '1', 'padding': '10px', 'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'}, 
                 children=[
            html.Button(
                genre.title(),
                id={'type': 'genre-button', 'index': genre},
                n_clicks=0,
                style={
                    'backgroundColor': genre_colors.get(genre, '#CCCCCC'),
                    'color': 'white',
                    'border': 'none',
                    'padding': '10px 20px',
                    'cursor': 'pointer',
                    'borderRadius': '5px'
                }
            ) for genre in genre_colors.keys()
        ]),
        #centrer diagramme
        html.Div(style={'flex': '2', 'padding': '10px'}, children=[
            dcc.Graph(id='sankey-graph', style={'height': '375px'})
        ]),
        # Stockage de l'état des genres sélectionnés
        dcc.Store(id='selected-genres', data={genre: genre == 'electronic' for genre in genres}),
    ]),

    html.Div(id='collaboration-table-container', style={'marginTop': '10px'}, children=[
        html.H4("Top 10 Collaborations", style={'color': 'white', 'textAlign': 'center'}),
        dash_table.DataTable(
            id='collaboration-table',
            columns=[
                {"name": "Artiste 1", "id": "artist1"},
                {"name": "Artiste 2", "id": "artist2"},
                {"name": "Popularité", "id": "track_popularity"},
                {"name": "Track ID", "id": "track_id"}
            ],
            style_table={'width': '80%', 'margin': '0 auto'},
            style_cell={'backgroundColor': 'black', 'color': 'white', 'textAlign': 'center'},
            style_header={'backgroundColor': 'grey', 'fontWeight': 'bold'}
        )
    ]),
    
    # Pied de page
    html.Footer(
        html.Small(
            [
                "Les données sont fournies par l' ",
                html.A("API Spotify", href="https://developer.spotify.com/documentation/web-api", target="_blank", style={'color': 'white'}),
            ]
        ),
        style={
            "textAlign": "center",
            "padding": "10px",
            "backgroundColor": "black",
            "width": "100%",
            "fontSize": "12px",
            "color": "#999"
        },
    ),
])

def register_callback(app):
    @app.callback(
        Output('sankey-graph', 'figure'),
        Input('selected-genres', 'data')
    )
    def display_sankey(selected_genres):
        active_genres = [genre for genre, selected in selected_genres.items() if selected]
        datamanager = DataManager()
        
        genre_matrix = datamanager.create_genre_collaboration_matrix(active_genres)
        
        if genre_matrix.empty:
            return go.Figure()

        # Liste de tous les genres uniques dans la matrice de collaboration
        all_genres = list(genre_matrix.columns.union(genre_matrix.index))
        genre_indices = {genre: i for i, genre in enumerate(all_genres)}

        source, target, value, link_colors, link_customdata = [], [], [], [], []
        for genre1 in genre_matrix.index:
            for genre2 in genre_matrix.columns:
                collaborations = genre_matrix.loc[genre1, genre2]
                if collaborations > 0:
                    source.append(genre_indices[genre1])
                    target.append(genre_indices[genre2])
                    value.append(collaborations)
                    link_colors.append(genre_colors.get(genre1.lower(), '#CCCCCC'))
                    # Ajouter des données custom pour chaque lien indiquant les genres source et cible
                    link_customdata.append(f"Collaboration entre {genre1} et {genre2}")

        # Couleurs des nœuds
        node_colors = [genre_colors.get(genre.lower(), '#CCCCCC') for genre in all_genres]
        node_customdata = [f"Genre: {genre}" for genre in all_genres]  # Données custom pour chaque nœud

        # Créer la figure de Sankey avec customdata pour nœuds et liens
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_genres,
                color=node_colors,
                customdata=node_customdata,  # Ajouter customdata aux nœuds
                hovertemplate='%{label}<extra>%{customdata}</extra>'  # Afficher customdata au survol des nœuds
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=link_colors,
                customdata=link_customdata,  # Ajouter customdata aux liens
                hovertemplate='%{customdata}<extra></extra>'  # Afficher customdata au survol des liens
            )
        )])

        fig.update_layout(
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white')
        )

        return fig

    
    @app.callback(
        Output('selected-genres', 'data'),
        Output({'type': 'genre-button', 'index': ALL}, 'style'),
        Input({'type': 'genre-button', 'index': ALL}, 'n_clicks'),
        State('selected-genres', 'data')
    )
    def toggle_genre_selection(n_clicks_list, selected_genres):
        triggered = callback_context.triggered
        if not triggered:
            return selected_genres, [{'backgroundColor': genre_colors.get(genre, '#CCCCCC'),
                                      'color': 'white',
                                      'border': 'none',
                                      'padding': '15px 25px',
                                      'cursor': 'pointer',
                                      'fontSize': '16px', 
                                      'borderRadius': '5px'} for genre in genres]

        # Extraire l'ID du bouton qui a été cliqué
        triggered_id = triggered[0]['prop_id'].split('.')[0]
        genre = eval(triggered_id)['index']
        selected_genres[genre] = not selected_genres[genre]

        # MAJ des styles de boutons
        button_styles = []
        for genre in genres:
            style = {
                'backgroundColor': '#555555' if selected_genres[genre] else genre_colors.get(genre, '#CCCCCC'),
                'color': 'white',
                'border': 'none',
                'padding': '15px 25px',
                'cursor': 'pointer',
                'fontSize': '16px',
                'borderRadius': '5px'
            }
            button_styles.append(style)

        return selected_genres, button_styles

    @app.callback(
    Output('collaboration-table', 'data'),
    Output('collaboration-table', 'columns'),
    Input('sankey-graph', 'clickData')
)


    def update_collaboration_table(clickData):
        if clickData is None or not callback_context.triggered:
            source_genre = "electronic"
            target_genre = "indie" #par defaut
        else:
            try:
                customdata = clickData['points'][0]['customdata']
                genres = customdata.replace("Collaboration entre ", "").split(" et ")
                source_genre = genres[0]
                target_genre = genres[1]
            except KeyError:
                source_genre = "pop"
                target_genre = "electronic"

        datamanager = DataManager()
        top_collabs_df = datamanager.get_top_collabs_between_genres(source_genre, target_genre)

        top_collabs_df = top_collabs_df.rename(columns={
            'artist1': source_genre,  # Renomme 'artist1' par le genre source
            'artist2': target_genre,  # Renomme 'artist2' par le genre cible
            'track_name': 'titre'    
        })
        
        columns = [{"name": col, "id": col} for col in top_collabs_df.columns]
        records = top_collabs_df.to_dict('records')

        return records, columns
