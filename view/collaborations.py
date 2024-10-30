from dash import html, dcc, Output, Input, ALL, callback_context
from dash.dependencies import State
import plotly.graph_objects as go
from data.data_manager import DataManager
from static.enumerations import genre_colors, genres

layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1('Collaboration entre genres', style={'textAlign': 'center', 'color': 'white'}),
    
    html.H3(
        "Analyser la diversité des genres au sein des featurings entre artistes de différents genres. Cette page montre comment les genres se mélangent et s’influencent mutuellement.",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}
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
            dcc.Graph(id='sankey-graph', style={'height': '500px'})
        ]),
        # Stockage de l'état des genres sélectionnés
        dcc.Store(id='selected-genres', data={genre: genre == 'indie' for genre in genres}),
    ]),

    html.Div(style={'width': '100%', 'textAlign': 'center', 'marginTop': '30px'}, children=[
        html.P(
            "Le diagramme de Sankey illustre les collaborations musicales entre les différents genres sélectionnés. "
            "Chaque cercle représente un genre musical, et les tailles des cercles indiquent leur importance dans les collaborations. "
            "Les branches qui relient les cercles représentent les collaborations entre les genres, avec leur épaisseur reflétant "
            "le nombre de collaborations. Plus une branche est épaisse, plus les collaborations entre ces genres sont nombreuses.",
            style={'color': 'white', 'fontSize': '16px', 'maxWidth': '800px', 'margin': '0 auto', 'lineHeight': '1.5'}
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
            "color": "#999",
            "position": "fixed",
            "bottom": "0",
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
