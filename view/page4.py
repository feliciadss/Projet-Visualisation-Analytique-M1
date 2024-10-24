from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from data.data_manager import DataManager
from static.enumerations import genres
from static.enumerations import genre_colors

layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '20px'}, children=[
    html.H1('Caractéristiques musicales par genre', style={'color': 'white', 'textAlign': 'center'}),
    
    # Conteneur général ici
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
        # Checklist des genres sur la gauche
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.P("Sélectionnez un ou plusieurs genres :", style={'fontWeight': 'bold', 'color': 'white'}),
            dcc.Checklist(
                id="genre-checklist",
                options=genres,
                value=["pop", "rock"],
                inline=False,
                style={'color': 'white'}
            ),
        ]),
        
        # Radar chart au centre
        html.Div(style={'flex': '2', 'padding': '10px'}, children=[
            dcc.Graph(id="radar-graph", style={'height': '400px', 'backgroundColor': 'black'})
        ]),

        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            dcc.Graph(id="bar-chart", style={'height': '400px', 'backgroundColor': 'black'})
        ]),
    ]),
])

def register_callback(app):
    @app.callback(
        Output("radar-graph", "figure"),
        Input("genre-checklist", "value")
    )
    def update_radar(selected_genres):
        data_manager = DataManager()
        df = data_manager.create_audiofeatures_dataframe(selected_genres)

        if df is None or df.empty:
            print("Le DataFrame est vide ou None")
            return go.Figure()

        features = ['tempo', 'energy', 'danceability', 'acousticness', 'valence', 'duration_ms']
        df[features] = df[features].apply(normalize_column)

        fig = go.Figure()

        for genre in selected_genres:
            df_genre = df[df['genre'] == genre]
            if df_genre.empty:
                continue

            mean_features = df_genre[features].mean()

            fig.add_trace(go.Scatterpolar(
                r=mean_features.values,
                theta=features,
                fill='toself',
                name=f'Average Features for {genre}',
                line_color=genre_colors.get(genre, '#ffffff'), 
                hoverinfo='theta+r', 
                mode='lines+markers', 
                marker=dict(size=10, symbol='circle')  
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, showline=False, showticklabels=False)),
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white'),
            showlegend=True,
            title='Radar Chart Comparing Audio Features by Genre',
            title_font=dict(color='white'),
            clickmode='event+select'  
        )

        return fig

    @app.callback(
        Output("bar-chart", "figure"),
        Input("radar-graph", "clickData"), 
        Input("genre-checklist", "value")
    )
    def update_barchart(clickData, selected_genres):
        if clickData is None or 'points' not in clickData:
            return go.Figure()
        clicked_feature = clickData['points'][0]['theta']
        data_manager = DataManager()
        df = data_manager.create_audiofeatures_dataframe(selected_genres)

        if df is None or df.empty:
            return go.Figure()
        df_avg = df.groupby('genre')[clicked_feature].mean().reset_index()
        colors = [genre_colors.get(genre, '#ffffff') for genre in df_avg['genre']]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_avg['genre'],
            y=df_avg[clicked_feature],
            text=df_avg[clicked_feature],
            textposition='auto',
            marker_color=colors,
        ))

        fig.update_layout(
            title=f'Comparaison des genres pour {clicked_feature}',
            xaxis_title='Genres',
            yaxis_title=clicked_feature,
            paper_bgcolor='black',
            plot_bgcolor='black',
            font=dict(color='white'),
            showlegend=False
        )

        return fig
    
#normalise colonnes
def normalize_column(col):
    return (col - col.min()) / (col.max() - col.min())
