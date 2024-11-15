from dash import html, dcc, Output, Input, callback_context, dash_table, callback
from dash.dependencies import State
import plotly.graph_objects as go
import pandas as pd
from data.data_manager import DataManager
from static.enumerations import genre_colors, genres
import dash

dash.register_page(__name__, path="/collaborations", name="Collaborations entre genres")

layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1('Collaboration entre genres', style={'textAlign': 'center', 'color': 'white'}),
    
    html.H3(
        "Analyser la diversité des genres au sein des featurings entre artistes de différents genres. "
        "Cette page montre comment les genres se mélangent et s’influencent mutuellement. Cliquez sur le lien entre "
        "deux genres pour afficher le top 10 des titres en collaboration associés à ces deux genres.",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal', 'paddingLeft': '50px', 'paddingRight': '50px'}
    ),
    html.P(
        "Le diagramme de Sankey illustre les collaborations musicales entre les différents genres sélectionnés. "
        "Chaque cercle représente un genre musical, et les tailles des cercles indiquent leur importance dans les collaborations. "
        "Les branches qui relient les cercles représentent les collaborations entre les genres, avec leur épaisseur reflétant "
        "le nombre de collaborations. Plus une branche est épaisse, plus les collaborations entre ces genres sont nombreuses.",
        style={'color': 'white', 'fontSize': '12px', 'textAlign': 'center', 'marginTop': '10px', 'paddingLeft': '60px', 'paddingRight': '60px'}
    ),
    
    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, children=[
        # Back to home button
        html.Div(style={'position': 'absolute', 'top': '30px', 'right': '30px', 'z-index': '1000', 'font-size': '40px'}, children=[
            dcc.Link('🏠', href='/'),
        ]),

        # Genre selection buttons
        html.Div(id='collab-genre-colored-button', style={'flex': '1', 'padding': '10px', 'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'}, 
                 children=[
            html.Button(
                genre.title(),
                id=f'collab-genre-button-{genre}',  # Unique ID for each genre button
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
        
        # Sankey Diagram
        html.Div(style={'flex': '2', 'padding': '10px'}, children=[
            dcc.Graph(id='sankey-graph', style={'height': '375px'})
        ]),

        dcc.Store(id='selected-genres-collab', data={genre: genre == 'electronic' for genre in genres}),
    ]),

    # Collaboration table for top 10 collaborations
    html.Div(id='collaboration-table-container', style={'marginTop': '10px'}, children=[
        html.H4("Top 10 Collaborations", style={'color': 'white', 'textAlign': 'center'}),
        dash_table.DataTable(
            id='collaboration-table',
            columns=[
                {"name": "Artiste 1", "id": "artist1"},
                {"name": "Artiste 2", "id": "artist2"},
                {"name": "Popularité", "id": "track_popularity"},
                {"name": "Track ID", "id": "track_id"},
                {"name": "Écoute-moi", "id": "preview_url"}
            ],
            style_table={'width': '80%', 'margin': '0 auto', 'fontFamily': 'Courier Newx'},
            style_cell={'backgroundColor': 'black', 'color': 'white', 'textAlign': 'center', 'fontFamily': 'Courier New'},
            style_header={'backgroundColor': 'grey', 'fontWeight': 'bold'}
        )
    ]),
    
    # Footer
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


@callback(
    Output('sankey-graph', 'figure'),
    Input('selected-genres-collab', 'data')
)
def display_sankey(selected_genres):
    active_genres = [genre for genre, selected in selected_genres.items() if selected]
    data_manager = DataManager()
    
    genre_matrix = data_manager.create_genre_collaboration_matrix(active_genres)
    
    if genre_matrix.empty:
        return go.Figure()
    
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
                link_customdata.append(f"Collaboration entre {genre1} et {genre2}")

    # Colors for nodes
    node_colors = [genre_colors.get(genre.lower(), '#CCCCCC') for genre in all_genres]
    node_customdata = [f"Genre: {genre}" for genre in all_genres]

    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_genres,
            color=node_colors,
            customdata=node_customdata,
            hovertemplate='%{label}<extra>%{customdata}</extra>'
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors,
            customdata=link_customdata,
            hovertemplate='%{customdata}<extra></extra>'
        )
    )])

    fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font=dict(color='white'))
    return fig


@callback(
    Output('selected-genres-collab', 'data'),
    [Output(f'collab-genre-button-{genre}', 'style') for genre in genres],
    [Input(f'collab-genre-button-{genre}', 'n_clicks') for genre in genres],
    State('selected-genres-collab', 'data')
)
def toggle_genre_selection(*args):
    n_clicks_list = args[:-1]
    selected_genres = args[-1]
    triggered = callback_context.triggered

    if triggered:
        triggered_id = triggered[0]['prop_id'].split('.')[0]
        genre = triggered_id.split('-')[-1]
        selected_genres[genre] = not selected_genres[genre]

    button_styles = [
        {
            'backgroundColor': genre_colors.get(genre, '#CCCCCC') if selected_genres[genre] else '#555555',
            'color': 'white',
            'border': 'none',
            'padding': '15px 25px',
            'cursor': 'pointer',
            'fontSize': '16px',
            'borderRadius': '5px'
        }
        for genre in genres
    ]

    return (selected_genres, *button_styles)

@callback(
    Output('collaboration-table', 'data'),
    Output('collaboration-table', 'columns'),
    Input('sankey-graph', 'clickData')
)
def update_collaboration_table(click_data):
    if not click_data or 'customdata' not in click_data['points'][0]:
        source_genre, target_genre = "electronic", "pop"  # default genres
    else:
        customdata = click_data['points'][0]['customdata']
        genres = customdata.replace("Collaboration entre ", "").split(" et ")
        source_genre, target_genre = genres[0], genres[1]

    data_manager = DataManager()
    top_collabs_df = data_manager.get_top_collabs_between_genres(source_genre, target_genre)

    top_collabs_df = top_collabs_df.rename(columns={
        'artist1': f'{source_genre}',
        'artist2': f'{target_genre}',
        'track_popularity': 'Popularité',
        'track_name': 'Nom du track',
        'preview_url' : 'Lien vers le track'
    })
    # Make "Lien vers le track" column clickable
    top_collabs_df['Lien vers le track'] = top_collabs_df['Lien vers le track'].apply(
        lambda url: f'[Écoute moi]({url})' if pd.notnull(url) else 'N/A'
    )

    columns = [{"name": col, "id": col, "presentation":"markdown"} for col in top_collabs_df.columns]
    records = top_collabs_df.to_dict('records')

    return records, columns
