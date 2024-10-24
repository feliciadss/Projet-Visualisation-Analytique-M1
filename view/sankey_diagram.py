from dash import html, dcc, Output, Input
import plotly.graph_objects as go
from data.data_manager import DataManager
from static.enumerations import genre_colors

layout = html.Div([
    html.H1('Collaboration entre genres', style={'textAlign': 'center', 'color': 'white'}),
    html.H3(
        "Sur cette page, des diagrammes de Sankey sont utilisés pour illustrer la collaboration entre un genre sélectionné et les autres ",
        style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal'}
    ),
    html.P("Sélectionnez un genre musical:", style={'color': 'white', 'fontWeight': 'bold'}),
    dcc.RadioItems(
        id='sankey-genre-radio', 
        options=[{'label': genre, 'value': genre} for genre in genre_colors.keys()],
        value=list(genre_colors.keys())[0], 
        labelStyle={'display': 'block', 'color': 'white'}, 
        style={'color': 'white', 'backgroundColor': 'black'}, 
        inputStyle={'color': 'white'} 
    ),
    dcc.Graph(id='sankey-graph') 
], style={'backgroundColor': 'black', 'padding': '20px'}) 

def register_callback(app):
    @app.callback(
        Output('sankey-graph', 'figure'),
        Input('sankey-genre-radio', 'value')
    )
    def display_sankey(selected_genre):
        datamanager = DataManager()
        genre_matrix = datamanager.create_genre_collaboration_matrix([selected_genre])
        
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
