from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from data.data_manager import DataManager
from static.enumerations import genre_colors

# Layout de la page d'accueil
home_layout = html.Div(
    style={'backgroundColor': 'black', 'minHeight': '100vh', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center', 'color': 'white'},
    children=[
        html.H1("Analyse des Genres Musicaux en Europe"),
        html.H2(
            "Ce site web vous offre des informations essentielles sur la popularité des genres musicaux en Europe, l’évolution des tendances par pays et les collaborations entre artistes...",
            style={'textAlign': 'center', 'color': 'white', 'fontWeight': 'normal', 'paddingLeft': '50px', 'paddingRight': '50px'}
        ),
        html.Div([
            dcc.Link(
                html.Button('Popularité des genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': '#fefee2', 'fontSize': '20px', 'padding': '15px 30px', 'borderRadius': '10px'}),
                href='/popularite'
            ),
            dcc.Link(
                html.Button('Évolution des genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': '#fefee2', 'fontSize': '20px', 'padding': '15px 30px', 'borderRadius': '10px'}),
                href='/evolution_genres'
            ),
            dcc.Link(
                html.Button('Collaborations entre genres', style={'margin': '10px', 'color': 'black', 'backgroundColor': '#fefee2', 'fontSize': '20px', 'padding': '15px 30px', 'borderRadius': '10px'}),
                href='/collaborations'
            ),
            dcc.Link(
                html.Button('Caractéristiques musicales', style={'margin': '10px', 'color': 'black', 'backgroundColor': '#fefee2', 'fontSize': '20px', 'padding': '15px 30px', 'borderRadius': '10px'}),
                href='/caract_musicales'
            ),
        ], style={'display': 'flex', 'justifyContent': 'center', 'flexDirection': 'row', 'gap': '10px'}),
        html.H3(
            "Pour rendre l'expérience plus agréable, nous avons classé les genres en 13 grandes catégories...",
            style={'textAlign': 'left', 'color': 'white', 'fontWeight': 'normal', 'paddingLeft': '50px', 'paddingRight': '50px'}
        ),
        html.Div(style={'display': 'flex', 'justifyContent': 'flex-start', 'alignItems': 'center', 'width': '100%', 'padding': '10px'}, children=[
            html.Div(style={'flex': '0 0 40%', 'padding': '10px'}, children=[
                dcc.Graph(id="pie-chart", style={'height': '600px', 'width': '100%'})
            ]),
            html.Div(style={'flex': '1', 'padding': '10px', 'textAlign': 'left'}, children=[
                dcc.Graph(id="histogram-chart", style={'height': '600px', 'width': '100%'})
            ]),
        ]),
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
            },
        ),
    ]
)

# Enregistrement des callbacks
def register_callbacks(app):
    @app.callback(
        Output("pie-chart", "figure"),
        Output("histogram-chart", "figure"),
        [Input("pie-chart", "clickData")]
    )
    def update_charts(click_data):
        data_manager = DataManager()
        genre_counts_df = data_manager.create_genre_count_dataframe()

        genre_counts_df['transformed_count'] = np.sqrt(genre_counts_df['total_count'])
        customdata = np.array(genre_counts_df[['total_count']])

        fig_pie = px.pie(
            genre_counts_df,
            names='genre',
            values='transformed_count',
            color='genre',
            color_discrete_map=genre_colors,
        )
        fig_pie.update_traces(
            textinfo='label',
            textposition='inside',
            customdata=customdata,
            hovertemplate='Nombre de musiques: %{customdata[0]} <br>Proportion: %{percent}'
        )
        fig_pie.update_layout(
            plot_bgcolor='black',
            paper_bgcolor='black',
            font_color='white',
            showlegend=False
        )

        selected_genre = "reggae"
        if click_data:
            selected_genre = click_data['points'][0]['label']

        df_subgenres = data_manager.get_top_subgenres_per_genre(selected_genre)
        df_subgenres = df_subgenres[df_subgenres['subgenre'] != selected_genre]

        fig_histogram = go.Figure()
        fig_histogram.add_trace(
            go.Bar(
                x=df_subgenres['count'][::-1],
                y=df_subgenres['subgenre'][::-1],
                orientation='h',
                marker=dict(color=genre_colors.get(selected_genre.lower(), 'white'))
            )
        )
        fig_histogram.update_layout(
            plot_bgcolor='black',
            paper_bgcolor='black',
            font_color='white',
            title=f"Répartition des sous-genres pour {selected_genre}",
            xaxis=dict(title="Nombre d'artistes"),
            yaxis=dict(title=None)
        )

        return fig_pie, fig_histogram
